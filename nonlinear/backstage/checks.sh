#!/bin/bash
# checks.sh - Unified POLICY + HEALTH enforcement
# Separates Executable (deterministic) vs Interpretive (contextual) rules

set -e

PROJECT_ROOT="${1:-.}"
MODE="${2:-start}" # start or end

cd "$PROJECT_ROOT"

echo "🔍 Running backstage checks (mode: $MODE)..."
echo ""

# ============================================================================
# STEP 1: Locate POLICY/HEALTH files (global + project)
# ============================================================================

GLOBAL_POLICY="$HOME/Documents/backstage/backstage/global/POLICY.md"
PROJECT_POLICY="backstage/POLICY.md"
GLOBAL_HEALTH="$HOME/Documents/backstage/backstage/global/HEALTH.md"
PROJECT_HEALTH="backstage/HEALTH.md"

echo "📋 Locating POLICY + HEALTH files..."

POLICY_FILES=()
HEALTH_FILES=()

if [ -f "$GLOBAL_POLICY" ]; then
    echo "  ✅ Global POLICY: $GLOBAL_POLICY"
    POLICY_FILES+=("$GLOBAL_POLICY")
fi

if [ -f "$PROJECT_POLICY" ]; then
    echo "  ✅ Project POLICY: $PROJECT_POLICY (takes precedence)"
    POLICY_FILES+=("$PROJECT_POLICY")
fi

if [ -f "$GLOBAL_HEALTH" ]; then
    echo "  ✅ Global HEALTH: $GLOBAL_HEALTH"
    HEALTH_FILES+=("$GLOBAL_HEALTH")
fi

if [ -f "$PROJECT_HEALTH" ]; then
    echo "  ✅ Project HEALTH: $PROJECT_HEALTH (takes precedence)"
    HEALTH_FILES+=("$PROJECT_HEALTH")
fi

# ============================================================================
# STEP 2: Extract EXECUTABLE rules from POLICY (deterministic)
# ============================================================================

echo ""
echo "🔧 Extracting executable rules from POLICY..."

# Extract current backstage version from POLICY
VERSION=""
for policy in "${POLICY_FILES[@]}"; do
    VERSION=$(grep -o 'backstage rules.*v[0-9.]*' "$policy" | sed 's/.*v\([0-9.]*\).*/\1/' | head -1)
    if [ -n "$VERSION" ]; then
        echo "  ✅ Found version: v$VERSION"
        break
    fi
done

if [ -z "$VERSION" ]; then
    echo "  ⚠️  No version found in POLICY"
    VERSION="unknown"
fi

# Extract navigation block template (between specific markers)
NAV_TEMPLATE=$(awk '/Navigation block template \(current version\):/,/```markdown/,/```/' "${POLICY_FILES[0]}" 2>/dev/null || echo "")

if [ -n "$NAV_TEMPLATE" ]; then
    echo "  ✅ Navigation block template extracted"
else
    echo "  ⚠️  No navigation block template found"
fi

# ============================================================================
# STEP 3: Extract EXECUTABLE rules from HEALTH (code blocks)
# ============================================================================

echo ""
echo "🧪 Extracting executable rules from HEALTH..."

HEALTH_CHECKS=()

for health in "${HEALTH_FILES[@]}"; do
    # Extract bash code blocks
    while IFS= read -r block; do
        if [ -n "$block" ]; then
            HEALTH_CHECKS+=("$block")
        fi
    done < <(awk '/```bash/,/```/ {if (!/```/) print}' "$health")
done

echo "  ✅ Found ${#HEALTH_CHECKS[@]} executable checks"

# ============================================================================
# STEP 4: Execute DETERMINISTIC rules (SH domain)
# ============================================================================

echo ""
echo "⚙️  Executing deterministic rules..."

EXEC_PASS=true

# Check: Navigation blocks exist in backstage files
for file in README.md backstage/ROADMAP.md backstage/CHANGELOG.md backstage/POLICY.md backstage/HEALTH.md; do
    if [ -f "$file" ]; then
        if grep -q "> 🤖" "$file"; then
            echo "  ✅ $file has navigation block"
        else
            echo "  ⚠️  $file missing navigation block (AI will add)"
            EXEC_PASS=false
        fi
    fi
done

# Check: Versions match
if [ -f "README.md" ]; then
    README_VERSION=$(grep -o 'backstage rules.*v[0-9.]*' README.md | sed 's/.*v\([0-9.]*\).*/\1/' | head -1 || echo "")
    if [ "$README_VERSION" = "$VERSION" ]; then
        echo "  ✅ README version matches POLICY (v$VERSION)"
    else
        echo "  ⚠️  README version mismatch (has: $README_VERSION, expected: $VERSION)"
        EXEC_PASS=false
    fi
fi

# Execute HEALTH checks
for check in "${HEALTH_CHECKS[@]}"; do
    if eval "$check" >/dev/null 2>&1; then
        echo "  ✅ HEALTH check passed: ${check:0:50}..."
    else
        echo "  ❌ HEALTH check failed: ${check:0:50}..."
        EXEC_PASS=false
    fi
done

# ============================================================================
# STEP 5: Report INTERPRETIVE rules (AI domain)
# ============================================================================

echo ""
echo "🤖 Interpretive rules (AI handles):"
echo "  - README protection (needs confirmation before edits)"
echo "  - Surgical changes only (quality judgment)"
echo "  - Context decisions (project wins on conflict)"
echo "  - Mermaid diagram propagation (ROADMAP → all files)"
echo ""
echo "  → AI will enforce these via prompts in backstage-start/end"

# ============================================================================
# STEP 6: Integrated report
# ============================================================================

echo ""
echo "📊 Integrated Compliance Report:"
echo ""

if [ "$EXEC_PASS" = true ]; then
    echo "  ✅ All deterministic checks passed"
    echo "  ✅ Executable enforcement: COMPLETE"
else
    echo "  ⚠️  Some deterministic checks failed (see above)"
    echo "  ⚠️  Executable enforcement: NEEDS FIXES"
fi

echo "  🤖 Interpretive enforcement: Pending AI action"
echo ""

# ============================================================================
# STEP 7: Exit code (mode-aware)
# ============================================================================

if [ "$EXEC_PASS" = true ]; then
    echo "✅ checks.sh complete (all deterministic rules passed)"
    exit 0
else
    if [ "$MODE" = "start" ]; then
        echo "🛑 checks.sh failed (blocking commit - fix issues above)"
        exit 1
    else
        echo "⚠️  checks.sh soft fail (add issues to ROADMAP)"
        exit 0
    fi
fi
