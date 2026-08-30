# Contributing

Thank you for helping make this evaluation more reproducible. Contributions should
favor auditable evidence over stronger-looking claims.

## Development setup

Python 3.10 or newer is required. Create an isolated environment and install the
package with its development dependencies:

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade --constraint constraints/ci.txt pip
python -m pip install --constraint constraints/ci.txt -e ".[dev]"
```

Then inspect the installed command-line interface before choosing flags:

```bash
prompt-refinement-eval validate --help
prompt-refinement-eval analyze --help
prompt-refinement-eval report --help
```

## Evidence rules

- Treat `AutoTest/` and `Model Fine-Tuning/` as historical evidence. Do not silently
  correct or replace raw inputs, generated candidates, or recorded judge outcomes.
- Put corrections and derived outputs in new, reviewable files. Record the source,
  task IDs, configuration, and a content fingerprint.
- Join experiment arms by task ID. Report each denominator, missing IDs, paired wins
  and losses, effect size, and uncertainty. An unpaired percentage is descriptive,
  not evidence that one strategy improved correctness.
- Keep negative and inconclusive findings visible. The checked-in historical results
  do not demonstrate an improvement from prompt refinement.
- Never commit credentials, cookies, CSRF values, model tokens, or session data.

The historical online-judge automation is not a routine development workflow. Do not
submit to an online judge, call a paid model, or incur API spend without explicit
authorization for that exact action and scope. Routine tests and CI must remain
deterministic and make no model or online-judge calls.

## Quality checks

Run the same gates as CI before opening a pull request:

```bash
python -m ruff format --check src tests
python -m ruff check src tests
python -m mypy --strict
python -m pip_audit --skip-editable
python -m pytest --cov=prompt_refinement_eval --cov-report=term-missing --cov-report=xml
python -m build
```

Use `python -m ruff format src tests` to apply formatting. Add focused tests for every
behavior change, including missing or malformed observations when analysis logic is
affected. Tests must use local fixtures and fakes; they must not require an API key,
browser session, network service, or online judge.

## Pull requests

Keep changes narrow and explain:

1. what changed and why;
2. which source artifacts and task IDs are affected;
3. how the result was validated;
4. what remains uncertain or out of scope; and
5. whether public claims or reproducibility instructions changed.

Do not include generated environments, coverage output, build artifacts, local runs,
or secrets. Include third-party material only when you have permission to contribute it
and preserve any required attribution.
