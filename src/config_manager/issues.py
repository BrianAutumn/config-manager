from dataclasses import dataclass
from typing import override

@dataclass
class EnvIssue:
    """
    Represents an issue related to an environment variable.

    :param env: The name of the environment variable associated with the issue.
    :param description: A description of the issue.
    """
    env: str
    description: str

    @override
    def __str__(self) -> str:
        return f"{self.env}: {self.description}"
