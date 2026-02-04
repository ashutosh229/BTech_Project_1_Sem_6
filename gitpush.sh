#!/bin/bash

# Check if commit message is provided
if [ -z "$1" ]; then
  echo "❌ Error: Commit message required"
  echo "Usage:"
  echo "  ./gitpush.sh \"commit message\" [path]"
  exit 1
fi

COMMIT_MESSAGE="$1"
TARGET_PATH="${2:-.}"   # if $2 empty → "."

echo "📦 Adding files from: $TARGET_PATH"
git add "$TARGET_PATH"

echo "📝 Committing changes..."
git commit -m "$COMMIT_MESSAGE"

if [ $? -ne 0 ]; then
  echo "❌ Commit failed (nothing to commit?)"
  exit 1
fi

echo "🔄 Pulling latest changes (rebase)..."
git pull --rebase

if [ $? -ne 0 ]; then
  echo "❌ Pull failed. Resolve conflicts and retry."
  exit 1
fi

echo "🚀 Pushing to GitHub..."
git push

echo "✅ Done!"
