# Security policy

## Supported code

Security fixes target the current `main` branch. Historical datasets and result
artifacts remain available for provenance, but legacy model-calling, browser-login,
and online-judge automation are not supported as routine execution paths.

## Reporting a vulnerability

Please report vulnerabilities privately through the repository's **Security** tab and
GitHub private vulnerability reporting, which is enabled for this repository. If the
form is unexpectedly unavailable, open a minimal public issue requesting a private
contact channel; include no vulnerability details. Do not publish credentials, tokens,
cookies, session material, personal data, or a working exploit.

Include the affected revision, component, reproduction steps, impact, and any suggested
mitigation. Reports are handled on a best-effort basis; this project does not promise a
fixed response or disclosure timeline. Please allow time for triage before disclosure.

## Operational boundary

The normal evaluator and test suite are local and deterministic. CI does not receive
model-provider credentials and must never call a paid model, authenticate to an online
judge, or submit solutions. A workflow change that introduces any of those actions is a
security-sensitive change and requires explicit review and authorization.

For authorized local experiments:

- load secrets from the environment, never command-line arguments or tracked files;
- use a narrowly scoped key and set a spending limit at the provider;
- redact request diagnostics and generated reports;
- never reuse contest, hiring-assessment, or personal browser sessions; and
- stop after an ambiguous submission result instead of retrying automatically.

If a secret may have entered Git history, logs, an artifact, or a judge response,
revoke it first. Removing the visible file is not sufficient.
