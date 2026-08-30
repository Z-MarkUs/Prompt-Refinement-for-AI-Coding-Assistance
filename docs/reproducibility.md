# Reproducing the historical analysis

This guide reproduces descriptive and paired correctness summaries from the checked-in
historical artifacts. It does not rerun model inference or submit code to LeetCode.

## Environment

Use Python 3.10 or newer from the repository root:

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade --constraint constraints/ci.txt pip
python -m pip install --constraint constraints/ci.txt -e ".[dev]"
```

The constraints file pins the tested CI and release toolchain. The dependency ranges in
`pyproject.toml` remain the compatibility contract for package consumers.

Before relying on a command, inspect the installed interface:

```bash
prompt-refinement-eval validate --help
prompt-refinement-eval analyze --help
prompt-refinement-eval report --help
```

The analysis itself makes no model or judge calls. Do not set `OPENAI_API_KEY`, launch a
browser, or run judge-submission code for this workflow. The development extra may install
the optional provider SDK for adapter tests, but the tests use an injected fake client.

## Evidence inputs

The benchmark is the 200-record `AutoTest/test.csv` export. The three result inputs are:

| Arm label used here | Historical result file |
| --- | --- |
| Direct GPT-3.5 generation | `AutoTest/leetcode_summary/3.5_score_readable.json` |
| GPT-4o refinement, then GPT-3.5 generation | `AutoTest/leetcode_summary/4o_3.5_score_readable.json` |
| Fine-tuned GPT-4o refinement, then GPT-3.5 generation | `AutoTest/leetcode_summary/finetuned_score_readable.json` |

The labels describe the historical repository convention; they do not claim that these
artifacts measure current model versions. Keep the raw files unchanged. Record the Git
revision and the SHA-256 values emitted by the analysis in any derived report.

## Audit the raw datasets

Run validation separately because its non-zero status is meaningful:

```bash
prompt-refinement-eval validate --output results/data-validation.json
```

For the checked-in raw files, exit status `1` is expected. The benchmark itself is
structurally valid with six warnings: three repeated entry-point signatures and three
likely prompt/signature identity conflicts. The fine-tuning files contain two duplicate
training conversations, one additional repeated training prompt, one empty assistant
object, and one empty validation prompt. Cross-dataset validation hard-fails exact
normalized matches and verifies the hash-bound human review of semantic candidates. That
review confirms equivalent variants of benchmark tasks 1009 and 1038 in the retained
training export. Four fuzzy candidates were reviewed as related but distinct and are not
automatically excluded.

The preserved repository does not bind that exact export to the evaluated fine-tuned
model, so the two findings establish a leakage risk rather than proving which records the
model saw. Excluding both tasks leaves 192 direct-versus-fine-tuned pairs, with the same
23 direct-only and 16 refined-only successes and exact p = 0.3368. The conclusion is
unchanged. The full machine-readable findings are written before the command exits. They
are an audit result, not a validator crash; routine CI tests the validator deterministically
and does not require the historical evidence to pass validation.

Do not make the raw command pass by editing `AutoTest/test.csv` or the fine-tuning
JSONL. The three known identity repairs for task IDs 1003, 1564, and 1672 are documented
separately in `data/curated/benchmark_corrections.json` for a future versioned dataset.
Training/benchmark decisions are recorded in the source-fingerprinted
`data/curated/train_benchmark_overlaps.json` manifest.

## Run the ID-keyed analysis

The CLI defaults to the three result artifacts listed above. Reproduce the structured
analysis with:

```bash
prompt-refinement-eval analyze --output results/historical-analysis.json
```

Those defaults are available from a repository checkout. A wheel installed elsewhere
does not bundle the historical judge payloads; pass at least two explicit
`--arm NAME=PATH` arguments when analyzing external artifacts.

Or reproduce the human-readable result and its machine-readable companion together:

```bash
prompt-refinement-eval report --output docs/results.md --analysis-output results/historical-analysis.json
```

Both analysis commands return `0` when the result artifacts are readable and
structurally usable. Declared-count discrepancies, if present, are preserved in the
report's `issues` array rather than silently corrected. The JSON report contains source
hashes, the benchmark-validation and correction-manifest fingerprints, the 200-ID union,
each missing-ID set, the 193-task complete-case set, observed judge windows, every exact
pairwise comparison, an identity-conflict sensitivity analysis, and the hash-bound
training/benchmark overlap-risk sensitivity. Generated totals in `docs/results.md` should
be regenerated with the CLI, not hand-edited.

## Expected descriptive results

These separate-denominator rates are an inventory of the artifacts, not a fair
head-to-head test:

| Arm | Accepted / observed | Rate | Missing from 200-ID union |
| --- | ---: | ---: | --- |
| Direct GPT-3.5 | 134 / 197 | 68.02% | 1057, 1573, 1576 |
| Fine-tuned GPT-4o refinement | 126 / 196 | 64.29% | 1002, 1005, 1576, 1579 |
| GPT-4o refinement | 55 / 199 | 27.64% | 1154 |

On the 193 tasks observed by every arm, the accepted counts are 131 (67.88%),
124 (64.25%), and 53 (27.46%) in the same order.

## Expected exact paired comparisons

Each row uses only the task IDs shared by that pair. `B - A` is the paired acceptance-
rate difference. The p-value is the unadjusted, two-sided exact McNemar binomial test.

| A | B | Paired tasks | A-only accepted | B-only accepted | Ties | B - A | Exact p-value |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Direct GPT-3.5 | Fine-tuned GPT-4o refinement | 194 | 23 | 16 | 155 | -3.61 pp | 0.3367836 |
| Direct GPT-3.5 | GPT-4o refinement | 196 | 85 | 5 | 106 | -40.82 pp | 7.532842e-20 |
| Fine-tuned GPT-4o refinement | GPT-4o refinement | 195 | 79 | 9 | 107 | -35.90 pp | 4.152441e-15 |

The direct-versus-fine-tuned comparison is inconclusive under a conventional 0.05
threshold, and its observed difference favors the direct arm. The other refined arm is
worse on these historical paired observations. Accordingly, this benchmark provides no
demonstrated improvement from prompt refinement. The experiment is historical and
observational; the p-values do not establish a causal model or prompt effect.

Excluding likely identity conflicts 1003, 1564, and 1672 leaves 191 direct-versus-
fine-tuned pairs. There are 22 direct-only and 16 refined-only successes, a -3.14
percentage-point difference, and exact p = 0.4177. The conclusion is unchanged. See the
generated report for the full 190-task all-arm sensitivity table.

## Verification checklist

1. Confirm the report's task union contains 200 IDs and its complete-case set contains
   193 IDs.
2. Confirm declared totals in each source equal the number of detailed observations.
3. Review every missing-ID list rather than imputing a result.
4. Match paired wins and losses to the exact intersection before interpreting a rate.
5. Preserve validation errors, exclusions, and multiplicity caveats in downstream prose.
6. Run the local quality suite (dependency installation and `pip-audit` need package-index
   or advisory access; analysis and tests make no model or judge calls):

   ```bash
   python -m ruff format --check src tests
   python -m ruff check src tests
   python -m mypy --strict
   python -m pip_audit --skip-editable
   python -m pytest --cov=prompt_refinement_eval --cov-report=term-missing --cov-report=xml
   python -m build
   ```

The legacy online-judge automation is not a reproducibility prerequisite or routine
project path. CI intentionally performs no paid model inference and no judge action.
