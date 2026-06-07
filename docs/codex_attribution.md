# Codex Track attribution

This project uses **OpenAI Codex CLI** as a coding agent. To follow the
official `config.toml` attribution model, Codex-generated commits include
a `Co-authored-by: Codex <noreply@openai.com>` trailer.

## Codex-authored commits in this repo

- `1ca7a5e` — feat(lora): add fine-tuning pipeline with Codex
- `627c7bf` — feat(traces): add sharing-is-caring trace pipeline with Codex
- `9841d9c` — feat: implement drama manager with Codex (authored via Codex CLI)

For the drama-manager commit, the file changes were produced by Codex CLI;
the commit author was set to `OpenAI Codex <codex@openai.com>`. The
`Co-authored-by:` trailer was added on subsequent commits in line with the
official spec.

## Continuing the convention

Going forward, every Codex-generated commit will use both:

- `git commit --author="OpenAI Codex <codex@openai.com>"`
- `Co-authored-by: Codex <noreply@openai.com>` trailer

This matches the spec at:
https://developers.openai.com/codex/config-reference
(key `commit_attribution`, default `Codex <noreply@openai.com>`).
