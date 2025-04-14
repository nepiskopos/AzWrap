import sys
import os
import logging
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path to import AzWrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import AzWrap classes
from AzWrap.wrapper import (
    Identity,
    Subscription,
    ResourceGroup,
    StorageAccount,
    Container,
    BlobType,
    SearchService,
    SearchIndex,
    get_std_vector_search
)

from dotenv import load_dotenv
load_dotenv(r'C:\Users\mkatsili\projects\AzWrap\.env')

# Get environment variables
AZURE_TENANT_ID = os.getenv('AZURE_TENANT_ID')
AZURE_CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
AZURE_CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')
AZURE_SUBSCRIPTION_ID = os.getenv('AZURE_SUBSCRIPTION_ID')
AZURE_RESOURCE_GROUP = os.getenv('AZURE_RESOURCE_GROUP')
AZURE_STORAGE_ACCOUNT_NAME = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
AZURE_STORAGE_CONTAINER_NAME = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
AZURE_SEARCH_SERVICE_NAME = os.getenv('AZURE_SEARCH_SERVICE_NAME')
AZURE_INDEX_NAME = os.getenv('AZURE_INDEX_NAME')

# Import Azure Search specific models for defining fields
from azure.search.documents.indexes.models import (
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Main function that demonstrates:
    1. Reading a DOCX file from blob storage
    2. Creating a basic index in Azure AI Search
    3. Uploading the content to the index
    """
    logger.info("Starting search workflow demonstration")
    
    try:
        # Step 1: Set up authentication and get resources
        logger.info("Setting up authentication and accessing resources")
        
        # Create Identity object for authentication with Azure
        identity = Identity(AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
        logger.info("Identity created successfully")
        
        # Get subscription
        subscription = identity.get_subscription(AZURE_SUBSCRIPTION_ID)
        logger.info(f"Accessed subscription: {subscription.subscription_id}")
        
        # Step 2: Get resource group
        # Check if resource group name is provided
        if not AZURE_RESOURCE_GROUP:
            logger.info("AZURE_RESOURCE_GROUP not specified in environment variables, listing available resource groups")
            resource_groups = subscription.get_resource_groups()
            if not resource_groups:
                logger.error("No resource groups found in the subscription")
                return
                
            # Use the first resource group found
            resource_group = resource_groups[0]
            resource_group_name = resource_group.get_name()
            logger.info(f"Using first available resource group: {resource_group_name}")
        else:
            # Get specified resource group
            resource_group = subscription.get_resource_group(AZURE_RESOURCE_GROUP)
            if not resource_group:
                logger.error(f"Resource group '{AZURE_RESOURCE_GROUP}' not found")
                return
            resource_group_name = resource_group.get_name()
            logger.info(f"Accessed resource group: {resource_group_name}")
        
        # Step 3: Access storage account and container
        # Check if storage account name is provided
        if not AZURE_STORAGE_ACCOUNT_NAME:
            logger.info("AZURE_STORAGE_ACCOUNT_NAME not specified in environment variables, listing available storage accounts")
            storage_accounts = resource_group.get_storage_accounts()
            if not storage_accounts:
                logger.error("No storage accounts found in the resource group")
                return
                
            # Use the first storage account found
            storage_account = storage_accounts[0]
            logger.info(f"Using first available storage account: {storage_account.get_name()}")
        else:
            # Get specified storage account
            storage_account = resource_group.get_storage_account(AZURE_STORAGE_ACCOUNT_NAME)
            if not storage_account:
                logger.error(f"Storage account '{AZURE_STORAGE_ACCOUNT_NAME}' not found")
                return
            logger.info(f"Accessed storage account: {storage_account.get_name()}")
        
        # Check if container name is provided
        if not AZURE_STORAGE_CONTAINER_NAME:
            logger.info("AZURE_STORAGE_CONTAINER_NAME not specified in environment variables, listing available containers")
            containers = storage_account.get_containers()
            if not containers:
                logger.error("No containers found in the storage account")
                return
                
            # Use the first container found
            container = containers[0]
            logger.info(f"Using first available container: {container.get_name()}")
        else:
            # Get specified container
            container = storage_account.get_container(AZURE_STORAGE_CONTAINER_NAME)
            if not container:
                logger.error(f"Container '{AZURE_STORAGE_CONTAINER_NAME}' not found")
                return
            logger.info(f"Accessed container in storage account")
        
        # Step 4: Find a DOCX file in the container
        logger.info("Searching for DOCX files in the container")
        
        # List all blobs in the container
        blob_names = container.get_blob_names()
        
        # Filter for DOCX files
        docx_files = [blob for blob in blob_names if blob.lower().endswith('.docx')]
        
        if not docx_files:
            logger.error("No DOCX files found in the container")
            return
        
        # Select the first DOCX file for demonstration
        target_file = docx_files[0]
        logger.info(f"Found DOCX file: {target_file}")
        
        # Step 5: Read the DOCX file content
        logger.info(f"Reading content from file: {target_file}")
        
        # Use the process_blob_by_type method which handles DOCX files appropriately
        docx_content = container.process_blob_by_type(target_file)
        
        if not docx_content:
            logger.error("Failed to extract content from DOCX file")
            return
        
        logger.info(f"Successfully extracted {len(docx_content)} characters from the document")
        
        # Step 6: Access or create the search service
        # Check if search service name is provided
        if not AZURE_SEARCH_SERVICE_NAME:
            logger.info("AZURE_SEARCH_SERVICE_NAME not specified in environment variables, listing available search services")
            search_services = subscription.get_search_services()
            if not search_services:
                logger.error("No search services found in the subscription")
                return
                
            # Use the first search service found
            search_service = SearchService(resource_group, search_services[0])
            logger.info(f"Using first available search service: {search_services[0].name}")
        else:
            # Get specified search service
            search_service = subscription.get_search_service(AZURE_SEARCH_SERVICE_NAME)
            if not search_service:
                logger.error(f"Search service '{AZURE_SEARCH_SERVICE_NAME}' not found")
                return
            logger.info(f"Accessed search service: {search_service.get_service_endpoint()}")
        
        # Step 7: Define and create the search index
        # Generate a test index name if not provided
        if not AZURE_INDEX_NAME:
            test_index_name = f"test_index_{datetime.now().strftime('%Y%m%d%H%M')}"
        else:
            test_index_name = f"{AZURE_INDEX_NAME}_test_{datetime.now().strftime('%Y%m%d%H%M')}"
            
        logger.info(f"Creating search index: {test_index_name}")
        
        # Define index fields
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="content", type=SearchFieldDataType.String, 
                          analyzer_name="en.microsoft"),
            SimpleField(name="filename", type=SearchFieldDataType.String, 
                        filterable=True, sortable=True),
            SimpleField(name="timestamp", type=SearchFieldDataType.DateTimeOffset, 
                        filterable=True, sortable=True)
        ]
        
        # Add vector search capability if needed
        vector_search = get_std_vector_search()
        
        # Create or update index
        index = search_service.create_or_update_index(test_index_name, fields, vector_search)
        logger.info(f"Created search index: {test_index_name}")
        
        # Step 8: Upload document content to the index
        logger.info("Uploading document content to the search index")
        
        # Create document to index
        document = {
            "id": f"doc_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "content": docx_content,
            "filename": target_file,
            "timestamp": datetime.utcnow().isoformat() + 'Z'  # Adding Z to indicate UTC timezone
        }
        
        # Use the upload_documents method to add the document to the index
        results = index.upload_documents([document])
        
        # Check if upload was successful
        succeeded = sum(1 for r in results if r.succeeded)
        errors = [r.error_message for r in results if not r.succeeded]
        
        if succeeded > 0:
            logger.info(f"Document uploaded successfully to index {test_index_name}")
            logger.info(f"Upload statistics: {succeeded} succeeded, {len(results) - succeeded} failed")
        else:
            logger.error(f"Document upload failed: {errors}")
        
        # Step 9: Perform a simple search to verify (optional)
        logger.info("Performing a simple search to verify indexing")
        
        # Extract some sample text to search for
        sample_text = docx_content[:50].split()[0] if len(docx_content) > 50 else docx_content
        
        # Perform search
        search_results = index.perform_search(query_text=sample_text, top=1, highlight_fields="content")
        
        # Check results
        result_count = search_results.get_count()
        logger.info(f"Search for '{sample_text}' returned {result_count} results")
        
        for result in search_results:
            logger.info(f"Found document: {result['filename']}")
        
        logger.info("Search workflow demonstration completed successfully")
        
    except Exception as e:
        logger.error(f"Error in search workflow: {str(e)}")
        raise

if __name__ == "__main__":
    main()