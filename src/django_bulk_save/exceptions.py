"""Exceptions raised for invalid bulk-save operations."""


class BulkSaveError(Exception):
    """Base exception for errors raised by this library."""


class InvalidInstanceError(BulkSaveError, TypeError):
    """A registered instance does not belong to the context's model."""


class InvalidUpdateFieldsError(BulkSaveError, ValueError):
    """The requested update fields are invalid or unsupported."""
