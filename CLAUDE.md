# Project instructions

This repository is a local-first, reproducible re-analysis of historical prompt-refinement strategies for code generation. Favor auditable evidence over impressive-looking claims.

## Working agreements

- Preserve raw benchmark inputs and historical result artifacts. Put corrections or derived outputs in clearly named, reviewable files instead of silently rewriting evidence.
- Keep every experiment arm traceable to its benchmark version, model or strategy, parameters, run identifier, and result source.
- Compare arms on the same task IDs. Report missing or excluded tasks, effect size, and uncertainty; an unpaired headline rate does not prove an improvement.
- Keep tests deterministic and offline. Use small fixtures for routine development.
- Treat `AutoTest/` and `Model Fine-Tuning/` as legacy research material unless a task explicitly calls for migration.

## Commands

Use the repository environment, then inspect the installed interface before choosing flags:

```text
python -m pytest
prompt-refinement-eval validate --help
prompt-refinement-eval analyze --help
prompt-refinement-eval report --help
```

Run the narrowest relevant tests while editing, followed by the full suite before handoff. Validation should precede analysis, and analysis should precede publishing a report.

## Safety and permissions

- Never print, persist, or pass credentials, cookies, tokens, CSRF values, or session data through command-line arguments. Use documented environment configuration and redact diagnostics.
- Do not submit to an online judge, call a paid model, or incur API spend without explicit authorization for that action and scope. Bulk judge submission is never an implicit test step.
- Do not use this project for live contests or hiring assessments.
- Never claim that prompt refinement improves correctness without paired evidence on comparable tasks. State negative and inconclusive findings plainly.

## Agent workflow

For benchmark validation, experiment analysis, new experiment arms, or claim audits, load `.claude/skills/prompt-refinement-evals/SKILL.md`. Codex uses the byte-identical mirror at `.agents/skills/prompt-refinement-evals/SKILL.md`.
