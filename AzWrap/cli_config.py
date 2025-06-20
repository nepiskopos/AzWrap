"""
CLI configuration file for AzWrap.
This module contains configuration for all CLI commands and options.
"""

CLI_CONFIG = {
    "name": "azwrap",
    "description": "Azure Wrapper (AzWrap) CLI tool for managing Azure resources",
    "commands": {
        # Resource Management Commands
        "subscription": {
            "description": "Manage Azure subscriptions",
            "subcommands": {
                "list": {
                    "description": "List available Azure subscriptions",
                    "options": []
                },
                "get": {
                    "description": "Get details of a specific subscription",
                    "options": [
                        {"name": "subscription-id", "short": "s", "required": True, "help": "Azure subscription ID"}
                    ]
                }
            }
        },
        
        "resource-group": {
            "description": "Manage Azure resource groups",
            "subcommands": {
                "list": {
                    "description": "List resource groups in a subscription",
                    "options": [
                        {"name": "subscription-id", "short": "s", "required": False, "help": "Azure subscription ID"}
                    ]
                },
                "create": {
                    "description": "Create a new resource group",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Resource group name"},
                        {"name": "location", "short": "l", "required": True, "help": "Azure region (e.g., westus2)"},
                        {"name": "subscription-id", "short": "s", "required": False, "help": "Azure subscription ID"}
                    ]
                },
                "get": {
                    "description": "Get details of a specific resource group",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Resource group name"},
                        {"name": "subscription-id", "short": "s", "required": False, "help": "Azure subscription ID"}
                    ]
                }
            }
        },
        
        # Search Service Commands
        "search": {
            "description": "Manage Azure AI Search services",
            "subcommands": {
                "list": {
                    "description": "List Azure AI Search services",
                    "options": [
                        {"name": "subscription-id", "short": "s", "required": False, "help": "Azure subscription ID"},
                        {"name": "resource-group", "short": "g", "required": False, "help": "Resource group name"},
                    ]
                },
                "create": {
                    "description": "Create a new search service",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "location", "short": "l", "required": True, "help": "Azure region"},
                        {"name": "sku", "required": False, "help": "SKU (free, basic, standard, standard2, standard3)", "default": "basic"}
                    ]
                },
                "get": {
                    "description": "Get details of a specific search service",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"}
                    ]
                }
            }
        },
        
        # Index Commands
        "index": {
            "description": "Manage search indexes",
            "subcommands": {
                "list": {
                    "description": "List indexes in a search service",
                    "options": [
                        {"name": "search-service", "short": "s", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"}
                    ]
                },
                "create": {
                    "description": "Create a new search index",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Index name"},
                        {"name": "search-service", "short": "s", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "fields", "short": "f", "required": True, "help": "JSON string defining fields"}
                    ]
                },
                "get": {
                    "description": "Get details of a specific index",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Index name"},
                        {"name": "search-service", "short": "s", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"}
                    ]
                },
                "delete": {
                    "description": "Delete a search index",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Index name"},
                        {"name": "search-service", "short": "s", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "force", "is_flag": True, "help": "Force deletion without confirmation"}
                    ]
                },
                "copy": {
                    "description": "Copy an index (structure and/or data)",
                    "options": [
                        {"name": "source", "required": True, "help": "Source index name"},
                        {"name": "target", "required": True, "help": "Target index name"},
                        {"name": "search-service", "short": "s", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "structure-only", "is_flag": True, "help": "Copy only the index structure, not data"},
                        {"name": "fields", "help": "Comma-separated list of fields to copy"}
                    ]
                }
            }
        },
        
        # Data Source Commands
        "datasource": {
            "description": "Manage search data sources",
            "subcommands": {
                "list": {
                    "description": "List data source connections",
                    "options": [
                        {"name": "search-service", "short": "s", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"}
                    ]
                },
                "create": {
                    "description": "Create a data source connection",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Data source name"},
                        {"name": "type", "short": "t", "required": True, "help": "Data source type (e.g., azureblob, azuretable, azuresql)"},
                        {"name": "connection-string", "short": "c", "required": True, "help": "Connection string"},
                        {"name": "container", "required": True, "help": "Container name"},
                        {"name": "search-service", "short": "s", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"}
                    ]
                },
                "get": {
                    "description": "Get details of a specific data source",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Data source name"},
                        {"name": "search-service", "short": "s", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"}
                    ]
                },
                "delete": {
                    "description": "Delete a data source",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Data source name"},
                        {"name": "search-service", "short": "s", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "force", "is_flag": True, "help": "Force deletion without confirmation"}
                    ]
                }
            }
        },
        
        # Indexer Commands
        "indexer": {
            "description": "Manage search indexers",
            "subcommands": {
                "list": {
                    "description": "List indexers",
                    "options": [
                        {"name": "search-service", "short": "s", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"}
                    ]
                },
                "create": {
                    "description": "Create an indexer",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Indexer name"},
                        {"name": "data-source", "short": "d", "required": True, "help": "Data source name"},
                        {"name": "target-index", "short": "i", "required": True, "help": "Target index name"},
                        {"name": "search-service", "short": "s", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "skillset", "help": "Skillset name to use with this indexer"},
                        {"name": "schedule", "help": "Indexing schedule (cron expression)"}
                    ]
                },
                "run": {
                    "description": "Run an indexer",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Indexer name"},
                        {"name": "search-service", "short": "s", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"}
                    ]
                },
                "reset": {
                    "description": "Reset an indexer",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Indexer name"},
                        {"name": "search-service", "short": "s", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"}
                    ]
                },
                "status": {
                    "description": "Get indexer status",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Indexer name"},
                        {"name": "search-service", "short": "s", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"}
                    ]
                },
                "update": {
                    "description": "Update an indexer",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Indexer name"},
                        {"name": "search-service", "short": "s", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "schedule", "help": "Indexing schedule (cron expression)"},
                        {"name": "parameters", "help": "JSON string with indexing parameters"}
                    ]
                },
                "delete": {
                    "description": "Delete an indexer",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Indexer name"},
                        {"name": "search-service", "short": "s", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "force", "is_flag": True, "help": "Force deletion without confirmation"}
                    ]
                }
            }
        },
        
        # Skillset Commands
        "skillset": {
            "description": "Manage search skillsets",
            "subcommands": {
                "list": {
                    "description": "List skillsets",
                    "options": [
                        {"name": "search-service", "short": "s", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"}
                    ]
                },
                "create": {
                    "description": "Create a skillset",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Skillset name"},
                        {"name": "skills", "required": True, "help": "Skills JSON or path to JSON file"},
                        {"name": "search-service", "short": "s", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "description", "help": "Skillset description"}
                    ]
                },
                "get": {
                    "description": "Get details of a specific skillset",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Skillset name"},
                        {"name": "search-service", "short": "s", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"}
                    ]
                },
                "update": {
                    "description": "Update a skillset",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Skillset name"},
                        {"name": "skills", "required": True, "help": "Skills JSON or path to JSON file"},
                        {"name": "search-service", "short": "s", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "description", "help": "Skillset description"}
                    ]
                },
                "delete": {
                    "description": "Delete a skillset",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Skillset name"},
                        {"name": "search-service", "short": "s", "required": True, "help": "Search service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "force", "is_flag": True, "help": "Force deletion without confirmation"}
                    ]
                }
            }
        },
        
        # AI Service Commands
        "ai": {
            "description": "Manage Azure OpenAI services and deployments",
            "subcommands": {
                "list": {
                    "description": "List Azure OpenAI services",
                    "options": [
                        {"name": "subscription-id", "short": "s", "required": False, "help": "Azure subscription ID"},
                        {"name": "resource-group", "short": "g", "required": False, "help": "Resource group name"}
                    ]
                },
                "get": {
                    "description": "Get details of a specific OpenAI service",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"}
                    ]
                },
                "models": {
                    "description": "List available models for an OpenAI service",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "location", "short": "l", "help": "Azure region (e.g., westus2)"}
                    ]
                },
                "deployments": {
                    "description": "List deployments for an OpenAI service",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"}
                    ]
                },
                "deploy": {
                    "description": "Create a new model deployment",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Deployment name"},
                        {"name": "model", "short": "m", "required": True, "help": "Model name"},
                        {"name": "service", "required": True, "help": "OpenAI service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "capacity", "short": "c", "help": "Capacity in TPM", "default": "1"},
                        {"name": "sku", "help": "SKU name", "default": "Standard"},
                        {"name": "version", "short": "v", "help": "Model version"}
                    ]
                },
                "update-deployment": {
                    "description": "Update a model deployment",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Deployment name"},
                        {"name": "service", "required": True, "help": "OpenAI service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "capacity", "short": "c", "help": "New capacity in TPM"},
                        {"name": "sku", "help": "New SKU name"}
                    ]
                },
                "delete-deployment": {
                    "description": "Delete a model deployment",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Deployment name"},
                        {"name": "service", "required": True, "help": "OpenAI service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "force", "is_flag": True, "help": "Force deletion without confirmation"}
                    ]
                },
                "embedding": {
                    "description": "Generate embeddings for text",
                    "options": [
                        {"name": "text", "short": "t", "required": True, "help": "Text to embed or path to text file"},
                        {"name": "service", "required": True, "help": "OpenAI service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "model", "short": "m", "help": "Embedding model", "default": "text-embedding-3-small"},
                        {"name": "api-version", "short": "a", "required": True, "help": "API version"}
                    ]
                },
                "chat": {
                    "description": "Generate chat completion",
                    "options": [
                        {"name": "message", "short": "m", "required": True, "help": "User message"},
                        {"name": "service", "required": True, "help": "OpenAI service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "model", "required": True, "help": "Model deployment name"},
                        {"name": "api-version", "short": "a", "required": True, "help": "API version"},
                        {"name": "temperature", "help": "Temperature (0-1)", "default": "0.7"},
                        {"name": "max-tokens", "help": "Maximum tokens", "default": "800"},
                        {"name": "system", "short": "s", "help": "System message"}
                    ]
                }
            }
        },
        
        # Storage Account Commands
        "storage": {
            "description": "Manage Azure Storage accounts",
            "subcommands": {
                "list": {
                    "description": "List storage accounts",
                    "options": [
                        {"name": "subscription-id", "short": "s", "required": False, "help": "Azure subscription ID"}
                    ]
                },
                "get": {
                    "description": "Get details of a specific storage account",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Storage account name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"}
                    ]
                },
                "create": {
                    "description": "Create a new storage account",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Storage account name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "location", "short": "l", "required": True, "help": "Azure region (e.g., westus2)"},
                        {"name": "sku", "help": "SKU name", "default": "Standard_LRS"}
                    ]
                },
                "containers": {
                    "description": "List containers in a storage account",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Storage account name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"}
                    ]
                },
                "blobs": {
                    "description": "List blobs in a container",
                    "options": [
                        {"name": "account", "short": "a", "required": True, "help": "Storage account name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "container", "short": "c", "required": True, "help": "Container name"}
                    ]
                },
                "folder-structure": {
                    "description": "Get folder structure in a container",
                    "options": [
                        {"name": "account", "short": "a", "required": True, "help": "Storage account name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "container", "short": "c", "required": True, "help": "Container name"}
                    ]
                }
            }
        },
        
        # Document Intelligence Commands
        "document": {
            "description": "Manage Azure Document Intelligence services and analyze documents",
            "subcommands": {
                "list": {
                    "description": "List Document Intelligence services",
                    "options": [
                        {"name": "subscription-id", "short": "s", "required": False, "help": "Azure subscription ID"},
                        {"name": "resource-group", "short": "g", "required": False, "help": "Resource group name"}
                    ]
                },
                "get": {
                    "description": "Get details of a specific Document Intelligence service",
                    "options": [
                        {"name": "name", "short": "n", "required": True, "help": "Document Intelligence service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "subscription-id", "short": "s", "required": False, "help": "Azure subscription ID"}
                    ]
                },
                "analyze": {
                    "description": "Analyze a document using Document Intelligence",
                    "options": [
                        {"name": "service-name", "short": "s", "required": True, "help": "Document Intelligence service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "model", "short": "m", "required": True, "help": "Model ID (e.g., prebuilt-layout, prebuilt-receipt, custom-model-id)"},
                        {"name": "document-path", "short": "d", "required": False, "help": "Path to local document file"},
                        {"name": "document-url", "short": "u", "required": False, "help": "URL of document to analyze"},
                        {"name": "subscription-id", "required": False, "help": "Azure subscription ID"},
                        {"name": "output-file", "short": "f", "required": False, "help": "Save results to file"}
                    ]
                },
                "analyze-layout": {
                    "description": "Analyze document layout to extract text, tables, and structure",
                    "options": [
                        {"name": "service-name", "short": "s", "required": True, "help": "Document Intelligence service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "document-path", "short": "d", "required": False, "help": "Path to local document file"},
                        {"name": "document-url", "short": "u", "required": False, "help": "URL of document to analyze"},
                        {"name": "subscription-id", "required": False, "help": "Azure subscription ID"},
                        {"name": "output-file", "short": "f", "required": False, "help": "Save results to file"}
                    ]
                },
                "analyze-receipt": {
                    "description": "Analyze receipt to extract key information",
                    "options": [
                        {"name": "service-name", "short": "s", "required": True, "help": "Document Intelligence service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "document-path", "short": "d", "required": False, "help": "Path to local receipt file"},
                        {"name": "document-url", "short": "u", "required": False, "help": "URL of receipt to analyze"},
                        {"name": "subscription-id", "required": False, "help": "Azure subscription ID"},
                        {"name": "output-file", "short": "f", "required": False, "help": "Save results to file"}
                    ]
                },
                "analyze-invoice": {
                    "description": "Analyze invoice to extract key information",
                    "options": [
                        {"name": "service-name", "short": "s", "required": True, "help": "Document Intelligence service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "document-path", "short": "d", "required": False, "help": "Path to local invoice file"},
                        {"name": "document-url", "short": "u", "required": False, "help": "URL of invoice to analyze"},
                        {"name": "subscription-id", "required": False, "help": "Azure subscription ID"},
                        {"name": "output-file", "short": "f", "required": False, "help": "Save results to file"}
                    ]
                },
                "analyze-id": {
                    "description": "Analyze identity document to extract key information",
                    "options": [
                        {"name": "service-name", "short": "s", "required": True, "help": "Document Intelligence service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "document-path", "short": "d", "required": False, "help": "Path to local ID document file"},
                        {"name": "document-url", "short": "u", "required": False, "help": "URL of ID document to analyze"},
                        {"name": "subscription-id", "required": False, "help": "Azure subscription ID"},
                        {"name": "output-file", "short": "f", "required": False, "help": "Save results to file"}
                    ]
                },
                "analyze-business-card": {
                    "description": "Analyze business card to extract key information",
                    "options": [
                        {"name": "service-name", "short": "s", "required": True, "help": "Document Intelligence service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "document-path", "short": "d", "required": False, "help": "Path to local business card file"},
                        {"name": "document-url", "short": "u", "required": False, "help": "URL of business card to analyze"},
                        {"name": "subscription-id", "required": False, "help": "Azure subscription ID"},
                        {"name": "output-file", "short": "f", "required": False, "help": "Save results to file"}
                    ]
                },
                "analyze-w2": {
                    "description": "Analyze W-2 tax form to extract key information",
                    "options": [
                        {"name": "service-name", "short": "s", "required": True, "help": "Document Intelligence service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "document-path", "short": "d", "required": False, "help": "Path to local W-2 file"},
                        {"name": "document-url", "short": "u", "required": False, "help": "URL of W-2 to analyze"},
                        {"name": "subscription-id", "required": False, "help": "Azure subscription ID"},
                        {"name": "output-file", "short": "f", "required": False, "help": "Save results to file"}
                    ]
                },
                "analyze-custom": {
                    "description": "Analyze document using a custom trained model",
                    "options": [
                        {"name": "service-name", "short": "s", "required": True, "help": "Document Intelligence service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "model-id", "short": "m", "required": True, "help": "Custom model ID"},
                        {"name": "document-path", "short": "d", "required": False, "help": "Path to local document file"},
                        {"name": "document-url", "short": "u", "required": False, "help": "URL of document to analyze"},
                        {"name": "subscription-id", "required": False, "help": "Azure subscription ID"},
                        {"name": "output-file", "short": "f", "required": False, "help": "Save results to file"}
                    ]
                },
                "analyze-batch": {
                    "description": "Analyze multiple documents in batch",
                    "options": [
                        {"name": "service-name", "short": "s", "required": True, "help": "Document Intelligence service name"},
                        {"name": "resource-group", "short": "g", "required": True, "help": "Resource group name"},
                        {"name": "model", "short": "m", "required": True, "help": "Model ID to use for all documents"},
                        {"name": "document-folder", "short": "d", "required": False, "help": "Folder containing documents to analyze"},
                        {"name": "document-list", "short": "l", "required": False, "help": "File containing list of document paths/URLs"},
                        {"name": "subscription-id", "required": False, "help": "Azure subscription ID"},
                        {"name": "output-folder", "short": "f", "required": False, "help": "Folder to save batch results"}
                    ]
                }
            }
        }
    },
    "global_options": [
        {"name": "verbose", "short": "v", "is_flag": True, "help": "Enable verbose output"},
        {"name": "quiet", "short": "q", "is_flag": True, "help": "Suppress all output except errors and results"},
        {"name": "output", "short": "o", "help": "Output format (text, json, table)", "default": "text"},
        {"name": "config", "help": "Path to configuration file"}
    ]
}