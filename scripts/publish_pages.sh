#!/usr/bin/env bash
# Rebuild the static demo and force-push it to the gh-pages branch.
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON="${PYTHON:-.venv/bin/python}"
"$PYTHON" scripts/build_pages.py
REMOTE="$(git remote get-url origin)"
NAME="$(git config user.name)"
EMAIL="$(git config user.email)"
cd _site
rm -rf .git
git init -q -b gh-pages
git add -A
git -c user.name="$NAME" -c user.email="$EMAIL" commit -qm "Publish demo from $(git -C .. rev-parse --short HEAD)"
git push -qf "$REMOTE" gh-pages
rm -rf .git
echo "Published to gh-pages"
