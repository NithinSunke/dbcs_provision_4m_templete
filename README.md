# DBCS Provisioning Review and Approval App

This project provides a Flask-based web app that imports a DBCS provisioning Excel template, shows the entries in a review page, validates the input, and starts OCI DBCS deployment only after approval.

## What The App Does

- Imports Oracle-style provisioning templates and regular tabular Excel sheets
- Supports multiple database entries from the same workbook
- Shows imported values in the web UI for review before deployment
- Blocks approval when required values are missing or invalid
- Generates a new SSH key pair for every deployment
- Stores generated keys under `keys/<dbcs_name>/`
- Keeps execution history persistently in `data/batches.json`
- Supports dry run mode for safe testing
- Includes a Docker setup with OCI CLI available inside the container

## Project Structure

```text
.
|-- app.py
|-- run_server.py
|-- requirements.txt
|-- templates/
|-- static/
|-- docker/
|   |-- Dockerfile
|   |-- docker-compose.yml
|   `-- entrypoint.py
|-- data/
`-- keys/
```

## Prerequisites

Before running the app, make sure you have:

- Python 3.12 or later
- Access to the target OCI tenancy
- OCI API key and OCI config file
- A valid DBCS provisioning Excel workbook

For Docker-based execution, also install:

- Docker Desktop for Windows
- Docker Compose support

## Environment Configuration

Create the runtime file from the sample:

```powershell
Copy-Item .env.example .env
```

Current environment variables:

- `DRY_RUN=true`
  Uses simulated deployment responses and does not call OCI.
- `OCI_PROFILE=DEFAULT`
  OCI profile name from the OCI config file.
- `PORT=8080`
  Web application port.
- `OCI_CONNECT_TIMEOUT=10`
  OCI SDK connect timeout in seconds.
- `OCI_READ_TIMEOUT=45`
  OCI SDK read timeout in seconds.

Recommended values:

- Set `DRY_RUN=true` while validating templates and UI behavior
- Set `DRY_RUN=false` only when OCI config, IAM policy, subnet, shape, and compartment values are confirmed

## OCI Configuration

The app uses the OCI Python SDK and expects a working OCI config.

Typical host config location on Windows:

```text
C:\Users\<your-user>\.oci\config
```

Example profile:

```ini
[DEFAULT]
user=ocid1.user.oc1...
fingerprint=11:22:33:44:55:66:77:88:99:aa:bb:cc:dd:ee:ff:00
key_file=C:\Users\<your-user>\.oci\oci_api_key.pem
tenancy=ocid1.tenancy.oc1...
region=me-jeddah-1
```

If you run the app in Docker, keep a container-friendly profile in the same config file, for example:

```ini
[CONTAINER]
user=ocid1.user.oc1...
fingerprint=11:22:33:44:55:66:77:88:99:aa:bb:cc:dd:ee:ff:00
key_file=/root/.oci/oci_api_key.pem
tenancy=ocid1.tenancy.oc1...
region=me-jeddah-1
```

Then set:

```env
OCI_PROFILE=CONTAINER
```

## Local Setup And Run

### 1. Create and activate a virtual environment

