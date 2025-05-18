# AzWrap package
"""
Azure Wrapper Library - Simplifies interaction with Azure services
"""

# Version
__version__ = "0.1.5"

# Identity and Resource Management
from .wrapper import (
    Identity,
    Subscription,
    ResourceGroup,
    
    # Storage
    StorageAccount,
    Container,

    BlobType,
    
    # Search
    SearchService, 
    SearchIndex,
    SearchIndexerManager,
    DataSourceConnection,
    Indexer,
    Skillset,
    get_std_vector_search,
    
    # AI Services
    AIService,
    OpenAIClient
)

# CLI functionality
from .main import main as cli_main

# Convenient access to common classes and functions
__all__ = [
    # Identity and Resource Management
    "Identity",
    "Subscription", 
    "ResourceGroup",
    
    # Storage
    "StorageAccount",
    "Container",

    "BlobType",
    
    # Search Services
    "SearchService",
    "SearchIndex",
    "SearchIndexerManager",
    "DataSourceConnection",
    "Indexer",
    "Skillset",
    "get_std_vector_search",
    
    # AI Services
    "AIService",
    "OpenAIClient",
    
    # CLI
    "cli_main"
]
