# A.I.M.S. — Agnostic Immutable Memory System

A.I.M.S. is a local-first, model-agnostic memory system. It preserves
authoritative evidence in append-only ledgers, separates A Priori knowledge
from A Posteriori learning, and derives indexes and current relevance without
rewriting historical truth.

## Release status

**v0.2.0 — Functional Prototype.** The integrity ledger, Vault replay,
indexes, retrieval receipts, and basic adaptive graph behavior are implemented.
The three-SKG model, hybrid retrieval, authority classification, formal outcome
signals, recovery hardening, scale evidence, and Display Hub are not yet
complete. See [the v1 hardening contract](HARDENING_CONTRACT.md) for the
measurable release gates.

The **v0.3 work in progress** includes logical A Priori, A Posteriori, and
Collective SKG domains with a zero-dependency Python reference backend.
GraphQLite is the selected optional embedded accelerator; it remains derived
state and is never Vault authority. Install it only when needed with
`pip install .[graphqlite]`, then provide its backend factory to the host
integration.

> The Vault preserves truth.
>
> The indexes locate truth.
>
> The SKG organizes relevance.
>
> Short-Term Memory carries active cognition.
>
> The Retrieval Ledger remembers every return forever.

## Storage hierarchy

```text
Immutable Vault event ledger     authoritative evidence and provenance
  A Priori / A Posteriori atoms  replayed from append-only Vault events
  evaluation / retirement events evidence for changing interpretation
  relationship evidence          rebuilds the SKG

Derived persistent indexes       A Priori, A Posteriori, Collective
Structured Knowledge Graph       mutable and rebuildable interpretation
Short-Term Memory                temporary, decaying cache
SQLite Retrieval Ledger          permanent retrieval sets and feedback
```

The Vault is never self-pruning. The SKG evaluates relevance and records
resulting evaluation or retirement evidence in the Vault ledger.

## Integrity modes

Every ledger begins with an immutable genesis security policy.

- `visual`: zero-secret SHA-256 hash chain with deterministic visual Glyphs.
- `authenticated`: SHA-256 canonical entry hashes plus an HMAC-SHA-256 Glyph
  chain. `glyph_mode` and `glyph_key_id` are part of the canonical hash.

Authenticated ledgers fail closed without the corresponding runtime keyring.
Secrets are never serialized into ledgers, Vault records, indexes, retrieval
receipts, API responses, or logs. Key rotations create immutable events; old
records continue to validate with their recorded key IDs.

## Embedded memory integration

A.I.M.S. is a memory library under the canonical `orbs_vault_system` authority.
It has no standalone HTTP server, service configuration, or required listener.
The host uses `memory_core` directly and supplies a separate storage directory
for each customer. Visitor observations and retrieved records do not independently
establish approved prices, policies, offers, or other business truth.

```python
from pathlib import Path
from memory_core import AIMSMemorySystem

# Supplied by the trusted host, inside orbs_vault_system.
customer_store = Path(vault_root) / "clients" / customer_id / "memory"
memory = AIMSMemorySystem(customer_store, matrix_id="customer_memory")
```

The trusted host validates customer identity and storage scope before constructing
the memory instance. Preserve the existing single-writer integration; do not open
a competing writer for the same customer store.

Authenticated ledger mode remains available through the existing library
parameters `security_mode`, `glyph_key`, `glyph_key_id`, and `glyph_keys`.
The host supplies key material securely; keys are never stored in ledger records.
Append-only evidence, integrity verification, temporal provenance, retrieval
receipts, indexing, reconstruction, and semantic graphs remain library features.

## Validation

```powershell
python -m unittest discover -s tests -v
```

## License

This repository is proprietary and confidential. See [LICENSE](LICENSE).
