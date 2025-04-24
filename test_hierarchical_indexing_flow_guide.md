# Hierarchical Indexing Guide

## Environmental Variables

Ensure the following variables are added to the `.env` file:

* `AZURE_TENANT_ID`
* `AZURE_CLIENT_ID`
* `AZURE_CLIENT_SECRET`
* `SUBSCRIPTION_NAME`
* `RESOURCE_GROUP_NAME`
* `AI_SERVICE_ACCOUNT_NAME`
* `AI_SEARCH_ACCOUNT_NAME`
* `INDEXING_TEMPLATE_PATH`
* `INDEX-CORE`
* `INDEX-DETAIL`
* `AZURE_STORAGE_ACCOUNT_NAME`
* `AZURE_CONTAINER`

## Run Pipeline script

In order to run `hierarchical_indexing_flow.py` , execute the below command inside the `pipelines` directory:

`python hierarchical_indexing_flow.py`