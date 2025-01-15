import string
import secrets


def generate_rand_secret(length: int, exclude_chars: str) -> str:
    """
    Generates a cryptographically secure random secret, excluding specified characters.
    """
    # Define the default character set
    all_characters = string.ascii_letters + string.digits + string.punctuation
    effective_characters = all_characters

    if exclude_chars:
        effective_characters = [
            char for char in all_characters if char not in exclude_chars
        ]

        # Check if the exclusion set doesn't leave us with too few characters
        if len(effective_characters) < length:
            raise ValueError(
                f"Excluding '{exclude_chars}' leaves insufficient characters to generate a {length}-character secret."
            )

    # Generate the secret using secrets.choice for cryptographically secure randomness
    return "".join(secrets.choice(effective_characters) for _ in range(length))
