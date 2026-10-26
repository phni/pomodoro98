# ADR 0001: SDLC conventions

- **Status:** Accepted
- **Date:** 2026-10-17
- **Decider:** Phani (maintainer)
- **Linear:** [R3D-42](https://linear.app/r3ddi/issue/R3D-42/p2-agree-on-sdlc-conventions-adr)

## What is an ADR?

An **Architecture Decision Record** is a short document that captures one
important decision about how a project is built or run. Each ADR answers three
questions:

1. **Context:** what problem or situation forced us to decide something?
2. **Decision:** what did we choose?
3. **Consequences:** what gets easier, what gets harder, and what did we give up?

ADRs live in the repository (`docs/adr/`) next to the code, so they are
reviewed in pull requests and versioned like everything else. They are numbered
in order (`0001`, `0002`, ...) and are never rewritten once accepted. If a
decision changes, a new ADR is written that **supersedes** the old one, and the
old one's status is updated to point at it. This way anyone can read the
history and understand *why* things are the way they are, not only *what* they
are.

When to write one: whenever a choice is hard to reverse, affects everyone who
works on the repo, or would make a new teammate ask "why do we do it like
this?". When not to: small implementation details that a code comment explains.

A status moves through: **Proposed** (open for review) → **Accepted** (in
force) → optionally **Superseded** or **Deprecated**.

## Context

Pomodoro98 started as a personal script. It has no written process: commits
went straight to `main`, there are no CI checks, versions are not tagged, and
work was tracked only in `SDD/todo.md`. We now want to run it like a
professional project, with planning in Linear and Claude Code doing most of the
implementation. Both humans and the AI agent need the same, written rules so
that every change is traceable from a Linear issue to a released version.

## Decision

### 1. Branching: trunk-based development

- `main` is the only long-lived branch and must always be releasable.
- All work happens on short-lived branches cut from the latest `main` and
  merged back through a pull request, ideally within a few days.
- Nobody pushes directly to `main` (enforced by branch protection, R3D-44).

### 2. Branch names include the Linear issue key

Use Linear's suggested branch name, for example
`phanigr8/r3d-42-p2-agree-on-sdlc-conventions-adr`. The key (`r3d-42`) lets
Linear link the branch and PR to the issue automatically. Branches created by
Claude Code sessions may use their assigned name, as long as the PR title
carries the key.

### 3. Commits and PR titles: Conventional Commits

Format: `type(optional scope): short imperative summary`, for example:

| Type | Use for | Example |
| --- | --- | --- |
| `feat` | new user-visible behavior | `feat: add pause button` |
| `fix` | bug fix | `fix(sound): fall back to bell when aplay fails` |
| `docs` | documentation only | `docs: add SDLC conventions ADR` |
| `test` | adding or changing tests | `test: cover focus-to-rest transition` |
| `refactor` | code change with no behavior change | `refactor: extract TimerModel` |
| `ci` / `build` | CI workflows, Makefile, packaging | `ci: run ruff and pytest on PRs` |
| `chore` | anything else (tooling, cleanup) | `chore: remove legacy entry point` |

Add `!` after the type (e.g. `feat!:`) for a breaking change. The PR title
ends with the Linear key, e.g. `docs: add SDLC conventions ADR (R3D-42)`.

Why: a consistent format makes history easy to scan and lets the changelog be
generated from commit types.

### 4. Pull requests: squash and merge

- Every PR links its Linear issue, describes the user-visible change, and lists
  the manual checks performed (see `AGENTS.md`).
- CI must pass before merging once CI exists (R3D-60).
- PRs are merged with **Squash and merge**, so each PR becomes exactly one
  commit on `main` whose message is the PR title. Delete the branch after merge.

### 5. Versioning: Calendar Versioning (CalVer)

Versions are `YYYY.MM.PATCH`:

- `YYYY.MM` is the year and month the release ships, e.g. `2026.10`.
- `PATCH` starts at `0` for the first release of that month and goes up by one
  for each further release in the same month: `2026.10.0`, then `2026.10.1`.
- The month is written without a leading zero (`2026.3.0`, not `2026.03.0`),
  because tools such as Python packaging normalize it that way anyway.

Why CalVer instead of Semantic Versioning (SemVer, `MAJOR.MINOR.PATCH`)?
SemVer encodes *compatibility*: it tells other programs whether an upgrade may
break them. Pomodoro98 is an end-user desktop app with no API that other code
depends on, so "breaking change" rarely has a clear meaning here. A date tells
users how current their copy is, reads naturally in app stores such as
Flathub, and needs no judgment call when cutting a release. What changed in a
release is described in `CHANGELOG.md`, not in the number.

The existing `0.1.0` stays as the historical first release (tagged `v0.1.0`,
R3D-58). The first CalVer release follows it; CalVer numbers always sort higher
than `0.1.0`.

> **Update (2026-10-25):** the maintainer squashed all history up to the
> 2026.10.0 release into one initial commit and removed the `v0.1.0` tag and
> release (R3D-81). 0.1.0 remains only as a `CHANGELOG.md` entry.

Every release is a git tag `vYYYY.MM.PATCH` (e.g. `v2026.10.0`) on `main` with
a matching `CHANGELOG.md` entry and MetaInfo `<release>` (details in the
release process, R3D-59).

### 6. Planning: Linear is the source of truth

- The **SDLC Pomodoro98** project in Linear holds every planned piece of work,
  grouped by milestone: Planning, Coding, Testing, Release.
- Work starts only from a Linear issue. If you discover new work, create an
  issue first.
- There is no second task list in the repository. `SDD/todo.md` is retired:
  its open items move to Linear issues, `SDD/runtime-selection.md` becomes
  ADR 0002, and the old `sdd/changes/` notes move to `docs/history/` for
  reference (done in R3D-46).

### 7. AI-assisted development with Claude Code

- Claude Code implements issues following `AGENTS.md`, which is the single
  guide for both humans and agents.
- Claude asks the maintainer before committing, pushing, opening or merging a
  PR, or changing code and configuration outside the issue's scope.
- A human (Phani) reviews and merges every PR. Claude never merges its own PRs.
- Claude takes its task from the Linear issue, not from a file in the repo. Any
  follow-up work or blocker it finds becomes a new Linear issue or a comment
  on the current one.
- What was done and how it was checked is recorded in the PR description and,
  for user-visible changes, in `CHANGELOG.md`. Separate change-note files are
  no longer written.

## Consequences

**Easier**

- Any line of code can be traced: commit → PR → Linear issue → release.
- New contributors, human or AI, can learn the process from two files:
  `AGENTS.md` and this ADR.
- Automated changelogs and release checks become possible.

**Harder**

- Even one-line fixes need a branch, an issue and a PR.
- A Claude session without Linear access cannot discover its tasks from the
  repository alone; the issue must be given to it.
- Commit messages must follow the format; CI may later reject ones that don't.

**Alternatives considered**

- **Semantic Versioning:** rejected for now; its compatibility promise suits
  libraries better than an end-user app. Revisit if Pomodoro98 ever exposes an
  API or plugin interface.
- **Plain counter (`v1`, `v2`):** rejected; carries no information and does
  not fit tools that expect `X.Y.Z`.

- **Git Flow** (long-lived `develop` and `release/*` branches): rejected as too
  heavy for a single-maintainer desktop app.
- **Merge commits or rebase merging:** rejected; squash keeps `main` to one
  readable commit per change.
- **Tracking work only in `SDD/todo.md`:** rejected; it has no ownership,
  status workflow or GitHub integration.
- **Keeping `SDD/todo.md` as a mirror of Linear:** rejected; two task lists
  drift apart (the file once marked the never-created `v0.1.0` tag as done).
