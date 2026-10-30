# Specializing the ledger

Read when planning work governed by domain knowledge, specialist skills or external contracts.

Create a research file that defines the domain profile: authoritative sources and their revisions, mandatory
constraints, unresolved disagreements, validation methods and the specialist skills that apply. For each
requirement, record its source, its consequence, the task that owns it and the evidence that accepts it.
Consult primary material when facts need research, and keep supplied claims apart from observations.

Study the actual system and its dependencies before choosing a design. Inventory reusable resources,
evaluate their contracts, and record accept, extend or reject with reasons. Fix deliverable boundaries,
ownership, failure behavior and compatibility promises before dependent implementation starts.

The generic skills govern sequencing and persistence; specialist instructions govern domain correctness.
Read a specialist's preparation guidance before marking its dependent tasks ready, and its execution guidance
at those tasks. Record the paths actually used. If a needed skill is missing, the ledger either carries the
required contract and evidence itself or blocks that dependency.

| Work | Domain-specific preparation and evidence |
| --- | --- |
| Cryptography | Normative revision and errata, reuse and exact interfaces, an independently verified oracle, boundary and misuse cases, side-channel review scope; keep each applicable specialist gate |
| Data migration | Source snapshot, mapping and compatibility, restart and idempotency behavior, record counts and checksums, dry-run and cutover criteria |
| Research or documents | Primary-source provenance, definitions, conflicting claims, coverage criteria, reviewer rubric, document revision |
| Physical operations | Inventory identity, equipment and access dependencies, measured capacity, per-item quality and acceptance records |

Choose checks that can disprove the failure that matters. Internal consistency, or a round trip through the
same code, may not establish correctness. When independent reference evidence is required, establish its
provenance and method before trusting it. Record what each check cannot establish.
