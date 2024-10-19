## Whispr Usage Guide for Vault Type: GCP

Step 1: Authenticate to GCP using gcloud command:

```bash
gcloud auth application-default login
```

Step 2: Initialize a whispr configuration file for GCP.

```bash
whispr init gcp
```

Step 3: Define a `.env` file with secrets stored in GCP
```bash
DB_USERNAME=
DB_PASSWORD=
```

Step 4: Inject secrets into your app by running:
```bash
whispr run 'node script.js'
```

DB_USERNAME & DB_PASSWORD are now available in Node.js program environment.
