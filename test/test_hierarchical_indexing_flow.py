import sys
import os

sys.path.append(os.path.abspath(".."))

from dotenv import load_dotenv

def main():
    load_dotenv()

    from AzWrap.wrapper import (
        Identity,
        AIService,
        Subscription,
        get_exhaustive_KNN_vector_search
    )

    # Get Azure Identity from Tenant and Client 
    identity = Identity(
        tenant_id=os.getenv("AZURE_TENANT_ID"),
        client_id=os.getenv("AZURE_CLIENT_ID"),
        client_secret=os.getenv("AZURE_CLIENT_SECRET")
    )

    # Get Azure Subscription from Identity
    sub_name = os.getenv("SUBSCRIPTION_NAME")
    subscriptions = identity.get_subscriptions()
    for sub in subscriptions:
        if sub.display_name == sub_name:
            sub_azure = sub
            subscription_id = sub.subscription_id
            break
    
    if not subscription_id:
        raise ValueError(f"Subscription '{sub_name}' not found.")
    
    subscription = Subscription(identity=identity, subscription=sub_azure, subscription_id=subscription_id)

    # Get Resource Group, Storage Account, Container
    resource_group = subscription.get_resource_group(os.getenv("RESOURCE_GROUP_NAME"))

    account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    StAc = resource_group.get_storage_account(account_name)
    container_name = os.getenv("AZURE_CONTAINER")
    container = StAc.get_container(container_name)

    # Get AI Service and OpenAI Client
    cog_mgmt_client = subscription.get_cognitive_client()
    ai_service_name = os.getenv("AI_SERVICE_ACCOUNT_NAME")
    account_details = next(
                (acc for acc in cog_mgmt_client.accounts.list_by_resource_group(resource_group.azure_resource_group.name)
                 if acc.name == ai_service_name), None
            )
    if not account_details:
        raise ValueError(f"Azure OpenAI account '{ai_service_name}' not found in resource group '{resource_group}'.")

    ai_service = AIService(resource_group, cog_mgmt_client, account_details)
    print("AI Service is: ", ai_service)
    openai_client = ai_service.get_OpenAIClient(api_version='2024-05-01-preview')
    print("Azure OpenAI client is: ", openai_client)

    ai_search_name = os.getenv("AI_SEARCH_ACCOUNT_NAME")
    search_service = subscription.get_search_service(service_name=ai_search_name)

    # Get Indexing Template
    with open(os.getenv("INDEXING_TEMPLATE_PATH"), "r") as f:
        indexing_format = f.read()

    # Semantic configuration for Index
    semantic_config = {
                        "title_field": "process_name",
                        "content_fields": ["header_content"],
                        "keyword_fields": ["domain"],
                        "semantic_config_name": "main-data-test-semantic-config"
                    }
    
    # Vector Search configuration for embeddings in Index fields
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

    # Run the flow
    search_service.run_hierarchical_indexing_flow(container,
                                                  openai_client,
                                                  indexing_format,
                                                  semantic_config,
                                                  vector_search
                                                  )

if __name__ == "__main__":
    main()