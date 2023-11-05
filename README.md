
## Authenticate GCP environment

```bash
export PROJECT_ID=PROJECT_ID
export QUOTA_PROJECT_ID=QUOTA_PROJECT_ID

gcloud config set project $PROJECT_ID
gcloud auth application-default login
gcloud auth application-default set-quota-project $QUOTA_PROJECT_ID

```

## Integration Tests

Integration tests are located under `tests/*.yaml`, each test consists of set of question to feed to LLM in order appears in the test.

Output of tests are written to `tests_output/*.yaml`. To execute integration tests, make sure to authenticate with GCP environment, then run 

```bash
bash ./test.sh
```