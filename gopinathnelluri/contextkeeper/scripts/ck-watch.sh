#!/bin/bash
# ContextKeeper File Watcher v0.1.0
# Auto-checkpoints on file changes with intelligent debouncing
# Usage: ck-watch.sh [start|stop|status] [project_id]
#
# Features:
# - Debounced (waits 5s after last change before checkpointing)
# - Rate limited (max 1 checkpoint per 5 minutes)
# - Change threshold (only checkpoint if >3 files or meaningful changes)
# - PID tracking (prevents duplicate watchers)

set -e

CKPT_DIR="$HOME/.memory/contextkeeper"
WATCH_DIR="${1:-.}"  # Default to current directory
PROJECT_ID="${2:-}"
PIDFILE="$CKPT_DIR/.watch.pid"
LOGFILE="$CKPT_DIR/.watch.log"
LAST_CHECKPOINT_FILE="$CKPT_DIR/.last_auto_checkpoint"

# Configuration
DEBOUNCE_SECONDS=5
MIN_CHECKPOINT_INTERVAL=300  # 5 minutes
MIN_FILES_THRESHOLD=3
MIN_LINES_THRESHOLD=50

# Ensure CKPT_DIR exists
mkdir -p "$CKPT_DIR"

# Get the script directory for calling other scripts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log() {
    echo "[$(date '+%H:%M:%S')] $1" >> "$LOGFILE"
}

checkpoint_if_needed() {
    local git_root
    if ! git rev-parse --show-toplevel > /dev/null 2>&1; then
        return 0  # Not a git repo, skip
    fi
    
    git_root=$(git rev-parse --show-toplevel)
    cd "$git_root"
    
    # Get current changes
    local modified_count=$(git diff --name-only HEAD 2>/dev/null | wc -l)
    local staged_count=$(git diff --name-only --cached 2>/dev/null | wc -l)
    local total_changes=$((modified_count + staged_count))
    
    # Calculate lines changed
    local lines_changed=0
    if [ "$total_changes" -gt 0 ]; then
        lines_changed=$(git diff --numstat HEAD 2>/dev/null | awk '{sum+=$1+$2} END {print sum+0}')
    fi
    
    # Check time since last checkpoint
    local last_checkpoint_time=0
    if [ -f "$LAST_CHECKPOINT_FILE" ]; then
        last_checkpoint_time=$(cat "$LAST_CHECKPOINT_FILE")
    fi
    local current_time=$(date +%s)
    local time_since_last=$((current_time - last_checkpoint_time))
    
    # Decision: should we checkpoint?
    local should_checkpoint=false
    local reason=""
    
    if [ "$time_since_last" -lt "$MIN_CHECKPOINT_INTERVAL" ]; then
        reason="Rate limited (wait $((MIN_CHECKPOINT_INTERVAL - time_since_last))s)"
    elif [ "$total_changes" -ge "$MIN_FILES_THRESHOLD" ] || [ "$lines_changed" -ge "$MIN_LINES_THRESHOLD" ]; then
        should_checkpoint=true
        reason="Significant changes detected: $total_changes files, $lines_changed lines"
    else
        reason="Below threshold: $total_changes files, $lines_changed lines"
    fi
    
    log "$reason"
    
    if [ "$should_checkpoint" = true ]; then
        # Generate a summary based on what changed
        local summary="Auto-checkpoint: $total_changes files changed (+$lines_changed lines)"
        
        # Try to get a semantic summary from recent changes
        local changed_files=$(git diff --name-only HEAD | head -5 | tr '\n' ', ' | sed 's/, $//')
        if [ -n "$changed_files" ]; then
            summary="Auto: Modified $changed_files"
        fi
        
        # Truncate summary if too long
        if [ "${#summary}" -gt 100 ]; then
            summary="${summary:0:97}..."
        fi
        
        log "Creating checkpoint: $summary"
        
        # Call ckpt.sh to create the checkpoint
        "$SCRIPT_DIR/ckpt.sh" "$summary" "$PROJECT_ID" || true
        
        # Record checkpoint time
        echo "$current_time" > "$LAST_CHECKPOINT_FILE"
        
        log "Checkpoint created successfully"
    fi
}

