# AzWrap

A Python package that provides a streamlined wrapper for Azure resource management, making it easier to work with Azure services including:

- Azure Storage
- Azure AI Search
- Azure OpenAI

## Installation

```bash
pip install azwrap
```

## Configuration

AzWrap requires Azure credentials to be set either as environment variables or in a `.env` file:

```
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_SUBSCRIPTION_ID=your-subscription-id
```

## CLI Usage

Once installed, you can use the CLI to manage Azure resources:

```bash
# List all available subscriptions
azwrap list-subscriptions

# List resource groups in a subscription
azwrap list-resource-groups -s your-subscription-id

# List Azure AI Search services
azwrap list-search -s your-subscription-id

# List Azure OpenAI services
azwrap list-ai -s your-subscription-id
```

## Python API Usage

### Identity Management

```python
from azwrap import Identity

# Create an identity with your Azure credentials
identity = Identity(tenant_id, client_id, client_secret)

# Get a list of subscriptions
subscriptions = identity.get_subscriptions()

# Get a specific subscription
subscription = identity.get_subscription(subscription_id)
```

### Resource Management

```python
from azwrap import Subscription, ResourceGroup

# Work with resource groups
resource_group = subscription.get_resource_group(group_name)

# Create a new resource group
new_group = subscription.create_resource_group(group_name, location)
```

### Storage Management

```python
from azwrap import StorageAccount, Container

# Get a storage account
storage_account = resource_group.get_storage_account(account_name)

# Create a new storage account
new_account = resource_group.create_storage_account(account_name, location)

# Work with blob containers
container = storage_account.get_container(container_name)
blobs = container.get_blobs()
```

### Azure AI Search

```python
from azwrap import SearchService, SearchIndex, get_std_vector_search
from azure.search.documents.indexes.models import (
    SearchField, SearchFieldDataType, SimpleField, SearchableField
)

# Get a search service
search_service = subscription.get_search_service(service_name)

# Create a new search service
new_service = resource_group.create_search_service(name, location)

# Define fields for an index
fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="en.microsoft")
]

# Create a search index
index = search_service.create_or_update_index("my-index", fields)

# Add vector search capability
vector_search = get_std_vector_search()
```

### Azure OpenAI

```python
from azwrap import AIService, OpenAIClient

# Get an OpenAI service
ai_service = resource_group.get_ai_service(service_name)

# Get OpenAI client with Azure credentials
openai_client = ai_service.get_OpenAIClient(api_version="2023-05-15")

# Generate embeddings
embeddings = openai_client.generate_embeddings("Your text here", model="deployment-name")

# Generate chat completions
response = openai_client.generate_chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about Azure."}
    ],
    model="deployment-name",
    temperature=0.7,
    max_tokens=800
)
```

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/yourusername/azwrap.git
cd azwrap

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies for development
uv sync

# Build the package
python -m build

# Install in development mode
pip install -e .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.