```powershell
cd D:\automation_db_provisioning
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Create the environment file

```powershell
Copy-Item .env.example .env
```

### 4. Start the app

```powershell
python run_server.py
```

Open the UI in a browser:

```text
http://localhost:8080
```

## Docker Setup And Run

The Docker image includes:

- Python runtime for the app
- OCI CLI in a separate virtual environment
- PostgreSQL client tools
- Basic network troubleshooting tools

### 1. Verify `.env`

For container execution, set the profile to the container-safe OCI config profile:

```env
DRY_RUN=false
OCI_PROFILE=CONTAINER
PORT=8080
OCI_CONNECT_TIMEOUT=10
OCI_READ_TIMEOUT=45
```

### 2. Build the image

```powershell
cd D:\automation_db_provisioning\docker
docker compose build --no-cache
```

### 3. Start the container

```powershell
docker compose up -d
```

### 4. Verify the container is running

```powershell
docker ps
```

### 5. Open the app

```text
http://localhost:8080
```

### 6. Verify OCI CLI inside the container

```powershell
docker exec -it dbcs-app oci iam region list --profile CONTAINER
```

If OCI config is mounted correctly, the command should return a valid OCI response instead of a config or key error.

## How The Deployment Flow Works

### Step 1. Upload Excel template

You upload the workbook through the web page.

### Step 2. App parses the workbook

The app supports:

- Standard tabular Excel sheets with headers in row 1
- Oracle-style key/value provisioning templates

### Step 3. Review imported values

The app shows the parsed entries in the UI so they can be checked before deployment.

### Step 4. Validation runs

The app checks required values and prevents approval if important deployment fields are missing or malformed.

### Step 5. Approval triggers deployment

Once approved:

- A new SSH key pair is generated
- Keys are stored in `keys/<dbcs_name>/`
- OCI DBCS provisioning starts when `DRY_RUN=false`
- A simulated response is stored when `DRY_RUN=true`

### Step 6. History is saved

Execution details are stored in:

```text
data/batches.json
```

The history remains available after the app restarts.

## Supported Excel Input Formats

### Format 1. Tabular sheets

Use headers in row 1. Header names are normalized to lowercase with underscores.

Required fields:

- `display_name`
- `compartment_id`
- `subnet_id`
- `shape`
- `database_edition`
- `db_version`
- `db_name`
- `admin_password`
- `cpu_core_count`
- `data_storage_size_in_gbs`

Optional fields:

- `availability_domain`
- `hostname`
- `node_count`
- `license_model`
- `pdb_name`
- `db_workload`
- `ssh_public_keys`
- `nsg_ids`
- `character_set`
- `ncharacter_set`
- `auto_backup_enabled`

Notes:

- `availability_domain` can be left blank if you want OCI selection logic to decide the best availability domain
- `ssh_public_keys` can be comma-separated
- `nsg_ids` can be comma-separated

### Format 2. Oracle-style key/value template

For Oracle-style templates:

- Labels are typically in the first column
- Values are typically in the following columns
- Multiple database entries can exist in the same sheet
- Each database block is parsed as a separate deployment record

Important behavior:

- Availability domain may be blank
- New keys are always generated during deployment
- Backup time fractions are converted automatically to `HH:MM` UTC where applicable

## Database Editions Supported

The app accepts the DBCS editions supported by OCI DBCS payload mapping configured in the app. If needed, validate the exact edition values in your template against the current OCI DBCS API values used in your tenancy.

Common values typically used are:

- `ENTERPRISE_EDITION`
- `ENTERPRISE_EDITION_HIGH_PERFORMANCE`
- `ENTERPRISE_EDITION_EXTREME_PERFORMANCE`
- `STANDARD_EDITION`

## Persistence

The following folders are important at runtime:

- `data/`
  Stores deployment execution history
- `keys/`
  Stores generated SSH keys for each DBCS deployment

These folders are intentionally excluded from Git.

## Troubleshooting

### App opens but deployment does not start

Check:

- `DRY_RUN` is set to `false`
- OCI config is valid
- The selected OCI profile exists
- The target compartment, subnet, and shape are valid
- The user has IAM permissions to create DBCS

### OCI CLI works on host but not in Docker

Check:

- `${USERPROFILE}\.oci` is mounted into the container
- `OCI_PROFILE=CONTAINER` is set in `.env`
- The `CONTAINER` profile uses `/root/.oci/oci_api_key.pem`
- The key file exists on the host and is readable

### Only one database is shown after import

Check:

- The workbook really contains multiple value sections
- Each database block is filled consistently
- The template follows the expected Oracle-style layout

### Wrong storage type is being created

If OCI is creating Grid Infrastructure storage instead of the expected logical volume configuration, verify that the exact template field and final API payload value match the supported OCI DBCS parameter names. Storage model behavior depends on the payload sent to OCI, not only on the label visible in Excel.

### Docker push or GitHub push fails on Windows

Common fixes:

```powershell
git config --global --add safe.directory D:/automation_db_provisioning
git config --global http.sslBackend schannel
```

## Security Notes

- Do not commit `.env`, OCI keys, Excel files with passwords, generated keys, or runtime history
- Treat `admin_password` values in Excel as secrets
- Use a dedicated OCI user or limited-scope policy for automation where possible

## Recommended Next Improvements

- Add app login and role-based approval
- Store history in PostgreSQL instead of JSON
- Add detailed job logs per deployment
- Add retry and rollback handling
- Add background workers for long-running deployments
- Add GitHub Actions CI pipeline

