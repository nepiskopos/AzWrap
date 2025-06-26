# AzWrap Table Storage Integration

The `Table` class provides access to Azure Table Storage resources through a connected `StorageAccount` class. It enables listing, creating, deleting tables, and performing entity-level operations (insert, delete, retrieve) using data from CSV files.

### Hierarchy

`Identity → Subscription → ResourceGroup → StorageAccount → Table`

### Requirements

- Azure Storage Account with Table service enabled
- `azure-data-tables` Python package
- CSV files formatted with expected schema in utf-8 encoding and pipe delimiter


## Installation

The Table Storage integration requires the `azure-data-tables ` package:

```bash
pip install azure-data-tables==12.7.0
```

This dependency is automatically included when installing AzWrap:

```bash
pip install azwrap
```

## Usage

### Getting a Table Storage Service

```python
from azwrap import Identity, Subscription, ResourceGroup, DocumentIntelligenceService

# Create an identity with your Azure credentials
identity = Identity(tenant_id, client_id, client_secret)

# Get a subscription
subscription = identity.get_subscription(subscription_id)

# Get a resource group
resource_group = subscription.get_resource_group(group_name)

# Get a Document Intelligence service
doc_intelligence = resource_group.get_document_intelligence_service(service_name)

# Get Storage Account service
storage_account = resource_group.get_storage_account(strogage_account_name)

# Get Storage Tables client
tables_client = storage_account.get_tables_client()
```
