<!--
Sync Impact Report
==================
Version change: TEMPLATE → 1.0.0 (initial ratification)
Modified principles: N/A (all new — template placeholders replaced)
Added sections:
  - Core Principles (I–VIII)
  - Phase Standards & Technology
  - Cross-Cutting Quality & Constraints
  - Governance
Removed sections: None
Templates requiring updates:
  ✅ .specify/templates/plan-template.md — Constitution Check gate
     populated at runtime by /sp.plan; no static edit required.
  ✅ .specify/templates/spec-template.md — no mandatory-section
     additions triggered by this constitution.
  ✅ .specify/templates/tasks-template.md — task categories
     (observability, migration, typing) already covered by
     Polish phase pattern; no structural change needed.
  ✅ .claude/commands/*.md — reviewed; no agent-only references
     requiring genericisation.
  ⚠ README.md — does not exist yet; MUST be created before
     Phase I implementation begins. See Governance TODOs.
Deferred items:
  - TODO(README): Create project-level README.md before first
    feature branch is opened.
-->

# Progressive Todo Application Constitution

## Core Principles

### I. Simplicity First, Extensibility Always
Every design choice MUST optimise for clarity and minimal
complexity at the current phase. Extensibility MUST be achieved
through clean interfaces and separation of concerns — never
through speculative abstractions or premature generality.
Adding complexity is only permitted when a concrete, present
need justifies it; future-phase needs MUST be addressed in
that future phase.

**Rationale:** Early phases set the cognitive baseline for the
entire project. Overengineering in Phase I makes Phases II–V
harder to reason about, not easier.

### II. Progressive Enhancement — No Throwaway Code
Every module, interface, and data structure introduced in an
earlier phase MUST remain usable (possibly extended, never
rewritten from scratch) in all subsequent phases. Code written
in Phase I is production code, not a prototype.

**Rationale:** Rewriting core abstractions between phases
signals that the original design was wrong. This constitution
requires designs that are correct for today and extensible
for tomorrow.

### III. Separation of Concerns
The codebase MUST maintain four distinct layers at all times:

- **Domain** — Todo entity definitions, value objects,
  business rules. MUST be framework-agnostic.
- **Logic** — Orchestration, workflows, use cases. MUST
  depend only on the Domain layer.
- **Interface** — Console, REST API, Chat UI, etc. MUST
  depend only on the Logic layer.
- **Infrastructure** — Storage, messaging, cloud services.
  MUST depend only on the Logic layer via defined ports.

No layer MUST reach across more than one boundary.

**Rationale:** This layering is the single enabler of the
progressive-enhancement promise. If Domain logic is
entangled with a console UI in Phase I, extracting it for
a web API in Phase II becomes a rewrite.

### IV. Deterministic Behaviour in Non-AI Components
All components that do not involve an AI/LLM call MUST
produce the same output for the same input, every time.
Side-effects (I/O, time, randomness) MUST be injected —
never reached for implicitly.

**Rationale:** Determinism is the foundation of testability.
AI components (Phase III+) are explicitly exempted; their
outputs are validated at the interface boundary.

### V. Explicit State Management & Predictable Data Flow
State transitions MUST be explicit and documented. Data MUST
flow in one direction through the system: input → logic →
output. Mutation of shared state without an explicit
owner is forbidden.

**Rationale:** Predictable data flow is required for both
correctness and auditability, especially once AI agents
can trigger state changes (Phase III).

### VI. Interface Evolution Without Breaking Contracts
When an interface (API endpoint, CLI command, entity schema)
is extended, all existing consumers MUST continue to work
without modification. Additive changes (new fields, new
endpoints) are permitted. Removals and renames MUST be
preceded by a deprecation phase.

**Rationale:** Phases II–V layer on top of Phase I. Breaking
a contract at any boundary forces cascading changes across
the stack.

### VII. AI Components Are Additive, Not Foundational
AI/LLM-powered features (Phase III+) MUST operate exclusively
through the established Logic-layer interfaces. AI MUST NOT
reach directly into storage, domain models, or infrastructure.
Every AI action MUST be explainable, auditable, and
reproducible via a non-AI path.

**Rationale:** AI outputs are non-deterministic by nature.
Grounding them in the deterministic system ensures the
application remains reliable and testable even as AI
capabilities evolve.

### VIII. Zero Hard-Coded Environment Assumptions
All environment-specific values (ports, URLs, credentials,
feature flags, cloud region) MUST be supplied via environment
variables or configuration files. No value MUST be baked into
source code.

**Rationale:** The same codebase MUST run locally, in
Minikube (Phase IV), and in DigitalOcean (Phase V) with
only configuration changes.

## Phase Standards & Technology

This section records the agreed technology stack and
standards for each phase. Additions here require a MINOR
version bump; removals or stack changes require a MAJOR bump.

| Phase | Name | Technology |
|-------|------|------------|
| I | In-Memory Console App | Python 3.x, stdlib only |
| II | Full-Stack Web App | Next.js, FastAPI, SQLModel, Neon DB |
| III | AI-Powered Chatbot | OpenAI ChatKit, Agents SDK, MCP SDK |
| IV | Local K8s Deployment | Docker, Minikube, Helm, kubectl-ai, kagent |
| V | Cloud Deployment | Kafka, Dapr, DigitalOcean DOKS |

### Phase I Standards
- Pure in-memory data storage; no file or database I/O.
- Console interaction only (stdin/stdout).
- CRUD operations: create, list, update, complete, delete.
- Deterministic command handling.
- Clear error messages on all failure paths.
- No external dependencies beyond Python standard library.
- Stateless across executions; single-user context.

### Phase II Standards
- Domain and Logic layers MUST be reused from Phase I
  without modification to their public interfaces.
- RESTful API with explicit schema definitions (OpenAPI).
- Persistent storage via SQLModel; schema migrations MUST
  be versioned.
- Frontend and backend MUST be independently deployable.
- Authentication-ready architecture (auth module present
  but MAY be a no-op until required).

### Phase III Standards
- AI MUST operate exclusively through Logic-layer tools.
- No direct AI manipulation of database state.
- All AI actions MUST be logged and auditable.
- Chat interactions MUST map 1-to-1 to existing Todo CRUD
  operations.
- Prompt design MUST be safety-first; tool constraints
  MUST limit AI to permitted actions only.

### Phase IV Standards
- Each service MUST be containerised with a single
  responsibility.
- Infrastructure MUST be declared via Helm charts.
- Local dev environment MUST achieve production-parity
  architecture.
- All containers MUST expose health-check endpoints.
- Structured logging MUST be enabled from container start.

### Phase V Standards
- Todo lifecycle events MUST be published to Kafka topics.
- Inter-service communication MUST use Dapr sidecars.
- Services MUST be horizontally scalable; no shared
  in-process state between replicas.
- 12-factor principles MUST be followed.

## Cross-Cutting Quality & Constraints

### Code Quality
- Explicit typing MUST be used wherever the language
  supports it (type hints in Python, types in TypeScript).
- Meaningful naming: variables, functions, and modules
  MUST be named for what they represent, not how they
  are implemented.
- Code MUST be readable by a single developer without
  prior context; inline comments are permitted only where
  logic is non-obvious.

### Testing Discipline
- Every public interface MUST have a corresponding test
  before it is considered done.
- Phase I MUST include unit tests for all Domain and Logic
  functions using Python stdlib `unittest`.
- Integration tests MUST be added whenever a new
  infrastructure boundary is introduced (Phase II+).
- Contract tests MUST gate every API schema change.

### Migration & Continuity
- Each phase MUST ship a migration note documenting:
  what changed, what was preserved, and how to verify
  correctness.
- No phase MAY delete or rename a Domain-layer entity
  without first confirming all consumers are updated.

### Performance & Scalability
- No premature optimisation. Performance work is permitted
  only when a concrete, measured bottleneck exists.
- Phase I MUST start and respond to commands in under
  100 ms on a modern machine (no I/O).
- Phase II+ performance targets MUST be defined in the
  feature spec before implementation begins.

### Security
- Secrets MUST never appear in source code or logs.
- All user-facing inputs MUST be validated at the
  interface boundary before reaching Logic.
- Authentication and authorisation boundaries MUST be
  defined in Phase II even if enforcement is deferred.

### Vendor Lock-In
- Prefer open standards (OpenAPI, OCI, CNCF tooling).
- Cloud-specific SDKs are permitted in the
  Infrastructure layer only; Logic and Domain MUST NOT
  import them.

## Governance

1. **Supremacy:** This constitution supersedes all other
   project practices. When a practice conflicts with a
   principle here, the principle wins.
2. **Amendments:** Any change to this constitution MUST be
   documented with a rationale, reviewed by the architext,
   and reflected in a version bump following semantic
   versioning (see Version Policy below).
3. **Compliance:** All PRs and planning documents MUST
   include a Constitution Check confirming no principle
   is violated. Violations MUST be justified in a
   Complexity Tracking table (see plan-template).
4. **Version Policy:**
   - MAJOR — principle removal, redefinition, or
     backward-incompatible governance change.
   - MINOR — new principle or materially expanded
     guidance in an existing section.
   - PATCH — clarifications, wording fixes, or
     non-semantic refinements.
5. **Runtime Guidance:** Use `.claude/commands/` command
   files for day-to-day development workflows. The
   constitution is the source of truth for *what* and
   *why*; command files define *how*.

**Version**: 1.0.0 | **Ratified**: 2026-02-05 | **Last Amended**: 2026-02-05
