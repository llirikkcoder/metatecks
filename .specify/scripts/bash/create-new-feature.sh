#!/usr/bin/env bash
# Create a new feature

set -e

# Default values
JSON_OUTPUT=false
SHORT_NAME=""
NUMBER=0
HELP=false
FEATURE_DESC=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --short-name)
            SHORT_NAME="$2"
            shift 2
            ;;
        --number)
            NUMBER="$2"
            shift 2
            ;;
        --help)
            HELP=true
            shift
            ;;
        *)
            if [ -z "$FEATURE_DESC" ]; then
                FEATURE_DESC="$1"
            else
                FEATURE_DESC="$FEATURE_DESC $1"
            fi
            shift
            ;;
    esac
done

# Show help
if [ "$HELP" = true ]; then
    echo "Usage: ./create-new-feature.sh [--json] [--short-name <name>] [--number N] <feature description>"
    echo ""
    echo "Options:"
    echo "  --json               Output in JSON format"
    echo "  --short-name <name>  Provide a custom short name (2-4 words) for the branch"
    echo "  --number N           Specify branch number manually (overrides auto-detection)"
    echo "  --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./create-new-feature.sh 'Add user authentication system' --short-name 'user-auth'"
    echo "  ./create-new-feature.sh 'Implement OAuth2 integration for API'"
    exit 0
fi

# Check if feature description provided
if [ -z "$FEATURE_DESC" ]; then
    echo "Error: Usage: ./create-new-feature.sh [--json] [--short-name <name>] <feature description>" >&2
    exit 1
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

# Get highest number from specs directory
get_highest_from_specs() {
    local specs_dir="$1"
    local highest=0

    if [ -d "$specs_dir" ]; then
        for dir in "$specs_dir"/[0-9]*; do
            if [ -d "$dir" ]; then
                local num=$(basename "$dir" | grep -oE '^[0-9]+')
                if [ -n "$num" ] && [ "$num" -gt "$highest" ]; then
                    highest=$num
                fi
            fi
        done
    fi

    echo "$highest"
}

# Get highest number from branches
get_highest_from_branches() {
    local highest=0

    if command -v git &> /dev/null && git rev-parse --git-dir &> /dev/null; then
        # Get all branches (local and remote)
        while IFS= read -r branch; do
            # Extract number from branch name (format: NNN-name)
            local num=$(echo "$branch" | grep -oE '^[0-9]+')
            if [ -n "$num" ] && [ "$num" -gt "$highest" ]; then
                highest=$num
            fi
        done < <(git branch -a 2>/dev/null | sed 's/^[* ]*//;s/^remotes\/[^\/]*\///' | grep -E '^[0-9]+-')
    fi

    echo "$highest"
}

# Get next branch number
get_next_number() {
    local specs_dir="$1"

    # Fetch all remotes (suppress errors if no remotes)
    git fetch --all --prune &>/dev/null || true

    # Get highest from branches and specs
    local highest_branch=$(get_highest_from_branches)
    local highest_spec=$(get_highest_from_specs "$specs_dir")

    # Return max + 1
    local max=$highest_branch
    [ "$highest_spec" -gt "$max" ] && max=$highest_spec

    echo $((max + 1))
}

# Clean branch name
clean_branch_name() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g;s/-\{2,\}/-/g;s/^-//;s/-$//'
}

