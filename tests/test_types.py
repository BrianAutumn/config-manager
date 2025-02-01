import pytest
from decimal import Decimal
from config_manager.types import EnvConfig, EnvIssue, ResolvedEnv, ConfiguredEnv

def test_env_config_creation():
    """Test EnvConfig creation and validation"""
    config = EnvConfig(
        name="TEST_ENV",
        description="A test environment variable",
        env_type=str,
        default="default_value",
        secure=True,
        prod_critical=False,
        prod_value=None
    )
    
    assert config.name == "TEST_ENV"
    assert config.description == "A test environment variable"
    assert config.env_type == str
    assert config.default == "default_value"
    assert config.secure is True
    assert config.prod_critical is False
    assert config.prod_value is None

def test_env_issue_str_representation():
    """Test EnvIssue string representation"""
    issue = EnvIssue(
        env="TEST_ENV",
        description="Test issue description"
    )
    
    assert str(issue) == "TEST_ENV: Test issue description"

def test_resolved_env_creation():
    """Test ResolvedEnv creation and validation"""
    config = EnvConfig(
        name="TEST_ENV",
        description="A test environment variable",
        env_type=str
    )
    
    resolved = ResolvedEnv(
        config=config,
        value="test_value",
        raw="test_value"
    )
    
    assert resolved.config == config
    assert resolved.value == "test_value"
    assert resolved.raw == "test_value"

def test_configured_env_dict():
    """Test ConfiguredEnv TypedDict usage"""
    config_dict: ConfiguredEnv = {
        "name": "TEST_ENV",
        "description": "A test environment variable",
        "env_type": "str",
        "default": "default_value",
        "secure": True,
        "prod_critical": False,
        "prod_value": "prod_value",
        "value": "current_value",
        "raw": "current_value"
    }
    
    assert config_dict["name"] == "TEST_ENV"
    assert config_dict["description"] == "A test environment variable"
    assert config_dict["env_type"] == "str"
    assert config_dict["default"] == "default_value"
    assert config_dict["secure"] is True
    assert config_dict["prod_critical"] is False
    assert config_dict["prod_value"] == "prod_value"
    assert config_dict["value"] == "current_value"
    assert config_dict["raw"] == "current_value"

def test_env_config_type_validation():
    """Test EnvConfig type validation"""
    # Test valid types
    EnvConfig(name="TEST_STR", description="Test", env_type=str)
    EnvConfig(name="TEST_BOOL", description="Test", env_type=bool)
    EnvConfig(name="TEST_INT", description="Test", env_type=int)
    EnvConfig(name="TEST_FLOAT", description="Test", env_type=float)
    EnvConfig(name="TEST_DECIMAL", description="Test", env_type=Decimal)

def test_resolved_env_value_types():
    """Test ResolvedEnv value type validation"""
    config = EnvConfig(name="TEST_ENV", description="Test", env_type=str)
    
    # Test string value
    resolved = ResolvedEnv(config=config, value="test", raw="test")
    assert resolved.value == "test"
    assert resolved.raw == "test"
    
    # Test boolean value
    resolved = ResolvedEnv(config=config, value=True, raw="true")
    assert resolved.value is True
    assert resolved.raw == "true"
    
    # Test integer value
    resolved = ResolvedEnv(config=config, value=42, raw="42")
    assert resolved.value == 42
    assert resolved.raw == "42"
    
    # Test float value
    resolved = ResolvedEnv(config=config, value=3.14, raw="3.14")
    assert resolved.value == 3.14
    assert resolved.raw == "3.14"
    
    # Test decimal value
    resolved = ResolvedEnv(config=config, value=Decimal("1.23"), raw="1.23")
    assert resolved.value == Decimal("1.23")
    assert resolved.raw == "1.23"
