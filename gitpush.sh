#!/bin/bash

# Check if commit message is provided
if [ -z "$1" ]; then
  echo "❌ Error: Commit message required"
  echo "Usage: ./gitpush.sh \"commit message\" [path]"
  exit 1
fi

COMMIT_MESSAGE="$1"
TARGET_PATH="${2:-.}"

echo "📦 Adding files from: $TARGET_PATH"
git add "$TARGET_PATH"

echo "📝 Committing changes..."
git commit -m "$COMMIT_MESSAGE"

if [ $? -ne 0 ]; then
  echo "❌ Commit failed (nothing to commit?)"
  exit 1
fi

echo "📥 Stashing any remaining changes..."
git stash push -u -m "auto-stash before pull"

echo "🔄 Pulling latest changes (rebase)..."
git pull --rebase

if [ $? -ne 0 ]; then
  echo "❌ Pull failed. Fix conflicts and retry."
  exit 1
fi

echo "📤 Restoring stashed changes..."
git stash pop >/dev/null 2>&1

echo "🚀 Pushing to GitHub..."
git push

echo "✅ Done!"
