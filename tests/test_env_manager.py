import os
import pytest
from decimal import Decimal
from config_manager.types import EnvConfig, EnvIssue
from config_manager.exceptions import (
    AlreadyConfiguredException,
    ConfigurationValidationFailedException,
    ConfigurationNotFoundException,
    PrematureConfigurationRetrievalException
)
from config_manager.env_manager import (
    validate_env,
    get_config,
    get_config_str,
    get_config_bool,
    get_config_int,
    get_config_float,
    get_config_decimal,
    get_configuration
)

@pytest.fixture(autouse=True)
def clean_env():
    """Clean up environment variables before and after each test"""
    # Store original environment
    original_env = dict(os.environ)
    
    # Clear all environment variables
    os.environ.clear()
    
    # Reset module state
    from config_manager.env_configs import env_configs
    import config_manager.env_manager as env_manager
    
    env_configs.clear()
    env_manager.resolved_envs.clear()
    env_manager.prod_validation.clear()
    env_manager.validated = False
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
    
    # Reset module state again after test
    env_configs.clear()
    env_manager.resolved_envs.clear()
    env_manager.prod_validation.clear()
    env_manager.validated = False

def test_string_env():
    """Test string environment variable configuration and retrieval"""
    EnvConfig(
        name="TEST_STRING",
        description="A test string environment variable",
        env_type=str,
        default="default_value"
    )
    
    # Test with default value
    validate_env()
    assert get_config("TEST_STRING") == "default_value"
    assert get_config_str("TEST_STRING") == "default_value"
    
    # Reset validation state for next test
    import config_manager.env_manager as env_manager
    env_manager.validated = False
    env_manager.resolved_envs.clear()
    
    # Test with set value
    os.environ["TEST_STRING"] = "custom_value"
    validate_env()
    assert get_config("TEST_STRING") == "custom_value"
    assert get_config_str("TEST_STRING") == "custom_value"

def test_boolean_env():
    """Test boolean environment variable configuration and retrieval"""
    EnvConfig(
        name="TEST_BOOL",
        description="A test boolean environment variable",
        env_type=bool,
        default="true"
    )
    
    # Test with default value
    validate_env()
    assert get_config("TEST_BOOL") == "TRUE"
    assert get_config_bool("TEST_BOOL") is True
    
    # Reset validation state for next test
    import config_manager.env_manager as env_manager
    env_manager.validated = False
    env_manager.resolved_envs.clear()
    
    # Test with false value
    os.environ["TEST_BOOL"] = "false"
    validate_env()
    assert get_config("TEST_BOOL") == "FALSE"
    assert get_config_bool("TEST_BOOL") is False

def test_integer_env():
    """Test integer environment variable configuration and retrieval"""
    EnvConfig(
        name="TEST_INT",
        description="A test integer environment variable",
        env_type=int,
        default="42"
    )
    
    # Test with default value
    validate_env()
    assert get_config("TEST_INT") == "42"
    assert get_config_int("TEST_INT") == 42
    
    # Reset validation state for next test
    import config_manager.env_manager as env_manager
    env_manager.validated = False
    env_manager.resolved_envs.clear()
    
    # Test with custom value
    os.environ["TEST_INT"] = "123"
    validate_env()
    assert get_config("TEST_INT") == "123"
    assert get_config_int("TEST_INT") == 123

def test_float_env():
    """Test float environment variable configuration and retrieval"""
    EnvConfig(
        name="TEST_FLOAT",
        description="A test float environment variable",
        env_type=float,
        default="3.14"
    )
    
    # Test with default value
    validate_env()
    assert get_config("TEST_FLOAT") == "3.14"
    assert get_config_float("TEST_FLOAT") == 3.14
    
    # Reset validation state for next test
    import config_manager.env_manager as env_manager
    env_manager.validated = False
    env_manager.resolved_envs.clear()
    
    # Test with custom value
    os.environ["TEST_FLOAT"] = "2.718"
    validate_env()
    assert get_config("TEST_FLOAT") == "2.718"
    assert get_config_float("TEST_FLOAT") == 2.718

