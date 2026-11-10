# Security policy

This is a portfolio project. Nothing in it is deployed, and it holds no real data: the operator
(Halvorsk Mobile) is fictional and every customer, note, phone number and campaign result is simulated.

## Report a vulnerability

Please report privately to the repository owner through GitHub (the **Security** tab, **Report a
vulnerability**, when available). Please do not open a public issue. First reply within a week.

## Controls in place

- The copilot only recommends. Every reply passes `guard` in `retention/copilot.py` before a desk agent
  sees it: unknown, ineligible or over-limit offers, forbidden promises, contact details in the talk
  track and numbers that are not in the account data are caught, and the reply is replaced by the
  uplift model's offer and escalated to a supervisor.
- Age band and region are never shown to the model and never used by any model or rule.
- Customer notes are treated as data; an injection stress run is part of the measured results.
- The CI gate fails if any offer that reached the desk breaks the offer rules.
- Model output is scrubbed of real brand names before it is stored or scored; the brand check excludes
  no file.
- gitleaks over the full git history in CI; Dependabot version updates for pip, Terraform and Actions.
- Every GitHub Action pinned to a commit SHA; workflow tokens are read-only.
- The deploy workflow is manual, gated by `DEPLOY_ENABLED`, and logs in with OIDC (no client secret).
- Model weights come from pinned revisions and are checked by SHA-256; GGUF only, never pickle files.
- The synthetic data and measured runs are checked against a hash manifest.

## Not active while the repository is private

- **Code scanning (CodeQL)**: the workflow is in `.github/workflows/codeql.yml` but the job is skipped
  while the repository is private, because code scanning needs GitHub Code Security on private
  repositories.
- **Secret scanning and push protection** on GitHub are not available for this private repository on
  the current plan; gitleaks in CI covers secrets instead.
- **Branch rules** on `main` (no force-push or deletion, required CI checks) are not enforced on a
  private repository on the current plan. They are applied once the repository is public or the plan
  allows it.
