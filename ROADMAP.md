# photoram Roadmap

## Status Snapshot (v1.0.1)

photoram has moved past the original v0.x hardening phase. The core architecture and CLI contract are now in place and released as stable:

- Service-layer architecture is implemented (`cli.py -> service.py -> model.py`).
- JSON output contract is stable (always a list).
- CLI input validation and standardized exit codes are implemented.
- Batch inference (`--batch-size`) is implemented.
- Custom error hierarchy and clearer diagnostics are implemented.
- Automated tests for CLI/utils/schemas/errors are present.
- RAM dependency is pinned to a commit in `pyproject.toml`.

## What Is Already Complete

### Completed from the original roadmap

1. CLI contract hardening (validation + deterministic output).
2. Runtime error model (typed exceptions + exit-code mapping).
3. Service-layer refactor and schema formalization.
4. Initial reliability improvements for checkpoint handling.
5. Core unit/integration test suite for CLI contracts.

## Current Gaps

1. Test ergonomics from a fresh clone: `pytest` fails unless package is installed editable (or `PYTHONPATH=src` is set).
2. Batch inference currently preloads all transformed images before running mini-batches, which can spike memory on very large sets.
3. Performance benchmarks and regression thresholds are not yet formalized.
4. CI/release automation is not documented in-repo.
5. Output docs should continue to track edge-case behavior (especially partial failures).

## Forward Roadmap

## Milestone 1: Operational Quality (v1.1.x)

Scope:

- Make local test runs deterministic without requiring prior editable install.
- Expand documentation for first-run model download and failure modes.
- Add tests for partial-failure output behavior and metadata warning paths.

Exit Criteria:

- `pytest` succeeds in a clean clone with documented one-command setup.
- README accurately reflects current command and output behavior.
- Partial-failure behavior is covered by integration tests.

## Milestone 2: Performance at Scale (v1.2.x)

Scope:

- Refactor batch path to stream/load per batch instead of preloading all tensors.
- Add benchmark fixtures and baseline throughput metrics (CPU/CUDA/MPS).
- Tune batch defaults and document tradeoffs.

Exit Criteria:

- Large directory runs avoid unbounded memory growth.
- Measured throughput improvements are documented.
- No regressions in tagging correctness/output contracts.

## Milestone 3: Delivery & Release Discipline (v1.3.x)

Scope:

- Add/standardize CI checks for tests and packaging sanity.
- Define release checklist (tests, changelog, docs alignment).
- Improve contributor workflow documentation.

Exit Criteria:

- CI is green and enforced on mainline changes.
- Releases follow a repeatable checklist.
- Contributor setup is documented and reproducible.

## Success Metrics

- Reliability: valid invocations complete without unexpected crashes.
- Contract stability: no breaking output changes without versioned notice.
- Performance: improved images/minute and bounded memory on large batches.
- Developer UX: fresh-clone test run succeeds with documented steps.
- Maintainability: core behavior covered by tests and CI.

## Immediate Next Actions

1. Address test bootstrap ergonomics (editable install vs source-path strategy).
2. Rework `model.tag_images` to avoid preloading every image into memory.
3. Add benchmark script + baseline numbers to the repo.
4. Keep README and ROADMAP updated per release changes.
