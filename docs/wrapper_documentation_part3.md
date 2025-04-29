### Storage Services

#### StorageAccount Class

The `StorageAccount` class represents an Azure Storage Account and provides methods to work with blob storage.

**Purpose**: Manage blob storage containers and access blob data.

**Key Attributes**:
- `resource_group`: Reference to the ResourceGroup object
- `storage_account`: Azure storage account object
- `storage_key`: Storage account access key
- `connection_string_description`: Connection string for the storage account

**Key Methods**:
- `get_name()`: Gets the name of the storage account
- `get_blob_service_client()`: Gets a blob service client
- `get_containers()`: Lists all containers in the storage account
- `get_container(container_name)`: Gets a specific container by name

**Usage Example**:
```python
# Get the storage account name
account_name = storage_account.get_name()

# List all containers
containers = storage_account.get_containers()
for container in containers:
    print(f"Container: {container.name}")

# Get a specific container
container = storage_account.get_container("my-container")
```

#### Container Class

The `Container` class represents a blob container in Azure Storage.

**Purpose**: Access and manage blobs within a container.

**Key Attributes**:
- `storage_account`: Reference to the StorageAccount object
- `container_client`: Azure container client object

**Key Methods**:
- `get_blob_names()`: Lists all blob names in the container
- `get_blobs()`: Lists all blobs with their properties
- `process_blob_by_type(blob_name)`: Processes blob files of type "MS_WORD", "MS_EXCEL", "PDF", or just plain text, and returns their content in the appropriate format

**Usage Example**:
```python
# List all blob names in the container
blob_names = container.get_blob_names()
for name in blob_names:
    print(f"Blob: {name}")

# Get all blobs with properties
blobs = container.get_blobs()
for blob in blobs:
    print(f"Blob: {blob.name}, Size: {blob.size} bytes")
```

### Search Services

#### SearchService Class

The `SearchService` class represents an Azure AI Search service and provides methods to manage search indexes.

**Purpose**: Manage search indexes and perform search operations.

**Key Attributes**:
- `resource_group`: Reference to the ResourceGroup object
- `search_service`: Azure search service object
- `index_client`: Azure search index client
- `search_client`: Azure search client
- `openai_client`: OpenAI client for vector search

**Key Methods**:
- `get_admin_key()`: Gets the admin key for the search service
- `get_credential()`: Gets an Azure credential for the search service
- `get_service_endpoint()`: Gets the service endpoint URL
- `get_index_client()`: Gets a search index client
- `get_indexes()`: Lists all indexes in the search service
- `get_index(index_name)`: Gets a specific index by name
- `add_simple_field(field_args)`: Execute the Azure "SimpleField" function
- `add_searchable_field(field_args)`: Execute the Azure "SearchableField" function
- `add_search_field(field_args)`: Return a "SearchField" object
- `create_or_update_index(index_name, fields)`: Creates or updates an index
- `add_semantic_configuration(config_args)`: Adds semantic search configuration to an index

**Usage Example**:
```python
# Get the service endpoint
endpoint = search_service.get_service_endpoint()

# List all indexes
indexes = search_service.get_indexes()
for index in indexes:
    print(f"Index: {index.name}")

# Get a specific index
index = search_service.get_index("my-index")

# Add SearchFields
fields = [
    search_service.add_simple_field("id", "String", searchable=True, filterable=True, retrievable=True, is_key=True),
    search_service.add_searchable_field("content_field", "String", searchable=True, filterable=True, retrievable=True),
    search_service.add_search_field("vector_field", "Collection(Edm.Single)", searchable=True,
                        vector_search_dimensions=3072, vector_search_profile_name="vector_search_profile_name")
]

# Create or update an index
index = search_service.create_or_update_index("my-index", fields)

# Add semantic configuration
search_service.add_semantic_configuration(
    index_name="my-index",
    title_field="title",
    content_fields=["content"],
    keyword_fields=["keywords"],
    semantic_config_name="semantic_config_name"
)
```

#### SearchIndex Class

The `SearchIndex` class represents an index in Azure AI Search and provides methods for search operations.

**Purpose**: Perform search operations and manage index data.

**Key Attributes**:
- `search_service`: Reference to the SearchService object
- `index_name`: Name of the index
- `fields`: List of fields in the index
- `vector_search`: Vector search configuration
- `azure_index`: Azure search index object

**Key Methods**:
- `get_search_client()`: Gets a search client for the index
- `extend_index_schema(new_fields)`: Extends the index schema with new fields
- `process_data_in_batches()`: Processes data in batches for large operations
- `upload_rows()`: Directly uploads documents to new rows of the specified Index
- `copy_index_data()`: Copies data from one index to another
- `copy_index_structure()`: Copies the structure of the index to a new index
- `perform_search()`: Performs a basic search
- `search_with_context_window()`: Performs a search with context window
- `perform_hybrid_search()`: Performs a hybrid search (keyword + vector)

**Usage Example**:
```python
# Get a search client
search_client = index.get_search_client()

# Extend the index schema with new fields
new_fields = [
    search_service.add_simple_field(name="category", type=SearchFieldDataType.String, filterable=True)
]

index.extend_index_schema(new_fields)

# Perform a basic search
results = index.perform_search(
    search_text="example query",
    top=10
)

for result in results:
    print(f"Result: {result['id']}, Score: {result['@search.score']}")

# Perform a hybrid search (keyword + vector)
results = index.perform_hybrid_search(
    query_text="example query",
    query_vector=[0.1, 0.2, 0.3, ...],  # Vector embedding
    display_fields=["content_field"],
    search_fields=["content_field"],
    include_total_count=True,
    filter_by="additional_content_field",
    filter_vals=["value_to_check"],
    vector_fields=["vector_field"],
    use_semantic_search=True,
    top=10,
    vectorized_query_kind=vectorized_query_kind,
    exhaustive=True,
    k_nearest_neighbors_vector_search=5,
    semantic_config_name="semantic_config_name",
    query_answer="exhaustive",
    search_options=None
)