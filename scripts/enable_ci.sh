#!/usr/bin/env bash
# enable_ci.sh — افزودن .github/workflows/ci.yml به ریپو با توکنی که workflow scope دارد
#
# دلیل: PAT فاین‌گریند فعلی فاقد مجوز "Workflows" است و GitHub فایل‌های
# زیر .github/workflows/ را با HTTP 403 رد می‌کند. این اسکریپت با یک PAT
# جدید (دارای مجوز Workflows) فایل را ثبت می‌کند.
#
# استفاده / Usage:
#   PAT_WITH_WORKFLOW=<your_new_token> bash scripts/enable_ci.sh
#
# اگر متغیر محیطی تنظیم نباشد، از شما می‌پرسد.
set -euo pipefail

REPO="parsasohrab1/inno-kartoniran-shasta"
BRANCH="main"
FILE_PATH=".github/workflows/ci.yml"
LOCAL_FILE="$(cd "$(dirname "$0")/.." && pwd)/docs/ci.yml"

if [[ -z "${PAT_WITH_WORKFLOW:-}" ]]; then
  read -r -p "Enter PAT with workflow scope: " PAT_WITH_WORKFLOW
fi

if [[ ! -f "$LOCAL_FILE" ]]; then
  echo "ERROR: $LOCAL_FILE not found." >&2
  exit 1
fi

echo ">> Reading $LOCAL_FILE"
CONTENT_B64=$(base64 -w 0 "$LOCAL_FILE")

echo ">> Fetching current main HEAD (to avoid non-fast-forward)"
HEAD_SHA=$(curl -fsSL \
  -H "Authorization: token $PAT_WITH_WORKFLOW" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$REPO/git/refs/heads/$BRANCH" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['object']['sha'])")
echo "   HEAD = $HEAD_SHA"

echo ">> Creating blob for $FILE_PATH"
BLOB_SHA=$(curl -fsSL \
  -H "Authorization: token $PAT_WITH_WORKFLOW" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$REPO/git/blobs" \
  -X POST \
  -d "{\"content\":\"$CONTENT_B64\",\"encoding\":\"base64\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['sha'])")
echo "   blob = $BLOB_SHA"

echo ">> Fetching base tree of HEAD commit"
BASE_TREE=$(curl -fsSL \
  -H "Authorization: token $PAT_WITH_WORKFLOW" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$REPO/git/commits/$HEAD_SHA" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['tree']['sha'])")
echo "   base tree = $BASE_TREE"

echo ">> Creating new tree with $FILE_PATH added"
NEW_TREE=$(curl -fsSL \
  -H "Authorization: token $PAT_WITH_WORKFLOW" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$REPO/git/trees" \
  -X POST \
  -d "{\"base_tree\":\"$BASE_TREE\",\"tree\":[{\"path\":\"$FILE_PATH\",\"mode\":\"100644\",\"type\":\"blob\",\"sha\":\"$BLOB_SHA\"}]}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['sha'])")
echo "   new tree = $NEW_TREE"

echo ">> Creating commit on top of HEAD"
NEW_COMMIT=$(curl -fsSL \
  -H "Authorization: token $PAT_WITH_WORKFLOW" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$REPO/git/commits" \
  -X POST \
  -d "{\"message\":\"ci: add .github/workflows/ci.yml for GitHub Actions\",\"tree\":\"$NEW_TREE\",\"parents\":[\"$HEAD_SHA\"]}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['sha'])")
echo "   new commit = $NEW_COMMIT"

echo ">> Updating refs/heads/$BRANCH to new commit"
curl -fsSL \
  -H "Authorization: token $PAT_WITH_WORKFLOW" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$REPO/git/refs/heads/$BRANCH" \
  -X PATCH \
  -d "{\"sha\":\"$NEW_COMMIT\"}" >/dev/null

echo ""
echo "SUCCESS: $FILE_PATH added to $REPO@$BRANCH"
echo "Commit: https://github.com/$REPO/commit/$NEW_COMMIT"
echo "Workflow: https://github.com/$REPO/actions"
