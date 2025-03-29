import pytest
import sys
import os

# Add parent directory to path to import AzWrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AzWrap.wrapper import Identity
from azure.core.exceptions import ClientAuthenticationError

from config import (
    AZURE_TENANT_ID,
    AZURE_CLIENT_ID,
    AZURE_CLIENT_SECRET,
    AZURE_SUBSCRIPTION_ID
)

def test_identity_init_with_valid_credentials():
    """Test Identity initialization with valid credentials from config"""
    # Create Identity instance using real credentials from config
    identity = Identity(AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
    
    # Verify attributes are set correctly
    assert identity.tenant_id == AZURE_TENANT_ID
    assert identity.client_id == AZURE_CLIENT_ID
    assert identity.client_secret == AZURE_CLIENT_SECRET
    
    # Verify credential and subscription_client are created
    assert identity.credential is not None
    assert identity.subscription_client is not None

def test_identity_init_with_empty_credentials():
    """Test Identity initialization with empty credentials"""
    # Test with empty tenant_id
    with pytest.raises(ValueError):
        Identity("", AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
    
    # Test with empty client_id
    with pytest.raises(ValueError):
        Identity(AZURE_TENANT_ID, "", AZURE_CLIENT_SECRET)
    
    # Test with empty client_secret
    with pytest.raises(ValueError):
        Identity(AZURE_TENANT_ID, AZURE_CLIENT_ID, "")

def test_identity_init_with_invalid_credentials():
    """Test Identity initialization with invalid credentials"""
    # Using invalid credentials but valid format
    invalid_tenant_id = "00000000-0000-0000-0000-000000000000"
    invalid_client_id = "11111111-1111-1111-1111-111111111111"
    invalid_client_secret = "invalid_secret"
    
    # This should create the Identity object but fail when using the credential
    identity = Identity(invalid_tenant_id, invalid_client_id, invalid_client_secret)
    
    # Verify attributes are set correctly even with invalid credentials
    assert identity.tenant_id == invalid_tenant_id
    assert identity.client_id == invalid_client_id
    assert identity.client_secret == invalid_client_secret
    
    # Verify credential is created (even though it's invalid)
    assert identity.credential is not None
    assert identity.subscription_client is not None
    
    # When trying to use the invalid credential, it should fail
    # This will only fail if we try to actually use the credential
    with pytest.raises(Exception):
        # This will try to use the invalid credential
        identity.get_subscriptions()

def test_get_credential():
    """Test get_credential method returns the credential"""
    identity = Identity(AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
    credential = identity.get_credential()
    assert credential is not None
    assert credential == identity.credential

def test_get_subscriptions():
    """Test get_subscriptions method returns a list of subscriptions"""
    # Skip if credentials are not available
    if not all([AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET]):
        pytest.skip("Azure credentials not available")
    
    # Create Identity instance
    identity = Identity(AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
    
    # Get subscriptions
    subscriptions = identity.get_subscriptions()
    
    # Verify subscriptions is a list
    assert isinstance(subscriptions, list)
    
    # Verify each subscription has an id
    for subscription in subscriptions:
        assert hasattr(subscription, 'subscription_id')

def test_get_subscription_found():
    """Test get_subscription method returns a subscription when found"""
    # Skip if credentials or subscription ID are not available
    if not all([AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_SUBSCRIPTION_ID]):
        pytest.skip("Azure credentials or subscription ID not available")
    
    # Create Identity instance
    identity = Identity(AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
    
    # Get subscription
    subscription = identity.get_subscription(AZURE_SUBSCRIPTION_ID)
    
    # Verify subscription is found
    assert subscription is not None
    assert subscription.subscription_id == AZURE_SUBSCRIPTION_ID

def test_get_subscription_not_found():
    """Test get_subscription method returns None when subscription is not found"""
    # Skip if credentials are not available
    if not all([AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET]):
        pytest.skip("Azure credentials not available")
    
    # Create Identity instance
    identity = Identity(AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
    
    # Use an invalid subscription ID
    invalid_subscription_id = "00000000-0000-0000-0000-000000000000"
    
    # Try to get subscription with invalid ID
    subscription = identity.get_subscription(invalid_subscription_id)
    
    # Verify subscription is not found
    assert subscription is None

def test_with_none_arguments():
    """Test Identity with None arguments"""
    # Test with None tenant_id
    with pytest.raises(TypeError):
        Identity(None, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
    
    # Test with None client_id
    with pytest.raises(TypeError):
        Identity(AZURE_TENANT_ID, None, AZURE_CLIENT_SECRET)
    
    # Test with None client_secret
    with pytest.raises(TypeError):
        Identity(AZURE_TENANT_ID, AZURE_CLIENT_ID, None)
    
    # Test get_subscription with None subscription_id
    identity = Identity(AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
    with pytest.raises(AttributeError):
        identity.get_subscription(None)

def test_with_wrong_argument_types():
    """Test Identity with wrong argument types"""
    # Test with integer tenant_id
    with pytest.raises(TypeError):
        Identity(123, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
    
    # Test with integer client_id
    with pytest.raises(TypeError):
        Identity(AZURE_TENANT_ID, 123, AZURE_CLIENT_SECRET)
    
    # Test with integer client_secret
    with pytest.raises(TypeError):
        Identity(AZURE_TENANT_ID, AZURE_CLIENT_ID, 123)
    
    # Test get_subscription with integer subscription_id
    identity = Identity(AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
    with pytest.raises(TypeError):
        identity.get_subscription(123)