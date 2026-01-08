#!/bin/bash
# Install AAGIES Global Command

AEGIS_DIR="$HOME/Desktop/Aegis-Core"
PROFILE="$HOME/.zshrc"

echo "Installing AAGIES..."

# Add alias if not exists
if ! grep -q "alias aagies=" "$PROFILE"; then
    echo "" >> "$PROFILE"
    echo "# AAGIES Self-Healing Tool" >> "$PROFILE"
    echo "alias aagies=\"python3 $AEGIS_DIR/aagies.py\"" >> "$PROFILE"
    echo "alias aagies-start=\"python3 $AEGIS_DIR/aagies.py --start\"" >> "$PROFILE"
    echo "✅ Added 'aagies' and 'aagies-start' aliases to $PROFILE"
else
    echo "ℹ️  'aagies' alias already exists"
fi

echo "Installation complete."
echo "Please run: source ~/.zshrc"
