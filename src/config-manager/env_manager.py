import logging
import os
from decimal import Decimal
from .exceptions import AlreadyConfiguredException, ConfigurationValidationFailedException, IncorrectConfigTypeException, ConfigurationNotFoundException, PrematureConfigurationRetrievalException
from .types import EnvIssue, ResolvedEnv, ConfiguredEnv
from .env_configs import env_configs


resolved_envs = {}
validated = False
prod_validation = []

logger = logging.getLogger(__name__)


def validate_env():
    """
    Validates the environment configuration. This function must be called before getting any configuration values.

    :raise AlreadyConfiguredException: If the environment configuration is already configured.
    :raise Exception: If there was an attempt to get the system configuration before the env configs were validated.
    """
    global resolved_envs
    global env_configs
    global validated
    global prod_validation

    if validated:
        raise AlreadyConfiguredException()

    issues = []
    resolved_envs = {}

    for config in env_configs:
        if config.name is None:
            issues.append(EnvIssue(
                env='Unknown',
                description="'name' is not configured."
            ))
            continue
        if config.description is None:
            issues.append(EnvIssue(
                env=config.name,
                description="'description' is not configured."
            ))
            continue
        if config.env_type is None:
            issues.append(EnvIssue(
                env=config.name,
                description="'env_type' is not configured."
            ))
            continue
        if config.prod_critical and config.prod_value is None:
            issues.append(EnvIssue(
                env=config.name,
                description="'prod_critical' is set to True but 'prod_value' is not configured."
            ))
            continue
        if config.env_type not in [str, bool, int, float, Decimal]:
            issues.append(EnvIssue(
                env=config.name,
                description="Invalid 'env_type' configuration."
            ))
            continue

        env_value = os.environ.get(config.name, None)

        if config.default is None and env_value is None:
            issues.append(EnvIssue(
                env=config.name,
                description="Required env has not been set."
            ))
            continue
        if env_value is None:
            env_value = config.default

        env_value_resolved = None

        try:
            if config.env_type == bool:
                env_value_resolved = env_value.lower() == 'true'
                if env_value_resolved:
                    env_value = 'TRUE'
                else:
                    env_value = 'FALSE'
            elif config.env_type == str:
                env_value_resolved = env_value
            elif config.env_type == int:
                env_value_resolved = int(env_value)
            elif config.env_type == float:
                env_value_resolved = float(env_value)
            elif config.env_type == Decimal:
                env_value_resolved = Decimal(env_value)
            else:
                issues.append(EnvIssue(
                    env=config.name,
                    description=f"Unsupported type: {config.env_type}"
                ))
                continue
        except ValueError:
            issues.append(EnvIssue(
                env=config.name,
                description="Type validation failed."
            ))
            continue

        # Ensure env_value_resolved is not None before creating ResolvedEnv
        if env_value_resolved is None:
            issues.append(EnvIssue(
                env=config.name,
                description="Failed to resolve environment value"
            ))
            continue

        os.environ[config.name] = env_value

        resolved_envs[config.name] = ResolvedEnv(
            config=config,
            value=env_value_resolved,
            raw=env_value
        )
        if config.prod_critical:
            prod_validation.append(resolved_envs[config.name])
    if len(issues) > 0:
        raise ConfigurationValidationFailedException(issues)

    for prod_env in prod_validation:
        if prod_env.raw != prod_env.config.prod_value:
            logger.warning(f'Production critical env {prod_env.config.name} is not set to the expected value.')

    validated = True


def get_config(name: str) -> str:
    """
    Get a raw config value. Validations must be run before this function is called. Prefer using one of the type specific
    functions to add an additional layer of validation.

    :param name: The name of the config.
    :return: The raw value of the config.
    """
    _basic_config_checks(name)

    return resolved_envs[name].raw


def get_config_str(name: str) -> str:
    """
    Get a string config value. Validations must be run before this function is called.

    :param name: The name of the config.
    :return: The value of the config.
    """
    _basic_config_checks(name)

    if resolved_envs[name].config.env_type != str:
        raise IncorrectConfigTypeException(f'The env config {name} is not a string.')

    return resolved_envs[name].value


def get_config_bool(name: str) -> bool:
    """
    Get a boolean config value. Validations must be run before this function is called.

    :param name: The name of the config.
    :return: The value of the config.
    """
    _basic_config_checks(name)

    if resolved_envs[name].config.env_type != bool:
        raise IncorrectConfigTypeException(f'The env config {name} is not a boolean.')

    return resolved_envs[name].value


def get_config_int(name: str) -> int:
    """
    Get an integer config value. Validations must be run before this function is called.

    :param name: The name of the config.
    :return: The value of the config.
    """
    _basic_config_checks(name)

    if resolved_envs[name].config.env_type != int:
        raise IncorrectConfigTypeException(f'The env config {name} is not an integer.')

    return resolved_envs[name].value


def get_config_float(name: str) -> float:
    """
    Get a float config value. Validations must be run before this function is called.

    :param name: The name of the config.
    :return: The value of the config.
    """
    _basic_config_checks(name)

    if resolved_envs[name].config.env_type != float:
        raise IncorrectConfigTypeException(f'The env config {name} is not a float.')
    return resolved_envs[name].value


def get_config_decimal(name: str) -> Decimal:
    """
    Get a decimal config value. Validations must be run before this function is called.

    :param name: The name of the config.
    :return: The value of the config.
    """
    _basic_config_checks(name)

    if resolved_envs[name].config.env_type != Decimal:
        raise IncorrectConfigTypeException(f'The env config {name} is not a decimal.')

    return resolved_envs[name].value


def _basic_config_checks(name: str):
    global validated

    if not validated:
        raise PrematureConfigurationRetrievalException('There was an attempt to get a config before the env configs were validated.')

    if name not in resolved_envs:
        raise ConfigurationNotFoundException(f'The env config {name} does not exist.')


def get_configuration() -> list:
    """
    Get a list of the current configurations.

    :return: The configuration list.
    """
    if not validated:
        raise PrematureConfigurationRetrievalException('There was an attempt to get the system configuration before the env configs were validated.')

    result = []
    for config in resolved_envs:
        secure = resolved_envs[config].config.secure
        result.append(ConfiguredEnv(
            name=config,
            description=resolved_envs[config].config.description,
            env_type=str(resolved_envs[config].config.env_type),
            default=mask_secure(resolved_envs[config].config.default, secure),
            secure=resolved_envs[config].config.secure,
            prod_critical=resolved_envs[config].config.prod_critical,
            prod_value=mask_secure(resolved_envs[config].config.prod_value, secure),
            value=mask_secure(resolved_envs[config].value, secure),
            raw=mask_secure(resolved_envs[config].raw, secure)
        ))
    return result


def mask_secure(value, secure: bool):
    if secure:
        return '***'
    return value
