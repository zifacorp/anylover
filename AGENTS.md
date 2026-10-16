# AnyLover contributor guide

## Product invariant

AnyLover owns companion identity, consent, provenance, memory, deletion, and backup. Model providers and agent surfaces are replaceable adapters.

## Commands

- User/Agent one-click install: `bash install.sh --agent auto`
- Portable Skill install: `npx skills add zifacorp/anylover`
- The distributable Skill is self-contained under `integrations/anylover-companion/skills/anylover-companion/`; its setup script installs only the runtime and its CLI reference is the fallback when MCP tools are unavailable.
- Inspect the install without writes: `bash install.sh --dry-run --agent all`
- Follow `AGENT_INSTALL.md` when the task is to install AnyLover into Agent tools.
- Install: `python -m pip install .`
- Editable install: standard CPython may use `python -m pip install -e .`; some Anaconda/Conda Python 3.13 builds skip the generated hidden `.pth`, so use a regular install when imports fail.
- Test: `python -m unittest discover -s tests -v`
- Networked Skills CLI smoke test (temporary HOME only): `python scripts/verify_skills_install.py`
- Syntax check: `python -m compileall -q src tests`
- CLI smoke test: `ANYLOVER_HOME=$(mktemp -d) anylover init --name Any`
- MCP entrypoint: `anylover-mcp`

The one-click installer must preserve an existing MCP entry named `anylover` unless the user explicitly authorizes `--force-agent-config`. Never run the installer against global Agent configuration merely to test it; use `--dry-run` or isolated config-home overrides.

## Privacy and safety rules

- Never persist passwords, API keys, cookies, bearer tokens, private keys, or raw tool traces.
- Do not add automatic full-transcript capture. Memory writes must remain selective and provenance-bearing.
- Boundaries and sensitive memories require explicit consent. Secret-class data is rejected.
- Deletion must preserve a content-free tombstone until multi-device sync can propagate it.
- Never represent the companion as human, conscious, a therapist, or the user's exclusive relationship.
- Never implement affection scores, streak pressure, paid intimacy, or guilt-based retention.

## Architecture

- Keep domain logic under `src/anylover/service.py` independent of transport.
- Treat MCP, HTTP, CLI, and future mobile SDKs as adapters over the same service.
- Keep storage migrations additive and versioned in `src/anylover/storage.py` until a migration package is introduced.
- Prefer deterministic retrieval tests before adding embeddings or model-based extraction.
