import sys
import os
import json
import logging
import codecs
from typing import Dict, Any, List, Optional, Tuple, Union
from io import BytesIO
from datetime import datetime

from AzWrap.wrapper import Container, DocParsing, MultiProcessHandler, OpenAIClient
import azure.search.documents.indexes.models as azsdim
from docx import Document

sys.path.append(os.path.abspath(".."))

from dotenv import load_dotenv
from azure.search.documents.indexes.models import SearchField, SimpleField, SearchableField, SearchFieldDataType

# Import the logger module
from logger import get_logger

# Set up logger
logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
logger = get_logger(
    logger_name="hierarchical_indexing_flow",
    log_file="hierarchical_indexing.log",
    log_dir=logs_dir
)

class HierarchicalIndexingFlow:
    """
    A class to manage the hierarchical indexing workflow for Azure Cognitive Search.
    This class handles the creation of indices, processing of documents, and uploading 
    of records to Azure Cognitive Search.
    """
    
    def __init__(self, search_service, vector_search_profile_name="vector-search-profile"):
        """
        Initialize the HierarchicalIndexingFlow with a search service.
        
        Args:
            search_service: The Azure Cognitive Search service
            vector_search_profile_name: The name to use for vector search profile configuration
        """
        self.search_service = search_service
        self.vector_search_profile_name = vector_search_profile_name
        self.failed_files = []
        
    def _validate_config(self, indexing_format: str, semantic_config: Dict[str, Any]) -> None:
        """
        Validate configuration parameters.
        
        Args:
            indexing_format: The indexing template
            semantic_config: Semantic configuration
            
        Raises:
            ValueError: If any required configuration is missing or invalid
        """
        # Check if indexing format is valid JSON
        try:
            if not indexing_format or indexing_format.isspace():
                raise ValueError("Indexing format is empty")
            json.loads(indexing_format)
        except json.JSONDecodeError:
            raise ValueError("Indexing format is not valid JSON")
        
        # Check semantic config has all required fields
        required_semantic_fields = ["title_field", "content_fields", "keyword_fields", "semantic_config_name"]
        if semantic_config:
            missing_fields = [field for field in required_semantic_fields if field not in semantic_config]
            if missing_fields:
                raise ValueError(f"Semantic configuration is missing required fields: {missing_fields}")
                
    def _create_index_fields(self) -> Tuple[List[Union[SearchField, SimpleField, SearchableField]], 
                                             List[Union[SearchField, SimpleField, SearchableField]]]:
        """
        Create index fields for core and detail indices.
        
        Returns:
            Tuple containing lists of core and detail index fields
        """
        logger.info("Creating index field definitions...")
        analyzer_normalizer_config = {
            "analyzer_name": "el.lucene",
            "normalizer_name": "lowercase"
        }
        
        # Helper function to select the appropriate field creation method
        def create_field(field_name, field_type, **kwargs):
            if kwargs.get("vector_search_dimensions"):
                method = self.search_service.add_search_field
            elif kwargs.get("searchable") and field_type == "String" and not kwargs.get("is_key"):
                method = self.search_service.add_searchable_field
            else:
                method = self.search_service.add_simple_field
            
            # Apply text search config to String fields if not overridden
            if field_type == "String" and kwargs.get("searchable") and "analyzer_name" not in kwargs:
                kwargs.update(analyzer_normalizer_config)
                
            return method(field_name=field_name, field_type=field_type, **kwargs)
        
        # Define core index fields
        core_index_fields = [
            create_field("process_id", "String", searchable=True, filterable=True, retrievable=True, is_key=True),
            create_field("process_name", "String", searchable=True, retrievable=True),
            create_field("doc_name", "String", searchable=True, retrievable=True, filterable=True),
            create_field("domain", "String", searchable=True, retrievable=True, filterable=True),
            create_field("sub_domain", "String", searchable=True, retrievable=True, filterable=True),
            create_field("functional_area", "String", searchable=True, retrievable=True),
            create_field("functional_subarea", "String", searchable=True, retrievable=True),
            create_field("process_group", "String", searchable=True, retrievable=True),
            create_field("process_subgroup", "String", searchable=True, retrievable=True),
            create_field("reference_documents", "String", searchable=True, retrievable=True),
            create_field("related_products", "String", searchable=True, retrievable=True),
            create_field("additional_information", "String", searchable=True, retrievable=True),
            create_field("non_llm_summary", "String", searchable=True, retrievable=True),
            create_field("embedding_summary", "Collection(Edm.Single)", searchable=True,
                        vector_search_dimensions=3072, vector_search_profile_name=self.vector_search_profile_name)
        ]
        
        # Define detail index fields
        detail_index_fields = [
            create_field("id", "String", searchable=True, filterable=True, retrievable=True, is_key=True),
            create_field("process_id", "String", searchable=True, filterable=True, retrievable=True),
            create_field("step_number", "Int64", searchable=True, sortable=True, filterable=True, retrievable=True),
            create_field("step_name", "String", searchable=True, retrievable=True),
            create_field("step_content", "String", searchable=True, retrievable=True),
            create_field("documents_used", "String", searchable=True, retrievable=True),
            create_field("systems_used", "String", searchable=True, retrievable=True),
            create_field("embedding_title", "Collection(Edm.Single)", searchable=True, 
                        vector_search_dimensions=3072, vector_search_profile_name=self.vector_search_profile_name),
            create_field("embedding_content", "Collection(Edm.Single)", searchable=True, 
                        vector_search_dimensions=3072, vector_search_profile_name=self.vector_search_profile_name)
        ]
        
        logger.info(f"Created {len(core_index_fields)} core index fields and {len(detail_index_fields)} detail index fields")
        return core_index_fields, detail_index_fields
    
    def _setup_indices(self, core_index_fields: List, detail_index_fields: List, 
                      vector_search: azsdim.VectorSearch, semantic_config: Optional[Dict[str, Any]]) -> Tuple[str, str]:
        """
        Set up core and detail indices in Azure Cognitive Search.
        
        Args:
            core_index_fields: List of fields for core index
            detail_index_fields: List of fields for detail index
            vector_search: Vector search configuration
            semantic_config: Semantic configuration
            
        Returns:
            Tuple of core and detail index names
        """
        # Get index names from environment variables
        core_index_name = os.getenv("INDEX-CORE")
        detail_index_name = os.getenv("INDEX-DETAIL")
        
        if not core_index_name or not detail_index_name:
            raise ValueError("Missing required environment variables: INDEX-CORE or INDEX-DETAIL")
        
        logger.info(f"Setting up indices: {core_index_name} and {detail_index_name}")
        
        # Create or update indices with proper semantic configuration if provided
        self.search_service.create_or_update_index(
            index_name=core_index_name, 
            fields=core_index_fields, 
            vector_search=vector_search
        )
        
        self.search_service.create_or_update_index(
            index_name=detail_index_name, 
            fields=detail_index_fields, 
            vector_search=vector_search
        )
        
        logger.info("Successfully created or updated indices")
        return core_index_name, detail_index_name
    
    def _process_document(self, file_path: str, container: Container, openai_client: OpenAIClient, 
                         indexing_format: str, core_index: Any, detail_index: Any, 
                         core_index_name: str, detail_index_name: str) -> bool:
        """
        Process a single document and upload it to indices.
        
        Args:
            file_path: Path to the document in the container
            container: Storage container
            openai_client: OpenAI client for embeddings
            indexing_format: Indexing format template
            core_index: Core index object
            detail_index: Detail index object
            core_index_name: Name of the core index
            detail_index_name: Name of the detail index
            
        Returns:
            True if successful, False otherwise
        """
        folder = os.path.dirname(file_path)
        file = os.path.basename(file_path)
        
        try:
            logger.info(f"Processing document: {file_path}")
            
            # Get blob content
            blob = container.get_blob_content(file_path)
            byte_stream = BytesIO(blob)
            doc = Document(byte_stream)

            # Parse document
            parsing = DocParsing(doc, openai_client, indexing_format, "domain", folder, "gpt-4o-global-standard", file)
            parsed = parsing.doc_to_json()
            
            # Process document
            processor = MultiProcessHandler(parsed, core_index, detail_index, openai_client)
            records = processor.process_documents()
            
            # Upload to Azure Cognitive Search indices
            upload_result = processor.upload_to_azure_index(records, core_index_name, detail_index_name)
            
            logger.info(f"Successfully processed document: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}", exc_info=True)
            self.failed_files.append({
                "path": file_path,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            return False
    
    def run(self, 
           container: Container, 
           openai_client: OpenAIClient, 
           indexing_format: str, 
           semantic_config: Optional[Dict[str, Any]], 
           vector_search: azsdim.VectorSearch) -> Dict[str, Any]:
        """
        Runs the hierarchical indexing flow.

        Args:
            container: The container to read blob files from
            openai_client: The OpenAIClient class instance for generating embeddings
            indexing_format: The indexing template
            semantic_config: Semantic configuration to be added to the Index
            vector_search: The vector search configuration for embeddings in Index fields
        
        Returns:
            Dictionary containing summary information about the process
        
        Raises:
            Exception: If the flow fails for any reason
        """
        start_time = datetime.now()
        successful_files = 0
        total_files = 0
        
        try:
            # Validate configuration
            logger.info("Starting hierarchical indexing flow")
            self._validate_config(indexing_format, semantic_config)
            
            # Create index fields
            core_index_fields, detail_index_fields = self._create_index_fields()
            
            # Set up indices
            core_index_name, detail_index_name = self._setup_indices(
                core_index_fields, detail_index_fields, vector_search, semantic_config
            )
            
            # Get core and detail index objects
            core_index = self.search_service.get_index(core_index_name)
            detail_index = self.search_service.get_index(detail_index_name)
            
            # Get folder structure from container
            logger.info("Retrieving folder structure from storage container")
            folder_structure = container.get_folder_structure()
            
            # Log the full folder structure for debugging
            logger.info(f"Full folder structure retrieved from container:")
            for folder_path, files_list in folder_structure.items():
                logger.info(f"  Folder: '{folder_path}'")
                for file_name in files_list:
                    logger.info(f"    File: {file_name}")
            
            # Calculate total files for progress tracking
            for folder, files in folder_structure.items():
                total_files += len(files)
            
            logger.info(f"Found {total_files} files to process across {len(folder_structure)} folders")
            
            # Process files in each folder
            file_counter = 0
            for folder, files in folder_structure.items():
                logger.info(f"Processing folder: {folder} ({len(files)} files)")
                
                for file in files:
                    file_counter += 1
                    file_path = f"{folder}/{file}"
                    
                    logger.info(f"Processing file {file_counter} of {total_files}: {file_path}")
                    
                    if self._process_document(
                        file_path, container, openai_client, indexing_format,
                        core_index, detail_index, core_index_name, detail_index_name
                    ):
                        successful_files += 1
                        
                    # Log progress
                    progress_pct = (file_counter / total_files) * 100
                    logger.info(f"Progress: {progress_pct:.1f}% ({file_counter}/{total_files})")
            
            # Write processing summary
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            failed_count = len(self.failed_files)
            
            logger.info("\n" + "="*50)
            logger.info("Hierarchical Indexing Flow - Processing Summary:")
            logger.info(f"Total files processed: {total_files}")
            logger.info(f"Successfully processed: {successful_files}")
            logger.info(f"Failed to process: {failed_count}")
            logger.info(f"Total processing time: {duration:.2f} seconds")
            logger.info("="*50)
            
            # Write failed files to log
            if failed_count > 0:
                logger.warning("Failed files:")
                for failed in self.failed_files:
                    logger.warning(f"  - {failed['path']}: {failed['error']}")
            
            # Return summary information
            return {
                "status": "completed" if failed_count == 0 else "completed_with_errors",
                "total_files": total_files,
                "successful_files": successful_files,
                "failed_files": failed_count,
                "failed_files_details": self.failed_files,
                "processing_time_seconds": duration,
                "timestamp": end_time.isoformat()
            }
                
        except Exception as e:
            logger.error(f"Hierarchical indexing flow failed: {str(e)}", exc_info=True)
            raise Exception(f"Hierarchical indexing flow failed: {str(e)}") from e

def main():
    """
    Main entry point for the hierarchical indexing flow.
    
    This function:
    1. Loads environment variables from .env file
    2. Sets up the Azure resources (Identity, Subscription, Storage, AI Service)
    3. Configures vector search and semantic configuration
    4. Creates and runs the hierarchical indexing flow
    """
    try:
        # Start tracking execution time
        start_time = datetime.now()
        logger.info("Starting hierarchical indexing workflow...")
        
        # Load environment variables
        load_dotenv()
        
        # Check for required environment variables
        required_env_vars = [
            "AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", 
            "SUBSCRIPTION_NAME", "RESOURCE_GROUP_NAME", 
            "AZURE_STORAGE_ACCOUNT_NAME", "AZURE_CONTAINER",
            "AI_SERVICE_ACCOUNT_NAME", "AI_SEARCH_ACCOUNT_NAME",
            "INDEXING_TEMPLATE_PATH", "INDEX-CORE", "INDEX-DETAIL"
        ]
        
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        from AzWrap.wrapper import (
            Identity,
            AIService,
            Subscription,
            get_exhaustive_KNN_vector_search
        )

        # 1. Set up Azure Identity
        logger.info("Setting up Azure Identity...")
        identity = Identity(
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET")
        )

        # 2. Get Azure Subscription
        logger.info("Getting Azure Subscription...")
        sub_name = os.getenv("SUBSCRIPTION_NAME")
        subscriptions = identity.get_subscriptions()
        
        subscription_id = None
        for sub in subscriptions:
            if sub.display_name == sub_name:
                sub_azure = sub
                subscription_id = sub.subscription_id
                break
        
        if not subscription_id:
            raise ValueError(f"Subscription '{sub_name}' not found in available subscriptions. "
                            f"Available subscriptions: {[sub.display_name for sub in subscriptions]}")
        
        subscription = Subscription(
            identity=identity, 
            subscription=sub_azure, 
            subscription_id=subscription_id
        )
        logger.info(f"Found subscription: {sub_name} (ID: {subscription_id})")

        # 3. Set up resource group and storage
        logger.info("Setting up resource group and storage...")
        resource_group = subscription.get_resource_group(os.getenv("RESOURCE_GROUP_NAME"))
        if not resource_group:
            raise ValueError(f"Resource group '{os.getenv('RESOURCE_GROUP_NAME')}' not found.")

        # 4. Set up storage account and container
        account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        logger.info(f"Getting storage account: {account_name}")
        storage_account = resource_group.get_storage_account(account_name)
        if not storage_account:
            raise ValueError(f"Storage account '{account_name}' not found in resource group.")
            
        container_name = os.getenv("AZURE_CONTAINER")
        logger.info(f"Getting container: {container_name}")
        container = storage_account.get_container(container_name)
        if not container:
            raise ValueError(f"Container '{container_name}' not found in storage account.")

        # 5. Set up AI service and OpenAI client
        logger.info("Setting up AI services...")
        cog_mgmt_client = subscription.get_cognitive_client()
        ai_service_name = os.getenv("AI_SERVICE_ACCOUNT_NAME")
        
        account_details = next(
            (acc for acc in cog_mgmt_client.accounts.list_by_resource_group(resource_group.azure_resource_group.name)
             if acc.name == ai_service_name), None
        )
        if not account_details:
            raise ValueError(f"Azure OpenAI account '{ai_service_name}' not found in resource group.")

        ai_service = AIService(resource_group, cog_mgmt_client, account_details)
        logger.info(f"AI Service initialized: {ai_service_name}")
        
        openai_client = ai_service.get_OpenAIClient(api_version='2024-05-01-preview')
        logger.info("Azure OpenAI client initialized successfully")

        # 6. Set up search service
        ai_search_name = os.getenv("AI_SEARCH_ACCOUNT_NAME")
        logger.info(f"Getting search service: {ai_search_name}")
        search_service = subscription.get_search_service(service_name=ai_search_name)
        if not search_service:
            raise ValueError(f"Azure Cognitive Search service '{ai_search_name}' not found.")

        # 7. Load indexing template
        template_path = os.getenv("INDEXING_TEMPLATE_PATH")
        logger.info(f"Loading indexing template from: {template_path}")
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Indexing template file not found: {template_path}")
            
        with open(template_path, "r", encoding="utf-8") as f:
            indexing_format = f.read()
            
        # Validate that the template is valid JSON
        try:
            json.loads(indexing_format)
        except json.JSONDecodeError as e:
            raise ValueError(f"Indexing template is not valid JSON: {str(e)}")

        # 8. Set up semantic configuration for Index
        logger.info("Setting up semantic configuration...")
        semantic_config = {
            "title_field": "process_name",
            "content_fields": ["header_content"],
            "keyword_fields": ["domain"],
            "semantic_config_name": "main-data-test-semantic-config"
        }
        
        # 9. Set up Vector Search configuration
        logger.info("Setting up vector search configuration...")
        vector_search_config = {
            "algorithm_name": "vector-config",
            "vector_search_profile_name": "vector-search-profile",
            "metric": "cosine"
        }
        
        vector_search = get_exhaustive_KNN_vector_search(
            vector_search_config['algorithm_name'], 
            vector_search_config['vector_search_profile_name'], 
            vector_search_config['metric']
        )

        # 10. Run the hierarchical indexing flow
        logger.info("Initializing hierarchical indexing flow...")
        hierarchical_indexing_flow = HierarchicalIndexingFlow(search_service)
        
        logger.info("Starting execution of the hierarchical indexing flow...")
        result = hierarchical_indexing_flow.run(
            container,
            openai_client,
            indexing_format,
            semantic_config,
            vector_search
        )
        
        # 11. Report final results
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "="*50)
        logger.info("Hierarchical Indexing Flow - Execution Complete")
        logger.info(f"Status: {result['status']}")
        logger.info(f"Files processed: {result['total_files']}")
        logger.info(f"Successful: {result['successful_files']}")
        logger.info(f"Failed: {result['failed_files']}")
        logger.info(f"Total execution time: {duration:.2f} seconds")
        logger.info("="*50)
        
        # Return execution summary
        return result
        
    except Exception as e:
        logger.error(f"Fatal error in main function: {str(e)}", exc_info=True)
        print(f"ERROR: {str(e)}")
        return {"status": "failed", "error": str(e)}

if __name__ == "__main__":
    main()