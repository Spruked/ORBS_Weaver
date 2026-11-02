# ORBS vault authority

Owner decision: November 1, 2026.

`orbs_vault_system` is the single source of truth within the unified ORBS Weaver
repository. This directory was renamed from `Vault-Logic-System-Template`.

It owns approved Site World facts, commercial offers and policies, semantic and
pointer maps, source evidence, approval records, release evidence, and durable
customer-isolated memory. Derived indexes, reasoning results, visitor observations,
and temporary Session World state cannot independently overwrite approved truth.

The other source directories provide implementation capabilities. Existing
bundled Vault copies, including `Orbot/Orbot_Vault-Logic-System`, are retained
implementation/reference material, not competing authorities for this system.
Historical component documents describing those copies as sole authority are
superseded by this workspace decision.

Orbot's default host-memory and token locations and the standalone AIMS service's
default data location are rooted here. Existing explicit environment overrides
remain supported; deployment configuration must keep authoritative storage within
this boundary. Existing external data has not been migrated or deleted.

This ownership decision does not complete the template's placeholder evaluator,
compiler, or governance implementations. Those require separate implementation
and verification before production claims can be made.

Source code belongs in Git. Local credentials, tokens, ledgers, and databases must
remain ignored. Website deployment must package only public website artifacts,
not this entire source workspace.
