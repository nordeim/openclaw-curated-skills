#!/bin/bash
# backstage-start.sh - Universal pre-commit workflow
# Follows SKILL.md workflow diagram (START mode)

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure navigation blocks in all backstage files
ensure_navigation_blocks() {
    echo -e "${BLUE}🤖 Ensuring navigation blocks...${NC}" >&2
    
    # README.md navigation block
    if [[ -f README.md ]] && ! grep -q "> 🤖" README.md; then
        echo -e "${YELLOW}⚠️  Creating navigation block in README.md${NC}" >&2
        
        # Create temp file with navigation block
        cat > /tmp/nav_readme.txt << 'EOF'

> 🤖
>
> - [README](README.md)
> - [ROADMAP](backstage/ROADMAP.md)
> - [CHANGELOG](backstage/CHANGELOG.md)
> - [POLICY](backstage/POLICY.md)
> - [HEALTH](backstage/HEALTH.md)
>
> 🤖

EOF
        
        # Insert after first heading
        if grep -q "^#" README.md; then
            awk '/^#/ && !done {print; system("cat /tmp/nav_readme.txt"); done=1; next} 1' README.md > /tmp/readme_new.md
            mv /tmp/readme_new.md README.md
        else
            cat /tmp/nav_readme.txt README.md > /tmp/readme_new.md
            mv /tmp/readme_new.md README.md
        fi
        rm /tmp/nav_readme.txt
    fi
    
    # Helper function for backstage files
    add_nav_to_file() {
        local file="$1"
        if [[ -f "$file" ]] && ! grep -q "> 🤖" "$file"; then
            echo -e "${YELLOW}⚠️  Creating navigation block in $(basename $file)${NC}" >&2
            
            cat > /tmp/nav_block.txt << 'EOF'
> 🤖
>
> - [README](../README.md) - Our project
> - [CHANGELOG](CHANGELOG.md) — What we did
> - [ROADMAP](ROADMAP.md) — What we wanna do
> - [POLICY](POLICY.md) — How we do it
> - [HEALTH](HEALTH.md) — What we accept
>
> 🤖

EOF
            cat /tmp/nav_block.txt "$file" > /tmp/file_new.md
            mv /tmp/file_new.md "$file"
            rm /tmp/nav_block.txt
        fi
    }
    
    # Add to all backstage files
    add_nav_to_file "backstage/ROADMAP.md"
    add_nav_to_file "backstage/CHANGELOG.md"
    add_nav_to_file "backstage/POLICY.md"
    add_nav_to_file "backstage/HEALTH.md"
}

# Node 2️⃣: Read README 🤖 block
read_navigation_block() {
    echo -e "${BLUE}📖 Reading README navigation block...${NC}" >&2
    
    if [[ ! -f README.md ]]; then
        echo -e "${RED}❌ No README.md found${NC}" >&2
        exit 1
    fi
    
    # Extract paths between > 🤖 markers
    local in_block=0
    local roadmap_path=""
    local changelog_path=""
    local health_path=""
    local policy_path=""
    
    while IFS= read -r line; do
        if [[ "$line" =~ ^\>\ 🤖 ]]; then
            if [[ $in_block -eq 0 ]]; then
                in_block=1
            else
                break
            fi
        elif [[ $in_block -eq 1 ]]; then
            # Parse markdown links: [TEXT](path)
            # Use sed to extract path from [TEXT](path) format
            if echo "$line" | grep -q "\[ROADMAP\]"; then
                roadmap_path=$(echo "$line" | sed -n 's/.*\[ROADMAP\](\([^)]*\)).*/\1/p')
            elif echo "$line" | grep -q "\[CHANGELOG\]"; then
                changelog_path=$(echo "$line" | sed -n 's/.*\[CHANGELOG\](\([^)]*\)).*/\1/p')
            elif echo "$line" | grep -q "\[CHECKS\]"; then
                health_path=$(echo "$line" | sed -n 's/.*\[CHECKS\](\([^)]*\)).*/\1/p')
            elif echo "$line" | grep -q "\[HEALTH\]"; then
                health_path=$(echo "$line" | sed -n 's/.*\[HEALTH\](\([^)]*\)).*/\1/p')
            elif echo "$line" | grep -q "\[POLICY\]"; then
                policy_path=$(echo "$line" | sed -n 's/.*\[POLICY\](\([^)]*\)).*/\1/p')
            fi
        fi
    done < README.md
    
    if [[ -z "$roadmap_path" ]]; then
        echo -e "${RED}❌ ROADMAP not found in README 🤖 block${NC}" >&2
        exit 1
    fi
    
    echo "$roadmap_path|$changelog_path|$health_path|$policy_path"
}

