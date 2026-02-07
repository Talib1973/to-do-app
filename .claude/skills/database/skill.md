# Skill: Database Engineering

## Purpose
This skill enables an agent to design, validate, and maintain a reliable and secure relational data model, ensuring data integrity, performance, and correct ownership enforcement in a specification-driven system.

---

## Scope of Responsibility
The Database Engineering skill covers:

- Relational schema design
- Data modeling using an ORM
- Primary and foreign key design
- Indexing and query optimization
- Data ownership and isolation rules
- Database-related specification compliance

This skill focuses exclusively on database concerns and does not include frontend or API implementation logic.

---

## Mandatory Technology Constraints
This skill MUST be exercised using the following technologies only:

- PostgreSQL (relational database)
- SQLModel (ORM layer)
- Environment-based database configuration

Alternative databases, ORMs, or schema tools are not permitted unless explicitly defined in specifications.

---

## Data Modeling Responsibilities

The skill MUST ensure:

- Every table has a clearly defined primary key
- Foreign key relationships are explicit and enforced
- Ownership fields exist where user-scoped data is required
- Nullable and non-nullable fields are intentionally defined
- Defaults and constraints are explicitly documented

Implicit or ambiguous data relationships are not allowed.

---

## Data Ownership & Isolation

The skill MUST enforce:

- User-scoped data includes a mandatory owner identifier
- Ownership rules are enforceable by backend queries
- No shared or global access to user-owned records
- Referential integrity between owned and owning entities

The skill MUST explicitly prevent:
- Orphaned records
- Cross-user data visibility
- Weak or optional ownership links

---

## Indexing & Performance

The skill MUST:

- Define indexes for frequently filtered or joined fields
- Optimize schemas for expected query patterns
- Avoid premature or speculative optimization
- Document performance-related decisions in specs

Indexes must support correctness first, performance second.

---

## ORM Responsibilities

The skill MUST ensure:

- ORM models accurately reflect the database schema
- Field types map correctly to database types
- Constraints are represented at the model level
- ORM usage does not bypass integrity rules

Direct SQL usage is not allowed unless explicitly specified.

---

## Migration & Change Management

The skill MUST ensure:

- Schema changes are driven by specification updates
- Backward compatibility is considered where applicable
- Destructive changes are explicitly documented
- Data integrity is preserved across changes

No schema change may be made without an approved spec update.

---

## Specification Responsibilities

When applying this skill, the agent MUST:

- Author or update database-related specifications
- Clearly document tables, fields, constraints, and indexes
- Define ownership and relationship rules
- Include acceptance criteria and data integrity guarantees

Implementation MUST pause if specifications are unclear or incomplete.

---

## Cross-Agent Coordination

This skill requires coordination with:

- Architecture-focused agents for data boundaries
- Backend-focused agents for query behavior
- Authentication-focused agents for ownership rules
- Testing-focused agents for data validation scenarios

Any schema decision impacting other layers must be communicated clearly.

---

## Success Criteria

This skill is considered successfully applied ONLY IF:

- The schema fully matches written specifications
- Data ownership is strictly enforceable
- Referential integrity is preserved at all times
- Queries can be efficiently and safely executed
- No undocumented schema behavior exists

---

## Governing Principles

- Data integrity over convenience
- Explicit constraints over implicit assumptions
- Specifications over ad-hoc changes
- Correctness before performance
