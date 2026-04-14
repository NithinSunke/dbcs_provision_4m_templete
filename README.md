# DBCS Provisioning Review + Approval Web App

This app lets you:
1. Upload an Excel provisioning sheet.
2. Review rows in a web page.
3. Approve the batch.
4. Trigger DBCS provisioning only after approval.
5. Parse both tabular sheets and Oracle-style key/value templates.
6. Persist execution history and show past batches after restart.

## Quick Start

```powershell
cd D:\automation_db_provisioning
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Open: `http://localhost:8080`

## Expected Excel Columns

Use headers in row 1. They are normalized to lowercase with underscores.

Required:
- `display_name`
- `compartment_id`
- `availability_domain`
- `subnet_id`
- `shape`
- `database_edition`
- `db_version`
- `db_name`
- `admin_password`
- `cpu_core_count`
- `data_storage_size_in_gbs`

Optional (recommended):
- `hostname`
- `node_count`
- `license_model`
- `pdb_name`
- `db_workload`
- `ssh_public_keys` (comma-separated)
- `nsg_ids` (comma-separated)
- `character_set`
- `ncharacter_set`
- `auto_backup_enabled` (`true/false`)

## Oracle Key/Value Template Support

If your sheet is Oracle-style (labels in column A and values in column B), the app maps key fields automatically.
You can include multiple database blocks in the same sheet; each block starts at `Database Basic Details` and is treated as one deployment row.

Important:
- `Compartment` and subnet fields must eventually resolve to OCIDs (`ocid1...`) before approval/deploy.
- `Availability domain` can be left blank; app auto-selects one during deploy.
- App always generates a new SSH key pair per deployment and stores it in `keys/<dbcs_name>/`.
- Excel backup time fractions are auto-converted to `HH:MM` UTC.
- Validation blocks approval if required deploy fields are missing or OCIDs are invalid.

## Deployment Modes

- `DRY_RUN=true`: Simulates provisioning and returns fake OCIDs.
- `DRY_RUN=false`: Calls OCI `launch_db_system` API using OCI SDK.

## OCI Prerequisites for Real Deploy

1. Configure OCI CLI/SDK profile in `~/.oci/config`.
2. Ensure IAM policy allows DBCS create actions in target compartment.
3. Verify your Excel values match OCI expectations for shape, AD, subnet, etc.

## Important Notes

- Execution details are stored persistently in `data/batches.json` and shown as history on the home page.
- For production, add authentication, DB persistence, audit logs, and approval roles.
- This is intended as a starter automation framework you can harden.
