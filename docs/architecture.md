# Architecture

This repository separates historical evidence, offline evaluation, optional model
access, and presentation. The supported default path reads local artifacts and produces
auditable local outputs; it does not require a model provider or an online judge.

## Component map

| Area | Responsibility | Trust boundary |
| --- | --- | --- |
| `AutoTest/` | Original 200-task benchmark, generated candidates, and recorded results | Historical evidence; do not silently rewrite |
| `Model Fine-Tuning/` | Historical training, validation, and metrics artifacts | Historical evidence; not a routine training pipeline |
| `data/curated/` | Versioned correction and cross-dataset review manifests backed by source and component hashes | Derivative metadata; raw sources remain unchanged |
| `dataset.py` | Typed CSV/JSONL loading, validation findings, and stable fingerprints | Pure local file processing |
| `analysis.py` | Per-arm summaries, ID-keyed intersections, missingness, and exact paired McNemar tests | Pure local computation |
| `reporting.py` | Deterministic evidence-led Markdown rendering | Consumes structured analysis only |
| `cli.py` | `validate`, `analyze`, and `report` orchestration with repository defaults | Local command boundary and explicit exit statuses |
| `pipeline.py` | Direct and refinement-assisted generation with run context, stage settings, response IDs, and timings | No provider dependency in the core |
| `config.py` | Independent per-stage model settings and explicit secret lookup | Secrets remain in the caller's environment |
| `providers/openai.py` | Optional Responses API adapter for separately authorized runs | Paid, networked boundary; never used by CI |
| `results/` and `docs/results.md` | Checked-in validation and analysis snapshots | Generated outputs; regenerate instead of hand-editing |
| `site/` | Static, dependency-free public explanation of the evidence | Presentation only; no live data or model calls |

The package follows a dependency-inversion boundary: evaluation logic depends on the
small `ChatBackend` protocol, while a provider adapter implements that protocol. Each new
run carries a caller-supplied run/task ID, UTC start time, strategy version, exact requested
stage settings, and provider response identifiers when available. Tests
inject fakes. Importing or testing the core therefore neither imports the optional SDK
nor performs network activity.

## Data and analysis flow

1. Audit the immutable benchmark and fine-tuning files with `validate`; hard-fail exact
   train/benchmark matches, verify curated semantic decisions, and preserve all findings
   even when the historical data returns a non-zero validation status.
2. Load the result artifacts and check their structure, status values, and declared
   counts independently of the dataset audit.
3. Fingerprint the evaluated inputs so a report can identify its evidence exactly.
4. Join arms by task ID. Preserve every arm's observed denominator and missing IDs.
5. Compute complete-case and pairwise summaries on explicit intersections.
6. Serialize derived results deterministically, then render explanatory documentation
   or the static site from those results.

The separation between validation and analysis is deliberate. A malformed record or
task-identity conflict must be reported and repaired in a curated derivative; it must
not disappear through an implicit row drop. Similarly, separate headline acceptance
rates are not substituted for paired comparisons.

## Historical experiment boundary

The checked-in evidence covers a union of 200 LeetCode problem IDs and three historical
arms: direct generation, generation after GPT-4o prompt refinement, and generation after
fine-tuned GPT-4o prompt refinement. The result files contain 197, 199, and 196 observed
tasks respectively, leaving 193 tasks observed by all three arms. These are historical
artifacts, not a live model leaderboard, and the paired results do not demonstrate an
improvement from prompt refinement.

Historical online-judge automation is not part of routine operation. It is excluded
from tests and CI, as are paid model calls. Any future external run must be explicitly
authorized, versioned as a new experiment, and kept behind the existing provider and
configuration boundaries.

## Extension points

- Add a benchmark revision as a new, fingerprinted dataset; retain the raw source.
- Add an experiment arm through the common arm/result schema rather than special-case
  analysis logic.
- Add a provider by implementing `ChatBackend` in an optional module and testing it
  with an injected fake client.
- Add a statistic to the structured report first, with deterministic tests, before
  exposing it in prose or the site.

All extensions should remain compatible with Python 3.10 and keep analysis and tests
independent of credentials, model calls, judges, and external services.