# Generate branch name from description
generate_branch_name() {
    local desc="$1"

    # Stop words to filter
    local stop_words="i a an the to for of in on at by with from is are was were be been being have has had do does did will would should could can may might must shall this that these those my your our their want need add get set"

    # Convert to lowercase and extract words
    local words=$(echo "$desc" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9 ]/ /g' | tr -s ' ')

    # Filter meaningful words
    local meaningful=""
    for word in $words; do
        # Skip stop words
        if echo " $stop_words " | grep -q " $word "; then
            continue
        fi

        # Keep words >= 3 chars or uppercase acronyms
        if [ ${#word} -ge 3 ]; then
            meaningful="$meaningful $word"
        fi
    done

    # Take first 3-4 words
    local result=$(echo "$meaningful" | awk '{for(i=1;i<=3 && i<=NF;i++) printf "%s%s", $i, (i<3 && i<NF ? "-" : "")}')

    if [ -z "$result" ]; then
        result=$(clean_branch_name "$desc" | cut -d'-' -f1-3)
    fi

    echo "$result"
}

# Find repository root
REPO_ROOT=$(find_repo_root)
if [ -z "$REPO_ROOT" ]; then
    echo "Error: Could not determine repository root. Please run this script from within the repository." >&2
    exit 1
fi

cd "$REPO_ROOT"

# Check if git is available
HAS_GIT=false
if command -v git &> /dev/null && git rev-parse --git-dir &> /dev/null; then
    HAS_GIT=true
fi

# Create specs directory
SPECS_DIR="$REPO_ROOT/specs"
mkdir -p "$SPECS_DIR"

# Generate branch name
if [ -n "$SHORT_NAME" ]; then
    BRANCH_SUFFIX=$(clean_branch_name "$SHORT_NAME")
else
    BRANCH_SUFFIX=$(generate_branch_name "$FEATURE_DESC")
fi

# Determine branch number
if [ "$NUMBER" -eq 0 ]; then
    if [ "$HAS_GIT" = true ]; then
        NUMBER=$(get_next_number "$SPECS_DIR")
    else
        NUMBER=$(( $(get_highest_from_specs "$SPECS_DIR") + 1 ))
    fi
fi

# Format number with leading zeros
FEATURE_NUM=$(printf "%03d" "$NUMBER")
BRANCH_NAME="${FEATURE_NUM}-${BRANCH_SUFFIX}"

# Check branch name length (GitHub limit: 244 bytes)
MAX_LENGTH=244
if [ ${#BRANCH_NAME} -gt $MAX_LENGTH ]; then
    # Truncate suffix
    MAX_SUFFIX_LENGTH=$((MAX_LENGTH - 4))
    TRUNCATED_SUFFIX="${BRANCH_SUFFIX:0:$MAX_SUFFIX_LENGTH}"
    TRUNCATED_SUFFIX="${TRUNCATED_SUFFIX%-}"  # Remove trailing hyphen

    echo "Warning: Branch name exceeded GitHub's 244-byte limit" >&2
    echo "Warning: Original: $BRANCH_NAME (${#BRANCH_NAME} bytes)" >&2
    BRANCH_NAME="${FEATURE_NUM}-${TRUNCATED_SUFFIX}"
    echo "Warning: Truncated to: $BRANCH_NAME (${#BRANCH_NAME} bytes)" >&2
fi

# Create git branch
if [ "$HAS_GIT" = true ]; then
    if ! git checkout -b "$BRANCH_NAME" 2>/dev/null; then
        echo "Warning: Failed to create git branch: $BRANCH_NAME" >&2
    fi
else
    echo "Warning: Git repository not detected; skipped branch creation for $BRANCH_NAME" >&2
fi

# Create feature directory
FEATURE_DIR="$SPECS_DIR/$BRANCH_NAME"
mkdir -p "$FEATURE_DIR"

# Copy template
TEMPLATE="$REPO_ROOT/.specify/templates/spec-template.md"
SPEC_FILE="$FEATURE_DIR/spec.md"
if [ -f "$TEMPLATE" ]; then
    cp "$TEMPLATE" "$SPEC_FILE"
else
    touch "$SPEC_FILE"
fi

# Set environment variable
export SPECIFY_FEATURE="$BRANCH_NAME"

# Output results
if [ "$JSON_OUTPUT" = true ]; then
    cat <<EOF
{"BRANCH_NAME":"$BRANCH_NAME","SPEC_FILE":"$SPEC_FILE","FEATURE_NUM":"$FEATURE_NUM","HAS_GIT":$HAS_GIT}
EOF
else
    echo "BRANCH_NAME: $BRANCH_NAME"
    echo "SPEC_FILE: $SPEC_FILE"
    echo "FEATURE_NUM: $FEATURE_NUM"
    echo "HAS_GIT: $HAS_GIT"
    echo "SPECIFY_FEATURE environment variable set to: $BRANCH_NAME"
fi
