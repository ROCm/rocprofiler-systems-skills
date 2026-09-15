#!/bin/bash
#
# Radisha Installer
# Installs radisha skills globally to ~/.claude/skills/
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$HOME/.claude/skills"
AGENTS_DIR="$HOME/.claude/agents"
REPO_URL="git@github.com:ROCm/rocprofiler-systems-skills.git"
# Set once a fresh clone happens (non-local install), so install_agents can
# reuse it instead of cloning the repo a second time.
CLONE_DIR=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${BLUE}Radisha Installer${NC}"
    echo "=================="
    echo ""
}

print_success() {
    echo -e "  ${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "  ${BLUE}→${NC} $1"
}

print_warning() {
    echo -e "  ${YELLOW}!${NC} $1"
}

print_error() {
    echo -e "  ${RED}✗${NC} $1"
}

# Check if running from radisha repo or downloading fresh
is_local_install() {
    [ -f "$SCRIPT_DIR/skills/radisha/help/SKILL.md" ] ||
        [ -f "$SCRIPT_DIR/skills/radisha-help/SKILL.md" ]
}

# Symlinks $SCRIPT_DIR/<src_subdir> (or a fresh clone of it) into $dest_dir.
# Shared by install_skills and install_agents so both directories are kept
# in sync the same way, instead of duplicating the symlink/clone logic.
install_dir() {
    local label="$1" src_subdir="$2" dest_dir="$3"
    echo "Installing $label to $dest_dir..."

    # Create .claude directory if needed
    mkdir -p "$HOME/.claude"

    if is_local_install; then
        # Installing from local clone
        local src="$SCRIPT_DIR/$src_subdir"
        if [ -L "$dest_dir" ]; then
            # Already a symlink
            local existing_target
            existing_target=$(readlink -f "$dest_dir")
            if [ "$existing_target" = "$src" ]; then
                print_success "$label already linked to $src"
            else
                print_warning "Existing symlink points to $existing_target"
                read -p "  Replace with link to $src? [y/N] " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    rm "$dest_dir"
                    ln -s "$src" "$dest_dir"
                    print_success "Symlink updated"
                else
                    print_info "Keeping existing symlink"
                fi
            fi
        elif [ -d "$dest_dir" ]; then
            # Directory exists (not symlink)
            print_warning "Directory already exists at $dest_dir"
            read -p "  Replace with symlink to $src? [y/N] " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                rm -rf "$dest_dir"
                ln -s "$src" "$dest_dir"
                print_success "Replaced with symlink"
            else
                print_info "Keeping existing directory"
            fi
        else
            # Fresh install - create symlink
            ln -s "$src" "$dest_dir"
            print_success "Created symlink: $dest_dir -> $src"
        fi
    else
        # Installing from curl/wget - clone the repo
        if [ -d "$dest_dir" ] || [ -L "$dest_dir" ]; then
            print_warning "$label directory already exists"
            if [ -d "$dest_dir/.git" ] || [ -L "$dest_dir" ]; then
                print_info "Updating existing installation..."
                if [ -L "$dest_dir" ]; then
                    cd "$(readlink -f "$dest_dir")/.."
                else
                    cd "$dest_dir/.."
                fi
                git pull origin main --quiet 2>/dev/null || true
                print_success "Updated to latest version"
            else
                print_info "Keeping existing directory"
            fi
        else
            # Clone the repo once and reuse it for every dest_dir in this run
            if [ -z "$CLONE_DIR" ]; then
                CLONE_DIR=$(mktemp -d)
                git clone --quiet "$REPO_URL" "$CLONE_DIR/radisha"
            fi
            ln -s "$CLONE_DIR/radisha/$src_subdir" "$dest_dir"
            print_success "Cloned and linked $label"
            print_info "Repo location: $CLONE_DIR/radisha"
        fi
    fi

    print_success "$label installation complete"
}

install_skills() {
    install_dir "Skills" "skills" "$SKILLS_DIR"
}

install_agents() {
    install_dir "Agents" "agents" "$AGENTS_DIR"
}

