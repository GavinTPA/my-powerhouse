#!/bin/bash
# scan-git-secrets.sh - Scan git history for accidentally committed secrets
# Part of the security-check skill
#
# Usage: ./scan-git-secrets.sh [--verbose] [path]
#   path: Optional path to git repo (defaults to current directory)
#
# Exit codes:
#   0 - No secrets found
#   1 - Secrets found
#   2 - Not a git repository

set -euo pipefail

VERBOSE="${VERBOSE:-false}"
REPO_PATH="."

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        *)
            REPO_PATH="$1"
            shift
            ;;
    esac
done

cd "$REPO_PATH" 2>/dev/null || { echo "Error: Cannot access $REPO_PATH"; exit 2; }

# Verify git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not a git repository"
    exit 2
fi

# File patterns to search (space-separated for git pathspec)
FILE_PATTERNS="*.env *.env.* .env* *.yaml *.yml *.json *.config *.conf *.sh *.properties *.toml"

# Secret patterns with risk levels
# Format: "PATTERN|DESCRIPTION|RISK"
declare -a SECRET_PATTERNS=(
    'AKIA[0-9A-Z]{16}|AWS Access Key|HIGH'
    'ASIA[0-9A-Z]{16}|AWS Temp Access Key|HIGH'
    '[a-zA-Z0-9/+=]{40}(?=.*AWS)|AWS Secret Key (near AWS)|HIGH'
    'ghp_[a-zA-Z0-9]{36}|GitHub Personal Access Token|HIGH'
    'gho_[a-zA-Z0-9]{36}|GitHub OAuth Token|HIGH'
    'ghu_[a-zA-Z0-9]{36}|GitHub User Token|HIGH'
    'ghs_[a-zA-Z0-9]{36}|GitHub Server Token|HIGH'
    'github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}|GitHub Fine-grained PAT|HIGH'
    'sk-[a-zA-Z0-9]{48}|OpenAI API Key|HIGH'
    'sk-proj-[a-zA-Z0-9-_]{80,}|OpenAI Project Key|HIGH'
    'sk-ant-[a-zA-Z0-9-_]{80,}|Anthropic API Key|HIGH'
    'xoxb-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{24}|Slack Bot Token|HIGH'
    'xoxp-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{24}|Slack User Token|HIGH'
    'xoxa-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{24}|Slack App Token|HIGH'
    'AIza[0-9A-Za-z-_]{35}|Google API Key|MEDIUM'
    'ya29\.[0-9A-Za-z_-]+|Google OAuth Token|MEDIUM'
    'npm_[a-zA-Z0-9]{36}|NPM Token|MEDIUM'
    'pypi-[a-zA-Z0-9-_]{50,}|PyPI Token|MEDIUM'
    'sq0csp-[a-zA-Z0-9-_]{43}|Square Access Token|HIGH'
    'sq0atp-[a-zA-Z0-9-_]{22}|Square OAuth Token|HIGH'
    'PRIVATE KEY-----[^-]+-----END|Private Key|HIGH'
    'password\s*[:=]\s*["\047][^\s"]{8,}["\047]|Hardcoded Password|HIGH'
    'secret\s*[:=]\s*["\047][^\s"]{8,}["\047]|Hardcoded Secret|MEDIUM'
    'api[_-]?key\s*[:=]\s*["\047][a-zA-Z0-9_-]{16,}["\047]|Generic API Key|MEDIUM'
    'token\s*[:=]\s*["\047][a-zA-Z0-9_-]{20,}["\047]|Generic Token|MEDIUM'
    'Bearer [a-zA-Z0-9_-]{20,}|Bearer Token|MEDIUM'
    '[A-Za-z0-9+/]{60,}={0,2}|Base64 Encoded Secret|MEDIUM'
)

# Temporary file for results
RESULTS_FILE=$(mktemp)
trap "rm -f $RESULTS_FILE" EXIT

# Track unique findings to avoid duplicates
declare -A SEEN_FINDINGS

log_verbose() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo "[DEBUG] $1" >&2
    fi
}

# Function to search git history for a pattern
search_pattern() {
    local pattern="$1"
    local description="$2"
    local risk="$3"

    log_verbose "Searching for: $description ($pattern)"

    # Use git log -p to get patches, then grep for patterns
    # We search through the diff content, not just commit messages
    # Using -G for regex matching in diffs

    # Build the pathspec for file patterns
    local pathspec=""
    for fp in $FILE_PATTERNS; do
        pathspec="$pathspec -- '*$fp' ':!*.md'"
    done

    # Search git history
    # Note: We use extended grep and look through all branches
    git log --all --oneline --diff-filter=ACMR -p $pathspec 2>/dev/null | \
    grep -En "$pattern" 2>/dev/null | \
    while IFS=: read -r line_num match; do
        # Find the commit this belongs to by looking backwards for commit line
        # This is a simplified approach - we'll enhance with commit context
        echo "$match|$description|$risk"
    done
}

