# Azure Resource Usage in `azwrap/wrapper.py`

This document details, for each class (and relevant enum) in `azwrap/wrapper.py`, which Azure resources are used and in what manner (read, create, update, get details, etc.).

---

## 1. `Identity` (Lines 24–73)

**Azure Resources Used:**
- Azure Active Directory (for authentication)
- Azure Subscription (via `SubscriptionClient`)

**Operations:**
- Authenticate using DefaultAzureCredential or ClientSecretCredential (read)
- List subscriptions (read)
- Get subscription details (read)

---

## 2. `Subscription` (Lines 77–139)

**Azure Resources Used:**
- Resource Groups (`ResourceManagementClient`)
- Storage Accounts (`StorageManagementClient`)
- Search Services (`SearchManagementClient`)
- Cognitive Services (`CognitiveServicesManagementClient`)

**Operations:**
- List resource groups (read)
- Get resource group details (read)
- Create resource group (create)
- List storage accounts (read)
- Get storage account details (read)
- List search services (read)
- Get search service details (read)
- Get Cognitive Services client (read)

---

## 3. `ResourceGroup` (Lines 143–213)

**Azure Resources Used:**
- Resource Group (context)
- Storage Accounts (`StorageManagementClient`)
- Search Services (`SearchManagementClient`)
- Cognitive Services Accounts (`CognitiveServicesManagementClient`)

**Operations:**
- List resources in group (read)
- Get storage account (read)
- Create storage account (create)
- Create search service (create)
- Get AI (OpenAI) service (read/get details)

---

## 4. `StorageAccount` (Lines 217–254)

**Azure Resources Used:**
- Storage Account (`StorageManagementClient`)
- Blob Service (`BlobServiceClient`)

**Operations:**
- List storage account keys (read)
- Get blob service client (read)
- Get container client (read)
- List containers (read)
- Get container (read)

---

## 5. `BlobType` (Lines 257–419)

**Type:** Enum

**Role:**
- Encodes blob types based on file extension and MIME type.
- Used as a helper for blob processing logic in the wrapper.
- **Does not directly interact with Azure resources**, but is essential for determining how blobs are handled by other classes (e.g., `Container`).

---

## 6. `Container` (Lines 421–743)

**Azure Resources Used:**
- Blob Container (`ContainerClient`, `BlobClient`)

**Operations:**
- List blobs (read)
- Get blob content (read)
- Get DOCX blob content (read)
- Delete blob (delete)

---

## 7. `SearchService` (Lines 753–1299)

**Azure Resources Used:**
- Azure Cognitive Search Service (`SearchManagementClient`, `SearchIndexClient`)

**Operations:**
- Get admin key (read)
- List indexes (read)
- Get index details (read)
- Add fields to index (update)
- Add semantic configuration (update)
- Create or update index (create/update)

---

## 8. `SearchIndexerManager` (Lines 1370–1536)

**Azure Resources Used:**
- Azure Cognitive Search IndexerClient

**Operations:**
- List/get/create data source connections (read/create)
- List/get/create indexers (read/create)
- List/get/create skillsets (read/create)

---

## 9. `DataSourceConnection` (Lines 1538–1587)

**Azure Resources Used:**
- Azure Cognitive Search Data Source Connection

**Operations:**
- Get name/details (read)
- Update data source connection (update)
- Delete data source connection (delete)

---

## 10. `Indexer` (Lines 1589–1659)

**Azure Resources Used:**
- Azure Cognitive Search Indexer

**Operations:**
- Get name/details (read)
- Run indexer (execute)
- Reset indexer (execute)
- Get status (read)
- Update indexer (update)
- Delete indexer (delete)

---

## 11. `Skillset` (Lines 1661–1710)

**Azure Resources Used:**
- Azure Cognitive Search Skillset

**Operations:**
- Get name/details (read)
- Update skillset (update)
- Delete skillset (delete)

---

## 12. `SearchIndex` (Lines 1712–2166)

**Azure Resources Used:**
- Azure Cognitive Search Index (`SearchIndexClient`, `SearchClient`)

**Operations:**
- Create/update index (create/update)
- Extend index schema (update)
- Upload documents (create)
- Copy data/structure between indexes (read/create)
- Perform search/hybrid search (read)

---

## 13. `AIService` (Lines 2170–2414)

**Azure Resources Used:**
- Cognitive Services Account (`CognitiveServicesManagementClient`)
- Azure OpenAI (via endpoint)

**Operations:**
- List account keys (read)
- Get Azure OpenAI client (read)
- List models (read)
- Get model details (read)
- (Other methods likely: manage deployments, not shown in snippet)

---

# Summary Table

| Class/Enum           | Lines     | Azure Resource(s) Used                      | Operations (Read/Create/Update/Delete/Get Details)                                               |
| -------------------- | --------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Identity             | 24–73     | Azure AD, Subscription                      | Authenticate (read), List/Get subscriptions (read)                                               |
| Subscription         | 77–139    | Resource Groups, Storage, Search, Cognitive | List/Get/Create resource groups (read/create), List/Get storage/search/cognitive services (read) |
| ResourceGroup        | 143–213   | Resource Group, Storage, Search, Cognitive  | List resources (read), Get/Create storage/search/AI services (read/create)                       |
| StorageAccount       | 217–254   | Storage Account, Blob Service               | List keys (read), Get containers (read)                                                          |
| BlobType (Enum)      | 257–419   | —                                           | Helper for blob type logic; no direct Azure interaction                                          |
| Container            | 421–743   | Blob Container                              | List/Get/Delete blobs, Get DOCX content (read/delete)                                            |
| SearchService        | 753–1299  | Cognitive Search                            | Get admin key (read), List/Get/Update indexes (read/update), Add fields/config (update)          |
| SearchIndexerManager | 1370–1536 | Cognitive Search IndexerClient              | List/Get/Create data sources, indexers, skillsets (read/create)                                  |
| DataSourceConnection | 1538–1587 | Cognitive Search Data Source                | Get (read), Update, Delete                                                                       |
| Indexer              | 1589–1659 | Cognitive Search Indexer                    | Get (read), Run, Reset, Status, Update, Delete                                                   |
| Skillset             | 1661–1710 | Cognitive Search Skillset                   | Get (read), Update, Delete                                                                       |
| SearchIndex          | 1712–2166 | Cognitive Search Index                      | Create/Update, Extend schema, Upload, Copy, Search                                               |
| AIService            | 2170–2414 | Cognitive Services, Azure OpenAI            | List keys/models (read), Get model details (read)                                                |