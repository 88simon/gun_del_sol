"""
Observability Package

Provides structured logging and metrics collection for monitoring
and debugging the Gun Del Sol backend.
"""

from .structured_logger import (
    logger,
    log_info,
    log_warning,
    log_error,
    log_debug,
    log_analysis_start,
    log_analysis_complete,
    log_analysis_failed,
    set_request_id,
    set_job_id,
    clear_context,
    sanitize_address
)

from .metrics import metrics_collector

__all__ = [
    # Logger
    'logger',
    'log_info',
    'log_warning',
    'log_error',
    'log_debug',
    'log_analysis_start',
    'log_analysis_complete',
    'log_analysis_failed',
    'set_request_id',
    'set_job_id',
    'clear_context',
    'sanitize_address',
    # Metrics
    'metrics_collector',
]