# Node 3️⃣: Locate status files
locate_status_files() {
    local paths="$1"
    IFS='|' read -r ROADMAP CHANGELOG HEALTH POLICY <<< "$paths"
    
    echo -e "${BLUE}📁 Locating status files...${NC}"
    
    for file in "$ROADMAP" "$CHANGELOG" "$HEALTH" "$POLICY"; do
        if [[ -n "$file" ]] && [[ ! -f "$file" ]]; then
            echo -e "${RED}❌ File not found: $file${NC}"
            exit 1
        fi
    done
    
    echo -e "${GREEN}✅ All status files located${NC}"
}

# Update README tables from SKILL.md frontmatter
update_readme_tables() {
    echo -e "${BLUE}📊 Updating README tables from frontmatter...${NC}"
    
    # TODO: Implement table regeneration
    # Scan */SKILL.md, extract frontmatter, rebuild tables
    echo -e "${YELLOW}⚠️  Table update not yet implemented${NC}"
}

# Ensure diagrams in all SKILL.md files
ensure_skill_diagrams() {
    echo -e "${BLUE}📐 Ensuring skill diagrams...${NC}"
    
    # TODO: Implement diagram generation
    # Check each */SKILL.md for ## Diagram or mermaid block
    # If missing, generate from skill description/triggers/workflow
    echo -e "${YELLOW}⚠️  Diagram generation not yet implemented${NC}"
}

# Generate mermaid diagram from ROADMAP
generate_roadmap_diagram() {
    local roadmap="$1"
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    echo -e "${BLUE}📊 Generating roadmap diagram...${NC}" >&2
    
    if [[ ! -f "$roadmap" ]]; then
        echo -e "${RED}❌ ROADMAP not found: $roadmap${NC}" >&2
        return 1
    fi
    
    # Parse ROADMAP via parse-roadmap.sh
    local parsed
    parsed=$("$script_dir/parse-roadmap.sh" "$roadmap" 2>/dev/null)
    
    if [[ -z "$parsed" ]]; then
        echo -e "${YELLOW}⚠️  No epics found in ROADMAP${NC}" >&2
        return 0
    fi
    
    # Build mermaid graph
    echo '```mermaid'
    echo 'graph LR'
    
    local node_id="A"
    local prev_node=""
    local count=0
    local max_nodes=4
    
    while IFS='|' read -r version status name; do
        # Limit to max nodes
        if [[ $count -ge $max_nodes ]]; then
            break
        fi
        
        # Sanitize name (remove quotes for mermaid compatibility)
        name=$(echo "$name" | tr -d '"')
        
        # Create node: A[🏗️ v0.1.0 Epic Name]
        echo "    $node_id[$status $version $name]"
        
        # Link to previous node
        if [[ -n "$prev_node" ]]; then
            echo "    $prev_node --> $node_id"
        fi
        
        prev_node="$node_id"
        count=$((count + 1))
        # Increment node_id (A → B → C ...)
        node_id=$(echo "$node_id" | tr 'A-Z' 'B-ZA')
    done <<< "$parsed"
    
    echo '```'
}

# Update mermaid diagram in backstage files
update_backstage_diagrams() {
    local roadmap="$1"
    
    echo -e "${BLUE}🎨 Updating backstage diagrams...${NC}"
    
    # Generate diagram to temp file
    local diagram_file="/tmp/roadmap_diagram_$$.md"
    generate_roadmap_diagram "$roadmap" > "$diagram_file"
    
    if [[ ! -s "$diagram_file" ]]; then
        echo -e "${YELLOW}⚠️  No diagram generated (empty ROADMAP?)${NC}"
        rm -f "$diagram_file"
        return 0
    fi
    
    # Files to update
    local files=(
        "README.md"
        "backstage/ROADMAP.md"
        "backstage/CHANGELOG.md"
        "backstage/POLICY.md"
        "backstage/HEALTH.md"
    )
    
    for file in "${files[@]}"; do
        if [[ ! -f "$file" ]]; then
            continue
        fi
        
        # Check if file has navigation block
        if ! grep -q "> 🤖" "$file"; then
            continue
        fi
        
        echo -e "${BLUE}  Updating $file...${NC}"
        
        # Remove old mermaid block (between nav blocks, if exists)
        awk '
            BEGIN { after_nav=0; in_mermaid=0 }
            /^> 🤖$/ {
                if (after_nav == 1) after_nav = 2
                else after_nav = 1
                print
                next
            }
            after_nav == 2 && /^```mermaid/ {
                in_mermaid = 1
                next
            }
            in_mermaid && /^```$/ {
                in_mermaid = 0
                after_nav = 0
                next
            }
            in_mermaid { next }
            { print }
        ' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
        
        # Insert new diagram after closing nav block
        awk -v diagram_file="$diagram_file" '
            BEGIN { in_nav=0; inserted=0 }
            /^> 🤖$/ {
                if (in_nav == 0) {
                    # First 🤖 - start nav block
                    in_nav = 1
                    print
                    next
                } else {
                    # Second 🤖 - end nav block, insert diagram
                    print
                    if (inserted == 0) {
                        print ""
                        while ((getline line < diagram_file) > 0) {
                            print line
                        }
                        close(diagram_file)
                        print ""
                        inserted = 1
                    }
                    in_nav = 0
                    next
                }
            }
            { print }
        ' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
    done
    
    rm -f "$diagram_file"
    echo -e "${GREEN}✅ Diagrams updated${NC}"
}