def test_decimal_env():
    """Test decimal environment variable configuration and retrieval"""
    EnvConfig(
        name="TEST_DECIMAL",
        description="A test decimal environment variable",
        env_type=Decimal,
        default="1.23456789"
    )
    
    # Test with default value
    validate_env()
    assert get_config("TEST_DECIMAL") == "1.23456789"
    assert get_config_decimal("TEST_DECIMAL") == Decimal("1.23456789")
    
    # Reset validation state for next test
    import config_manager.env_manager as env_manager
    env_manager.validated = False
    env_manager.resolved_envs.clear()
    
    # Test with custom value
    os.environ["TEST_DECIMAL"] = "9.87654321"
    validate_env()
    assert get_config("TEST_DECIMAL") == "9.87654321"
    assert get_config_decimal("TEST_DECIMAL") == Decimal("9.87654321")

def test_required_env():
    """Test required environment variable validation"""
    EnvConfig(
        name="REQUIRED_ENV",
        description="A required environment variable",
        env_type=str
    )
    
    # Should raise exception when required env is not set
    with pytest.raises(ConfigurationValidationFailedException) as exc_info:
        validate_env()
    
    assert any(
        issue.env == "REQUIRED_ENV" and "Required env has not been set" in issue.description
        for issue in exc_info.value.issues
    )
    
    # Reset validation state for next test
    import config_manager.env_manager as env_manager
    env_manager.validated = False
    env_manager.resolved_envs.clear()
    
    # Should pass when required env is set
    os.environ["REQUIRED_ENV"] = "value"
    validate_env()
    assert get_config("REQUIRED_ENV") == "value"

def test_invalid_type_conversion():
    """Test invalid type conversion handling"""
    EnvConfig(
        name="TEST_INT",
        description="A test integer environment variable",
        env_type=int
    )
    
    os.environ["TEST_INT"] = "not_an_integer"
    
    with pytest.raises(ConfigurationValidationFailedException) as exc_info:
        validate_env()
    
    assert any(
        issue.env == "TEST_INT" and "Type validation failed" in issue.description
        for issue in exc_info.value.issues
    )

def test_premature_config_retrieval():
    """Test premature configuration retrieval handling"""
    EnvConfig(
        name="TEST_ENV",
        description="A test environment variable",
        env_type=str
    )
    
    # Should raise exception when trying to get config before validation
    with pytest.raises(PrematureConfigurationRetrievalException):
        get_config("TEST_ENV")

def test_nonexistent_config():
    """Test nonexistent configuration retrieval"""
    validate_env()
    
    with pytest.raises(ConfigurationNotFoundException):
        get_config("NONEXISTENT_ENV")

def test_double_validation():
    """Test double validation prevention"""
    EnvConfig(
        name="TEST_ENV",
        description="A test environment variable",
        env_type=str,
        default="value"
    )
    
    validate_env()
    
    with pytest.raises(AlreadyConfiguredException):
        validate_env()

def test_production_critical_env():
    """Test production critical environment variable validation"""
    EnvConfig(
        name="PROD_ENV",
        description="A production critical environment variable",
        env_type=str,
        prod_critical=True,
        prod_value="expected_value"
    )
    
    os.environ["PROD_ENV"] = "different_value"
    validate_env()  # Should log a warning about mismatched prod value

def test_get_configuration():
    """Test getting all configurations"""
    EnvConfig(
        name="TEST_ENV1",
        description="First test environment variable",
        env_type=str,
        default="value1"
    )
    EnvConfig(
        name="TEST_ENV2",
        description="Second test environment variable",
        env_type=int,
        default="42"
    )
    
    validate_env()
    configs = get_configuration()
    
    assert len(configs) == 2
    assert any(c["name"] == "TEST_ENV1" and c["value"] == "value1" for c in configs)
    assert any(c["name"] == "TEST_ENV2" and c["value"] == "42" for c in configs)

def test_secure_env_masking():
    """Test secure environment variable masking"""
    EnvConfig(
        name="SECURE_ENV",
        description="A secure environment variable",
        env_type=str,
        secure=True,
        default="secret_value"
    )
    
    validate_env()
    configs = get_configuration()
    
    secure_config = next(c for c in configs if c["name"] == "SECURE_ENV")
    assert secure_config["value"] == "***"  # Value should be masked
