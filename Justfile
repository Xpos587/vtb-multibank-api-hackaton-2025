# Suppress command echoing
set quiet

# Default recipe - show available commands
default:
    @just --list

# === Development ===

# Start frontend development server
dev-frontend:
    @echo "🎨 Starting frontend dev server..."
    bun --hot frontend/index.ts

# Start backend development server
dev-backend:
    @echo "🐍 Starting backend dev server..."
    uv run python -m backend

# Build frontend for production
build-frontend:
    @echo "🔨 Building frontend..."
    cd frontend && bun run build.ts

# === Formatting ===

# Format all code (backend + frontend)
format: format-backend format-frontend
    @echo "✅ All code formatted!"

# Format Python code
format-backend:
    @echo "🎨 Formatting Python..."
    @ruff format backend
    @ruff check --fix --select I backend

# Format TypeScript/React code
format-frontend:
    @echo "🎨 Formatting TypeScript..."
    @bun run prettier --write frontend/**/*.{ts,tsx,json,css}
    @bun run eslint frontend/**/*.{ts,tsx} --fix

# === Linting ===

# Run all linters and security checks
lint: lint-backend lint-frontend security-backend
    @echo "✅ All checks passed!"

# Lint Python code
lint-backend:
    @echo "🔍 Linting Python..."
    @ruff check backend
    @pyright backend

# Lint TypeScript/React code
lint-frontend:
    @echo "🔍 Linting TypeScript..."
    @bun run eslint frontend/**/*.{ts,tsx}

# Run security checks on backend
security-backend:
    @echo "🔒 Running security checks..."
    @bandit -r backend -ll
    @gitleaks detect --source backend --no-git --no-banner

# === Combined Commands ===

# Format and lint everything
analyze: format lint
    @echo "🎯 Full analysis complete!"

# Quick CI/CD check (no formatting)
check: lint
    @echo "✅ CI checks passed!"

# === Cleanup ===

# Clean Python cache files
clean:
    @echo "🧹 Cleaning cache..."
    @fd -t d "__pycache__" -x rm -rf {} 2>/dev/null || true
    @fd -t f "*.pyc" -x rm {} 2>/dev/null || true
    @fd -t d "*.egg-info" -x rm -rf {} 2>/dev/null || true
    @fd -t d ".ruff_cache" -x rm -rf {} 2>/dev/null || true
    @rm -rf node_modules/.cache 2>/dev/null || true
    @echo "✅ Cache cleaned!"
