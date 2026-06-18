"""Normalized errors for memory providers."""

from __future__ import annotations

import asyncio
from typing import Any


class MemoryProviderError(Exception):
    """Base error raised by the provider abstraction layer."""

    def __init__(
        self,
        message: str,
        *,
        provider: str = "",
        operation: str = "",
        code: str = "provider_error",
        retryable: bool = False,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.provider = provider
        self.operation = operation
        self.code = code
        self.retryable = retryable
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": str(self),
            "provider": self.provider,
            "operation": self.operation,
            "retryable": self.retryable,
            "details": self.details,
        }


class ProviderConfigError(MemoryProviderError):
    """Provider configuration is invalid or incomplete."""

    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message, code="provider_config_error", retryable=False, **kwargs)


class ProviderUnavailableError(MemoryProviderError):
    """Provider is unavailable or unhealthy."""

    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message, code="provider_unavailable", retryable=True, **kwargs)


class ProviderTimeoutError(MemoryProviderError):
    """Provider operation exceeded the configured timeout."""

    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message, code="provider_timeout", retryable=True, **kwargs)


class MemoryNotFoundError(MemoryProviderError):
    """Requested memory item does not exist in the provider."""

    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message, code="memory_not_found", retryable=False, **kwargs)


class UnsupportedCapabilityError(MemoryProviderError):
    """Provider does not support the requested capability."""

    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message, code="unsupported_capability", retryable=False, **kwargs)


def normalize_provider_error(
    exc: Exception,
    *,
    provider: str = "",
    operation: str = "",
) -> MemoryProviderError:
    """Map arbitrary provider exceptions into the stable error contract."""
    if isinstance(exc, MemoryProviderError):
        if not exc.provider:
            exc.provider = provider
        if not exc.operation:
            exc.operation = operation
        return exc

    if isinstance(exc, asyncio.TimeoutError):
        return ProviderTimeoutError(
            f"Provider operation timed out: {operation}",
            provider=provider,
            operation=operation,
            details={"exception": exc.__class__.__name__},
        )

    return ProviderUnavailableError(
        str(exc) or exc.__class__.__name__,
        provider=provider,
        operation=operation,
        details={"exception": exc.__class__.__name__},
    )
