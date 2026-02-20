#!/bin/bash
# ContextKeeper Git Diff Summarizer v0.1.2
# Creates human-readable summaries of code changes
# Usage: ck-summarize.sh [file|commit|recent]

set -e

MODE="${1:-recent}"
LINES="${2:-10}"

# Colors
if [ -t 1 ]; then
    BOLD='\033[1m'
    DIM='\033[2m'
    GREEN='\033[32m'
    YELLOW='\033[33m'
    BLUE='\033[34m'
    RESET='\033[0m'
else
    BOLD=''
    DIM=''
    GREEN=''
    YELLOW=''
    BLUE=''
    RESET=''
fi

# Check if in git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "⚠️ Not in a git repository"
    exit 1
fi

REPO=$(basename "$(git rev-parse --show-toplevel)")
BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")

echo -e "${BOLD}🔮 ContextKeeper Change Summary${RESET}"
echo -e "${DIM}Repository: $REPO | Branch: $BRANCH${RESET}"
echo ""

case "$MODE" in
    recent)
        # Summary of recent commits
        echo -e "${BOLD}📜 Recent Commits (last 5)${RESET}"
        echo "─────────────────────────────────────────────"
        git log --oneline -5 | while read line; do
            echo "  • $line"
        done
        echo ""
        
        # Changed files summary
        echo -e "${BOLD}📁 Files Changed (since last checkpoint)${RESET}"
        echo "─────────────────────────────────────────────"
        
        # Get modified files
        MODIFIED=$(git diff --name-only HEAD~5 2>/dev/null | head -20)
        if [ -z "$MODIFIED" ]; then
            echo "  ${DIM}No changes since last checkpoint${RESET}"
        else
            # Count by extension
            echo "$MODIFIED" | awk -F. '{if (NF>1) {print $NF} else {print "(no ext)"}}' | \
            sort | uniq -c | sort -rn | while read count ext; do
                printf "  %s%-3s${RESET} %s%d files${RESET}\n" "$BLUE" "$ext" "$GREEN" "$count"
            done
            echo ""
            echo "  ${DIM}Changed files:${RESET}"
            echo "$MODIFIED" | head -10 | while read file; do
                status=$(git diff --name-status HEAD~5 -- "$file" 2>/dev/null | cut -f1 | head -1)
                icon="📝"
                case "$status" in
                    A) icon="➕" ;;
                    D) icon="🗑️" ;;
                    M) icon="📝" ;;
                esac
                echo "    $icon $file"
            done
            
            total=$(echo "$MODIFIED" | wc -l)
            if [ "$total" -gt 10 ]; then
                echo "    ${DIM}...and $((total - 10)) more files${RESET}"
            fi
        fi
        ;;
        
    stats)
        # Detailed stat summary
        echo -e "${BOLD}📊 Change Statistics${RESET}"
        echo "─────────────────────────────────────────────"
        git diff --stat HEAD~5 2>/dev/null | tail -20 | while read line; do
            echo "  $line"
        done
        echo ""
        
        # Lines changed
        INSERTIONS=$(git diff --numstat HEAD~5 2>/dev/null | awk '{sum+=$1} END {print sum+0}')
        DELETIONS=$(git diff --numstat HEAD~5 2>/dev/null | awk '{sum+=$2} END {print sum+0}')
        NET=$((INSERTIONS - DELETIONS))
        
        echo "  ${GREEN}➕ $INSERTIONS insertions${RESET}"
        echo "  ${YELLOW}➖ $DELETIONS deletions${RESET}"
        if [ "$NET" -gt 0 ]; then
            echo "  ${BLUE}🔢 Net: +$NET lines${RESET}"
        else
            echo "  ${BLUE}🔢 Net: $NET lines${RESET}"
        fi
        ;;
        
    branch)
        # Branch comparison
        echo -e "${BOLD}🌿 Branch Status: $BRANCH${RESET}"
        echo "─────────────────────────────────────────────"
        AHEAD=$(git rev-list --count HEAD --not origin/$BRANCH 2>/dev/null || echo "0")
        BEHIND=$(git rev-list --count origin/$BRANCH --not HEAD 2>/dev/null || echo "0")
        
        if [ "$AHEAD" -gt 0 ]; then
            echo "  ⬆️ $AHEAD commits ahead of origin/$BRANCH"
        fi
        if [ "$BEHIND" -gt 0 ]; then
            echo "  ⬇️ $BEHIND commits behind origin/$BRANCH"
        fi
        if [ "$AHEAD" -eq 0 ] && [ "$BEHIND" -eq 0 ]; then
            echo "  ${GREEN}✓ Up to date with origin/$BRANCH${RESET}"
        fi
        ;;
        
    checkpoint)
        # Generate checkpoint-ready summary
        echo -e "${BOLD}📋 Checkpoint Summary${RESET}"
        echo "─────────────────────────────────────────────"
        echo ""
        echo "## ContextKeeper Checkpoint: $(date -u '+%Y-%m-%d %H:%M UTC')"
        echo ""
        
        # Recent activity
        RECENT=$(git log --oneline -5 --pretty=format:"%s" | head -1)
        echo "**Recent Activity:** $RECENT"
        echo ""
        
        # Changed files
        FILES=$(git diff --name-only HEAD~5 2>/dev/null | head -10 | tr '\n' ', ' | sed 's/, $//')
        if [ -n "$FILES" ]; then
            echo "**Modified:** ${FILES}"
        fi
        
        # Summary by file type
        echo ""
        echo "**Changes:**"
        git diff --numstat HEAD~5 2>/dev/null | head -10 | while read ins del file; do
            if [ "$ins" -gt 0 ] && [ "$del" -gt 0 ]; then
                echo "  • $file (+$ins, -$del)"
            elif [ "$ins" -gt 0 ]; then
                echo "  • $file (+$ins lines)"
            elif [ "$del" -gt 0 ]; then
                echo "  • $file (-$del lines)"
            fi
        done
        echo ""
        ;;
        
    *)
        echo "Usage: ck-summarize.sh [recent|stats|branch|checkpoint]"
        echo ""
        echo "Commands:"
        echo "  recent      - Summary of recent commits and file changes (default)"
        echo "  stats       - Detailed line change statistics"
        echo "  branch      - Branch sync status (ahead/behind)"
        echo "  checkpoint  - Generate checkpoint-ready summary format"
        ;;
esac

echo ""
