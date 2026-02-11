# Security Remediation Plan (photoram)

## Objective

Reduce high-impact security risk in model loading and image processing paths while preserving CLI usability and current output contracts.

## Implementation Status

- Phase 1: Completed
- Phase 2: Completed
- Phase 3: Completed
- Validation: Completed (`pytest` passing locally)

## Scope

This plan covers these findings from the latest security review:

1. Untrusted checkpoint integrity (remote `.pth` load risk).
2. Disabled decompression-bomb safeguards in PIL.
3. Potential exiftool option injection via dash-prefixed file names.
4. Memory-DoS risk from preloading all batch tensors.
5. Supply-chain hardening gaps in dependency management.

## Prioritization

### P1 (Immediate)

1. Add checkpoint integrity verification (SHA-256, fail closed).
2. Re-enable image bomb protections (bounded max pixels + explicit error handling).

### P2 (Next)

1. Harden metadata subprocess invocation for untrusted filenames.
2. Stream batch loading to avoid unbounded memory growth.

### P3 (Completed)

1. Add dependency and static security checks to CI.
2. Tighten dependency pinning strategy with reproducible installs.

## Work Plan

## Phase 1: Critical Controls (Implemented)

### Task 1: Checkpoint integrity enforcement

Files:

- `src/photoram/model.py`
- `src/photoram/errors.py`
- `tests/` (new/updated tests)

Actions:

1. Define trusted hash metadata for `HF_FILENAME` (config constant).
2. After download (and for cached file), compute SHA-256 and compare.
3. On mismatch:

- delete suspect file,
- raise explicit integrity exception,
- include remediation text in error output.

4. Ensure no model load occurs before hash validation passes.

Acceptance criteria:

1. Corrupted/tampered checkpoint is rejected deterministically.
2. CLI exits with model error code and actionable message.
3. Tests cover pass/fail hash paths and cache revalidation path.

### Task 2: Image decompression-bomb protection

Files:

- `src/photoram/model.py`
- `tests/` (new/updated tests)

Actions:

1. Remove global `Image.MAX_IMAGE_PIXELS = None` override.
2. Set a conservative application limit (configurable, default safe bound).
3. Catch PIL bomb/decompression exceptions and map to safe per-file failure.
4. Document limits and failure behavior in README.

Acceptance criteria:

1. Oversized/malicious image does not crash process.
2. Result for affected image includes failure reason; batch continues.
3. Normal large photos under threshold still process successfully.

## Phase 2: Abuse Resistance (Implemented)

### Task 3: exiftool argument hardening

Files:

- `src/photoram/metadata.py`
- `tests/test_cli_integration.py` or dedicated metadata tests

Actions:

1. Insert `--` argument before image path in exiftool command.
2. Add tests for filenames beginning with `-` and unusual characters.
3. Keep `shell=False` and argument-list invocation.

Acceptance criteria:

1. Dash-prefixed filenames are treated as file paths, not options.
2. Metadata write behavior remains unchanged for normal paths.

### Task 4: Streaming batch inference

Files:

- `src/photoram/model.py`
- `src/photoram/service.py`
- performance tests/bench scripts

Actions:

1. Refactor batch path to load/transform only current mini-batch.
2. Avoid retaining all tensors in memory across entire job.
3. Preserve order-stable outputs and per-image error reporting.
4. Add stress test for large input sets.

Acceptance criteria:

1. Memory footprint scales with batch size, not total image count.
2. Output order and schema remain unchanged.
3. No regression in existing CLI tests.

## Phase 3: Supply Chain & Continuous Assurance (Implemented)

### Task 5: Dependency and SAST controls in CI

Files:

- CI workflow config (new/updated)
- `pyproject.toml` (if needed)

Actions:

1. Add dependency vulnerability scan (`pip-audit` or equivalent).
2. Add static analysis job (`bandit` or equivalent).
3. Fail CI on high-severity findings; report medium findings.

Acceptance criteria:

1. Security scans run on pull requests and main branch.
2. Findings are surfaced in CI logs with actionable output.

### Task 6: Reproducible dependency posture

Files:

- `pyproject.toml`
- lockfile/constraints file (new)
- docs

Actions:

1. Move to hash-locked or constraints-based install for release builds.
2. Review direct dependencies for minimum required ranges.
3. Document trusted dependency update workflow.

Acceptance criteria:

1. Release builds are reproducible.
2. Dependency updates are auditable and low-risk.

## Test Strategy

1. Unit tests for hash validation and checkpoint rejection.
2. Unit/integration tests for decompression-bomb handling.
3. Integration tests for metadata path edge cases (dash-prefixed filenames).
4. Regression tests ensuring JSON/text/CSV contracts unchanged.
5. Stress/performance test for large batch memory behavior.

## Operational Rollout

1. Ship Phase 1 in patch release with release notes highlighting security hardening.
2. Ship Phase 2 in minor release with performance and hardening notes.
3. Gate future releases on Phase 3 CI checks.

## Definition of Done

1. All P1 and P2 items implemented with tests.
2. CI includes security scanning and passes on main.
3. README/ROADMAP updated to reflect implemented protections.
4. No regressions in CLI contract tests.

Status: All criteria implemented in this repository update.
