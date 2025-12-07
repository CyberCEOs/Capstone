#!/usr/bin/env bash
# scaffold_capstone.sh — Scaffold a generic Monorepo for "capstone-project"
# Compatible with macOS and Linux
set -euo pipefail
IFS=$'\n\t'

echo "Starting capstone-project scaffold..."

# Helper to create a file only if it doesn't already exist
create_file_if_missing() {
  local filepath="$1"
  shift
  local content="$*"
  if [ -e "$filepath" ]; then
    echo "Skipping existing: $filepath"
  else
    mkdir -p "$(dirname "$filepath")"
    cat > "$filepath" <<'EOF'
'"$content"'
EOF
    echo "Created: $filepath"
  fi
}

# Create directory structure
dirs=(
  "docs"
  "infrastructure/enterprise-vm"
  "infrastructure/blue-team-stack"
  "infrastructure/scripts"
  "red-team/agents"
  "red-team/tools"
  "red-team/memory"
  "blue-team/llm-brain"
  "blue-team/wazuh-rules"
  "blue-team/orchestrator"
  "dashboard/frontend"
  "dashboard/backend"
  ".vscode"
)
for d in "${dirs[@]}"; do
  mkdir -p "$d"
  echo "Ensured dir: $d"
done

# Create docs placeholder files (only if missing)
if [ ! -e "docs/MASTER_PLAN.md" ]; then
  cat > docs/MASTER_PLAN.md <<'EOF'
# Master Plan

This file outlines the high-level plan for the Capstone Project.
- Teams: Red, Blue, Infrastructure
- Goals: Simulate enterprise environment, run red/blue exercises, maintain infrastructure code.
EOF
  echo "Created: docs/MASTER_PLAN.md"
else
  echo "Skipping existing: docs/MASTER_PLAN.md"
fi

if [ ! -e "docs/RED_TEAM_OPS.md" ]; then
  cat > docs/RED_TEAM_OPS.md <<'EOF'
# Red Team Ops

Place red team operational procedures, scripts, and notes here.
EOF
  echo "Created: docs/RED_TEAM_OPS.md"
else
  echo "Skipping existing: docs/RED_TEAM_OPS.md"
fi

if [ ! -e "docs/BLUE_TEAM_OPS.md" ]; then
  cat > docs/BLUE_TEAM_OPS.md <<'EOF'
# Blue Team Ops

Place blue team detection rules, playbooks, and notes here.
EOF
  echo "Created: docs/BLUE_TEAM_OPS.md"
else
  echo "Skipping existing: docs/BLUE_TEAM_OPS.md"
fi

if [ ! -e "docs/INFRASTRUCTURE.md" ]; then
  cat > docs/INFRASTRUCTURE.md <<'EOF'
# Infrastructure

Infrastructure documentation, architecture diagrams, and docker files go here.
EOF
  echo "Created: docs/INFRASTRUCTURE.md"
else
  echo "Skipping existing: docs/INFRASTRUCTURE.md"
fi

# infrastructure/scripts/reset_demo.sh
if [ ! -e "infrastructure/scripts/reset_demo.sh" ]; then
  cat > infrastructure/scripts/reset_demo.sh <<'EOF'
#!/usr/bin/env bash
# reset_demo.sh — placeholder script to reset demo environment
set -euo pipefail

echo "This is a placeholder reset_demo.sh script."
echo "Implement demo reset steps here (e.g., docker-compose down/up, cleanup volumes)."
EOF
  chmod +x infrastructure/scripts/reset_demo.sh
  echo "Created and made executable: infrastructure/scripts/reset_demo.sh"
else
  echo "Skipping existing: infrastructure/scripts/reset_demo.sh"
fi

# red-team/agents/main.py
if [ ! -e "red-team/agents/main.py" ]; then
  cat > red-team/agents/main.py <<'EOF'
#!/usr/bin/env python3
"""
main.py — placeholder entrypoint for a red-team agent
"""
import sys

def main():
    print("Red Team Agent placeholder running.")
    print("Implement agent logic here.")

if __name__ == "__main__":
    main()
EOF
  chmod +x red-team/agents/main.py || true
  echo "Created: red-team/agents/main.py"
else
  echo "Skipping existing: red-team/agents/main.py"
fi

# Create a robust .gitignore if not present
if [ ! -e ".gitignore" ]; then
  cat > .gitignore <<'EOF'
# macOS
.DS_Store

# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
venv/
env/
ENV/
pip-log.txt
pip-delete-this-directory.txt

# Virtual environments / packaging
*.egg-info/
dist/
build/

# Sensitive files
.env
.env.local
*.pem
*.key

# Logs and databases
*.log
*.sqlite
chroma_db/

# Node/npm
node_modules/
npm-debug.log

# Test / coverage
.coverage
.cache
.pytest_cache/

# IDEs
.vscode/
.idea/

# Misc
*.swp
*.swo
*.DS_Store
EOF
  echo "Created: .gitignore"
else
  echo "Skipping existing: .gitignore"
fi

# Create VS Code team settings: .vscode/extensions.json
if [ ! -e ".vscode/extensions.json" ]; then
  cat > .vscode/extensions.json <<'EOF'
{
  // Recommended extensions for the Capstone project teams
  "recommendations": [
    "ms-python.python",
    "ms-azuretools.vscode-docker",
    "esbenp.prettier-vscode",
    "tamasfe.even-better-toml",
    "yzhang.markdown-all-in-one"
  ]
}
EOF
  echo "Created: .vscode/extensions.json"
else
  echo "Skipping existing: .vscode/extensions.json"
fi

# Initialize git if not already a repo
if [ ! -d ".git" ]; then
  if command -v git >/dev/null 2>&1; then
    git init
    echo "Initialized empty git repository."
  else
    echo "git not found in PATH — skipping git init."
  fi
else
  echo "Git repository already initialized — skipping git init."
fi

# Create root README.md
if [ ! -e "README.md" ]; then
  cat > README.md <<'EOF'
# Capstone Project

This repository is the monorepo scaffold for the Capstone Project (Red, Blue, Infrastructure teams).
See the `docs/` folder for team plans and operational notes.
EOF
  echo "Created: README.md"
else
  echo "Skipping existing: README.md"
fi

echo
echo "Scaffold complete."
echo "Next steps (suggested):"
echo "  - Inspect created directories and placeholder files."
echo "  - Customize team docs and add real Dockerfiles, scripts, and code."
echo "  - If you want an initial commit, run: git add . && git commit -m \"chore: initial scaffold\""
echo