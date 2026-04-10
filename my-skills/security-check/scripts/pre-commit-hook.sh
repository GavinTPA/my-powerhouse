#!/bin/bash
# pre-commit-hook.sh - Block commits containing hardcoded secrets
# Part of the security-check skill
#
# Scans staged files for secret patterns before allowing commits.
# Prevents secrets from entering git history in the first place.
# (scan-git-secrets.sh catches ones already there)
#
# Exit codes:
#   0 - No secrets found, commit allowed
#   1 - Secrets detected, commit blocked

set -euo pipefail

# Colors for terminal output
RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Find repo root
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

# Secret patterns with descriptions and risk levels
# Format: "PATTERN|DESCRIPTION|RISK"
# Consistent with scan-git-secrets.sh patterns
SECRET_PATTERNS=(
    'AKIA[0-9A-Z]{16}|AWS Access Key|HIGH'
    'ASIA[0-9A-Z]{16}|AWS Temp Access Key|HIGH'
    'ghp_[a-zA-Z0-9]{36}|GitHub Personal Access Token|HIGH'
    'gho_[a-zA-Z0-9]{36}|GitHub OAuth Token|HIGH'
    'ghu_[a-zA-Z0-9]{36}|GitHub User Token|HIGH'
    'ghs_[a-zA-Z0-9]{36}|GitHub Server Token|HIGH'
    'github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}|GitHub Fine-grained PAT|HIGH'
    'sk-[a-zA-Z0-9]{48}|OpenAI API Key|HIGH'
    'sk-proj-[a-zA-Z0-9_-]{80,}|OpenAI Project Key|HIGH'
    'sk-ant-[a-zA-Z0-9_-]{80,}|Anthropic API Key|HIGH'
    'xoxb-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{24}|Slack Bot Token|HIGH'
    'xoxp-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{24}|Slack User Token|HIGH'
    'xoxa-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{24}|Slack App Token|HIGH'
    'AIza[0-9A-Za-z_-]{35}|Google API Key|MEDIUM'
    'ya29\.[0-9A-Za-z_-]+|Google OAuth Token|MEDIUM'
    'npm_[a-zA-Z0-9]{36}|NPM Token|MEDIUM'
    'pypi-[a-zA-Z0-9_-]{50,}|PyPI Token|MEDIUM'
    'sq0csp-[a-zA-Z0-9_-]{43}|Square Access Token|HIGH'
    'sq0atp-[a-zA-Z0-9_-]{22}|Square OAuth Token|HIGH'
    '-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----|Private Key|HIGH'
    'password\s*[:=]\s*["\x27][^\s"\x27]{8,}["\x27]|Hardcoded Password|HIGH'
    'secret\s*[:=]\s*["\x27][^\s"\x27]{8,}["\x27]|Hardcoded Secret|MEDIUM'
    'api[_-]?key\s*[:=]\s*["\x27][a-zA-Z0-9_-]{16,}["\x27]|Generic API Key|MEDIUM'
    'token\s*[:=]\s*["\x27][a-zA-Z0-9_-]{20,}["\x27]|Generic Token|MEDIUM'
    'Bearer [a-zA-Z0-9_-]{20,}|Bearer Token|MEDIUM'
    'API_KEY=["\x27]?[a-zA-Z0-9_-]{16,}|API_KEY Assignment|MEDIUM'
    'SECRET=["\x27]?[a-zA-Z0-9_-]{16,}|SECRET Assignment|MEDIUM'
    'TOKEN=["\x27]?[a-zA-Z0-9_-]{20,}|TOKEN Assignment|MEDIUM'
    'PASSWORD=["\x27]?[^\s]{8,}|PASSWORD Assignment|HIGH'
)

