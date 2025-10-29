# Suppress command echoing
set quiet

# Default recipe - show available commands
default:
    @just --list

# Frontend
dev-frontend:
    @echo "🎨 Frontend dev..."
    bun run start

build-frontend:
    @echo "🔨 Building frontend..."
    bun run build

# Backend
dev-backend:
    @echo "🐍 Backend dev..."
    uv run python -m backend

format: format-backend format-frontend
    @echo "✅ All code formatting complete!"

format-backend:
    echo "🎨 Formatting Python code with black..."
    black backend
    echo "🔧 Fixing Python imports and style with ruff..."
    ruff check --fix backend

format-frontend:
    echo "🎨 Formatting React/TypeScript code..."
    bun run format

# Reformat code (alias for format)
reformat: format

lint: lint-backend lint-frontend security-backend
    @echo "✅ All linting and SCA checks complete!"

lint-backend:
    echo "🔍 Linting Python with ruff..."
    ruff check backend
    echo "🔍 Type checking with pyright..."
    pyright backend
    echo "🔍 Checking for unused code with vulture..."
    vulture backend

lint-frontend:
    echo "🔍 Linting React/TypeScript..."
    bun run lint

security-backend:
    echo "🔒 Security analysis with Bandit..."
    bandit -r backend -ll
    echo "🔒 Scanning for secrets with Gitleaks..."
    gitleaks detect --source backend --no-git --verbose

analyze: format lint
    @echo "🎯 Full code analysis and formatting complete!"

# Quick check without formatting (CI/CD mode)
check: lint-backend lint-frontend security-backend
    @echo "✅ All checks passed!"

# Clean cache files and build artifacts
clean:
    fd -t d "__pycache__" -x rm -rf {} 2>/dev/null || true
    fd -t f "*.pyc" -x rm {} 2>/dev/null || true
    fd -t d "*.egg-info" -x rm -rf {} 2>/dev/null || true
    echo "✅ Cache cleaned!"
