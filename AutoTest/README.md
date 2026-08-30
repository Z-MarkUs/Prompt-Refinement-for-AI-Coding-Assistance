# Historical experiment artifacts

This directory preserves inputs and outputs whose judge timestamps span December 8-9,
2024 UTC; the repository was published in March 2025. It is evidence for the re-analysis,
not the supported execution path.

## What is here

- `test.csv`: the original 200-task benchmark export.
- `leetcode_solutions/`: 600 model-generated Python candidates across three arms.
- `leetcode_verify/`: raw historical judge responses.
- `leetcode_summary/`: normalized result records and original aggregate summaries.
- `leetcode_question_id_slug_mapping.json`: the historical task mapping used by the run.

The supported, offline evaluator lives in `src/prompt_refinement_eval/`. It validates
task identity, joins outcomes by question ID, exposes missingness, and computes paired
comparisons. The project website is generated from those auditable aggregates.

## Important limitations

The original export contains three prompt/signature identity conflicts (task IDs 1003,
1564, and 1672). The raw file is kept unchanged for provenance; validation reports the
conflicts and the curated manifest records their corrections. Historical arms also have
different missing-task counts, so their headline percentages are descriptive rather than
a fair paired comparison.

The former browser-login, model-calling, judge-submission scripts, and hard-coded demo
were retired from the current tree. They passed session material through command-line
arguments, coupled evaluation to a third-party judge, and displayed placeholder metrics.
Their history remains recoverable from Git, while current tests and CI are deterministic
and make no paid API or online-judge calls.

Do not use these artifacts or this repository during a live contest or hiring assessment.