# More accurate search using git log with specific formatting
search_with_context() {
    local pattern="$1"
    local description="$2"
    local risk="$3"

    log_verbose "Searching with context for: $description"

    # Search each commit's diff for the pattern
    git log --all --pretty=format:"%h|%s" --name-only --diff-filter=ACMR -- \
        '*.env' '*.env.*' '.env*' '*.yaml' '*.yml' '*.json' '*.config' '*.conf' '*.sh' '*.properties' '*.toml' \
        ':!*.md' ':!package-lock.json' ':!yarn.lock' ':!pnpm-lock.yaml' 2>/dev/null | \
    while IFS='|' read -r commit_or_file msg; do
        if [[ -z "$commit_or_file" ]]; then
            continue
        fi

        # If it looks like a commit hash (7-40 hex chars), store it
        if [[ "$commit_or_file" =~ ^[a-f0-9]{7,40}$ ]]; then
            current_commit="$commit_or_file"
            current_msg="$msg"
            continue
        fi

        # Otherwise it's a filename - check if this file in this commit has the pattern
        if [[ -n "${current_commit:-}" ]] && [[ -f "$commit_or_file" ]] 2>/dev/null; then
            # Check if the file exists in that commit and contains the pattern
            if git show "$current_commit:$commit_or_file" 2>/dev/null | grep -qE "$pattern" 2>/dev/null; then
                echo "$current_commit|$commit_or_file|$description|$risk"
            fi
        fi
    done
}

# Main search function using git diff with pattern
search_all_history() {
    local pattern="$1"
    local description="$2"
    local risk="$3"

    # Use git log -S or -G to find commits that introduced the pattern
    # -G uses regex, -S uses literal string
    # We'll use -G for regex patterns

    git log --all -G "$pattern" --pretty=format:"%h" --name-only --diff-filter=ACMR -- \
        '*.env' '*.env.*' '.env*' '*.yaml' '*.yml' '*.json' '*.config' '*.conf' '*.sh' '*.properties' '*.toml' \
        ':!*.md' ':!package-lock.json' ':!yarn.lock' ':!pnpm-lock.yaml' ':!**/node_modules/**' 2>/dev/null | \
    while read -r line; do
        if [[ -z "$line" ]]; then
            continue
        fi

        # Commit hash (7 hex chars)
        if [[ "$line" =~ ^[a-f0-9]{7}$ ]]; then
            current_commit="$line"
            continue
        fi

        # Filename
        if [[ -n "${current_commit:-}" ]]; then
            local finding_key="${current_commit}|${line}|${description}"
            if [[ -z "${SEEN_FINDINGS[$finding_key]:-}" ]]; then
                SEEN_FINDINGS["$finding_key"]=1
                echo "$current_commit|$line|$description|$risk"
            fi
        fi
    done
}

echo "## Git History Secret Scan"
echo ""
echo "Scanning repository: $(git rev-parse --show-toplevel 2>/dev/null || pwd)"
echo "Commits analyzed: $(git rev-list --all --count 2>/dev/null || echo 'unknown')"
echo ""

# Run searches and collect results
finding_count=0

for pattern_def in "${SECRET_PATTERNS[@]}"; do
    IFS='|' read -r pattern description risk <<< "$pattern_def"

    results=$(search_all_history "$pattern" "$description" "$risk" 2>/dev/null || true)

    if [[ -n "$results" ]]; then
        echo "$results" >> "$RESULTS_FILE"
    fi
done

# Count and display results
if [[ -s "$RESULTS_FILE" ]]; then
    finding_count=$(wc -l < "$RESULTS_FILE" | tr -d ' ')

    echo "Found **$finding_count** potential secrets in git history:"
    echo ""
    echo "| Commit | File | Pattern | Risk |"
    echo "|--------|------|---------|------|"

    # Sort by risk (HIGH first) and deduplicate
    sort -t'|' -k4 -r "$RESULTS_FILE" | uniq | while IFS='|' read -r commit file desc risk; do
        # Truncate file path if too long
        if [[ ${#file} -gt 40 ]]; then
            file="...${file: -37}"
        fi
        echo "| $commit | $file | $desc | $risk |"
    done

    echo ""
    echo "---"
    echo ""
    echo "**Recommended actions:**"
    echo ""
    echo "1. **Rotate compromised credentials** - Any secret in git history should be considered leaked"
    echo "2. **Remove from history** using one of:"
    echo "   - \`git filter-branch\` (built-in, complex)"
    echo "   - \`git filter-repo\` (recommended, install via pip)"
    echo "   - BFG Repo-Cleaner (fast, Java-based)"
    echo "3. **Force-push** to update remote (coordinate with team)"
    echo "4. **Add to .gitignore** to prevent future commits"
    echo ""
    echo "Example using git filter-repo:"
    echo "\`\`\`bash"
    echo "pip install git-filter-repo"
    echo "git filter-repo --path-glob '*.env*' --invert-paths"
    echo "\`\`\`"

    exit 1
else
    echo "No secrets found in git history."
    echo ""
    echo "Patterns checked:"
    echo "- AWS access keys (AKIA/ASIA prefixes)"
    echo "- GitHub tokens (ghp_, gho_, ghu_, ghs_, github_pat_)"
    echo "- OpenAI keys (sk-)"
    echo "- Anthropic keys (sk-ant-)"
    echo "- Slack tokens (xoxb-, xoxp-, xoxa-)"
    echo "- Google API keys and OAuth tokens"
    echo "- Private keys"
    echo "- Generic hardcoded passwords, secrets, API keys, and tokens"
    echo ""
    echo "File types scanned: .env, .yaml, .yml, .json, .config, .conf, .sh, .properties, .toml"

    exit 0
fi
