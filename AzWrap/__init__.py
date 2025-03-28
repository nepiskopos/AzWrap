# AzWrap package
"""
Azure Wrapper Library - Simplifies interaction with Azure services
"""

# Version
__version__ = "0.1.1"

# Identity and Resource Management
from .wrapper import (
    Identity,
    Subscription,
    ResourceGroup,
    
    # Storage
    StorageAccount,
    Container,
    
    # Search
    SearchService, 
    SearchIndex,
    get_std_vector_search,
    
    # AI Services
    AIService,
    OpenAIClient
)

# Convenient access to common classes and functions
__all__ = [
    # Identity and Resource Management
    "Identity",
    "Subscription", 
    "ResourceGroup",
    
    # Storage
    "StorageAccount",
    "Container",
    
    # Search Services
    "SearchService",
    "SearchIndex",
    "get_std_vector_search",
    
    # AI Services
    "AIService",
    "OpenAIClient"
]
