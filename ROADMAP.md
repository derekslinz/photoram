# photoram Roadmap

## Purpose

Build photoram into a production-grade, modern replacement for photils-cli while preserving its CLI-first workflow and offline guarantees.

## Current State (v0.1.x)

- Core CLI flow is implemented (`tag`, `info`, output formats, metadata write path).
- RAM++ integration works with auto-download and device auto-detect.
- Project shape is clean and modular, but still in alpha with limited hardening.

## Product Goals

1. Keep local/offline tagging as the default user experience.
2. Maintain drop-in compatibility for photils-style workflows where practical.
3. Improve reliability, contract stability, and reproducibility.
4. Scale to larger photo batches without degrading usability.
5. Establish test coverage and release discipline for confident iteration.

## Non-Goals (Near Term)

- Hosted/cloud inference service.
- GUI application.
- Multi-model orchestration in the first stable release.

## Workstreams

### 1. CLI Contract Hardening

- Enforce strict option validation (`threshold`, `top-n`, file-path assumptions).
- Stabilize JSON contract (always list vs always object; choose one and document).
- Standardize exit codes and user-facing error messages.
- Ensure behavior remains script-friendly under `--quiet`.

### 2. Model & Runtime Reliability

- Pin RAM dependency to a known commit/tag for reproducible installs.
- Improve checkpoint download failure handling (network/auth/cache corruption).
- Add explicit startup diagnostics for model/cache/device failures.
- Validate threshold semantics against RAM++ defaults and document clearly.

### 3. Performance & Scale

- Add batch inference API (`tag_images`) and `--batch-size` control.
- Profile CPU vs CUDA vs MPS paths and tune defaults.
- Reduce per-image overhead in large directory runs.
- Define baseline throughput benchmarks for regression detection.

### 4. Architecture & Extensibility

- Introduce a `TaggingService` layer to decouple CLI from inference internals.
- Keep `model.py` focused on backend mechanics; move orchestration to service layer.
- Formalize result schemas/types used by all output writers.
- Prepare extension points for future metadata/output adapters.

### 5. Testing, Packaging, and Release Process

- Add unit tests for `utils`, output serialization, and metadata fallbacks.
- Add CLI integration smoke tests (single/multi-image, json/csv/text modes).
- Add reproducible local dev scripts and CI checks.
- Move from alpha toward stable versioning with release notes per milestone.

## Milestones

## Milestone 1: Hardening Baseline (target: v0.2.0)

Scope:

- Input validation and clear failure modes.
- Stable output contract and README alignment.
- Better model download/runtime error handling.

Exit Criteria:

- Invalid CLI inputs fail fast with actionable messages.
- Output formats are deterministic and documented.
- First-run failures provide explicit remediation guidance.

## Milestone 2: Reliability & Reproducibility (target: v0.3.0)

Scope:

- Pin dependency versions/commits for predictable installs.
- Add core test suite and CI for main paths.
- Improve metadata-write reliability diagnostics.

Exit Criteria:

- Clean install path is reproducible across supported environments.
- CI validates unit + smoke tests on each change.
- Metadata failures are visible and non-destructive.

## Milestone 3: Performance for Batch Workloads (target: v0.4.0)

Scope:

- Batched inference and configurable batch size.
- Runtime profiling and performance tuning.
- Optional progress/perf telemetry for long runs.

Exit Criteria:

- Measurable speedup over v0.2.x on multi-image jobs.
- No regressions in output correctness.
- Memory usage remains bounded for large directories.

## Milestone 4: Stable Architecture & 1.0 Readiness (target: v1.0.0)

Scope:

- Service-layer refactor complete.
- Test coverage expanded for critical paths.
- Backward-compatibility policy and migration notes finalized.

Exit Criteria:

- CLI behavior is stable and documented.
- Core modules have clear boundaries with maintainable internals.
- Release checklist (tests/docs/changelog) is consistently enforced.

## Success Metrics

- Functional reliability: failed-run rate on valid inputs trends toward zero.
- Contract stability: no breaking output changes without versioned notice.
- Performance: improved images/minute on representative batch workloads.
- Operability: actionable error messages for setup/runtime failures.
- Confidence: test coverage on critical paths and green CI on release branches.

## Immediate Next Actions

1. Implement Milestone 1 validation and output-contract fixes.
2. Pin RAM dependency and document the rationale.
3. Add initial test harness for utils + CLI smoke scenarios.
4. Update README examples to match final output contract choices.