# Load .secretsignore patterns (lines to ignore, like .gitignore for false positives)
load_ignore_patterns() {
    local ignore_file="${REPO_ROOT}/.secretsignore"
    IGNORE_PATTERNS=()

    if [[ -f "$ignore_file" ]]; then
        while IFS= read -r line; do
            # Skip empty lines and comments
            [[ -z "$line" || "$line" =~ ^# ]] && continue
            IGNORE_PATTERNS+=("$line")
        done < "$ignore_file"
    fi
}

# Check if a line matches any ignore pattern
is_ignored() {
    local line="$1"
    local file="$2"

    for pattern in "${IGNORE_PATTERNS[@]+"${IGNORE_PATTERNS[@]}"}"; do
        # Check if pattern matches the line content or file path
        if echo "$line" | grep -qE "$pattern" 2>/dev/null; then
            return 0
        fi
        if echo "$file" | grep -qE "$pattern" 2>/dev/null; then
            return 0
        fi
    done
    return 1
}

# Main detection logic
main() {
    load_ignore_patterns

    # Get list of staged files (added, copied, modified - not deleted)
    local staged_files
    staged_files=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null)

    if [[ -z "$staged_files" ]]; then
        exit 0
    fi

    local findings=()
    local finding_count=0

    # Get the staged content for each file
    while IFS= read -r file; do
        # Skip binary files
        if git diff --cached --numstat "$file" 2>/dev/null | grep -q "^-"; then
            continue
        fi

        # Get only the added/modified lines from staged changes
        local staged_diff
        staged_diff=$(git diff --cached -U0 "$file" 2>/dev/null | grep "^+" | grep -v "^+++" || true)

        if [[ -z "$staged_diff" ]]; then
            continue
        fi

        # Check each pattern against the staged diff
        for pattern_def in "${SECRET_PATTERNS[@]}"; do
            IFS='|' read -r pattern description risk <<< "$pattern_def"

            # Search for matches in the staged diff lines
            local matches
            matches=$(echo "$staged_diff" | grep -En "$pattern" 2>/dev/null || true)

            if [[ -n "$matches" ]]; then
                while IFS= read -r match_line; do
                    # Remove the leading + from diff output for display
                    local clean_line="${match_line#*:}"
                    clean_line="${clean_line#+}"

                    # Check if this match should be ignored
                    if is_ignored "$clean_line" "$file"; then
                        continue
                    fi

                    # Truncate the matched line for display (don't show full secrets)
                    local display_line="$clean_line"
                    if [[ ${#display_line} -gt 80 ]]; then
                        display_line="${display_line:0:77}..."
                    fi

                    findings+=("${risk}|${file}|${description}|${display_line}")
                    finding_count=$((finding_count + 1))
                done <<< "$matches"
            fi
        done
    done <<< "$staged_files"

    # Report results
    if [[ $finding_count -gt 0 ]]; then
        echo ""
        echo -e "${RED}${BOLD}SECRET DETECTED - COMMIT BLOCKED${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo -e "Found ${BOLD}${finding_count}${NC} potential secret(s) in staged files:"
        echo ""

        for finding in "${findings[@]}"; do
            IFS='|' read -r risk file description line <<< "$finding"

            local risk_color="$YELLOW"
            if [[ "$risk" == "HIGH" ]]; then
                risk_color="$RED"
            fi

            echo -e "  ${risk_color}[$risk]${NC} ${BOLD}$description${NC}"
            echo -e "    File: $file"
            echo -e "    Match: ${line}"
            echo ""
        done

        echo -e "${BOLD}What to do:${NC}"
        echo "  1. Remove the secret from the file"
        echo "  2. Use environment variables instead (export in ~/.zshrc)"
        echo "  3. If this is a false positive, add a pattern to .secretsignore"
        echo ""
        echo -e "${YELLOW}To add an exception:${NC}"
        echo "  echo 'pattern-to-ignore' >> .secretsignore"
        echo ""
        echo -e "${YELLOW}To bypass this hook (use with caution):${NC}"
        echo "  git commit --no-verify"
        echo ""

        exit 1
    fi

    # Clean - allow commit
    exit 0
}

main
