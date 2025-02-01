from dataclasses import dataclass, field
from decimal import Decimal
import os
from .issues import EnvIssue
from .exceptions import ConfigurationValidationFailedException
import logging

logger = logging.getLogger(__name__)

ResolvedType = str | bool | float | int | Decimal

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
    env_type: type[str | bool | int | float | Decimal]
    default: str | None
    prod_value: str | None
    secure: bool | None = True
    prod_critical: bool | None = False
    issues: list[EnvIssue] = field(init=False)
    resolved_value: ResolvedType | None = field(init=False, default=None)
    raw_value: str | None = field(init=False, default=None)
    valid:bool = field(init=False, default=False)
    
    def __post_init__(self):
        from .env_configs import env_configs

        self.issues = []
        self._validate()

        env_configs.append(self)

    def get_resolved(self) -> ResolvedEnv:
        """
        Returns a ResolvedEnv object representing the resolved configuration for the environment variable.

        :return: A ResolvedEnv object representing the resolved configuration for the environment variable.
        """
        if self.valid is False or self.resolved_value is None or self.raw_value is None:
            raise ConfigurationValidationFailedException(issues=self.issues)
        return ResolvedEnv(
            name=self.name,
            value=self.resolved_value,
            raw=self.raw_value
        )
        

    def _validate(self):
        if self.prod_critical and self.prod_value is None:
            self.issues.append(EnvIssue(
                env=self.name,
                description="'prod_critical' is set to True but 'prod_value' is not configured."
            ))
            return

        if self.env_type not in [str, bool, int, float, Decimal]:
            self.issues.append(EnvIssue(
                env=self.name,
                description="Invalid 'env_type' configuration."
            ))
            return

        env_value_raw:str | None = os.environ.get(self.name, None)

        env_value:str = ''
        if env_value_raw is None and self.default is not None:
            env_value = self.default
        elif env_value_raw is not None:
            env_value = env_value_raw
        else:
            self.issues.append(EnvIssue(
                env=self.name,
                description="Required env has not been set."
            ))
            return

        try:
            if self.env_type == bool:
                self.resolved_value = env_value.lower() == 'true'
                if self.resolved_value:
                    env_value = 'TRUE'
                else:
                    env_value = 'FALSE'
            elif self.env_type == str:
                self.resolved_value = env_value
            elif self.env_type == int:
                self.resolved_value = int(env_value)
            elif self.env_type == float:
                self.resolved_value = float(env_value)
            elif self.env_type == Decimal:
                self.resolved_value = Decimal(env_value)
            else:
                self.issues.append(EnvIssue(
                    env=self.name,
                    description=f"Unsupported type: {self.env_type}"
                ))
                return
        except ValueError:
            self.issues.append(EnvIssue(
                env=self.name,
                description="Type validation failed."
            ))
            return

        os.environ[self.name] = env_value

        if self.prod_critical is True and self.raw_value != self.prod_value:
            logger.warning(f'Production critical env {self.name} is not set to the expected value.')