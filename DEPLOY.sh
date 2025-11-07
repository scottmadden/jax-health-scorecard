#!/bin/bash
# Personalized deployment script for scottmadden
# Run this file to deploy your Jacksonville Health Scorecard to GitHub

set -e  # Exit on any error

echo "🚀 Deploying Jacksonville Health Scorecard for scottmadden..."
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not found."
    echo "📦 Install with: brew install gh"
    echo "🔑 Then authenticate: gh auth login"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "🔑 Please authenticate with GitHub:"
    gh auth login
fi

echo "✅ GitHub CLI authenticated"
echo ""

# Create and push repository
echo "📤 Creating GitHub repository: scottmadden/jax-health-scorecard..."
cd "/Users/scottmadden/Jax Health Scorecard"

gh repo create jax-health-scorecard --public --source=. --remote=origin --push

echo ""
echo "✅ Repository created and pushed!"
echo ""
echo "📍 Your repository: https://github.com/scottmadden/jax-health-scorecard"
echo ""
echo "🌐 Next steps:"
echo ""
echo "1. Enable GitHub Pages:"
echo "   → Open: https://github.com/scottmadden/jax-health-scorecard/settings/pages"
echo "   → Set Source: 'Deploy from a branch'"
echo "   → Set Branch: 'main' and Folder: '/docs'"
echo "   → Click Save"
echo ""
echo "2. Your live site will be at:"
echo "   → https://scottmadden.github.io/jax-health-scorecard/"
echo ""
echo "3. Test automation (optional):"
echo "   → Open: https://github.com/scottmadden/jax-health-scorecard/actions"
echo "   → Click 'build-scorecard' → 'Run workflow'"
echo ""
echo "🎉 Deployment complete! Check the links above."

