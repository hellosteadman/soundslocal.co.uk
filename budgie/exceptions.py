class ConfigError(Exception):
    pass


class NotFoundError(Exception):
    pass


class ComparisonError(Exception):
    pass


class ComparerNotFoundError(ComparisonError):
    pass


class ContentDefinitionError(Exception):
    pass
