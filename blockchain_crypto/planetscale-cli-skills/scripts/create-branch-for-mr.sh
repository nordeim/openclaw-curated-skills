#!/bin/bash
set -e

# create-branch-for-mr.sh
# Create PlanetScale branch matching your MR/PR branch name

show_help() {
  cat << EOF
Usage: $(basename "$0") [OPTIONS]

Create PlanetScale database branch matching MR/PR branch name.

OPTIONS:
  --database <name>       Database name (required)
  --branch <name>         Branch name (required)
  --from <source>         Source branch (default: main)
  --org <name>            Organization name (optional)
  -h, --help              Show this help message

EXAMPLES:
  # Create branch for MR/PR
  $(basename "$0") --database my-database \\
    --branch feature-user-settings

  # Create branch from specific source
  $(basename "$0") --database my-db --branch feature-x --from development

  # With organization
  $(basename "$0") --database my-db --branch feature-x --org my-org

EXIT CODES:
  0   Success
  1   Error (missing args, pscale command failed)
EOF
}

# Parse arguments
DATABASE=""
BRANCH=""
FROM="main"
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
    --from)
      FROM="$2"
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

# Build pscale command
CMD="pscale branch create \"$DATABASE\" \"$BRANCH\" --from \"$FROM\""
[[ -n "$ORG" ]] && CMD="$CMD --org \"$ORG\""

echo "📦 Creating PlanetScale branch..."
echo "  Database: $DATABASE"
echo "  Branch: $BRANCH"
echo "  From: $FROM"
[[ -n "$ORG" ]] && echo "  Org: $ORG"
echo ""

# Execute
eval $CMD

echo ""
echo "✅ Branch created successfully!"
echo ""
echo "Next steps:"
echo "  1. Make schema changes:"
echo "     pscale shell $DATABASE $BRANCH"
echo ""
echo "  2. View diff:"
echo "     pscale branch diff $DATABASE $BRANCH"
echo ""
echo "  3. Create deploy request:"
echo "     pscale deploy-request create $DATABASE $BRANCH"
