## Programmatic access of Whispr

In addition to installing Whispr as a tool, one can make use of core utility functions like this:

```bash
pip install whispr
```

Then from Python code you can import important functions like this:

```py
from whispr.utils.vault import fetch_secrets
from whispr.utils.process import execute_command

config = {
  "vault": "aws",
  "secret_name": "<your_secret_name>"
}

secrets = fetch_secrets(config)

# Now, inject secrets into your command's environment by calling this function
command = "ls -l"
execute_command(command.split(), no_env=False, secrets=secrets)
```

That's it. This is a programmatic equivalent to the tool usage.
