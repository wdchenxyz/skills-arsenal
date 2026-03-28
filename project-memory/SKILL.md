---
name: project-memory
description: Manages project context and structured documentation. Use this skill when starting new tasks, debugging issues, finalizing features, or whenever the user asks for project context. This skill guides Claude to read/write structured files in the docs/ directory to maintain long-term project memory.
---

# Project Memory Skill

## Documentation Index

#### 📍 [Context & Overview](docs/context.md)
- **Purpose**: The "Source of Truth" for the project's current state.
- **Content**: Project vision, high-level tech stack, and a "Current Focus" section.
- **Usage**: Read this at the start of every session to understand the immediate goals.

#### 🏗️ [Architecture & Standards](docs/architecture/)
- **Purpose**: Permanent technical rules and system design.
- **Content**: Data models (ERDs), API specifications, folder structures, and coding conventions.
- **Usage**: Consult these files before scaffolding new modules to ensure consistency.

#### 🗺️ [Plans & Roadmap](docs/plans/)
- **Purpose**: Future-facing tasks and implementation details.
- **Content**: `backlog.md` for prioritized ideas and specific `feature-*.md` files for active development.
- **Usage**: Update these files with "Done" checkboxes as you complete sub-tasks.

#### 🐞 [Issues & Lessons Learned](docs/issues/)
- **Purpose**: Historical record of problems and their solutions.
- **Content**: Root cause analysis, reproduction steps, and "Lesson Learned" for every major bug.
- **Usage**: Search this folder when encountering cryptic errors to see if they've been solved before.

#### ⚖️ [Decision Log (ADR)](docs/decisions/)
- **Purpose**: Tracking the "Why" behind technical choices.
- **Content**: Architecture Decision Records (ADR) documenting trade-offs (e.g., choosing a specific library).
- **Usage**: Refer to this to avoid re-litigating past technical decisions.

#### [Ideas](docs/ideas/)
- **Purpose**: A sandbox for brainstorming and future enhancements.
- **Content**: Unstructured notes, potential features, and experimental concepts.
- **Usage**: Use this space to jot down ideas without worrying about structure; revisit later for refinement.

## Workflow

1. **Memory Initialization**: Initialize the project memory with deeply research on the codebase, understanding the architecture, and familiarizing the pattern of coding style and used tech stacks. Init the docs/ folder structure if not already present.
2. **Task Initialization**: Before writing code, prioritize reading `docs/context.md` and `docs/architecture/` to ensure all implementations align with established project standards and technical stacks.
3. **Issue Troubleshooting**: When a bug is reported, search `docs/issues/` for similar historical entries. After resolving the bug, create a new record documenting the root cause and prevention steps.
4. **Plan Execution**: Create or update implementation checklists within `docs/plans/` to track progress and maintain a clear roadmap for the current feature.
5. **Knowledge Loop (Closing)**: Upon task completion, generate a comprehensive PR Summary and backfill this information into the relevant documents (plans or issues) to close the context loop.

## Documentation Standards

- **Context Maintenance**: Always keep the "Current Focus" or "Progress" section in `docs/context.md` updated after every major change.
- **Decision Tracking**: Every significant technical trade-off or architectural change must be recorded as an ADR (Architecture Decision Record) in `docs/decisions/`.
- **Consistency**: Ensure that all new files and code snippets follow the naming conventions and folder structures defined in `docs/architecture/`.

## Trigger Keywords
- "What is the current status?"
- "Start a new feature/task"
- "Fix this bug"
- "Summarize my changes"
- "Update the documentation"