# Debounced checkpoint - waits for changes to settle
decheckpoint() {
    (
        sleep $DEBOUNCE_SECONDS
        checkpoint_if_needed
    ) &
    local pid=$!
    echo $pid > "$CKPT_DIR/.debounce.pid"
    wait $pid 2>/dev/null || true
    rm -f "$CKPT_DIR/.debounce.pid"
}

start_watcher() {
    # Check if already running
    if [ -f "$PIDFILE" ]; then
        local old_pid=$(cat "$PIDFILE")
        if ps -p "$old_pid" > /dev/null 2>&1; then
            echo "⚠️ Watcher already running (PID: $old_pid)"
            echo "   Run: ck-watch.sh stop"
            exit 1
        fi
    fi
    
    echo "🔮 ContextKeeper File Watcher"
    echo "=============================="
    echo "Watching: $WATCH_DIR"
    echo "Project: ${PROJECT_ID:-auto-detected}"
    echo "Debounce: ${DEBOUNCE_SECONDS}s"
    echo "Rate limit: $((MIN_CHECKPOINT_INTERVAL / 60))min"
    echo "Threshold: ${MIN_FILES_THRESHOLD} files or ${MIN_LINES_THRESHOLD} lines"
    echo ""
    
    # Check for inotifywait
    if ! command -v inotifywait > /dev/null 2>&1; then
        echo "⚠️ inotifywait not found. Install: apt-get install inotify-tools"
        exit 1
    fi
    
    # Start background watcher
    (
        echo $$ > "$PIDFILE"
        log "Watcher started (PID: $$)"
        
        # Watch for changes
        inotifywait \
            -m -r -e modify,create,delete,move \
            --format '%w%f' \
            --exclude '\.(git|log|tmp|cache|pid)$' \
            "$WATCH_DIR" 2>/dev/null | while read -r changed_file; do
            
            # Skip certain paths
            if echo "$changed_file" | grep -qE '\.(log|tmp|cache|swp|swo)$|\.git/|node_modules/'; then
                continue
            fi
            
            log "Change detected: $changed_file"
            
            # Kill existing debounce and start new one
            if [ -f "$CKPT_DIR/.debounce.pid" ]; then
                kill "$(cat "$CKPT_DIR/.debounce.pid")" 2>/dev/null || true
            fi
            
            # Start debounced checkpoint
            decheckpoint
        done
    ) &
    
    sleep 0.5
    
    if [ -f "$PIDFILE" ]; then
        local pid=$(cat "$PIDFILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "✅ Watcher started (PID: $pid)"
            echo "   Log: tail -f $LOGFILE"
            echo "   Stop: ck-watch.sh stop"
        else
            echo "⚠️ Watcher failed to start. Check log: $LOGFILE"
        fi
    fi
}

stop_watcher() {
    if [ -f "$PIDFILE" ]; then
        local pid=$(cat "$PIDFILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid" 2>/dev/null || true
            echo "✅ Stopped watcher (PID: $pid)"
        else
            echo "⚠️ Watcher not running (stale PID file)"
        fi
        rm -f "$PIDFILE"
        rm -f "$CKPT_DIR/.debounce.pid"
    else
        echo "ℹ️ No watcher running"
    fi
}

show_status() {
    echo "🔮 ContextKeeper Watcher Status"
    echo "==============================="
    echo ""
    
    if [ -f "$PIDFILE" ]; then
        local pid=$(cat "$PIDFILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "Status: ✅ Running (PID: $pid)"
            echo "Watch directory: $WATCH_DIR"
            echo "Config:"
            echo "  • Debounce: ${DEBOUNCE_SECONDS}s"
            echo "  • Rate limit: $((MIN_CHECKPOINT_INTERVAL / 60))min"
            echo "  • File threshold: $MIN_FILES_THRESHOLD"
            echo "  • Line threshold: $MIN_LINES_THRESHOLD"
            echo ""
            echo "Recent log:"
            if [ -f "$LOGFILE" ]; then
                tail -5 "$LOGFILE" | sed 's/^/  /'
            else
                echo "  (no log yet)"
            fi
        else
            echo "Status: ⚠️ Stale PID file"
        fi
    else
        echo "Status: ⏸️ Not running"
        echo ""
        echo "Start with: ck-watch.sh start [project_id]"
    fi
    echo ""
}

show_help() {
    echo "🔮 ContextKeeper File Watcher"
    echo "Auto-checkpoints on file changes with debouncing"
    echo ""
    echo "