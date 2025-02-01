import logging
from decimal import Decimal
from .exceptions import AlreadyConfiguredException, ConfigurationValidationFailedException, IncorrectConfigTypeException, ConfigurationNotFoundException, PrematureConfigurationRetrievalException
from .env_configs import env_configs
from .issues import EnvIssue

validated = False

logger = logging.getLogger(__name__)


def validate_env():
    """
    Validates the environment configuration. This function must be called before getting any configuration values.

    :raise AlreadyConfiguredException: If the environment configuration is already configured.
    :raise Exception: If there was an attempt to get the system configuration before the env configs were validated.
    """
    global validated

    if validated:
        raise AlreadyConfiguredException()

    issues:list[EnvIssue] = []

    for config in env_configs:
        issues.extend(config.issues)
    if len(issues) > 0:
        raise ConfigurationValidationFailedException(issues)

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
