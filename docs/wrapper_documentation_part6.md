# AzWrap Indexer Documentation

## Overview

AzWrap now includes comprehensive support for Azure AI Search indexer capabilities. This includes managing data source connections, indexers, and skillsets through both a Python API and CLI commands.

## Python API

### SearchIndexerManager

The `SearchIndexerManager` class is the main entry point for working with indexer functionality:

```python
# Get a search service
search_service = resource_group.get_search_service("my-search-service")

# Create an indexer manager
indexer_manager = search_service.create_indexer_manager()
```

### Data Source Connections

Data source connections define where your data comes from:

```python
# List all data source connections
data_sources = indexer_manager.get_data_source_connections()

# Get a specific data source
data_source = indexer_manager.get_data_source_connection("my-data-source")

# Create a new data source connection
container = azsdim.SearchIndexerDataContainer(name="my-container")
data_source = indexer_manager.create_data_source_connection(
    name="my-data-source",
    type="azureblob",  # or "azuretable", "azuresql"
    connection_string="connection-string",
    container=container
)

# Update a data source connection
updated_ds = data_source.update(
    connection_string="new-connection-string",
    container=new_container
)

# Delete a data source connection
data_source.delete()
```

### Indexers

Indexers process your data sources and populate search indexes:

```python
# List all indexers
indexers = indexer_manager.get_indexers()

# Get a specific indexer
indexer = indexer_manager.get_indexer("my-indexer")

# Create a new indexer
schedule = azsdim.IndexingSchedule(interval=datetime.timedelta(days=1))
indexer = indexer_manager.create_indexer(
    name="my-indexer",
    data_source_name="my-data-source",
    target_index_name="my-index",
    schedule=schedule
)

# Run an indexer
indexer.run()

# Reset an indexer
indexer.reset()

# Get indexer status
status = indexer.get_status()

# Update an indexer
updated_indexer = indexer.update(
    schedule=new_schedule,
    parameters=new_parameters
)

# Delete an indexer
indexer.delete()
```

### Skillsets

Skillsets define AI enrichment steps for your data:

```python
# List all skillsets
skillsets = indexer_manager.get_skillsets()

# Get a specific skillset
skillset = indexer_manager.get_skillset("my-skillset")

# Create a new skillset
skills = [
    azsdim.EntityRecognitionSkill(
        inputs=[{"name": "text", "source": "/document/content"}],
        outputs=[{"name": "organizations", "targetName": "organizations"}]
    )
]
skillset = indexer_manager.create_skillset(
    name="my-skillset",
    skills=skills,
    description="My custom skillset"
)

# Update a skillset
updated_skillset = skillset.update(
    skills=new_skills,
    description="Updated skillset"
)

# Delete a skillset
skillset.delete()
```

## CLI Commands

AzWrap provides several CLI commands for working with indexers:

### Data Source Commands

```bash
# List data sources
azwrap list-data-sources -g my-resource-group -s my-search-service

# Create a data source
azwrap create-data-source -g my-resource-group -s my-search-service \
    --name my-data-source \
    --type azureblob \
    --connection-string "connection-string" \
    --container my-container
```

### Indexer Commands

```bash
# List indexers
azwrap list-indexers -g my-resource-group -s my-search-service

# Create an indexer
azwrap create-indexer -g my-resource-group -s my-search-service \
    --name my-indexer \
    --data-source my-data-source \
    --target-index my-index

# Run an indexer
azwrap run-indexer -g my-resource-group -s my-search-service \
    --name my-indexer

# Get indexer status
azwrap indexer-status -g my-resource-group -s my-search-service \
    --name my-indexer
```

### Skillset Commands

```bash
# List skillsets
azwrap list-skillsets -g my-resource-group -s my-search-service

# Create a skillset
azwrap create-skillset -g my-resource-group -s my-search-service \
    --name my-skillset \
    --skills skills.json