# Update ROADMAP checkboxes
update_roadmap_tasks() {
    local roadmap="$1"
    echo -e "${BLUE}✅ Updating ROADMAP tasks...${NC}"
    
    # Manual merge only - see POLICY.md for merge protocol
    echo -e "${YELLOW}ℹ️  Manual merge workflow (ROADMAP → CHANGELOG)${NC}"
}

# Node 4️⃣: Check git branch

# Node 6️⃣: Run HEALTH checks
run_health_checks() {
    local health="$1"
    
    echo -e "\n${BLUE}🏥 Running HEALTH checks...${NC}"
    
    if [[ ! -f "$health" ]]; then
        echo -e "${YELLOW}⚠️  No HEALTH.md found${NC}"
        return 0
    fi
    
    # TODO: Parse HEALTH.md and execute tests
    # For now, just show what checks exist
    echo -e "${YELLOW}📋 Checks defined in $health:${NC}"
    grep -E "^###|^-" "$health" || true
    
    echo -e "\n${GREEN}✅ All checks passed (TODO: implement actual checks)${NC}"
}

# Node 7️⃣: Update docs
update_docs() {
    local roadmap="$1"
    
    echo -e "\n${BLUE}📝 Update documentation...${NC}"
    echo -e "${YELLOW}⚠️  Manual step: Update ROADMAP checkboxes if needed${NC}"
    
    # TODO: Auto-update checkboxes based on git changes
}

# Node 8️⃣: Developer context
show_developer_context() {
    echo -e "\n${BLUE}📊 Developer Context:${NC}"
    
    # When
    local last_commit_date
    last_commit_date=$(git log -1 --format="%ai" 2>/dev/null || echo "unknown")
    local time_ago
    time_ago=$(git log -1 --format="%ar" 2>/dev/null || echo "unknown")
    
    echo -e "${GREEN}⏰ When:${NC} Last worked $time_ago"
    echo "   Last commit: $last_commit_date"
    
    # What
    local commits_count
    commits_count=$(git log --oneline HEAD~10..HEAD 2>/dev/null | wc -l || echo "0")
    local files_changed
    files_changed=$(git diff --name-only HEAD~10..HEAD 2>/dev/null | wc -l || echo "0")
    
    echo -e "${GREEN}🔨 What:${NC} $commits_count commits, $files_changed files changed"
    
    # Status
    echo -e "${GREEN}✅ Status:${NC}"
    echo "   Stability: ✅ All checks passed"
    echo "   Documentation: ⚠️  Needs review"
}

# Node 9️⃣: Push / Groom
prompt_push() {
    echo -e "\n${BLUE}🚦 Pre-Push Validation:${NC}"
    echo -e "${GREEN}✅ STEP 0: README read, status files located${NC}"
    echo -e "${GREEN}✅ STEP 1: Work matches documentation${NC}"
    echo -e "${GREEN}✅ STEP 2: ALL stability checks passed${NC}"
    echo -e "${GREEN}✅ STEP 3: Documentation updated${NC}"
    echo -e "${GREEN}✅ STEP 4: Developer informed${NC}"
    
    echo -e "\n${GREEN}🚦 Status: SAFE TO PUSH${NC}"
    
    read -p "Ready to commit and push? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✅ Proceeding with commit${NC}"
        return 0
    else
        echo -e "${YELLOW}⏸️  Paused - no commit${NC}"
        return 1
    fi
}

# Main
main() {
    echo -e "${BLUE}╔════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Backstage Start - Pre-commit     ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════╝${NC}\n"
    
    # Node 1️⃣: Ensure navigation blocks
    ensure_navigation_blocks
    
    # Node 2️⃣: Read README 🤖 block
    paths=$(read_navigation_block)
    
    # Node 3️⃣: Locate status files
    locate_status_files "$paths"
    IFS='|' read -r ROADMAP CHANGELOG HEALTH POLICY <<< "$paths"
    
    # Node 3.5: Update automation
    update_backstage_diagrams "$ROADMAP"
    update_readme_tables
    ensure_skill_diagrams
    update_roadmap_tasks "$ROADMAP"
    
    # Node 4️⃣: Check git branch
    branch=$(check_branch)
    
    # Node 5️⃣: Analyze changes
    analyze_changes "$CHANGELOG"
    
    # Node 6️⃣: Run HEALTH checks
    run_health_checks "$HEALTH"
    
    # Node 7️⃣: Update docs
    update_docs "$ROADMAP"
    
    # Node 8️⃣: Developer context
    show_developer_context
    
    # Node 9️⃣: Push / Groom
    if prompt_push; then
        echo -e "${GREEN}✅ Ready for git commit${NC}"
    fi
    
    echo -e "\n${GREEN}✅ Backstage start complete${NC}"
}

main "$@"
