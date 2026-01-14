#!/usr/bin/env bash
# Consolidated prerequisite checking script (Bash)
#
# This script provides unified prerequisite checking for Spec-Driven Development workflow.
#
# Usage: ./check-prerequisites.sh [OPTIONS]
#
# OPTIONS:
#   --json               Output in JSON format
#   --require-tasks      Require tasks.md to exist (for implementation phase)
#   --include-tasks      Include tasks.md in AVAILABLE_DOCS list
#   --paths-only         Only output path variables (no validation)
#   --help, -h           Show help message

set -e

# Default values
JSON_OUTPUT=false
REQUIRE_TASKS=false
INCLUDE_TASKS=false
PATHS_ONLY=false
HELP=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --require-tasks)
            REQUIRE_TASKS=true
            shift
            ;;
        --include-tasks)
            INCLUDE_TASKS=true
            shift
            ;;
        --paths-only)
            PATHS_ONLY=true
            shift
            ;;
        --help|-h)
            HELP=true
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Show help
if [ "$HELP" = true ]; then
    cat <<EOF
Usage: check-prerequisites.sh [OPTIONS]

Consolidated prerequisite checking for Spec-Driven Development workflow.

OPTIONS:
  --json               Output in JSON format
  --require-tasks      Require tasks.md to exist (for implementation phase)
  --include-tasks      Include tasks.md in AVAILABLE_DOCS list
  --paths-only         Only output path variables (no prerequisite validation)
  --help, -h           Show this help message

EXAMPLES:
  # Check task prerequisites (plan.md required)
  ./check-prerequisites.sh --json

  # Check implementation prerequisites (plan.md + tasks.md required)
  ./check-prerequisites.sh --json --require-tasks --include-tasks

  # Get feature paths only (no validation)
  ./check-prerequisites.sh --paths-only --json

EOF
    exit 0
fi

# Find repository root
find_repo_root() {
    local current="$PWD"
    while [ "$current" != "/" ]; do
        if [ -d "$current/.git" ] || [ -d "$current/.specify" ]; then
            echo "$current"
            return 0
        fi
        current="$(dirname "$current")"
    done
    return 1
}

# Get current branch
get_current_branch() {
    if command -v git &> /dev/null && git rev-parse --git-dir &> /dev/null; then
        git rev-parse --abbrev-ref HEAD 2>/dev/null || echo ""
    else
        echo ""
    fi
}

# Check if branch is a feature branch
is_feature_branch() {
    local branch="$1"
    [[ "$branch" =~ ^[0-9]{3}- ]]
}

# Find repository root
REPO_ROOT=$(find_repo_root)
if [ -z "$REPO_ROOT" ]; then
    echo "ERROR: Could not determine repository root." >&2
    exit 1
fi

cd "$REPO_ROOT"

# Check if git is available
HAS_GIT=false
if command -v git &> /dev/null && git rev-parse --git-dir &> /dev/null; then
    HAS_GIT=true
fi

# Get current branch
CURRENT_BRANCH=$(get_current_branch)

# Validate feature branch
if [ "$HAS_GIT" = true ] && [ -n "$CURRENT_BRANCH" ]; then
    if ! is_feature_branch "$CURRENT_BRANCH"; then
        echo "ERROR: Not on a feature branch (current: $CURRENT_BRANCH)" >&2
        echo "Feature branches must match pattern: NNN-feature-name" >&2
        exit 1
    fi
else
    # If no git, try to infer from SPECIFY_FEATURE env var or error
    if [ -n "$SPECIFY_FEATURE" ]; then
        CURRENT_BRANCH="$SPECIFY_FEATURE"
    else
        echo "ERROR: Could not determine current feature branch." >&2
        echo "Either checkout a feature branch or set SPECIFY_FEATURE environment variable." >&2
        exit 1
    fi
fi

# Set paths
FEATURE_DIR="$REPO_ROOT/specs/$CURRENT_BRANCH"
FEATURE_SPEC="$FEATURE_DIR/spec.md"
IMPL_PLAN="$FEATURE_DIR/plan.md"
TASKS="$FEATURE_DIR/tasks.md"
RESEARCH="$FEATURE_DIR/research.md"
DATA_MODEL="$FEATURE_DIR/data-model.md"
CONTRACTS_DIR="$FEATURE_DIR/contracts"
QUICKSTART="$FEATURE_DIR/quickstart.md"

# If paths-only mode, output paths and exit
if [ "$PATHS_ONLY" = true ]; then
    if [ "$JSON_OUTPUT" = true ]; then
        cat <<EOF
{"REPO_ROOT":"$REPO_ROOT","BRANCH":"$CURRENT_BRANCH","FEATURE_DIR":"$FEATURE_DIR","FEATURE_SPEC":"$FEATURE_SPEC","IMPL_PLAN":"$IMPL_PLAN","TASKS":"$TASKS"}
EOF
    else
        echo "REPO_ROOT: $REPO_ROOT"
        echo "BRANCH: $CURRENT_BRANCH"
        echo "FEATURE_DIR: $FEATURE_DIR"
        echo "FEATURE_SPEC: $FEATURE_SPEC"
        echo "IMPL_PLAN: $IMPL_PLAN"
        echo "TASKS: $TASKS"
    fi
    exit 0
fi

# Validate required directories and files
if [ ! -d "$FEATURE_DIR" ]; then
    echo "ERROR: Feature directory not found: $FEATURE_DIR" >&2
    echo "Run /speckit.specify first to create the feature structure." >&2
    exit 1
fi

if [ ! -f "$IMPL_PLAN" ]; then
    echo "ERROR: plan.md not found in $FEATURE_DIR" >&2
    echo "Run /speckit.plan first to create the implementation plan." >&2
    exit 1
fi

# Check for tasks.md if required
if [ "$REQUIRE_TASKS" = true ] && [ ! -f "$TASKS" ]; then
    echo "ERROR: tasks.md not found in $FEATURE_DIR" >&2
    echo "Run /speckit.tasks first to create the task list." >&2
    exit 1
fi

# Build list of available documents
DOCS=()

# Always check these optional docs
[ -f "$RESEARCH" ] && DOCS+=("research.md")
[ -f "$DATA_MODEL" ] && DOCS+=("data-model.md")

# Check contracts directory (only if it exists and has files)
if [ -d "$CONTRACTS_DIR" ] && [ -n "$(ls -A "$CONTRACTS_DIR" 2>/dev/null)" ]; then
    DOCS+=("contracts/")
fi

[ -f "$QUICKSTART" ] && DOCS+=("quickstart.md")

# Include tasks.md if requested and it exists
if [ "$INCLUDE_TASKS" = true ] && [ -f "$TASKS" ]; then
    DOCS+=("tasks.md")
fi

# Output results
if [ "$JSON_OUTPUT" = true ]; then
    # Build JSON array
    DOCS_JSON="["
    for i in "${!DOCS[@]}"; do
        [ $i -gt 0 ] && DOCS_JSON+=","
        DOCS_JSON+="\"${DOCS[$i]}\""
    done
    DOCS_JSON+="]"

    cat <<EOF
{"FEATURE_DIR":"$FEATURE_DIR","AVAILABLE_DOCS":$DOCS_JSON}
EOF
else
    # Text output
    echo "FEATURE_DIR: $FEATURE_DIR"
    echo "AVAILABLE_DOCS:"

    for doc in "${DOCS[@]}"; do
        echo "  - $doc"
    done
fi
