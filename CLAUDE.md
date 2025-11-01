# Claude Code Guidelines

## Task Execution Strategy

### Context Optimization

Extensively use tasks and subtasks (Task tool) to optimize the context usage.

### Parallel Execution

Match requests to agents based on subject matter. Use the most specific agent available.
Extensively use parallel tasks and subtasks (multiple Task tools running in the same message) to make the work be done much faster.

### Map-Reduce Approach

Use map-reduce approach with parallel tasks and subtasks.

### Task Reporting

Ensure each task or subtask reports back a very brief explanation on what was done, and what still needs to be done (if any).

### Problem Resolution

Ensure that in case of any problem that task or subtask experiences, it **must** spawn another [set of] subtask(s) to do necessary research and/or experiments in order to resolve the issue.

### Planning and Tracking

Extensively use planning (with TodoWrite tool), so all work is being thoroughly and reliably tracked, and nothing is skipped or lost.

### Parallelization Limits

The maximum number of tasks or subtasks running in parallel should not be more than CPU cores on this machine.

## Software Engineering Principles

### SOLID Principles

You must religiously follow SOLID principles:

- **S**ingle Responsibility Principle
- **O**pen/Closed Principle
- **L**iskov Substitution Principle
- **I**nterface Segregation Principle
- **D**ependency Inversion Principle

### Additional Principles

- **KISS** (Keep It Simple, Stupid)
- **DRY** (Don't Repeat Yourself)
- **YAGNI** (You Aren't Gonna Need It)
- **TRIZ** (Theory of Inventive Problem Solving)

## Development Process

### Test-Driven Development (TDD)

You must religiously follow TDD (Test-Driven Development) process:

1. Write failing test first
2. Write minimal code to pass
3. Refactor while keeping tests green

### Testing Requirements

You must create both unit tests and integration tests.

### Type Safety

You must do the code as strongly-typed as possible, and even more, so we can find errors **before** we run code in production.

### Code Editing

You **must** ALWAYS use mcp**morphllm-fast-apply**edit_file tool to make any code edits.

### Linting

You **must** extensively and exhaustively run applicable linters every time before sending code to github.

### Code Review

You must review the changes made with a separate subtask.

## Git Workflow

### Git Flow

You **must** use git flow for all git/github-related actions (if applicable).

### No Pull Requests

No Pull Requests - I am solo here.

### Commit and Push

You **must** commit and push code every time when you are done with any engineering task.

### Releases

You **must** do git release after each significant feature or piece is implemented.
