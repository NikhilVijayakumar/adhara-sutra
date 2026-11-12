"""Core application runtime, CLI protocol, connectors, and architecture inspection."""

from ._version import __version__
from .application import (Application, ApplicationContext, ApplicationDefinitionError, BootstrapError, ConnectorError,
                          ProtocolError)
from .diagnostics import configure_logging
from .discovery import Evidence, Finding, ProjectInspector, ProjectProfile
from .external import CommandResult, ExternalCommand
from .filesystem import AppDirectories, PathBoundary, PathViolation
from .http import HttpClient, HttpResponse
from .jobs import JobQueueFull
from .migration import (STRATEGIES, TASK_STATUSES, MigrationFinding, MigrationPlan, MigrationTask,
                        analyze_migration, load_statuses)
from .report import (REPORT_SCHEMA_VERSION, implementation_report, migration_report, render_json, render_markdown,
                     verification_report)
from .sqlite import SQLiteDatabase
from .testing import ApplicationTestClient
from .verification import (ArchitectureProfile, Check, RULE_CATALOG, VerificationResult, default_profile, verify)

__all__ = ["AppDirectories", "Application", "ApplicationContext", "ApplicationDefinitionError",
           "ApplicationTestClient", "ArchitectureProfile", "BootstrapError", "Check", "CommandResult",
           "ConnectorError", "Evidence", "ExternalCommand", "Finding", "HttpClient", "HttpResponse",
           "JobQueueFull", "MigrationFinding", "MigrationPlan", "MigrationTask", "PathBoundary",
           "PathViolation", "ProjectInspector", "ProjectProfile", "ProtocolError", "REPORT_SCHEMA_VERSION",
           "RULE_CATALOG", "SQLiteDatabase", "STRATEGIES", "TASK_STATUSES", "VerificationResult", "__version__",
           "analyze_migration", "configure_logging", "default_profile", "implementation_report",
           "load_statuses", "migration_report", "render_json", "render_markdown", "verification_report",
           "verify"]
