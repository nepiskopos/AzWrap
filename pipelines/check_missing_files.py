#!/usr/bin/env python
# check_missing_files.py - Script to check which files in the Azure container haven't been processed in the search index

import os
import sys
import hashlib
import json
from dotenv import load_dotenv

# Adjust import path to access the AzWrap package from parent directory
sys.path.append(os.path.abspath(".."))

from AzWrap.wrapper import (
    Identity,
    Container,
    AIService,
    Subscription, 
    SearchIndex,
    MultiProcessHandler
)

def compare_container_and_index(container_name: str, index_name: str):
    """
    Compare documents between a blob container and a search index.
    
    Args:
        container_name: Name of the Azure blob container
        index_name: Name of the Azure Cognitive Search index
        
    Returns:
        dict: A dictionary containing:
            - documents_in_both: List of documents that exist in both container and index
            - documents_only_in_container: List of documents that exist only in the container
            - documents_only_in_index: List of documents that exist only in the index
    """
    print(f"Comparing documents in container '{container_name}' and index '{index_name}'...")
    
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    required_env_vars = [
        "AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", 
        "SUBSCRIPTION_NAME", "RESOURCE_GROUP_NAME", 
        "AZURE_STORAGE_ACCOUNT_NAME", 
        "AI_SEARCH_ACCOUNT_NAME"
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        return {
            "documents_in_both": [],
            "documents_only_in_container": [],
            "documents_only_in_index": []
        }
    
    try:
        # 1. Set up Azure Identity
        print("Setting up Azure Identity...")
        identity = Identity(
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET")
        )

        # 2. Get Azure Subscription
        print("Getting Azure Subscription...")
        sub_name = os.getenv("SUBSCRIPTION_NAME")
        subscriptions = identity.get_subscriptions()
        
        subscription_id = None
        for sub in subscriptions:
            if sub.display_name == sub_name:
                sub_azure = sub
                subscription_id = sub.subscription_id
                break
        
        if not subscription_id:
            print(f"Subscription '{sub_name}' not found.")
            return {
                "documents_in_both": [],
                "documents_only_in_container": [],
                "documents_only_in_index": []
            }
        
        subscription = Subscription(
            identity=identity, 
            subscription=sub_azure, 
            subscription_id=subscription_id
        )

        # 3. Set up resource group and storage
        print("Setting up resource group and storage...")
        resource_group = subscription.get_resource_group(os.getenv("RESOURCE_GROUP_NAME"))
        if not resource_group:
            print(f"Resource group '{os.getenv('RESOURCE_GROUP_NAME')}' not found.")
            return {
                "documents_in_both": [],
                "documents_only_in_container": [],
                "documents_only_in_index": []
            }

        # 4. Set up storage account and container
        account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        print(f"Getting storage account: {account_name}")
        storage_account = resource_group.get_storage_account(account_name)
        if not storage_account:
            print(f"Storage account '{account_name}' not found.")
            return {
                "documents_in_both": [],
                "documents_only_in_container": [],
                "documents_only_in_index": []
            }
            
        print(f"Getting container: {container_name}")
        container = storage_account.get_container(container_name)
        if not container:
            print(f"Container '{container_name}' not found.")
            return {
                "documents_in_both": [],
                "documents_only_in_container": [],
                "documents_only_in_index": []
            }

        # 5. Set up search service
        ai_search_name = os.getenv("AI_SEARCH_ACCOUNT_NAME")
        print(f"Getting search service: {ai_search_name}")
        search_service = subscription.get_search_service(service_name=ai_search_name)
        if not search_service:
            print(f"Azure Cognitive Search service '{ai_search_name}' not found.")
            return {
                "documents_in_both": [],
                "documents_only_in_container": [],
                "documents_only_in_index": []
            }

        # 6. Get folder structure from container
        print("Retrieving folder structure from container...")
        folder_structure = container.get_folder_structure()
        
        # Create a list of all files in the container
        all_files = []
        process_handler = MultiProcessHandler([], None, None, None)
        
        for folder_path, files_list in folder_structure.items():
            for file_name in files_list:
                file_path = f"{folder_path}/{file_name}"
                # Only include Word documents
                if file_path.lower().endswith('.docx'):
                    # Use the file name without extension as process name
                    file_base_name = os.path.splitext(file_name)[0]
                    # Since we don't have short descriptions from files, use empty string
                    process_id = process_handler.generate_process_id(file_base_name, "")
                    all_files.append({
                        'file_path': file_path,
                        'file_name': file_name,
                        'process_id': process_id,
                        'process_name': file_base_name
                    })
        
        print(f"Found {len(all_files)} files in container")
        
        # 7. Get specified index
        print(f"Getting index: {index_name}")
        core_index = search_service.get_index(index_name)
        if not core_index:
            print(f"Index '{index_name}' not found.")
            return {
                "documents_in_both": [],
                "documents_only_in_container": [],
                "documents_only_in_index": []
            }
        
        # 8. Get all process IDs from core index
        print("Getting all process IDs from index...")
        search_client = core_index.get_search_client(index_name)
        
        # Search for all documents in the index
        results = list(search_client.search("*", include_total_count=True, select="process_id,process_name,doc_name"))
        
        # Extract process IDs and details from index
        processed_ids = set()
        processed_details = {}
        for doc in results:
            process_id = doc.get('process_id')
            if process_id:
                processed_ids.add(process_id)
                processed_details[process_id] = {
                    'process_name': doc.get('process_name', 'Unknown'),
                    'doc_name': doc.get('doc_name', 'Unknown')
                }
        
        print(f"Found {len(processed_ids)} process IDs in index")
        
        # 9. Compare files in container vs index
        container_process_ids = {file['process_id'] for file in all_files}
        
        # Documents that exist in both
        ids_in_both = container_process_ids.intersection(processed_ids)
        documents_in_both = []
        for file in all_files:
            if file['process_id'] in ids_in_both:
                documents_in_both.append({
                    'file_path': file['file_path'],
                    'file_name': file['file_name'],
                    'process_id': file['process_id'],
                    'process_name': file['process_name'],
                    'index_details': processed_details.get(file['process_id'], {})
                })
        
        # Documents only in container
        ids_only_in_container = container_process_ids - processed_ids
        documents_only_in_container = [file for file in all_files if file['process_id'] in ids_only_in_container]
        
        # Documents only in index
        ids_only_in_index = processed_ids - container_process_ids
        documents_only_in_index = []
        for process_id in ids_only_in_index:
            details = processed_details.get(process_id, {})
            documents_only_in_index.append({
                'process_id': process_id,
                'process_name': details.get('process_name', 'Unknown'),
                'doc_name': details.get('doc_name', 'Unknown')
            })
        
        # 10. Return the comparison results
        result = {
            'documents_in_both': documents_in_both,
            'documents_only_in_container': documents_only_in_container,
            'documents_only_in_index': documents_only_in_index
        }
        
        return result
                
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "documents_in_both": [],
            "documents_only_in_container": [],
            "documents_only_in_index": []
        }

