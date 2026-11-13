"""Core application runtime, CLI protocol, connectors, and architecture inspection."""

from ._version import __version__
from .application import (PROTOCOL_VERSION, SUPPORTED_PROTOCOL_VERSIONS, Application, ApplicationContext,
                          ApplicationDefinitionError, BootstrapError, ConnectorError, ProtocolError)
from .diagnostics import configure_logging, redact
from .discovery import AnalysisCache, Evidence, Finding, ProjectInspector, ProjectProfile
from .docs import validate_documentation
from .external import CommandResult, ExternalCommand, ExternalSession
from .filesystem import AppDirectories, ArtifactStore, PathBoundary, PathViolation
from .http import HttpClient, HttpResponse, HttpStreamResponse
from .jobs import JobQueueFull, SQLiteJobStore
from .migration import (STRATEGIES, TASK_STATUSES, MigrationFinding, MigrationPlan, MigrationTask,
                        analyze_migration, load_statuses)
from .persistent_state import SQLiteState
from .report import (REPORT_SCHEMA_VERSION, implementation_report, migration_report, render_json, render_markdown,
                     verification_report)
from .sqlite import SQLiteDatabase
from .websocket import WebSocketClient
from .state import ObservableState
from .testing import ApplicationTestClient, CLIContractTests
from .verification import (ArchitectureProfile, Baseline, BaselineEntry, Check, RULE_CATALOG,
                           VerificationResult, apply_baseline, default_profile, verify)

__all__ = ["AppDirectories", "ArtifactStore", "Application", "ApplicationContext", "ApplicationDefinitionError",
           "AnalysisCache",
           "ApplicationTestClient", "ArchitectureProfile", "Baseline", "BaselineEntry", "BootstrapError", "Check",
           "CLIContractTests", "CommandResult", "ExternalSession",
           "ConnectorError", "Evidence", "ExternalCommand", "Finding", "HttpClient", "HttpResponse", "HttpStreamResponse",
           "JobQueueFull", "MigrationFinding", "MigrationPlan", "MigrationTask", "ObservableState", "PathBoundary", "SQLiteJobStore",
           "PathViolation", "PROTOCOL_VERSION", "ProjectInspector", "ProjectProfile", "ProtocolError",
           "REPORT_SCHEMA_VERSION", "RULE_CATALOG", "SQLiteDatabase", "SQLiteJobStore", "SQLiteState", "STRATEGIES",
           "SUPPORTED_PROTOCOL_VERSIONS", "TASK_STATUSES", "VerificationResult", "WebSocketClient", "__version__",
           "analyze_migration", "apply_baseline", "configure_logging", "default_profile", "implementation_report",
           "load_statuses", "migration_report", "redact", "render_json", "render_markdown",
           "validate_documentation", "verification_report", "verify"]
