from azwrap import (
    Identity,
    AIService,
)

from config import(
    AZURE_TENANT_ID,
    AZURE_CLIENT_ID,
    AZURE_CLIENT_SECRET,
    AZURE_SUBSCRIPTION_ID,
    AZURE_RESOURCE_GROUP,
    AZURE_STORAGE_ACCOUNT_NAME,
    AZURE_STORAGE_CONTAINER_NAME,

    AZURE_SEARCH_SERVICE_NAME,
    AZURE_INDEX_NAME,

    AZURE_OPENAI_SERVICE_NAME,
    AZURE_OPENAI_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
)
def get_cognitive_sevices(): 
    identity = Identity(AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
    subscription = identity.get_subscription(subscription_id=AZURE_SUBSCRIPTION_ID)
    cognitive_services = subscription.get_cognitive_client()
    resource_group = subscription.get_resource_group(AZURE_RESOURCE_GROUP)
    aiservice = resource_group.get_ai_service(AZURE_OPENAI_SERVICE_NAME)

    openaiclient = aiservice.get_OpenAIClient(AZURE_OPENAI_API_VERSION)
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


def get_index(): 
    identity = Identity(AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
    subscription = identity.get_subscription(subscription_id=AZURE_SUBSCRIPTION_ID)
    resource_group = subscription.get_resource_group(AZURE_RESOURCE_GROUP)
    search_service = subscription.get_search_service(AZURE_SEARCH_SERVICE_NAME)
    index =  search_service.get_index(AZURE_INDEX_NAME)
    return index

def update_index_schema():
    index = get_index()
    index.extend_index_schema([
        azsdim.SimpleField(name="readable_url", type=azsdim.SearchFieldDataType.String, filterable=True, facetable=True),
        azsdim.SimpleField(name="category", type=azsdim.SearchFieldDataType.String, filterable=True, facetable=True),
        #azsdim.SimpleField(name="publication_date", type=azsdim.SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True),
        #azsdim.SearchableField(name="summary", type=azsdim.SearchFieldDataType.String, analyzer_name="el.lucene")
    ])
    return index

def update_fields():
    index = get_index()
    update_client = index.get_search_client()

    import urllib.parse

    def update_recs(recs: List[Dict[str, Any]]) -> int:
        for rec in recs:
            parsed = urllib.parse.unquote(rec["url"])
            rec["readable_url"] = parsed
            #rec["extension"] = rec["metadata_storage_file_extension"]
            #rec["content_type"] = rec["metadata_content_type"]

        result = update_client.upload_documents(documents=recs)
        succeeded = sum(1 for r in result if r.succeeded)
        return succeeded

    result = index.process_data_in_batches(index_name=None, transaction=update_recs, batch_size=100)
    return result

copy_index_name = AZURE_INDEX_NAME + "_2"

def get_index_copy(): 
    identity = Identity(AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
    subscription = identity.get_subscription(subscription_id=AZURE_SUBSCRIPTION_ID)
    search_service = subscription.get_search_service(AZURE_SEARCH_SERVICE_NAME)
    index =  search_service.get_index(copy_index_name)
    return index

fields_to_copy = [
    "chunk_id",
    "parent_id",
    "chunk",
    "title",
    "text_vector",
    "url",
    "name",
    "readable_url",
    "extension",
    "content_type",
    "category",
]

def copy_index_structure():
    index = get_index()
    new_index = index.copy_index_structure(fields_to_copy=fields_to_copy, new_index_name=copy_index_name) 
def copy_index_data():
    index = get_index()
    result = index.copy_index_data(source_index_name=None, target_index_name=copy_index_name, fields_to_copy=fields_to_copy)
    return result

def copy_index():
    index = get_index()
    new_index_name = index.copy_index_structure(fields_to_copy=fields_to_copy, new_index_name=copy_index_name) 
    result = index.copy_index_data(source_index_name=None, target_index_name=copy_index_name, fields_to_copy=fields_to_copy)

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
    
if __name__ == "__main__":
    # Test AIService implementation
    from config import(
        AZURE_TENANT_ID,
        AZURE_CLIENT_ID,
        AZURE_CLIENT_SECRET,
        AZURE_SUBSCRIPTION_ID,
        AZURE_RESOURCE_GROUP,
        AZURE_AI_SERVICE_NAME,
        AZURE_OPENAI_KEY,
        AZURE_OPENAI_ENDPOINT,
        AZURE_OPENAI_API_VERSION,
        AZURE_OPENAI_EMBEDDING_MODEL,
        AZURE_OPENAI_API_KEY,
        AZURE_OPENAI_CHAT_MODEL
    )
    
    get_cognitive_sevices()
    exit() 
