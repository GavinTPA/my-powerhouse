#!/bin/bash
#
# GHL Connect - First-time Setup
# Creates the config template at ~/.config/ghl-connect.yaml
#

CONFIG_PATH="$HOME/.config/ghl-connect.yaml"

# Create .config if it doesn't exist
mkdir -p "$HOME/.config"

# Check if config already exists
if [ -f "$CONFIG_PATH" ]; then
    echo "Config already exists at $CONFIG_PATH"
    echo "Delete it first if you want to recreate from template."
    exit 1
fi

# Create template config
cat > "$CONFIG_PATH" << 'EOF'
# GHL Connect Configuration
# ========================
# Get your Private Integration Token from:
# GHL > Settings > Private Integrations > Add Integration

# Your Private Integration Token (pit_XXXXX...)
api_token: "YOUR_TOKEN_HERE"

# Your Location ID (find in GHL URL or Settings > Business Info)
location_id: "YOUR_LOCATION_ID"

# API settings (usually don't need to change)
api_base: "https://services.leadconnectorhq.com"
api_version: "2021-07-28"

# Your "from" email address (the one GHL sends from)
default_from_email: ""

# Rate limiting (per session)
max_sends_per_session: 10

# --- Scope Tiers ---
# Start with read-only scopes, then add more as you need them.
#
# STARTER (read-only — safe to start here):
#   contacts.readonly, conversations.readonly, conversations/message.readonly
#
# INTERMEDIATE (when you're ready to interact):
#   contacts.write, conversations.write, conversations/message.write
#
# ADVANCED (media uploads, workflows):
#   medias.write, medias.readonly, workflows.readonly
#
# SOCIAL PLANNER (for ghl-social skill):
#   socialplanner/post.readonly, socialplanner/post.write,
#   socialplanner/account.readonly, socialplanner/category.readonly,
#   socialplanner/tag.readonly
#
# Tip: You can always go back to GHL > Settings > Private Integrations
# and add more scopes later. Build up — don't start with everything.
EOF

echo "Created config template at $CONFIG_PATH"
echo ""
echo "Next steps:"
echo "1. Go to GHL > Settings > Private Integrations > Add Integration"
echo "2. Start with read-only scopes (see config file for tiers)"
echo "3. Copy your token (pit_XXXXX...) into the config file"
echo "4. Add your location_id from GHL"
echo "5. Test with: python3 tools/ghl_client.py --test"
