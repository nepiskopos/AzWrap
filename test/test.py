import sys
import os
# import pytest - commented out as it's not needed for direct execution
import uuid
from typing import List, Dict, Any, Optional

# Add parent directory to path to import AzWrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from azwrap.wrapper import (
    Identity,
    Subscription,
    ResourceGroup,
    SearchService,
    SearchIndex,
    AIService,
    OpenAIClient,
    SearchIndexerManager,
    DataSourceConnection,
    Indexer,
    Skillset
)
from azure.core.exceptions import ClientAuthenticationError
import azure.search.documents.indexes.models as azsdim

from azwrap.config import(
    AZURE_TENANT_ID,
    AZURE_CLIENT_ID,
    AZURE_CLIENT_SECRET,
    AZURE_SUBSCRIPTION_ID,
    AZURE_RESOURCE_GROUP,
    AZURE_STORAGE_ACCOUNT_NAME,
    AZURE_STORAGE_CONTAINER_NAME,

    AZURE_SEARCH_SERVICE_NAME,
    AZURE_SEARCH_INDEX_NAME,

    AZURE_OPENAI_SERVICE_NAME,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
)

def get_identity() -> Identity:
    identity:Identity = Identity(AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
    print(f"{identity is not None = }")
    
    try:
        failed_attempt = Identity(AZURE_TENANT_ID, AZURE_CLIENT_ID, "mitsos")
        raise Exception("This should not be reached")
    except Exception as e:
        pass
    return identity

def get_subscription() -> Subscription:
    identity:Identity = get_identity()
    subscription:Subscription = identity.get_subscription(subscription_id=AZURE_SUBSCRIPTION_ID)
    print(f"{subscription is not None = }")
    try:
        failed_attempt = identity.get_subscription(subscription_id="mitsos")
        raise Exception("This should not be reached")
    except Exception as e:
        pass
    return subscription

def get_resource_group() -> ResourceGroup:
    subscription:Subscription = get_subscription()
    resource_group:ResourceGroup = subscription.get_resource_group(AZURE_RESOURCE_GROUP)
    print(f"{resource_group is not None = }")
    return resource_group

def get_search_service() -> SearchService:
    subscription:Subscription = get_subscription()
    resource_group:ResourceGroup = subscription.get_resource_group(AZURE_RESOURCE_GROUP)
    search_service:SearchService = subscription.get_search_service(AZURE_SEARCH_SERVICE_NAME)
    print(f"{search_service is not None = }")
    return search_service

def get_index() -> SearchIndex: 
    search_service:SearchService = get_search_service()
    index:SearchIndex = search_service.get_index(AZURE_SEARCH_INDEX_NAME)
    print(f"{index is not None = }")
    return index

def get_index_copy() -> SearchIndex:
    search_service:SearchService = get_search_service()
    index:SearchIndex = search_service.get_index(AZURE_SEARCH_INDEX_NAME + "_2")
    print(f"{index is not None = }")
    return index

def get_cognitive_sevices(): 
    subscription:Subscription = get_subscription()
    print(f"{subscription is not None = }")

    cognitive_services = subscription.get_cognitive_client()
    resource_group:ResourceGroup = subscription.get_resource_group(AZURE_RESOURCE_GROUP)
    aiservice:AIService = resource_group.get_ai_service(AZURE_OPENAI_SERVICE_NAME)

    openaiclient:OpenAIClient = aiservice.get_OpenAIClient(AZURE_OPENAI_API_VERSION)
    embeddings = openaiclient.generate_embeddings("Hello, how are you?")
    
    models = aiservice.get_models()
    model_details = [ AIService.get_model_details(model) for model in models ]  

    deployments = aiservice.get_deployments() 
    deployment_details = [ AIService.get_deployment_details(deployment) for deployment in deployments ]

    # to be fixed 
    #aiservice.update_deployment("test-deployment", capacity=12)  
    #aiservice.delete_deployment("test-deployment")
    #deployment = aiservice.create_deployment( "test-deployment", "gpt-4o")

    return cognitive_services

def get_storage_account():
    identity = Identity(AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
    subscription = identity.get_subscription(subscription_id=AZURE_SUBSCRIPTION_ID)
    resource_group = subscription.get_resource_group(AZURE_RESOURCE_GROUP)
    storage_account = resource_group.get_storage_account(AZURE_STORAGE_ACCOUNT_NAME)
    return storage_account

def get_containers():
    storage_account = get_storage_account()
    containers = storage_account.get_containers()
    return containers

def get_container():
    storage_account = get_storage_account()
    container = storage_account.get_container(AZURE_STORAGE_CONTAINER_NAME)
    return container

def get_blob_names():
    container = get_container()
    blob_names = container.get_blob_names()
    return blob_names    

# New functions for testing indexer functionality

def get_indexer_manager() -> SearchIndexerManager:
    """Get a SearchIndexerManager instance for testing"""
    search_service = get_search_service()
    indexer_manager = search_service.create_indexer_manager()
    print(f"{indexer_manager is not None = }")
    return indexer_manager

def test_get_data_source_connections():
    """Test getting all data source connections"""
    indexer_manager = get_indexer_manager()
    data_sources = indexer_manager.get_data_source_connections()
    print(f"Found {len(data_sources)} data source connections")
    for ds in data_sources:
        print(f"  - {ds.get_name()} (Type: {ds.data_source.type})")
    return data_sources

def test_create_data_source_connection():
    """Test creating a new data source connection"""
    indexer_manager = get_indexer_manager()
    storage_account = get_storage_account()
    
    # Create a unique name for the data source
    data_source_name = f"test-ds-{uuid.uuid4().hex[:8]}"
    
    # Create a container for the data source
    container = azsdim.SearchIndexerDataContainer(name=AZURE_STORAGE_CONTAINER_NAME)
    
    # Create the data source connection
    data_source = indexer_manager.create_data_source_connection(
        name=data_source_name,
        type="azureblob",
        connection_string=storage_account.connection_string_description,
        container=container
    )
    
    print(f"Created data source connection: {data_source.get_name()}")
    return data_source

def test_get_data_source_connection():
    """Test getting a specific data source connection"""
    # First create a data source
    data_source = test_create_data_source_connection()
    
    # Then try to get it
    indexer_manager = get_indexer_manager()
    retrieved_data_source = indexer_manager.get_data_source_connection(data_source.get_name())
    
    print(f"Retrieved data source connection: {retrieved_data_source.get_name()}")
    assert retrieved_data_source is not None
    assert retrieved_data_source.get_name() == data_source.get_name()
    
    return retrieved_data_source

def test_update_data_source_connection():
    """Test updating a data source connection"""
    # First create a data source
    data_source = test_create_data_source_connection()
    
    # Update the data source with a new container
    new_container = azsdim.SearchIndexerDataContainer(name=f"{AZURE_STORAGE_CONTAINER_NAME}-updated")
    updated_data_source = data_source.update(container=new_container)
    
    print(f"Updated data source connection: {updated_data_source.get_name()}")
    assert updated_data_source is not None
    assert updated_data_source.get_name() == data_source.get_name()
    assert updated_data_source.data_source.container.name == new_container.name
    
    return updated_data_source

def test_delete_data_source_connection():
    """Test deleting a data source connection"""
    # First create a data source
    data_source = test_create_data_source_connection()
    
    # Delete the data source
    data_source.delete()
    
    # Verify it's deleted
    indexer_manager = get_indexer_manager()
    deleted_data_source = indexer_manager.get_data_source_connection(data_source.get_name())
    
    print(f"Deleted data source connection: {data_source.get_name()}")
    assert deleted_data_source is None
    
    return True

def test_get_indexers():
    """Test getting all indexers"""
    indexer_manager = get_indexer_manager()
    indexers = indexer_manager.get_indexers()
    print(f"Found {len(indexers)} indexers")
    for indexer in indexers:
        print(f"  - {indexer.get_name()} (Target index: {indexer.indexer.target_index_name})")
    return indexers

def test_create_indexer():
    """Test creating a new indexer"""
    indexer_manager = get_indexer_manager()
    
    # First create a data source
    data_source = test_create_data_source_connection()
    
    # Create a unique name for the indexer
    # Use a UUID to ensure uniqueness
    uniqid = uuid.uuid4().hex[:8]
    indexer_name = f"test-indexer-{uniqid}"
    index_name = f"test-index-{uniqid}"
    indexer_manager.search_service.create_index(
        name=index_name,
        fields=[
            azsdim.SimpleField(name="id", type=azsdim.FieldType.String, key=True),
            azsdim.SimpleField(name="content", type=azsdim.FieldType.String)
        ]
    )
    print(f"Created index: {index_name}")
    # Create the indexer
    indexer = indexer_manager.create_indexer(
        name=indexer_name,
        data_source_name=data_source.get_name(),
        target_index_name=index_name
    )
    
    print(f"Created indexer: {indexer.get_name()}")
    return indexer

def test_get_indexer():
    """Test getting a specific indexer"""
    # First create an indexer
    indexer = test_create_indexer()
    
    # Then try to get it
    indexer_manager = get_indexer_manager()
    retrieved_indexer = indexer_manager.get_indexer(indexer.get_name())
    
    print(f"Retrieved indexer: {retrieved_indexer.get_name()}")
    assert retrieved_indexer is not None
    assert retrieved_indexer.get_name() == indexer.get_name()
    
    return retrieved_indexer

def test_run_indexer():
    """Test running an indexer"""
    # First create an indexer
    indexer = test_create_indexer()
    
    # Run the indexer
    indexer.run()
    
    print(f"Ran indexer: {indexer.get_name()}")
    return True

def test_reset_indexer():
    """Test resetting an indexer"""
    # First create an indexer
    indexer = test_create_indexer()
    
    # Reset the indexer
    indexer.reset()
    
    print(f"Reset indexer: {indexer.get_name()}")
    return True

def test_get_indexer_status():
    """Test getting the status of an indexer"""
    # First create an indexer
    indexer = test_create_indexer()
    
    # Get the status
    status = indexer.get_status()
    
    print(f"Indexer status: {status.status}")
    return status

def test_update_indexer():
    """Test updating an indexer"""
    # First create an indexer
    indexer = test_create_indexer()
    
    # Create a schedule
    schedule = azsdim.IndexingSchedule(interval=datetime.timedelta(days=1))
    
    # Update the indexer
    updated_indexer = indexer.update(schedule=schedule)
    
    print(f"Updated indexer: {updated_indexer.get_name()}")
    assert updated_indexer is not None
    assert updated_indexer.get_name() == indexer.get_name()
    assert updated_indexer.indexer.schedule is not None
    
    return updated_indexer

def test_delete_indexer():
    """Test deleting an indexer"""
    # First create an indexer
    indexer = test_create_indexer()
    
    # Delete the indexer
    indexer.delete()
    
    # Verify it's deleted
    indexer_manager = get_indexer_manager()
    deleted_indexer = indexer_manager.get_indexer(indexer.get_name())
    
    print(f"Deleted indexer: {indexer.get_name()}")
    assert deleted_indexer is None
    
    return True

def test_get_skillsets():
    """Test getting all skillsets"""
    indexer_manager = get_indexer_manager()
    skillsets = indexer_manager.get_skillsets()
    print(f"Found {len(skillsets)} skillsets")
    for skillset in skillsets:
        print(f"  - {skillset.get_name()}")
    return skillsets

def test_create_skillset():
    """Test creating a new skillset"""
    indexer_manager = get_indexer_manager()
    
    # Create a unique name for the skillset
    skillset_name = f"test-skillset-{uuid.uuid4().hex[:8]}"
    
    # Create a simple skill
    skill = azsdim.OcrSkill(
        name="test-ocr-skill",
        description="Test OCR skill",
        context="/document",
        inputs=[
            azsdim.InputFieldMappingEntry(
                name="image",
                source="/document/normalized_images/*"
            )
        ],
        outputs=[
            azsdim.OutputFieldMappingEntry(
                name="text",
                target_name="extractedText"
            )
        ]
    )
    
    # Create the skillset
    skillset = indexer_manager.create_skillset(
        name=skillset_name,
        skills=[skill],
        description="Test skillset"
    )
    
    print(f"Created skillset: {skillset.get_name()}")
    return skillset

def test_get_skillset():
    """Test getting a specific skillset"""
    # First create a skillset
    skillset = test_create_skillset()
    
    # Then try to get it
    indexer_manager = get_indexer_manager()
    retrieved_skillset = indexer_manager.get_skillset(skillset.get_name())
    
    print(f"Retrieved skillset: {retrieved_skillset.get_name()}")
    assert retrieved_skillset is not None
    assert retrieved_skillset.get_name() == skillset.get_name()
    
    return retrieved_skillset

def test_update_skillset():
    """Test updating a skillset"""
    # First create a skillset
    skillset = test_create_skillset()
    
    # Create a new skill
    new_skill = azsdim.KeyPhraseExtractionSkill(
        name="test-key-phrase-skill",
        description="Test key phrase extraction skill",
        context="/document",
        inputs=[
            azsdim.InputFieldMappingEntry(
                name="text",
                source="/document/content"
            )
        ],
        outputs=[
            azsdim.OutputFieldMappingEntry(
                name="keyPhrases",
                target_name="extractedKeyPhrases"
            )
        ]
    )
    
    # Update the skillset with the new skill
    updated_skillset = skillset.update(
        skills=[new_skill],
        description="Updated test skillset"
    )
    
    print(f"Updated skillset: {updated_skillset.get_name()}")
    assert updated_skillset is not None
    assert updated_skillset.get_name() == skillset.get_name()
    assert len(updated_skillset.skillset.skills) == 1
    assert updated_skillset.skillset.description == "Updated test skillset"
    
    return updated_skillset

def test_delete_skillset():
    """Test deleting a skillset"""
    # First create a skillset
    skillset = test_create_skillset()
    
    # Delete the skillset
    skillset.delete()
    
    # Verify it's deleted
    indexer_manager = get_indexer_manager()
    deleted_skillset = indexer_manager.get_skillset(skillset.get_name())
    
    print(f"Deleted skillset: {skillset.get_name()}")
    assert deleted_skillset is None
    
    return True

def test_end_to_end_indexer_workflow():
    """Test the complete indexer workflow"""
    # 1. Create a data source connection
    indexer_manager = get_indexer_manager()
    storage_account = get_storage_account()
    
    data_source_name = f"e2e-ds-{uuid.uuid4().hex[:8]}"
    container = azsdim.SearchIndexerDataContainer(name=AZURE_STORAGE_CONTAINER_NAME)
    
    data_source = indexer_manager.create_data_source_connection(
        name=data_source_name,
        type="azureblob",
        connection_string=storage_account.connection_string_description,
        container=container
    )
    print(f"1. Created data source: {data_source.get_name()}")
    
    # 2. Create a skillset
    skillset_name = f"e2e-skillset-{uuid.uuid4().hex[:8]}"
    skill = azsdim.OcrSkill(
        name="e2e-ocr-skill",
        description="E2E OCR skill",
        context="/document",
        inputs=[
            azsdim.InputFieldMappingEntry(
                name="image",
                source="/document/normalized_images/*"
            )
        ],
        outputs=[
            azsdim.OutputFieldMappingEntry(
                name="text",
                target_name="extractedText"
            )
        ]
    )
    
    skillset = indexer_manager.create_skillset(
        name=skillset_name,
        skills=[skill],
        description="E2E test skillset"
    )
    print(f"2. Created skillset: {skillset.get_name()}")
    
    # 3. Create an indexer
    uniqid = uuid.uuid4().hex[:8]
    indexer_name = f"e2e-indexer-{uniqid}"
    index_name = f"e2e-index-{uniqid}"
    indexer_manager.search_service.create_index(
        name=index_name,
        fields=[
            azsdim.SimpleField(name="id", type=azsdim.FieldType.String, key=True),
            azsdim.SimpleField(name="content", type=azsdim.FieldType.String)
        ]
    )
    print(f"Created index: {index_name}")
    
    # Create indexing parameters with the skillset
    parameters = azsdim.IndexingParameters(
        batch_size=100,
        max_failed_items=10,
        max_failed_items_per_batch=5
    )
    
    indexer = indexer_manager.create_indexer(
        name=indexer_name,
        data_source_name=data_source.get_name(),
        target_index_name=index_name,
        parameters=parameters
    )
    print(f"3. Created indexer: {indexer.get_name()}")
    
    # 4. Run the indexer
    try:
        indexer.run()
        print(f"4. Ran indexer: {indexer.get_name()}")
    except Exception as e:
        print(f"Error running indexer: {str(e)}")
    
    # 5. Get the indexer status
    try:
        status = indexer.get_status()
        print(f"5. Indexer status: {status.status}")
    except Exception as e:
        print(f"Error getting indexer status: {str(e)}")
    
    # 6. Clean up
    try:
        indexer.delete()
        print(f"6a. Deleted indexer: {indexer.get_name()}")
    except Exception as e:
        print(f"Error deleting indexer: {str(e)}")
    
    try:
        skillset.delete()
        print(f"6b. Deleted skillset: {skillset.get_name()}")
    except Exception as e:
        print(f"Error deleting skillset: {str(e)}")
    
    try:
        data_source.delete()
        print(f"6c. Deleted data source: {data_source.get_name()}")
    except Exception as e:
        print(f"Error deleting data source: {str(e)}")
    
    return True

if __name__ == "__main__":
    # Import required modules for test_update_indexer
    from datetime import datetime, timedelta
    
    # Test Containers 
    
    containers = get_containers()
    print(f"Found {len(containers)} containers")
    for container in containers:
        print(f"  - {container.name}")

    storage_account = get_storage_account()
    from azure.core.exceptions import ResourceNotFoundError
    container = storage_account.create_container("test-container")
    
    #get the worksing_docs_2 folder inside the current folder 
    files_folder = os.path.join(os.path.dirname(__file__), "..", "working_docs_3")

    #iterate through the files in the folder and print their names
    for root, dirs, files in os.walk(files_folder):
        for file in files:
            print(os.path.join(root, file))
    # Upload the files to the container
    for root, dirs, files in os.walk(files_folder):
        for file in files:
            file_path = os.path.join(root, file)
            blob_name = os.path.relpath(file_path, files_folder)
            container.upload_file(local_file_path=file_path, destination_blob_name=blob_name)

    pass 


    # from azwrap.wrapper import FolderProcessingResults, FolderProcessor
    # folder_processor = FolderProcessor(files_folder)

    # FolderProcessingResults = folder_processor.upload_directory(
    #     storage_account=storage_account,
    #     container_name="test-container")
    
    
    
    
    
    # try:
    #     storage_account.delete_container("test-container")
    # except ResourceNotFoundError as e:
    #     print(f"Error deleting container: {str(e)}")

    
    

    exit() 

    # Test the indexer functionality
    print("\n=== Testing SearchIndexerManager ===")
    indexer_manager = get_indexer_manager()
    
    print("\n=== Testing Data Source Connections ===")
    data_sources = test_get_data_source_connections()
    
    print("\n=== Testing Create Data Source Connection ===")
    data_source = test_create_data_source_connection()
    
    print("\n=== Testing Get Data Source Connection ===")
    retrieved_data_source = test_get_data_source_connection()
    
    print("\n=== Testing Update Data Source Connection ===")
    updated_data_source = test_update_data_source_connection()
    
    print("\n=== Testing Indexers ===")
    indexers = test_get_indexers()
    
    print("\n=== Testing Create Indexer ===")
    indexer = test_create_indexer()
    
    print("\n=== Testing Get Indexer ===")
    retrieved_indexer = test_get_indexer()
    
    print("\n=== Testing Get Indexer Status ===")
    status = test_get_indexer_status()
    
    print("\n=== Testing Run Indexer ===")
    test_run_indexer()
    
    print("\n=== Testing Reset Indexer ===")
    test_reset_indexer()
    
    print("\n=== Testing Update Indexer ===")
    updated_indexer = test_update_indexer()
    
    print("\n=== Testing Skillsets ===")
    skillsets = test_get_skillsets()
    
    print("\n=== Testing Create Skillset ===")
    skillset = test_create_skillset()
    
    print("\n=== Testing Get Skillset ===")
    retrieved_skillset = test_get_skillset()
    
    print("\n=== Testing Update Skillset ===")
    updated_skillset = test_update_skillset()
    
    print("\n=== Testing End-to-End Indexer Workflow ===")
    test_end_to_end_indexer_workflow()
    
    print("\n=== Testing Delete Skillset ===")
    test_delete_skillset()
    
    print("\n=== Testing Delete Indexer ===")
    test_delete_indexer()
    
    print("\n=== Testing Delete Data Source Connection ===")
    test_delete_data_source_connection()
    
    print("\n=== All tests completed successfully ===")
