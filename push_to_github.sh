#!/bin/bash
# Push script for Study-Time Predictor
# Usage: ./push_to_github.sh

# Initialize git if not already done
if [ ! -d .git ]; then
    git init
    echo "✓ Git initialized"
fi

# Add files one by one or all at once
echo "Adding files to staging..."
git add .

# Commit with message
echo "Committing files..."
git commit -m "Initial commit: Study-Time Predictor ML web app"

echo "✓ Files committed locally"
echo ""
echo "To push to GitHub, run:"
echo "  git remote add origin https://github.com/YOUR_USERNAME/Study-Time-Predictor.git"
echo "  git branch -M main"
echo "  git push -u origin main"
echo ""
echo "Or push one file at a time:"
echo "  git add filename"
echo "  git commit -m 'Add filename'"
echo "  git push"
