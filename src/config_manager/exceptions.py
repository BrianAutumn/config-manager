from .issues import EnvIssue

class AlreadyConfiguredException(Exception):

    def __init__(self):
        super().__init__('The env configs have already been validated.')

class ConfigurationValidationFailedException(Exception):

    def __init__(self, issues: list[EnvIssue]):
        issue_str = '\n\nThere is an issue with the env configuration:\n\n' + '\n'.join(
            [str(issue) for issue in issues])
        super().__init__(issue_str)

class IncorrectConfigTypeException(Exception):

    def __init__(self, message: str):
        super().__init__(message)

class ConfigurationNotFoundException(Exception):

    def __init__(self, message: str):
        super().__init__(message)

class PrematureConfigurationRetrievalException(Exception):

    def __init__(self, message: str):
        super().__init__(message)