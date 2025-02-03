"""Tests for auth/jwt_manager module"""

import json
import unittest
from datetime import timedelta, timezone
import datetime as dt
from freezegun import freeze_time

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from unittest.mock import patch

# Import the module to test
from whispr.server.auth import jwt_manager
from whispr.server.config import TOKEN_EXPIRATION_SECONDS, TOKEN_ALGORITHM

# A sample secret for testing purposes.
TEST_SECRET = "test_secret_key"

class JWTManagerTestCase(unittest.TestCase):
    """Unit tests for the JWT manager functions."""

    def setUp(self):
        """Reset the revoked tokens set before each test."""
        jwt_manager._revoked_tokens.clear()

    @freeze_time("2024-01-01 00:00:00+00:00")
    def test_generate_token_includes_exp_and_jti(self):
        """Test that generate_token adds expiration and jti to the payload with UTC-aware datetimes."""
        from datetime import datetime

        # datetime.now() will now return the frozen time.
        fixed_now = datetime.now(timezone.utc)
        payload = {"user_id": 123}
        token = jwt_manager.generate_token(payload.copy(), TEST_SECRET)
        decoded = jwt.decode(token, TEST_SECRET, algorithms=[TOKEN_ALGORITHM])
        self.assertIn("exp", decoded)
        self.assertIn("jti", decoded)

        # Verify jti is a valid UUID4.
        from uuid import UUID
        try:
            UUID(decoded["jti"], version=4)
        except ValueError:
            self.fail("jti is not a valid UUID4 string")

        # Calculate expected expiration timestamp.
        expected_exp = fixed_now + timedelta(seconds=TOKEN_EXPIRATION_SECONDS)
        self.assertAlmostEqual(
            decoded["exp"], int(expected_exp.timestamp()), delta=5,
            msg=f"Expected {int(expected_exp.timestamp())} but got {decoded['exp']}"
        )

    @freeze_time("2024-01-01 00:00:00+00:00")
    def test_renew_token_valid(self):
        """Test that renew_token creates a new token with extended expiration and new jti using UTC-aware time."""
        from datetime import datetime

        # Freeze time at the initial moment.
        fixed_now = datetime.now(timezone.utc)
        payload = {"user_id": 456}
        original_token = jwt_manager.generate_token(payload.copy(), TEST_SECRET)

        # Advance time by 1 second for renewal.
        new_time = fixed_now + timedelta(seconds=1)
        with freeze_time(new_time):
            new_token = jwt_manager.renew_token(original_token, TEST_SECRET)
            decoded_new = jwt.decode(new_token, TEST_SECRET, algorithms=[TOKEN_ALGORITHM])

        decoded_original = jwt.decode(original_token, TEST_SECRET, algorithms=[TOKEN_ALGORITHM])
        self.assertNotEqual(decoded_original.get("jti"), decoded_new.get("jti"))

        expected_new_exp = new_time + timedelta(seconds=TOKEN_EXPIRATION_SECONDS)
        self.assertAlmostEqual(
            decoded_new["exp"], int(expected_new_exp.timestamp()), delta=5,
            msg=f"Expected {int(expected_new_exp.timestamp())} but got {decoded_new['exp']}"
        )

    def test_validate_token_valid(self):
        """Test that a valid token is decoded correctly."""
        payload = {"user_id": 789}
        token = jwt_manager.generate_token(payload.copy(), TEST_SECRET)
        decoded = jwt_manager.validate_token(token, TEST_SECRET)
        self.assertEqual(decoded.get("user_id"), payload["user_id"])
        self.assertIn("jti", decoded)

    def test_validate_token_expired(self):
        """Test that validate_token raises ExpiredSignatureError for expired tokens."""
        payload = {"user_id": 101}
        # Manually set expiration to past time.
        past = dt.datetime.utcnow() - timedelta(seconds=10)
        payload["exp"] = past
        payload["jti"] = "dummy-jti"
        token = jwt.encode(payload, TEST_SECRET, algorithm=TOKEN_ALGORITHM)
        with self.assertRaises(ExpiredSignatureError):
            jwt_manager.validate_token(token, TEST_SECRET)

    def test_validate_token_invalid_signature(self):
        """Test that validate_token raises InvalidTokenError for tampered tokens."""
        payload = {"user_id": 202}
        token = jwt_manager.generate_token(payload.copy(), TEST_SECRET)

        # Split the token into header, payload, and signature.
        parts = token.split('.')
        self.assertEqual(len(parts), 3, "Token must have three parts separated by dots")

        # Tamper with the signature part explicitly.
        sig = parts[2]
        # Change the last character in the signature part.
        tampered_sig = sig[:-1] + ('a' if sig[-1] != 'a' else 'b')
        tampered_token = f"{parts[0]}.{parts[1]}.{tampered_sig}"

        with self.assertRaises(InvalidTokenError):
            jwt_manager.validate_token(tampered_token, TEST_SECRET)

    @patch("whispr.server.auth.jwt_manager.is_token_revoked", return_value=True)
    def test_validate_token_revoked(self, mock_revoked):
        """Test that validate_token raises an exception when token is revoked."""
        payload = {"user_id": 303}
        token = jwt_manager.generate_token(payload.copy(), TEST_SECRET)
        with self.assertRaises(Exception) as context:
            jwt_manager.validate_token(token, TEST_SECRET)
        self.assertIn("revoked", str(context.exception).lower())
        mock_revoked.assert_called()

    @patch("whispr.server.auth.jwt_manager.file_utils.write_file_atomic")
    def test_revoke_token(self, mock_write_atomic):
        """Test that revoke_token adds token jti to the revocation list and calls atomic file write."""
        payload = {"user_id": 404}
        token = jwt_manager.generate_token(payload.copy(), TEST_SECRET)
        decoded = jwt.decode(token, TEST_SECRET, algorithms=[TOKEN_ALGORITHM])
        jti = decoded.get("jti")
        self.assertNotIn(jti, jwt_manager._revoked_tokens)
        jwt_manager.revoke_token(token)
        self.assertIn(jti, jwt_manager._revoked_tokens)
        # Ensure atomic write was called for persistence.
        self.assertTrue(mock_write_atomic.called)

    @patch("whispr.server.auth.jwt_manager.file_utils.write_file_atomic")
    @patch("whispr.server.auth.jwt_manager.file_utils.read_file")
    def test_persist_and_load_tokens(self, mock_read_file, mock_write_atomic):
        """Test persist_token and load_persisted_tokens functions using file_utils mocks."""
        # Simulate no tokens file existing initially.
        with patch("os.path.exists", return_value=False):
            # Persist a token.
            test_token = "sample.token.value"
            jwt_manager.persist_token(test_token)
            self.assertTrue(mock_write_atomic.called)

        # Now simulate loading tokens from a file.
        tokens_list = ["token1", "token2"]
        mock_read_file.return_value = json.dumps(tokens_list)
        with patch("os.path.exists", return_value=True):
            loaded_tokens = jwt_manager.load_persisted_tokens()
            self.assertEqual(loaded_tokens, tokens_list)

    @patch("whispr.server.auth.jwt_manager.file_utils.write_file_atomic")
    def test_persist_token_file_error(self, mock_write_atomic):
        """Test persist_token raises an error when file_utils.write_file_atomic fails."""
        mock_write_atomic.side_effect = Exception("Write error")
        with patch("os.path.exists", return_value=False):
            with self.assertRaises(Exception) as context:
                jwt_manager.persist_token("token_error")
            self.assertIn("Write error", str(context.exception))
