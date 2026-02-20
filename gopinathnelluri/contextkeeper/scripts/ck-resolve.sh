#!/bin/bash
# ContextKeeper Intent Resolver v0.2.0
# Resolves ambiguous references to concrete project context
# Usage: ck-resolve.sh [ambiguous_phrase]
#
# Examples:
#   ck-resolve.sh "finish it"        → Returns active project with next steps
#   ck-resolve.sh "that thing"       → Resolves from recent context
#   ck-resolve.sh "yesterday"        → Returns yesterday's checkpoint
#   ck-resolve.sh "continue"         → Shows where to resume

set -e

CKPT_DIR="${HOME}/.memory/contextkeeper"
CHECKPOINTS_DIR="$CKPT_DIR/checkpoints"
PROJECTS_DIR="$CKPT_DIR/projects"
INTENT_FILE="$CKPT_DIR/intents.json"

# Colors
if [ -t 1 ]; then
  BOLD='\033[1m'
  DIM='\033[2m'
  RESET='\033[0m'
  CYAN='\033[36m'
  GREEN='\033[32m'
  YELLOW='\033[33m'
  RED='\033[31m'
else
  BOLD=''
  DIM=''
  RESET=''
  CYAN=''
  GREEN=''
  YELLOW=''
  RED=''
fi

# Ensure directories exist
mkdir -p "$CHECKPOINTS_DIR" "$PROJECTS_DIR"

# Build intent mappings from checkpoint history
build_intent_map() {
  local map_file="$1"
  local current_project=""
  local current_context=""
  
  # Find most recent checkpoint to determine current context
  if [ -L "$CKPT_DIR/current-state.json" ]; then
    current_project=$(grep '"project_id"' "$CKPT_DIR/current-state.json" 2>/dev/null | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
    current_context=$(grep '"summary"' "$CKPT_DIR/current-state.json" 2>/dev/null | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
  fi
  
  # Build JSON intent map
  cat > "$map_file" << JSON
{
  "current": {
    "project_id": "${current_project:-unknown}",
    "context": "${current_context:-unknown}",
    "timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  },
  "mappings": {
    "it": ["current_project", "recent_checkpoint"],
    "that": ["current_project", "recent_checkpoint"],
    "this": ["current_project", "recent_checkpoint"],
    "thing": ["current_project"],
    "finish": ["in_progress_project"],
    "continue": ["last_session"],
    "resume": ["last_session"],
    "yesterday": ["previous_day_checkpoint"],
    "last": ["previous_checkpoint"],
    "blocker": ["blocked_projects"],
    "stuck": ["blocked_projects"]
  }
}
JSON
}

# Extract project timeline
checkpoint_from_date() {
  local target_date="$1"
  local pattern=""
  
  case "$target_date" in
    yesterday) pattern="$(date -d 'yesterday' '+%Y-%m-%d')" ;;
    today) pattern="$(date '+%Y-%m-%d')" ;;
    *) pattern="$target_date" ;;
  esac
  
  find "$CHECKPOINTS_DIR" -name "${pattern}*" -type f 2>/dev/null | sort | tail -1
}

# Find project by ID
find_project() {
  local proj_id="$1"
  if [ -f "$PROJECTS_DIR/$proj_id/latest.json" ]; then
    cat "$PROJECTS_DIR/$proj_id/latest.json"
  fi
}

