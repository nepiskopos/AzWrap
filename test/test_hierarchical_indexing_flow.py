import sys
import os

sys.path.append(os.path.abspath(".."))

from dotenv import load_dotenv

def main():
    load_dotenv()

    from AzWrap.wrapper import (
        Identity,
        Subscription,
        AIService
    )

    identity = Identity(
        tenant_id=os.getenv("AZURE_TENANT_ID"),
        client_id=os.getenv("AZURE_CLIENT_ID"),
        client_secret=os.getenv("AZURE_CLIENT_SECRET")
    )

    subscription = identity.get_subscriptions()[0]
    subscription_id = subscription.subscription_id

    sub = Subscription(identity=identity, subscription=subscription, subscription_id=subscription_id)

    rg = sub.get_resource_group(os.getenv("RESOURCE_GROUP_NAME"))
    storage_accounts = sub.get_storage_accounts()
    account = storage_accounts[0]
    print("Storage account name: ", account.name)

    StAc = rg.get_storage_account(account.name)

    cog_mgmt_client = sub.get_cognitive_client()
    ai_service_name = os.getenv("AI_SERVICE_ACCOUNT_NAME")
    account_details = next(
                (acc for acc in cog_mgmt_client.accounts.list_by_resource_group(rg.azure_resource_group.name)
                 if acc.name == ai_service_name), None
            )
    if not account_details:
        raise ValueError(f"Azure OpenAI account '{ai_service_name}' not found in resource group '{rg}'.")

    ai_service = AIService(rg, cog_mgmt_client, account_details)
    print("AI Service is: ", ai_service)
    aoai_client = ai_service.get_OpenAIClient(api_version='2024-05-01-preview')
    print("Azure OpenAI client is: ", aoai_client)

    ai_search_name = os.getenv("AI_SEARCH_ACCOUNT_NAME")
    search_service = sub.get_search_service(service_name=ai_search_name)

    # Run the flow
    search_service.run_hierarchical_indexing_flow()

if __name__ == "__main__":
    main()