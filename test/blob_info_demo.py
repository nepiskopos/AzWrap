#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Blob Info Demo: Demonstrations of the get_blob_info function

This script provides several demonstrations of the Container.get_blob_info function
without using pytest. Instead, it uses simple print statements and logging to show
the functionality in action.

Five demonstrations are included:
1. Basic Properties Demo: Shows all the fundamental properties returned by get_blob_info
2. Folder Structure Demo: Demonstrates how the function handles blobs in nested folders
3. Error Handling Demo: Shows how the function handles requests for non-existent blobs
4. Performance Comparison: Compares execution time of get_blob_info vs. get_blob_content
5. Document Timeline: Focuses on time-related metadata like creation and modification dates
"""

import os
import sys
import time
import logging
from typing import Dict, Any, Optional

# Import the logger setup from the test directory
from logger import get_logger

# Add the parent directory to sys.path to allow importing AzWrap
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import AzWrap modules
from AzWrap import Identity, Subscription, ResourceGroup, StorageAccount, Container

# Initialize logger
logger = get_logger("blob_info_demo", "blob_info_demo.log")

def get_container() -> Optional[Container]:
    """
    Helper function to get a Container instance from environment variables.
    
    Returns:
        Container instance or None if there was an error.
    """
    try:
        # Get Azure credentials from environment variables
        tenant_id = os.environ.get("AZURE_TENANT_ID")
        client_id = os.environ.get("AZURE_CLIENT_ID")
        client_secret = os.environ.get("AZURE_CLIENT_SECRET")
        subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
        resource_group_name = os.environ.get("RESOURCE_GROUP_NAME")
        storage_account_name = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
        container_name = os.environ.get("AZURE_CONTAINER")
        
        # Verify all required environment variables are set
        if None in [tenant_id, client_id, client_secret, subscription_id, 
                    resource_group_name, storage_account_name, container_name]:
            logger.error("Missing required environment variables for Azure Storage access")
            return None
            
        # Set up the Azure Storage access chain
        logger.info(f"Connecting to Azure Storage container: {container_name}")
        identity = Identity(tenant_id, client_id, client_secret)
        subscription = identity.get_subscription(subscription_id)
        resource_group = subscription.get_resource_group(resource_group_name)
        storage_account = resource_group.get_storage_account(storage_account_name)
        container = storage_account.get_container(container_name)
        
        return container
    
    except Exception as e:
        logger.error(f"Error connecting to Azure Storage: {e}")
        return None

def print_blob_info(blob_info: Dict[str, Any], title: str = "Blob Information") -> None:
    """
    Helper function to print blob information in a readable format.
    
    Args:
        blob_info: Dictionary with blob information
        title: Optional title for the information section
    """
    print(f"\n{'=' * 70}")
    print(f" {title}")
    print(f"{'=' * 70}")
    
    # First print the most important information
    key_fields = ["name", "filename", "folder_path", "content_type", "size_bytes", 
                 "blob_type", "last_modified", "creation_time"]
    
    for key in key_fields:
        if key in blob_info:
            print(f"{key.replace('_', ' ').title()}: {blob_info[key]}")
    
    # Then print the rest of the information
    print(f"\n{'- ' * 35}")
    print("Additional Properties:")
    print(f"{'- ' * 35}")
    for key, value in blob_info.items():
        if key not in key_fields:
            print(f"{key.replace('_', ' ').title()}: {value}")

def demo_basic_properties(container: Container) -> None:
    """
    Demonstration 1: Basic Properties
    Shows all the fundamental properties returned by get_blob_info for a blob.
    """
    logger.info("Starting Basic Properties Demo")
    
    # List the first few blobs in the container
    blob_names = container.get_blob_names()
    if not blob_names:
        logger.error("No blobs found in container")
        return
    
    # Get info for the first blob
    first_blob = blob_names[0]
    logger.info(f"Getting information for blob: {first_blob}")
    
    try:
        blob_info = container.get_blob_info(first_blob)
        print_blob_info(blob_info, "DEMO 1: BASIC PROPERTIES")
        
        # Log some key information
        logger.info(f"Blob size: {blob_info['size_bytes']} bytes")
        logger.info(f"Content type: {blob_info['content_type']}")
        logger.info(f"Last modified: {blob_info['last_modified']}")
    
    except Exception as e:
        logger.error(f"Error in basic properties demo: {e}")

def demo_folder_structure(container: Container) -> None:
    """
    Demonstration 2: Folder Structure
    Demonstrates how the function handles blobs in nested folders versus root-level blobs.
    """
    logger.info("Starting Folder Structure Demo")
    
    # Get the folder structure
    try:
        folder_structure = container.get_folder_structure()
        
        # Find one blob in a nested folder and one at the root level
        nested_blob = None
        root_blob = None
        
        # Look for a nested blob (in a folder)
        for folder, files in folder_structure.items():
            if folder != 'root' and files:
                nested_blob = f"{folder}/{files[0]}"
                logger.info(f"Found nested blob: {nested_blob}")
                break
        
        # Look for a root-level blob
        if 'root' in folder_structure and folder_structure['root']:
            root_blob = folder_structure['root'][0]
            logger.info(f"Found root blob: {root_blob}")
        
        # Compare info for both blobs
        print("\n\n")
        if nested_blob:
            nested_info = container.get_blob_info(nested_blob)
            print_blob_info(nested_info, "DEMO 2A: NESTED FOLDER BLOB")
            logger.info(f"Folder path for nested blob: {nested_info['folder_path']}")
            logger.info(f"Filename for nested blob: {nested_info['filename']}")
        else:
            logger.warning("No nested blob found for demonstration")
        
        print("\n\n")
        if root_blob:
            root_info = container.get_blob_info(root_blob)
            print_blob_info(root_info, "DEMO 2B: ROOT-LEVEL BLOB")
            logger.info(f"Folder path for root blob: {root_info['folder_path']}")
            logger.info(f"Filename for root blob: {root_info['filename']}")
        else:
            logger.warning("No root-level blob found for demonstration")
    
    except Exception as e:
        logger.error(f"Error in folder structure demo: {e}")

def demo_error_handling(container: Container) -> None:
    """
    Demonstration 3: Error Handling
    Shows how the function gracefully handles requests for non-existent blobs.
    """
    logger.info("Starting Error Handling Demo")
    
    # Try to get info for a non-existent blob
    non_existent_blob = "this_blob_does_not_exist.txt"
    logger.info(f"Attempting to get info for non-existent blob: {non_existent_blob}")
    
    print("\n\n")
    print(f"{'=' * 70}")
    print(" DEMO 3: ERROR HANDLING")
    print(f"{'=' * 70}")
    print(f"Attempting to get info for: '{non_existent_blob}'")
    
    try:
        blob_info = container.get_blob_info(non_existent_blob)
        print("This line should not be reached if error handling works correctly")
    
    except ValueError as e:
        print(f"\nExpected error caught successfully:")
        print(f"ValueError: {str(e)}")
        logger.info(f"Error handling demonstration successful: {e}")
    
    except Exception as e:
        print(f"\nUnexpected error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        logger.warning(f"Unexpected error type in error handling demo: {type(e).__name__}")

def demo_performance_comparison(container: Container) -> None:
    """
    Demonstration 4: Performance Comparison
    Compares the execution time of get_blob_info vs. get_blob_content to highlight efficiency.
    """
    logger.info("Starting Performance Comparison Demo")
    
    # List the blobs in the container
    blob_names = container.get_blob_names()
    if not blob_names:
        logger.error("No blobs found in container")
        return
    
    # Select a medium-sized blob for the test if possible
    test_blob = None
    for blob_name in blob_names:
        try:
            info = container.get_blob_info(blob_name)
            size = info['size_bytes']
            # Look for a blob between 100KB and 10MB
            if 102400 <= size <= 10485760:
                test_blob = blob_name
                logger.info(f"Selected test blob: {test_blob} ({size} bytes)")
                break
        except Exception:
            continue
    
    # If no suitable blob found, use the first blob
    if not test_blob:
        test_blob = blob_names[0]
        logger.info(f"Using first blob for performance test: {test_blob}")
    
    print("\n\n")
    print(f"{'=' * 70}")
    print(" DEMO 4: PERFORMANCE COMPARISON")
    print(f"{'=' * 70}")
    print(f"Testing with blob: '{test_blob}'")
    
    try:
        # Test get_blob_info performance
        print("\nTesting get_blob_info performance...")
        start_time = time.time()
        info = container.get_blob_info(test_blob)
        info_time = time.time() - start_time
        print(f"get_blob_info execution time: {info_time:.4f} seconds")
        print(f"Retrieved {len(info)} properties without downloading full content")
        logger.info(f"get_blob_info took {info_time:.4f} seconds for {test_blob}")
        
        # Test get_blob_content performance
        print("\nTesting get_blob_content performance...")
        start_time = time.time()
        content = container.get_blob_content(test_blob)
        content_time = time.time() - start_time
        print(f"get_blob_content execution time: {content_time:.4f} seconds")
        print(f"Downloaded {len(content)} bytes of content")
        logger.info(f"get_blob_content took {content_time:.4f} seconds for {test_blob}")
        
        # Compare the results
        print("\nPerformance Comparison:")
        ratio = content_time / info_time if info_time > 0 else 0
        print(f"get_blob_content took {ratio:.1f}x longer than get_blob_info")
        if ratio > 1:
            print(f"get_blob_info is {ratio:.1f}x more efficient than downloading full content")
            print(f"This is especially important for large files or when you only need metadata")
    
    except Exception as e:
        logger.error(f"Error in performance comparison demo: {e}")
        print(f"Error during performance comparison: {str(e)}")

def demo_document_timeline(container: Container) -> None:
    """
    Demonstration 5: Document Timeline
    Focuses specifically on the temporal metadata of blobs, showing creation time, 
    last modified time, and other time-related properties.
    """
    logger.info("Starting Document Timeline Demo")
    
    # List the blobs in the container
    blob_names = container.get_blob_names()
    if not blob_names:
        logger.error("No blobs found in container")
        return
        
    # Try to find a document file for better demonstration (Word, PDF, etc.)
    doc_extensions = ['.docx', '.pdf', '.xlsx', '.pptx', '.txt']
    doc_blob = None
    
    for blob_name in blob_names:
        if any(blob_name.lower().endswith(ext) for ext in doc_extensions):
            doc_blob = blob_name
            logger.info(f"Found document blob for timeline demo: {doc_blob}")
            break
    
    # If no document file is found, use the first blob
    if not doc_blob:
        doc_blob = blob_names[0]
        logger.info(f"Using first available blob for timeline demo: {doc_blob}")
    
    try:
        # Get blob info
        blob_info = container.get_blob_info(doc_blob)
        
        print("\n\n")
        print(f"{'=' * 70}")
        print(" DEMO 5: DOCUMENT TIMELINE")
        print(f"{'=' * 70}")
        print(f"Document: {blob_info['name']}")
        
        # Extract and format time-related information
        create_time = blob_info.get('creation_time')
        modify_time = blob_info.get('last_modified')
        
        # Format the datetime objects for better readability if they exist
        if create_time:
            create_str = create_time.strftime('%Y-%m-%d %H:%M:%S %Z') if hasattr(create_time, 'strftime') else str(create_time)
            print(f"\nCreation Time: {create_str}")
            
        if modify_time:
            modify_str = modify_time.strftime('%Y-%m-%d %H:%M:%S %Z') if hasattr(modify_time, 'strftime') else str(modify_time)
            print(f"Last Modified: {modify_str}")
            
            # Calculate age of the document
            if hasattr(modify_time, 'replace'):
                now = time.time()
                modified_timestamp = time.mktime(modify_time.timetuple())
                age_seconds = now - modified_timestamp
                age_days = age_seconds / (60 * 60 * 24)
                
                print(f"Document Age: {age_days:.1f} days ({age_seconds:.0f} seconds)")
        
        # Show any other time-related metadata
        print("\nAdditional Timeline Information:")
        print("--------------------------------")
        time_related_keys = ['etag', 'lease_status', 'lease_state', 'access_tier']
        for key in time_related_keys:
            if key in blob_info and blob_info[key]:
                print(f"{key.replace('_', ' ').title()}: {blob_info[key]}")
        
        logger.info(f"Timeline information displayed for {doc_blob}")
            
    except Exception as e:
        logger.error(f"Error in document timeline demo: {e}")
        print(f"Error during document timeline demonstration: {str(e)}")

def main():
    """Main function to run all demonstrations."""
    logger.info("Starting Blob Info Demo script")
    print("\nBLOB INFO DEMONSTRATION SCRIPT")
    print("==============================")
    print("This script demonstrates the Container.get_blob_info functionality\n")
    
    # Get container client
    container = get_container()
    if not container:
        print("Failed to get Azure Storage container. Please check the environment variables and try again.")
        logger.error("Failed to get Azure Storage container")
        return
    
    # Run the demonstrations
    try:
        # Demo 1: Basic Properties
        demo_basic_properties(container)
        
        # Demo 2: Folder Structure
        demo_folder_structure(container)
        
        # Demo 3: Error Handling
        demo_error_handling(container)
        
        # Demo 4: Performance Comparison
        demo_performance_comparison(container)
        
        # Demo 5: Document Timeline
        demo_document_timeline(container)
        
        print("\n\nAll demonstrations completed successfully!")
        logger.info("All demonstrations completed")
    
    except Exception as e:
        print(f"\nAn error occurred during the demonstrations: {str(e)}")
        logger.error(f"Error during demonstrations: {e}", exc_info=True)
    
    print("\nCheck the log file for detailed information")

if __name__ == "__main__":
    main()