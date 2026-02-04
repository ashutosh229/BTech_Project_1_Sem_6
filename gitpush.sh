#!/bin/bash

# Check if commit message is provided
if [ -z "$1" ]; then
  echo "❌ Error: Commit message required"
  echo "Usage: ./gitpush.sh \"your commit message\""
  exit 1
fi

COMMIT_MESSAGE="$1"

echo "📦 Adding all files..."
git add .

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
