import os
import sys
from typing import List, Dict, Any, Callable, Optional, Generator, Tuple
from io import BytesIO

# Add parent directory to path to import AzWrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from azwrap import Identity, Subscription, ResourceGroup,StorageAccount, Container
from logger import logger, INFO, ERROR

from config import (
    AZURE_TENANT_ID,
    AZURE_CLIENT_ID,
    AZURE_CLIENT_SECRET,
    AZURE_SUBSCRIPTION_ID,
    AZURE_RESOURCE_GROUP,
    AZURE_STORAGE_ACCOUNT_NAME,
    AZURE_STORAGE_CONTAINER_NAME
)

def get_container() -> Container:
    """
    Get the blob container using AzWrap
    
    Returns:
        Container: The container object
    """
    identity: Identity = Identity(AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
    subscription: Subscription = identity.get_subscription(AZURE_SUBSCRIPTION_ID)
    resource_group: ResourceGroup = subscription.get_resource_group(AZURE_RESOURCE_GROUP)
    storage_account: StorageAccount = resource_group.get_storage_account(AZURE_STORAGE_ACCOUNT_NAME)
    container: Container = storage_account.get_container(AZURE_STORAGE_CONTAINER_NAME)
    return container

from azure.storage.blob import BlobServiceClient, ContainerProperties, ContainerClient, BlobProperties

def process_folder_files(container: Container, 
                         processor_function: Callable[[BytesIO, str, str], Any],
                         folder_prefix: Optional[str] = None) -> List[Tuple[str, Any]]:
    """
    Process all files in a folder or container by applying a function to each file
    
    Args:
        container: The blob container
        processor_function: Function to process each file, takes (file_content, file_name, folder_path)
        folder_prefix: Optional folder prefix to filter files
        
    Returns:
        List[Tuple[str, Any]]: List of (blob_path, result) tuples from processing
    """
    # Get all blobs in the container
    blobs = container.get_blobs()
    results = []
    
    # Download and process each blob
    for blob in blobs:
        blob_name = blob.name
        
        # Skip if not in specified folder, if folder_prefix is provided
        if folder_prefix and not blob_name.startswith(folder_prefix):
            continue
        
        # Determine folder path and file name
        if '/' in blob_name:
            folder_path = '/'.join(blob_name.split('/')[:-1])
            file_name = blob_name.split('/')[-1]
        else:
            folder_path = 'root'
            file_name = blob_name
        
        try:
            # Get the blob client to download content
            blob_client = container.container_client.get_blob_client(blob_name)
            
            # Download blob content
            download_stream = blob_client.download_blob()
            content = download_stream.readall()
            
            # Process the content using the provided function
            content_io = BytesIO(content)
            result = processor_function(content_io, file_name, folder_path)
            
            # Store the result
            results.append((blob_name, result))
            
            logger.log(INFO, f"Processed file: {blob_name}")
        except Exception as e:
            logger.log(ERROR, f"Error processing file {blob_name}: {str(e)}")
            results.append((blob_name, None))
    
    return results

def process_files_by_extension(container: Container, 
                               processor_function: Callable[[BytesIO, str, str], Any],
                               extensions: List[str]) -> List[Tuple[str, Any]]:
    """
    Process files with specific extensions
    
    Args:
        container: The blob container
        processor_function: Function to process each file, takes (file_content, file_name, folder_path)
        extensions: List of file extensions to process (without the dot, e.g. ['pdf', 'txt'])
        
    Returns:
        List[Tuple[str, Any]]: List of (blob_path, result) tuples from processing
    """
    # Get all blobs in the container
    blobs = container.get_blobs()
    results = []
    
    # Download and process each blob with matching extension
    for blob in blobs:
        blob_name = blob.name
        
        # Check if the file has one of the specified extensions
        if not any(blob_name.lower().endswith(f'.{ext.lower()}') for ext in extensions):
            continue
        
        # Determine folder path and file name
        if '/' in blob_name:
            folder_path = '/'.join(blob_name.split('/')[:-1])
            file_name = blob_name.split('/')[-1]
        else:
            folder_path = 'root'
            file_name = blob_name
        
        try:
            # Get the blob client to download content
            blob_client = container.container_client.get_blob_client(blob_name)
            
            # Download blob content
            download_stream = blob_client.download_blob()
            content = download_stream.readall()
            
            # Process the content using the provided function
            content_io = BytesIO(content)
            result = processor_function(content_io, file_name, folder_path)
            
            # Store the result
            results.append((blob_name, result))
            
            logger.log(INFO, f"Processed file: {blob_name}")
        except Exception as e:
            logger.log(ERROR, f"Error processing file {blob_name}: {str(e)}")
            results.append((blob_name, None))
    
    return results

def count_bytes_processor(content: BytesIO, file_name: str, folder_path: str) -> int:
    """
    Example processor function that counts the number of bytes in a file
    
    Args:
        content: File content as BytesIO
        file_name: Name of the file
        folder_path: Path to the folder containing the file
        
    Returns:
        int: Number of bytes in the file
    """
    content.seek(0, os.SEEK_END)
    size = content.tell()
    content.seek(0)
    return size

def text_file_processor(content: BytesIO, file_name: str, folder_path: str) -> str:
    """
    Example processor function that reads text files
    
    Args:
        content: File content as BytesIO
        file_name: Name of the file
        folder_path: Path to the folder containing the file
        
    Returns:
        str: Content of the text file
    """
    text = content.read().decode('utf-8')
    return text

# Example usage
if __name__ == "__main__":
    try:
        # Get the container
        container = get_container()
        
        # Print folder structure
        print("\nFolder Structure:")
        folder_structure = container.get_folder_structure()
        for folder, files in folder_structure.items():
            print(f"\nFolder: {folder}")
            for file in files:
                print(f"  - {file}")
        
        # Process all files and count bytes
        print("\nProcessing all files:")
        results = process_folder_files(container, count_bytes_processor)
        for blob_path, size in results:
            print(f"{blob_path}: {size} bytes")
        
        # Process only text files
        print("\nProcessing only text files:")
        text_results = process_files_by_extension(container, text_file_processor, ['txt', 'csv', 'json'])
        for blob_path, content in text_results:
            if content:
                # Show first 100 characters of each file
                preview = content[:100] + ('...' if len(content) > 100 else '')
                print(f"{blob_path}: {preview}")
    
    except Exception as e:
        print(f"Error: {str(e)}")