#!/bin/bash
#
# Radisha Installer
# Installs radisha skills globally to ~/.claude/skills/
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$HOME/.claude/skills"
REPO_URL="git@github.com:ROCm/rocprofiler-systems-skills.git"

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

install_skills() {
    echo "Installing skills to $SKILLS_DIR..."

    # Create .claude directory if needed
    mkdir -p "$HOME/.claude"

    if is_local_install; then
        # Installing from local clone
        if [ -L "$SKILLS_DIR" ]; then
            # Already a symlink
            EXISTING_TARGET=$(readlink -f "$SKILLS_DIR")
            if [ "$EXISTING_TARGET" = "$SCRIPT_DIR/skills" ]; then
                print_success "Skills already linked to $SCRIPT_DIR/skills"
            else
                print_warning "Existing symlink points to $EXISTING_TARGET"
                read -p "  Replace with link to $SCRIPT_DIR/skills? [y/N] " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    rm "$SKILLS_DIR"
                    ln -s "$SCRIPT_DIR/skills" "$SKILLS_DIR"
                    print_success "Symlink updated"
                else
                    print_info "Keeping existing symlink"
                fi
            fi
        elif [ -d "$SKILLS_DIR" ]; then
            # Directory exists (not symlink)
            print_warning "Directory already exists at $SKILLS_DIR"
            read -p "  Replace with symlink to $SCRIPT_DIR/skills? [y/N] " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                rm -rf "$SKILLS_DIR"
                ln -s "$SCRIPT_DIR/skills" "$SKILLS_DIR"
                print_success "Replaced with symlink"
            else
                print_info "Keeping existing directory"
            fi
        else
            # Fresh install - create symlink
            ln -s "$SCRIPT_DIR/skills" "$SKILLS_DIR"
            print_success "Created symlink: $SKILLS_DIR -> $SCRIPT_DIR/skills"
        fi
    else
        # Installing from curl/wget - clone the repo
        if [ -d "$SKILLS_DIR" ] || [ -L "$SKILLS_DIR" ]; then
            print_warning "Skills directory already exists"
            if [ -d "$SKILLS_DIR/.git" ] || [ -L "$SKILLS_DIR" ]; then
                print_info "Updating existing installation..."
                if [ -L "$SKILLS_DIR" ]; then
                    cd "$(readlink -f "$SKILLS_DIR")/.."
                else
                    cd "$SKILLS_DIR/.."
                fi
                git pull origin main --quiet 2>/dev/null || true
                print_success "Updated to latest version"
            else
                print_info "Keeping existing directory"
            fi
        else
            # Clone the repo
            TEMP_DIR=$(mktemp -d)
            git clone --quiet "$REPO_URL" "$TEMP_DIR/radisha"
            ln -s "$TEMP_DIR/radisha/skills" "$SKILLS_DIR"
            print_success "Cloned and linked skills"
            print_info "Repo location: $TEMP_DIR/radisha"
        fi
    fi

    print_success "Skills installation complete"
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
setup_project
print_usage
