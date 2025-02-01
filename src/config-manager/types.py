from dataclasses import dataclass
from decimal import Decimal
from typing import TypedDict, Type, Optional
from .env_configs import env_configs


@dataclass
class ResolvedEnv:
    """
    Represents a resolved environment variable.

    :param config: Configuration rules for parsing
    :param value: Type-converted value
    :param raw: Original environment string
    """
    config: 'EnvConfig'
    value: str | bool | float | int | Decimal
    raw: str

@dataclass
class EnvIssue:
    """
    Represents an issue related to an environment variable.

    :param env: The name of the environment variable associated with the issue.
    :param description: A description of the issue.
    """
    env: str
    description: str

    def __str__(self) -> str:
        """
        Returns a string representation of the environment issue.

        :return: A formatted string combining the environment variable name and its issue description.
        """
        return f'{self.env}: {self.description}'


@dataclass
class EnvConfig:
    """
    Represents the configuration for an environment variable.

    :param name: The name of the environment variable.
    :param description: A description of the environment variable's purpose.
    :param env_type: The expected type of the environment variable (e.g., str, bool, int, float, Decimal).
    :param default: The default value for the environment variable if not set. Environment variables without a default value are required. Defaults to None.
    :param secure: Whether the environment variable contains sensitive information. Defaults to True.
    :param prod_critical: Indicates if the environment variable is critical in production. If set to True, the environment variable will be validated to have the correct type and value in production. Defaults to False.
    :param prod_value: The expected value of the environment variable in production. Defaults to None.
    """
    name: str
    description: str
    env_type: Type[str | bool | int | float | Decimal]
    default: Optional[str] = None
    secure: Optional[bool] = True
    prod_critical: Optional[bool] = False
    prod_value: Optional[str] = None

    def __post_init__(self):
        global env_configs

        env_configs.append(self)

class ConfiguredEnv(TypedDict):
    """
    Represents a configured environment variable.

    :param name: The name of the environment variable.
    :param description: A description of the environment variable's purpose.
    :param env_type: The expected type of the environment variable (e.g., str, bool, int, float, Decimal).
    :param default: The default value for the environment variable if not set. Environment variables without a default value are required. Defaults to None.
    :param secure: Whether the environment variable contains sensitive information. Defaults to True.
    :param prod_critical: Indicates if the environment variable is critical in production. If set to True, the environment variable will be validated to have the correct type and value in production. Defaults to False.
    :param prod_value: The expected value of the environment variable in production. Defaults to None.
    :param value: The current value of the environment variable.
    :param raw: The raw environment variable string.
    """
    name: str
    description: str
    env_type: str
    default: str | None
    secure: bool
    prod_critical: bool
    prod_value: str | bool | int | float | Decimal
    value: str | bool | int | float | Decimal
    raw: str