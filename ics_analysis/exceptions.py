"""Custom exception hierarchy for ICS Analysis."""


class ICSError(Exception):
    """Base exception for all ICS analysis errors."""


class ConfigError(ICSError):
    """Configuration loading or validation error."""


class DataError(ICSError):
    """Data loading, validation, or processing error."""


class AnalysisError(ICSError):
    """Error during analysis execution."""


class ExportError(ICSError):
    """Error during report export."""
