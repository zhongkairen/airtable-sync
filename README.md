[![Unit Tests Status](https://github.com/zhongkairen/airtable-sync/actions/workflows/run-unit-tests.yml/badge.svg)](https://github.com/zhongkairen/airtable-sync/actions/workflows/run-unit-tests.yml)
[![flake8 lint](https://github.com/zhongkairen/airtable-sync/actions/workflows/flake8-lint.yml/badge.svg)](https://github.com/zhongkairen/airtable-sync/actions/workflows/flake8-lint.yml)
[![](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/zhongkairen/26163c99522a7bff93750c3a1a13d879/raw/airtable-sync.coverage.badge.json)]()
[![](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/zhongkairen/26502e2a8b93eedb9cd15229cdee4c59/raw/airtable-sync.status.json?cache=sdfs1)](https://github.com/zhongkairen/airtable-sync/actions/workflows/airtable-sync.yml)

# airtable_sync - Sync between GitHub and Airtable
A Python module to sync GitHub issues to Airtable records.


# What this does
The module first checks the records in a table in an Airtable base, find the linked issues on GitHub and retries the fields that have changed, then it syncs the new values of the updated fields to Airtable.

Currently only a single GitHub repository is checked against the records in the Airtable base, even though sources from different repos can exist in that base, i.e. projects or initiatives from different teams.

## Installation and Setup
Unless otherwise stated, all the commands are run in the parent directory of the package, i.e. one level up from this file.
### Setting up Python
See [details in doc](doc/py-env.md)

### Installing dependencies
Download the wheel file and install with pip:
```
pip install airtable_sync-0.1.0-py3-none-any.whl
```

## Running the tool
### Create Airtable access token
Go to `https://airtable.com/create/tokens`, and create a new personal access token with the name `airtable.records_wr.schema_base_r.github_sync_base.pat`, select the following access scopes:
```
data.records:read
data.records:write
schema.bases:read
```
Add base `GitHub Sync Base`, then click `Save changes` button.\
❗Make sure you copy the PAT immediately when prompted, the key won't re-appear after the prompt is dismissed.\
Create a pat file by pasting into the terminal:
```bash
echo "pat0K7pydcykHdApk.0fadd0a9<replace with your own token>" > ~/.ssh/airtable.records_wr.schema_base_r.github_sync_base.pat
```
Set the proper file permission.
```bash
chmod 600 ~/.ssh/airtable.records_wr.schema_base_r.github_sync_base.pat
```
### Create GitHub access token
Go to GitHub personal account settings » Developer settings » Personal access tokens » Fine-grained tokens, click `Generate new token` to create a fine-grained personal access token with the name `gh.read.repo.project.pat`,
**Resource owner**: `Unity-Technologies` \
**Repository access**: Check _Only select repositories_, then choose `Unity-Technologies/mz-<your>-team`

Use the following access scopes \
**Repository permissions**: `Issues` and `Metadata` as Read-only access. \
**Organization permissions**: `Projects` as Read-only access. \
❗Make sure you copy the token text immediately when prompted, the key won't re-appear after the prompt is dismissed.\
Create a pat file by pasting into the terminal:
```bash
echo "github_pat_<replace with your own token>" > ~/.ssh/gh.read.repo.project.pat
```
Set the proper file permission.
```bash
chmod 600 ~/.ssh/gh.read.repo.project.pat
```
### Configuration file
To use the module, a `config.json` file must be placed in either the current working directory or the package installation directory.

**Example configuration file**\
An example `config.json` file is provided in the root directory of the source package.

1. **Copy** the example file to your chosen location.
1. **Edit** the file as needed to fit your setup.

See the following sections for details on which settings to change.

### Set up tokens
Create environment variables
```bash
export GITHUB_TOKEN_PATH=/path/to/your/airtable.records_wr.schema_base_r.github_sync_base.pat
export AIRTABLE_TOKEN_PATH=/path/to/your/gh.read.repo.project.user.pat
```
Replace with proper file names if you in the earlier step with different names.

Alternatively put tokens directly in the file, not recommended as it's less secure.\
❗`Example`❗
```bash
export GITHUB_TOKEN=ghp_2n45dH8TJ3QrZ9b1hYV0Ck6Fp8AeGz5wXm
export AIRTABLE_TOKEN=pat4KwZLQ5yFmsJDa.22cd1ec678943216ae4b874f1d8814223c71a56d9d58371c0b1f8b3ef9e4a2f
```

If nothing has been exported to env, similar configuration can be done in `config.json`.
```json
  "github": {
    "token_path": "/path/to/your/gh.read.repo.project.user.pat",
  }
```
or directly using the token
```json
"airtable": {
  "token": "pat4KwZLQ5yFmsJDa.22cd1ec678943216ae4b874f1d8814223c71a56d9d58371c0b1f8b3ef9e4a2f",
}
```

#### GitHub secrets
To run a workflow that automates the sync, add the tokens to GitHub repo settings as secrets.
Go to your repo, e.g. `mz-ad-request-team` Settings tab » Secrets and variables » Actions, in Repository secrets section click `New repository secret`. The names of the secret should be consistent with variable names in the workflow `airtable-sync.yml`.
```yaml
env:
    GITHUB_TOKEN: ${{ secrets.AIRSYNC_GITHUB_TOKEN }}
    AIRTABLE_TOKEN: ${{ secrets.AIRSYNC_AIRTABLE_TOKEN }}
```
e.g. for a GitHub token, create a secret with the name `AIRSYNC_GITHUB_TOKEN` in the `Name *` field, then paste the token into the `Secret *` field.
Repeat the same also for the Airtable token.

### Configure GitHub and Airtable parameters
Change `config.json`, the base ID and table ID as needed, e.g. if your Airtable base has a URL `https://airtable.com/apptII3QtVU8j387f/tblWNyuu51KBQevsR/viw5GukP9N2HNuL2A?blocks=hide`, the base ID is the part that starts with `app` and table ID is the part that starts with `tbl`.
```json
{
    "airtable": {
        "baseId": "apptII3QtVU8j387f",
        "tableId": "tblWNyuu51KBQevsR"
    },
    ...
}
```

Change the repo name and project name as needed, e.g. if your GitHub repo base has a URL `https://github.com/Unity-Technologies/mz-ds-deep-learning`, the repo name is the last part, while as the project name is one of those that can be found in the `Projects` tab of your repo.
```json
{
    ...
    "github": {
        "owner": "Unity-Technologies",
        "repo": "mz-ds-deep-learning",
        "project": "ML Engineering"
    }
}
```

### Run
Run with the module name
```
python -m airtable_sync
```
Alternatively run directly with the command
```
airtable-sync
```

Need to ensure the Python bin folder is in the `PATH`.
```
DIR=$(dirname $(which python3));echo $PATH | grep -q "$DIR" && echo "In PATH" || echo "$DIR not in PATH"
```
