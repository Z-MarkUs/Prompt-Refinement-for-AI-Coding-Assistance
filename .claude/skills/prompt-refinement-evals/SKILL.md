---
name: prompt-refinement-evals
description: Validate coding benchmarks, analyze prompt-refinement experiments, add comparable experiment arms, and audit evidence-backed claims in this repository.
---

# Prompt Refinement Evaluations

Use this skill when work changes the benchmark, compares prompt-refinement results, adds an experiment arm, or checks whether a public claim is supported. Keep the workflow local and offline unless the user separately authorizes an external action.

## Establish the evidence boundary

1. Identify the benchmark version, task identifier, experiment arm, run metadata, and result source involved in the request.
2. Preserve raw inputs and results. Write corrections and derived artifacts separately with enough provenance to reproduce them.
3. Inspect the current CLI contract before selecting flags:

```text
prompt-refinement-eval validate --help
prompt-refinement-eval analyze --help
prompt-refinement-eval report --help
```

Treat these subcommands as the stable workflow and adapt arguments to the installed version. Prefer fixture-sized inputs while developing.

## Validate a benchmark

Run `prompt-refinement-eval validate` before trusting or comparing results. Check at least:

- unique and stable task IDs;
- required fields, parseable records, and consistent schemas;
- agreement between problem text, entry-point signature, and expected language;
- duplicates, missing values, malformed outputs, and unexplained exclusions;
- provenance and an immutable fingerprint for the evaluated input.

Stop the analysis when structural errors could change task identity or comparability. Report affected IDs and the repair path instead of silently dropping records.

## Analyze experiment arms

Run `prompt-refinement-eval validate` before analysis. Stop when its findings undermine
task identity or comparability. A preserved historical dataset may still be analyzed when
known defects are fingerprinted, explicitly scoped, and do not invalidate the requested
ID-keyed comparison; keep those findings visible in the report. Join arms by task ID and
make the paired intersection explicit. Report:

- numerator, denominator, missingness, and exclusions for every arm;
- paired wins, losses, and ties against the declared baseline;
- absolute effect size and an appropriate uncertainty interval or paired test;
- model and strategy metadata, benchmark fingerprint, and analysis settings;
- sensitivity to invalid, missing, timed-out, or otherwise non-comparable observations.

Never infer improvement from separate denominators or a higher raw percentage alone. Call a result improved only when comparable paired evidence supports that wording; otherwise use neutral language such as observed difference, inconclusive, or worse.

## Add an experiment arm

Follow the existing arm schema and CLI abstractions rather than branching analysis logic for one model. Give the arm a stable identifier, record its configuration and provenance, add deterministic fixtures, and verify that `validate`, `analyze`, and `report` can consume it without weakening comparisons. Do not overwrite an earlier run with a new configuration.

## Audit or publish claims

Use `prompt-refinement-eval report` to produce results from validated analysis artifacts, not hand-copied totals. Trace every headline number back to a benchmark fingerprint and run IDs. Keep negative results, limitations, missingness, and non-significant findings visible. If the available evidence does not prove the proposed claim, rewrite the claim rather than stretching the analysis.

## Safety boundary

- Never log or expose API keys, cookies, access tokens, CSRF values, session identifiers, or other credentials. Redact diagnostics and do not put secrets in command-line arguments or committed files.
- Never submit solutions to an online judge, mass-submit benchmark outputs, run paid model inference, or incur API spend without explicit authorization for the exact action and scope. Inspecting local artifacts is not authorization.
- If an authorized external run has ambiguous results, stop and report the uncertainty instead of retrying automatically.
- Never run this workflow against a live contest or hiring assessment.

## Completion check

Run the relevant targeted tests and then `python -m pytest`. Confirm that validation
either passed or produced only documented, scoped legacy findings; comparisons are paired;
provenance is present; generated claims match the analysis; and no credential-bearing
artifacts were created.
