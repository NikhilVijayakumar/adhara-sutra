"""Core application runtime, CLI protocol, connectors, and architecture inspection."""

from ._version import __version__
from .application import (PROTOCOL_VERSION, SUPPORTED_PROTOCOL_VERSIONS, Application, ApplicationContext,
                          ApplicationDefinitionError, BootstrapError, ConnectorError, ProtocolError)
from .diagnostics import configure_logging, redact
from .discovery import Evidence, Finding, ProjectInspector, ProjectProfile
from .external import CommandResult, ExternalCommand
from .filesystem import AppDirectories, ArtifactStore, PathBoundary, PathViolation
from .http import HttpClient, HttpResponse, HttpStreamResponse
from .jobs import JobQueueFull
from .migration import (STRATEGIES, TASK_STATUSES, MigrationFinding, MigrationPlan, MigrationTask,
                        analyze_migration, load_statuses)
from .persistent_state import SQLiteState
from .report import (REPORT_SCHEMA_VERSION, implementation_report, migration_report, render_json, render_markdown,
                     verification_report)
from .sqlite import SQLiteDatabase
from .state import ObservableState
from .testing import ApplicationTestClient, CLIContractTests
from .verification import (ArchitectureProfile, Check, RULE_CATALOG, VerificationResult, default_profile, verify)

__all__ = ["AppDirectories", "ArtifactStore", "Application", "ApplicationContext", "ApplicationDefinitionError",
           "ApplicationTestClient", "ArchitectureProfile", "BootstrapError", "Check", "CLIContractTests", "CommandResult",
           "ConnectorError", "Evidence", "ExternalCommand", "Finding", "HttpClient", "HttpResponse", "HttpStreamResponse",
           "JobQueueFull", "MigrationFinding", "MigrationPlan", "MigrationTask", "ObservableState", "PathBoundary",
           "PathViolation", "PROTOCOL_VERSION", "ProjectInspector", "ProjectProfile", "ProtocolError",
           "REPORT_SCHEMA_VERSION", "RULE_CATALOG", "SQLiteDatabase", "SQLiteState", "STRATEGIES",
           "SUPPORTED_PROTOCOL_VERSIONS", "TASK_STATUSES", "VerificationResult", "__version__",
           "analyze_migration", "configure_logging", "default_profile", "implementation_report",
           "load_statuses", "migration_report", "redact", "render_json", "render_markdown",
           "verification_report", "verify"]
