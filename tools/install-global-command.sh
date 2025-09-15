#!/bin/bash
# Installation script for global "run minty" command

set -e

echo "🍃 Setting up global 'run minty' command..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create a function-based alias for "run minty"
SHELL_RC=""
if [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
else
    echo "❌ Could not find .bashrc or .zshrc"
    exit 1
fi

# Check if the alias already exists
if ! grep -q "run minty" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# minty-maintenance global command" >> "$SHELL_RC"
    echo "run() {" >> "$SHELL_RC"
    echo "    if [ \"\$1\" = \"minty\" ]; then" >> "$SHELL_RC"
    echo "        shift" >> "$SHELL_RC"
    echo "        $SCRIPT_DIR/mint-maintainer.sh \"\$@\"" >> "$SHELL_RC"
    echo "    else" >> "$SHELL_RC"
    echo "        command run \"\$@\"" >> "$SHELL_RC"
    echo "    fi" >> "$SHELL_RC"
    echo "}" >> "$SHELL_RC"
    
    echo "✅ Added 'run minty' command to $SHELL_RC"
    echo ""
    echo "📝 To use the command immediately, run:"
    echo "   source $SHELL_RC"
    echo ""
    echo "Or open a new terminal window."
else
    echo "✅ 'run minty' command already configured in $SHELL_RC"
fi

# Alternative method: Create a symlink in ~/.local/bin
echo ""
echo "Additionally setting up 'minty' command..."
mkdir -p "$HOME/.local/bin"

# Create the wrapper script
cat > "$HOME/.local/bin/minty" << EOF
#!/bin/bash
# minty-maintenance launcher
exec "$SCRIPT_DIR/mint-maintainer.sh" "\$@"
EOF

chmod +x "$HOME/.local/bin/minty"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "" >> "$SHELL_RC"
    echo "# Add ~/.local/bin to PATH for minty command" >> "$SHELL_RC"
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$SHELL_RC"
    echo "✅ Added ~/.local/bin to PATH"
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "You can now use either:"
echo "  • run minty        (from anywhere)"
echo "  • minty            (from anywhere)"
echo ""
echo "Examples:"
echo "  run minty          # Launch interactive TUI"
echo "  run minty dry-run  # Run in dry-run mode"
echo "  minty              # Same as above"
echo ""
echo "Remember to run: source $SHELL_RC"
echo "Or open a new terminal for the commands to work."
