#!/bin/bash
set -e

# sync-branch-with-main.sh
# Sync a development branch with main (refresh schema)

show_help() {
  cat << EOF
Usage: $(basename "$0") [OPTIONS]

Sync development branch schema with main branch.

OPTIONS:
  --database <name>       Database name (required)
  --branch <name>         Branch name to sync (required)
  --org <name>            Organization name (optional)
  -h, --help              Show this help message

EXAMPLES:
  # Sync branch with main
  $(basename "$0") --database my-database --branch feature-branch

  # With organization
  $(basename "$0") --database my-db --branch dev-branch --org my-org

WHAT IT DOES:
  Refreshes the branch schema to match the current production (main) schema.
  Useful when main has been updated and your branch needs to catch up.

EXIT CODES:
  0   Success
  1   Error (missing args, pscale command failed)
EOF
}

# Parse arguments
DATABASE=""
BRANCH=""
ORG=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --database)
      DATABASE="$2"
      shift 2
      ;;
    --branch)
      BRANCH="$2"
      shift 2
      ;;
    --org)
      ORG="$2"
      shift 2
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      echo "❌ Unknown option: $1"
      echo "Run with --help for usage"
      exit 1
      ;;
  esac
done

# Validate required arguments
if [[ -z "$DATABASE" ]] || [[ -z "$BRANCH" ]]; then
  echo "❌ Error: --database and --branch are required"
  echo "Run with --help for usage"
  exit 1
fi

# Build org flag
ORG_FLAG=""
[[ -n "$ORG" ]] && ORG_FLAG="--org $ORG"

echo "🔄 Syncing branch with main..."
echo "  Database: $DATABASE"
echo "  Branch: $BRANCH"
[[ -n "$ORG" ]] && echo "  Org: $ORG"
echo ""

# Refresh schema
pscale branch refresh-schema "$DATABASE" "$BRANCH" $ORG_FLAG

echo ""
echo "✅ Branch schema refreshed!"
echo ""
echo "Next steps:"
echo "  1. Verify schema:"
echo "     pscale branch schema $DATABASE $BRANCH"
echo ""
echo "  2. Check diff (should show your changes only):"
echo "     pscale branch diff $DATABASE $BRANCH"
