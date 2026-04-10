#!/bin/bash
#
# Zoom Connect - First-time Setup
# Creates the config template at ~/.config/zoom-connect.yaml
#

CONFIG_PATH="$HOME/.config/zoom-connect.yaml"

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
# Zoom Connect Configuration (Multi-Profile)
# ============================================
# Each profile holds S2S OAuth credentials for a different Zoom account.
# Use --profile <name> on any tool command, or omit to use default_profile.
#
# Setup steps per profile:
# 1. Go to marketplace.zoom.us > Develop > Build App
# 2. Choose "Server-to-Server OAuth"
# 3. Name: "Zoom Connect" (or any name you like)
# 4. Add all 16 granular scopes (see docs/SETUP-GUIDE.md for details):
#    Meeting: meeting:read:list_meetings:admin, meeting:read:list_meetings:master,
#             meeting:read:meeting:admin, meeting:read:past_meeting:admin
#    Report:  report:read:list_meeting_participants:admin, report:read:user:admin,
#             report:read:chat_session:admin, report:read:list_chat_sessions:admin
#    Recording: cloud_recording:read:list_recording_files:admin,
#               cloud_recording:read:recording:admin,
#               cloud_recording:read:list_account_recordings:admin,
#               cloud_recording:read:recording_analytics_details:admin,
#               cloud_recording:read:recording_analytics_summary:admin,
#               cloud_recording:read:registrant_status:admin
#    User:    user:read:list_users:admin, user:read:user:admin
# 5. Copy Account ID, Client ID, Client Secret below

# Which profile to use when --profile is not specified
default_profile: "main"

profiles:
  main:
    account_id: "YOUR_ACCOUNT_ID"
    client_id: "YOUR_CLIENT_ID"
    client_secret: "YOUR_CLIENT_SECRET"
    user_email: "me"
    download_dir: "~/Downloads/zoom-recordings"

  # Add more profiles as needed:
  # secondary:
  #   account_id: "ANOTHER_ACCOUNT_ID"
  #   client_id: "ANOTHER_CLIENT_ID"
  #   client_secret: "ANOTHER_CLIENT_SECRET"
  #   user_email: "other@email.com"
  #   download_dir: "~/Downloads/zoom-recordings"
EOF

echo "Created config template at $CONFIG_PATH"
echo ""
echo "Next steps:"
echo "1. Go to marketplace.zoom.us > Develop > Build App"
echo "2. Create a Server-to-Server OAuth app"
echo "3. Add all 16 granular scopes (search by category prefix):"
echo "   Meeting:  meeting:read:list_meetings:admin, meeting:read:list_meetings:master,"
echo "             meeting:read:meeting:admin, meeting:read:past_meeting:admin"
echo "   Report:   report:read:list_meeting_participants:admin, report:read:user:admin,"
echo "             report:read:chat_session:admin, report:read:list_chat_sessions:admin"
echo "   Recording: cloud_recording:read:list_recording_files:admin, cloud_recording:read:recording:admin,"
echo "             cloud_recording:read:list_account_recordings:admin, cloud_recording:read:recording_analytics_details:admin,"
echo "             cloud_recording:read:recording_analytics_summary:admin, cloud_recording:read:registrant_status:admin"
echo "   User:     user:read:list_users:admin, user:read:user:admin"
echo "4. Copy Account ID, Client ID, Client Secret into the config file"
echo "5. Test with: python3 tools/zoom_client.py --test"
echo "6. Verify scopes: python3 tools/zoom_client.py --scopes"
echo "7. Add more profiles for additional Zoom accounts"