# Main resolution logic
resolve_intent() {
  local phrase="$1"
  local lowered=$(echo "$phrase" | tr '[:upper:]' '[:lower:]')
  
  echo -e "${BOLD}${CYAN}🔮 ContextKeeper Intent Resolution${RESET}"
  echo -e "${DIM}Query: \"$phrase\"${RESET}"
  echo ""
  
  # Pattern matching
  case "$lowered" in
    *[\ \"\']yesterday*|yesterday)
      echo -e "${BOLD}📅 Yesterday's Context${RESET}"
      echo "─────────────────────────────────────────"
      local yest_file=$(checkpoint_from_date yesterday)
      if [ -f "$yest_file" ]; then
        local yest_proj=$(grep '"project_name"' "$yest_file" | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
        local yest_sum=$(grep '"summary"' "$yest_file" | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
        local yest_time=$(grep '"timestamp"' "$yest_file" | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
        echo -e "${GREEN}●${RESET} Project: $yest_proj"
        echo -e "   Time:    $yest_time"
        echo -e "   Context: $yest_sum"
        echo ""
        if [ -n "$yest_proj" ]; then
          echo -e "${CYAN}→ Suggestion: Run 'ck-summarize.sh recent' for details${RESET}"
        fi
      else
        echo -e "${YELLOW}⚠️ No checkpoint found from yesterday${RESET}"
        echo "   Run: ckpt.sh \"Starting fresh\" to create one"
      fi
      ;;

    *[\ \"\']it*|*[\ \"\']that*|*[\ \"\']this*|it|that|this|thing|the\ thing)
      echo -e "${BOLD}📦 Current Context Resolution${RESET}"
      echo "─────────────────────────────────────────"
      local current="$CKPT_DIR/current-state.json"
      if [ -L "$current" ] && [ -f "$current" ]; then
        local proj=$(grep '"project_name"' "$current" | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
        local sum=$(grep '"summary"' "$current" | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
        local pid=$(grep '"project_id"' "$current" | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
        local branch=$(grep '"git_branch"' "$current" | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
        
        echo -e "${GREEN}✓ Resolved '${YELLOW}$phrase${RESET}${GREEN}' to:${RESET}"
        echo ""
        echo -e "   ${BOLD}Project:${RESET} $proj ($pid)"
        echo -e "   ${BOLD}Branch:${RESET}  ${branch:-unknown}"
        echo -e "   ${BOLD}Context:${RESET} $sum"
        echo ""
        echo -e "${CYAN}Actions you can take:${RESET}"
        echo "   • ck-summarize.sh recent   → See recent changes"
        echo "   • ckpt.sh \"message\"      → Create new checkpoint"
        echo "   • cd $(grep '"git_dir"' "$current" 2>/dev/null | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/' || echo 'project_dir')"
      else
        echo -e "${YELLOW}⚠️ No current context found${RESET}"
        echo "   Run: ckpt.sh from your project directory"
      fi
      ;;

    *finish*|*complete*|*wrap*)
      echo -e "${BOLD}🎯 Finish Intent Detected${RESET}"
      echo "─────────────────────────────────────────"
      # Find in-progress projects
      local found=0
      if [ -d "$PROJECTS_DIR" ]; then
        for proj in "$PROJECTS_DIR"/*/latest.json; do
          [ -f "$proj" ] || continue
          local status=$(grep '"status"' "$proj" | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
          if [ "$status" = "active" ]; then
            found=1
            local pid=$(basename "$(dirname "$proj")")
            local name=$(grep '"project_name"' "$proj" | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
            echo -e "${GREEN}●${RESET} $name ($pid) — status: $status"
            
            # Show last checkpoint
            local last=$(grep '"last_checkpoint"' "$proj" | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
            if [ -f "$CHECKPOINTS_DIR/$last.json" ]; then
              local last_sum=$(grep '"summary"' "$CHECKPOINTS_DIR/$last.json" | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
              echo -e "   Last: $last_sum"
            fi
          fi
        done
      fi
      
      if [ $found -eq 0 ]; then
        echo -e "${YELLOW}⚠️ No active projects to finish${RESET}"
        echo "   Use: ckpt.sh \"Starting work on X\" to track a project"
      else
        echo ""
        echo -e "${CYAN}→ Suggestion: Run 'dashboard.sh' for full status${RESET}"
      fi
      ;;

    *continue*|*resume*|*pick*up*|*where*|*left*off*)
      echo -e "${BOLD}▶️ Continue from Last Session${RESET}"
      echo "─────────────────────────────────────────"
      local newest=$(find "$CHECKPOINTS_DIR" -name "*.json" -type f 2>/dev/null | sort | tail -1)
      if [ -f "$newest" ]; then
        local proj=$(grep '"project_name"' "$newest" | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
        local sum=$(grep '"summary"' "$newest" | head -1 | sed 's/.*: *"\([^"]*\)".*/\1