setup_project() {
    echo ""
    read -p "Do you want to set up the current project? [y/N] " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return
    fi

    echo ""
    echo "Setting up project in $(pwd)..."

    # CLAUDE.md
    if [ -f "CLAUDE.md" ]; then
        print_warning "CLAUDE.md already exists"
    else
        if is_local_install; then
            cp "$SCRIPT_DIR/CLAUDE.md" "CLAUDE.md"
        else
            cat > "CLAUDE.md" << 'CLAUDEMD'
# Radisha

AI-assisted development with structured workflows.

## Quick Commands

| Command | Description |
|---------|-------------|
| `/plan` | Start planning (asks which type) |
| `/plan-feature` | Plan a new feature |
| `/plan-bugfix` | Plan a bug fix |
| `/plan-refactor` | Plan refactoring |
| `/commit` | Create a commit |
| `/pr` | Prepare a pull request |
| `/review` | Review a pull request |
| `/testplan` | Create test plan |
| `/explore` | Explore unfamiliar code |
| `/skills` | List all available skills |
| `/update` | Update radisha |

## Core Rules

### Planning First
Before starting ANY non-trivial task (more than 2 steps), invoke the appropriate planning skill (`planning/feature`, `planning/bugfix`, `planning/refactor`, or `planning/docs`).

### Step-by-Step Validation
After completing EACH implementation step:
1. Run autonomous verification (tests, linter)
2. Show summary of changes
3. Ask user for validation before proceeding

### English Output
ALL output MUST be in English, regardless of input language.

### Skill Invocation
If there is even a 1% chance a skill might apply to your task, you MUST invoke it. Use the `Skill` tool with the skill name (e.g., `planning/feature`).

### Simplicity First
Make every change as simple as possible. Only touch what's necessary. No over-engineering.

## How to Find Skills

Skills are located in `~/.claude/skills/` (global) or the project's `skills/` directory.

**Categories:**
- `planning/` - Feature, bugfix, refactor, docs planning
- `programming/` - Language-specific coding (cpp, python, cmake)
- `testing/` - Test plans and test frameworks
- `git/` - Pull requests and reviews
- `exploration/` - Code exploration
- `libraries/` - Library-specific knowledge (amd-smi)
- `radisha/` - Radisha management (update, help, skills)

**For full workflow reference:** Invoke the `radisha/help` skill.
CLAUDEMD
        fi
        print_success "Created CLAUDE.md"
    fi

    # .cursorrules
    if [ -f ".cursorrules" ]; then
        print_warning ".cursorrules already exists"
    else
        if is_local_install; then
            cp "$SCRIPT_DIR/.cursorrules" ".cursorrules"
        else
            cat > ".cursorrules" << 'CURSORRULES'
# Radisha

AI-assisted development with structured workflows.

## Quick Commands

| Command | Description |
|---------|-------------|
| `/plan` | Start planning (asks which type) |
| `/plan-feature` | Plan a new feature |
| `/plan-bugfix` | Plan a bug fix |
| `/plan-refactor` | Plan refactoring |
| `/commit` | Create a commit |
| `/pr` | Prepare a pull request |
| `/review` | Review a pull request |
| `/testplan` | Create test plan |
| `/explore` | Explore unfamiliar code |
| `/skills` | List all available skills |
| `/update` | Update radisha |

## Core Rules

### Planning First
Before starting ANY non-trivial task (more than 2 steps), invoke the appropriate planning skill (`planning/feature`, `planning/bugfix`, `planning/refactor`, or `planning/docs`).

### Step-by-Step Validation
After completing EACH implementation step:
1. Run autonomous verification (tests, linter)
2. Show summary of changes
3. Ask user for validation before proceeding

### English Output
ALL output MUST be in English, regardless of input language.

### Skill Invocation
If there is even a 1% chance a skill might apply to your task, you MUST invoke it. Use `@skill-name` to invoke skills (e.g., `@planning/feature`).

### Simplicity First
Make every change as simple as possible. Only touch what's necessary. No over-engineering.

## How to Find Skills

Skills are located in `.cursor/skills/` (project) or `~/.cursor/skills/` (global).

**Categories:**
- `planning/` - Feature, bugfix, refactor, docs planning
- `programming/` - Language-specific coding (cpp, python, cmake)
- `testing/` - Test plans and test frameworks
- `git/` - Pull requests and reviews
- `exploration/` - Code exploration
- `libraries/` - Library-specific knowledge (amd-smi)
- `radisha/` - Radisha management (update, help, skills)

**For full workflow reference:** Use `@radisha/help`.
CURSORRULES
        fi
        print_success "Created .cursorrules"
    fi
}

print_usage() {
    echo ""
    echo -e "${GREEN}Installation complete!${NC}"
    echo ""
    echo "Usage:"
    echo "  - Claude Code: Skills auto-loaded via CLAUDE.md"
    echo "  - Cursor: Rules auto-loaded via .cursorrules"
    echo "  - Commands: /plan, /pr, /skills, /explore, etc."
    echo ""
    echo "For help: invoke the radisha/help skill"
    echo ""
}

# Main
print_header
install_skills
install_agents
setup_project
print_usage
