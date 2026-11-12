"""Core application runtime, CLI protocol, connectors, and architecture inspection."""

from ._version import __version__
from .application import (Application, ApplicationContext, ApplicationDefinitionError, BootstrapError, ConnectorError,
                          ProtocolError)
from .diagnostics import configure_logging
from .discovery import Evidence, Finding, ProjectInspector, ProjectProfile
from .external import CommandResult, ExternalCommand
from .http import HttpClient, HttpResponse
from .jobs import JobQueueFull
from .report import REPORT_SCHEMA_VERSION, implementation_report, render_json, render_markdown
from .sqlite import SQLiteDatabase
from .testing import ApplicationTestClient

__all__ = ["Application", "ApplicationContext", "ApplicationDefinitionError", "ApplicationTestClient", "BootstrapError",
           "CommandResult", "ConnectorError", "Evidence", "ExternalCommand", "Finding", "HttpClient", "HttpResponse",
           "JobQueueFull", "ProjectInspector", "ProjectProfile", "ProtocolError", "REPORT_SCHEMA_VERSION",
           "SQLiteDatabase", "__version__", "configure_logging", "implementation_report", "render_json",
           "render_markdown"]
