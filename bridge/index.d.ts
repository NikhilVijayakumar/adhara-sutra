import { EventEmitter } from "node:events";

export declare const PROTOCOL_VERSION: "1.0";

export interface BridgeOptions {
  /** Executable to spawn, for example "python" or a packaged backend path. */
  command: string;
  /** Arguments for the backend, including its persistent-mode flag. */
  args?: string[];
  cwd?: string;
  env?: Record<string, string | undefined>;
  /** Per-request timeout in milliseconds; 0 disables it. */
  defaultTimeoutMs?: number;
}

export interface ProtocolError {
  code: string;
  category: string;
  message: string;
  retryable?: boolean | null;
  details?: unknown;
}

export interface ProtocolResponse<T = unknown> {
  kind: "response";
  protocol_version: string;
  request_id: string;
  success: boolean;
  data: T | null;
  error: ProtocolError | null;
}

export interface ProtocolEvent<T = unknown> {
  kind: "event";
  protocol_version: string;
  request_id?: string | null;
  job_id?: string;
  event: string;
  data: T;
}

export interface JobStatus {
  job_id: string;
  name: string;
  state: "queued" | "running" | "succeeded" | "failed" | "cancelled" | "interrupted";
  result: unknown;
  error: { code: string; message: string } | null;
  created_at: number;
  started_at: number | null;
  finished_at: number | null;
  persistence: { status: "pending" | "disabled" | "saved" | "failed"; error_code?: "JOB_PERSISTENCE_FAILED" };
}

export interface JobStatusResult {
  job_id: string;
  status: JobStatus | null;
}

export interface CancelResult {
  job_id: string;
  cancelled: boolean;
  cancellation: "requested" | "completed" | "unsupported" | "failed";
  status: JobStatus | null;
}

export interface HealthResult {
  status: "ok" | "degraded";
  state: string;
  services: Record<string, { status: string; error?: string }>;
}

export interface HelpResult {
  framework_version: string;
  actions: Array<{ name: string; description: string; input_schema: boolean; output_schema: boolean }>;
  jobs: Array<{ name: string; description: string; timeout: number | null }>;
}

export interface ExitInfo {
  code: number | null;
  signal: string | null;
  expected: boolean;
}

export declare class BridgeError extends Error {
  code: string;
  category: string;
  retryable: boolean | null;
  details?: unknown;
  response?: ProtocolResponse;
}

export declare class Bridge extends EventEmitter {
  constructor(options: BridgeOptions);
  readonly command: string;
  readonly args: string[];
  readonly started: boolean;
  start(options?: { timeoutMs?: number }): Promise<this>;
  request<T = unknown>(action: string, payload?: unknown, options?: { timeoutMs?: number }): Promise<T>;
  cancel(jobId: string): Promise<CancelResult>;
  jobStatus(jobId: string): Promise<JobStatusResult>;
  health(): Promise<HealthResult>;
  help(): Promise<HelpResult>;
  close(options?: { timeoutMs?: number }): Promise<void>;
  on(event: "event", listener: (event: ProtocolEvent) => void): this;
  on(event: "stderr", listener: (line: string) => void): this;
  on(event: "exit", listener: (info: ExitInfo) => void): this;
  on(event: "protocolError", listener: (info: { line: string; error: Error }) => void): this;
  on(event: "processError", listener: (error: Error) => void): this;
}