def main():
    """
    Main function to:
    1. Get all file names from the Azure container
    2. Generate process IDs for each file
    3. Get all process IDs from the core index
    4. Print files that aren't in the index
    """
    print("Starting missing files check...")
    
    # Load environment variables
    load_dotenv()
    
    # Use container and index from environment variables
    container_name = os.getenv("AZURE_CONTAINER")
    index_name = os.getenv("INDEX-CORE")
    
    if not container_name or not index_name:
        print("Missing required environment variables: AZURE_CONTAINER or INDEX-CORE")
        print("Provide container name and index name as arguments")
        print("Usage: python check_missing_files.py [container_name] [index_name]")
        # Check if arguments were provided
        if len(sys.argv) == 3:
            container_name = sys.argv[1]
            index_name = sys.argv[2]
        else:
            return
    
    # Run the comparison
    result = compare_container_and_index(container_name, index_name)
    
    # Print the results
    print("\n===== COMPARISON RESULTS =====")
    print(f"Documents in both container and index: {len(result['documents_in_both'])}")
    print(f"Documents only in container: {len(result['documents_only_in_container'])}")
    print(f"Documents only in index: {len(result['documents_only_in_index'])}")
    
    # Print details for missing files in the index
    if result['documents_only_in_container']:
        print("\nFiles in container that are missing from index:")
        for i, file in enumerate(result['documents_only_in_container'], 1):
            print(f"{i}. {file['file_path']} (Process ID: {file['process_id']})")
    
    # Print details for orphaned documents in the index
    if result['documents_only_in_index']:
        print("\nOrphaned documents in index (not in container):")
        for i, doc in enumerate(result['documents_only_in_index'], 1):
            print(f"{i}. {doc['process_name']} (Doc: {doc['doc_name']}, Process ID: {doc['process_id']})")
    
    return result

if __name__ == "__main__":
    main()