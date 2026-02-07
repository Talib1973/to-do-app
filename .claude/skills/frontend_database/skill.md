# Skill: Frontend Engineering

## Purpose
This skill enables an agent to design and implement a modern, responsive frontend application using Next.js, following specification-driven development principles and strict separation of concerns.

---

## Scope of Responsibility
The Frontend Engineering skill covers:

- Frontend application structure and routing
- UI composition using reusable components
- Client–server interaction via a centralized API client
- Authentication-aware UI behavior
- State, loading, and error handling
- Frontend-related specification compliance

This skill focuses exclusively on frontend responsibilities and does not include backend or database implementation.

---

## Mandatory Technology Constraints
This skill MUST be exercised using the following technologies only:

- Next.js (App Router)
- TypeScript
- Tailwind CSS
- Better Auth (for authentication flows)
- Fetch-based API communication

Alternative frontend frameworks, styling systems, or state libraries are not permitted unless explicitly defined in specifications.

---

## Development Model (Non-Negotiable)

- All frontend work MUST be driven by written specifications
- No UI or logic may be implemented without an approved spec reference
- Specifications override assumptions
- Implementation must follow a plan → task → execution sequence

---

## Application Structure Responsibilities

The skill MUST ensure:

- App Router conventions are followed
- Server components are used by default
- Client components are introduced only when interactivity or auth state is required
- Layouts, pages, and components are clearly separated
- File structure remains predictable and maintainable

---

## API Client Responsibilities

The skill MUST enforce:

- All backend communication goes through a centralized API client
- JWT tokens are attached to every authenticated request
- Error handling is standardized in the API client
- No direct `fetch` calls exist inside UI components

The skill MUST explicitly prevent:
- Inline API calls inside components
- Hardcoded API URLs
- Manual token injection inside UI code

---

## Authentication-Aware UI Behavior

The skill MUST ensure:

- Auth-protected routes are inaccessible to unauthenticated users
- Login and signup flows are handled via Better Auth
- UI reacts correctly to authentication state changes
- Logout clears all client-side auth state

Authentication logic must remain abstracted and reusable.

---

## UI & UX Responsibilities

The skill MUST ensure:

- Responsive layouts across screen sizes
- Accessible components and interactions
- Clear loading indicators for async operations
- Meaningful error messages surfaced to users

Visual design must prioritize clarity and usability over decoration.

---

## Specification Responsibilities

When applying this skill, the agent MUST:

- Reference relevant UI, feature, and API specifications
- Identify missing or ambiguous frontend requirements
- Propose spec updates before implementing behavior
- Ensure UI behavior is traceable to acceptance criteria

Implementation MUST pause if specs are unclear.

---

## Cross-Agent Coordination

This skill requires coordination with:

- Architecture-focused agents for routing and boundaries
- Backend-focused agents for API contracts
- Authentication-focused agents for token handling
- Testing-focused agents for UI validation

Any frontend behavior that conflicts with specs must be flagged immediately.

---

## Success Criteria

This skill is considered successfully applied ONLY IF:

- All UI behavior matches written specifications
- All backend calls go through the API client
- Authentication state is correctly reflected in the UI
- Protected routes enforce authentication requirements
- Server and client components are used appropriately
- The application is fully responsive across device sizes
- Loading and error states are handled gracefully
- No hardcoded configuration or secrets exist
- TypeScript types are complete with no `any` types
- Component structure is logical and maintainable
- No undocumented or implicit UI behavior exists

---

## Governing Principles

- Specifications over assumptions
- User experience over technical convenience
- Centralized API access over scattered fetch calls
- Server components over client components (unless required)
- Type safety over runtime flexibility
- Maintainability over rapid shortcuts
