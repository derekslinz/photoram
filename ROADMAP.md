# photoram Roadmap

## Status Snapshot (v1.1.0)

Security and resilience phases from the remediation plan are implemented.

Completed:

1. Checkpoint integrity verification (SHA-256, fail closed).
2. Decompression-bomb protection with configurable pixel cap.
3. exiftool argument hardening (`--` before filename).
4. Streaming mini-batch inference (bounded memory by batch size).
5. Fresh-clone test ergonomics (`pytest` works without editable install path tweaks).
6. CI automation for tests, SAST (`bandit`), and dependency audit (`pip-audit`).
7. Constraints-based reproducible install path (`constraints.txt`).

## Remaining Focus Areas

1. Add benchmark suite and baseline throughput metrics (CPU/CUDA/MPS).
2. Define release checklist (changelog, docs sync, security scan review).
3. Improve contributor guidance for dependency updates and vulnerability triage.

## Near-Term Milestones

## Milestone A: Performance Benchmarking (v1.2.x)

Scope:

- Add reproducible benchmark fixture set.
- Capture baseline images/min and memory profiles by device class.
- Track regressions in CI or scheduled jobs.

Exit Criteria:

- Benchmarks are documented and repeatable.
- Performance regression threshold is defined.

## Milestone B: Release Operations (v1.3.x)

Scope:

- Add release checklist and security sign-off process.
- Document dependency update cadence and audit workflow.
- Improve failure triage playbook for model download/integrity incidents.

Exit Criteria:

- Releases follow a standard checklist.
- Security scans and test gates are reviewed before release.

## Success Metrics

- Reliability: valid invocations complete without unexpected crashes.
- Contract stability: output schema remains backward-compatible by default.
- Security: integrity and scan controls remain green in CI.
- Performance: bounded memory and improving throughput on large batches.
- Developer UX: clean-clone setup and tests are reproducible.

## Immediate Next Actions

1. Add benchmark harness and representative dataset fixture.
2. Add release checklist document in repo.
3. Document dependency patching + CVE triage workflow.
