# Zoom Connect - Setup Guide

**Time required:** ~15 minutes for setup, ~10 minutes for testing
**What you need:** Your Zoom account (must be Pro plan or higher)

---

## What You're Building

You're creating a secure connection between Claude Code and your Zoom account. This uses something called **Server-to-Server OAuth** — a method Zoom provides for apps that run on your own computer.

Here's what that means in plain English: you create a small "app" inside your Zoom account that generates three credentials (like a username, password, and account number). You paste those into a config file on your machine. From that point on, the zoom-connect tools can pull data from your Zoom account automatically — no browser login needed, no popups, nothing to maintain.

The app only has **read access** — it can see your meetings and download recordings, and it cannot create, modify, or delete anything in your Zoom account.

---

## Part 1: Check Your Zoom Plan (2 minutes)

The attendance reports and cloud recordings we need require a paid Zoom plan.

1. Go to **zoom.us** and sign in
2. Click **Settings** (left sidebar) then **Billing**
3. Look for your plan name — it needs to say **Pro**, **Business**, or higher
4. If it says **Basic (Free)** — stop here. You need to upgrade to Pro first ($13.33/month). The API features we need are Pro-only.

**What this step accomplishes:** Confirms your Zoom account has the features zoom-connect needs. Without Pro, attendance data and cloud recordings simply aren't available through the API.

---

## Part 2: Turn On Cloud Recording (3 minutes)

Cloud recording tells Zoom to automatically save recordings, transcripts, and chat logs to the cloud after every meeting. Without this, there's nothing for the tools to download.

1. Still in zoom.us, go to **Settings** (left sidebar)
2. Click the **Recording** tab
3. Find **Cloud recording** and turn it **ON**
4. Under the cloud recording options, make sure these are checked:
   - [ ] **Record active speaker with shared screen**
   - [ ] **Save chat messages from the meeting/webinar** (this saves chat logs)
5. Scroll down and check **Audio transcript** is ON (this generates the VTT transcript files)
6. Click **Save** if prompted

**What this step accomplishes:** Enables the data pipeline. After each meeting, Zoom will automatically generate and store the recording, transcript, and chat log — making them available for download via the API.

---

## Part 3: Create the Zoom App (10 minutes)

This is the one-time setup that gives Claude permission to read your Zoom data.

1. Go to **marketplace.zoom.us**
2. Sign in with your Zoom account
3. Click **Develop** in the top menu, then **Build App**
4. You'll see app type options — choose **Server-to-Server OAuth**
5. Give it a name: **Zoom Connect** (or any name you like — this is just for your reference)
6. Click **Create**

You'll now see three values on the screen:

| Value | What It Is |
|-------|-----------|
| **Account ID** | Your Zoom account identifier — tells the API which account to connect to |
| **Client ID** | The app's public identifier — like a username for the app |
| **Client Secret** | The app's private key — like a password. Keep this secret. |

**Keep this page open.** You'll need these three values in Part 6.

**What this step accomplishes:** Creates the secure "bridge" between your machine and Zoom's servers. Server-to-Server OAuth is the simplest auth model — no redirect URLs, no consent screens, no token refresh to manage. You get three credentials and you're done forever.

---

## Part 4: Add All 16 Scopes (5 minutes)

Scopes tell Zoom exactly what the app is allowed to access. Each scope grants permission for one specific type of data. We need 16 of them to cover all the zoom-connect features.

Still on the marketplace.zoom.us app page:

1. Click the **Scopes** tab
2. Click **Add Scopes**
3. Add all 16 scopes listed below

**Meeting scopes (4)** — Let the app see your meeting list and details:

| Scope | What It Enables |
|-------|----------------|
| `meeting:read:list_meetings:admin` | List your upcoming meetings |
| `meeting:read:list_meetings:master` | Master-level meeting list access |
| `meeting:read:meeting:admin` | See individual meeting details |
| `meeting:read:past_meeting:admin` | See past meeting details (needed for attendance) |

**Report scopes (4)** — Let the app pull attendance and analytics:

| Scope | What It Enables |
|-------|----------------|
| `report:read:list_meeting_participants:admin` | Who joined, when, and how long they stayed |
| `report:read:user:admin` | List past meetings via the report endpoint |
| `report:read:chat_session:admin` | Chat session reports |
| `report:read:list_chat_sessions:admin` | List available chat sessions |

**Cloud recording scopes (6)** — Let the app access recordings, transcripts, and chat logs:

| Scope | What It Enables |
|-------|----------------|
| `cloud_recording:read:list_recording_files:admin` | List recording files for a meeting |
| `cloud_recording:read:recording:admin` | Download recording files |
| `cloud_recording:read:list_account_recordings:admin` | See all recordings on the account |
| `cloud_recording:read:recording_analytics_details:admin` | Recording analytics details |
| `cloud_recording:read:recording_analytics_summary:admin` | Recording analytics summary |
| `cloud_recording:read:registrant_status:admin` | Recording registrant data |

**User scopes (2)** — Let the app identify users on the account:

| Scope | What It Enables |
|-------|----------------|
| `user:read:list_users:admin` | List users on the account (useful for shared accounts) |
| `user:read:user:admin` | Get current user info (used by the connection test) |

**How to find them in the Zoom interface:** Use the search box. Search by category prefix — `meeting:read`, `report:read`, `cloud_recording:read`, `user:read` — and add all the `:admin` scopes listed above.

4. Click **Done** / **Save**

**What this step accomplishes:** Grants the minimum permissions needed for each zoom-connect feature. Every scope is read-only — none of them can modify or delete anything in your Zoom account.

---

## Part 5: Activate the App (1 minute)

1. Go to the **Activation** tab in your app settings
2. Click **Activate your app**
3. You should see a green checkmark

If activation fails, it usually means a required field is missing (like the app description or company name on the Information tab). Fill in whatever it asks for — these details don't affect functionality.

**What this step accomplishes:** Turns the app on. Until activated, the credentials won't work even if everything else is configured correctly.

---

## Part 6: Run Setup Script and Add Credentials (2 minutes)

Back in your terminal (Claude Code), tell Claude:

> "Run the zoom-connect setup script"

Claude will run `scripts/setup.sh` which creates a config file at `~/.config/zoom-connect.yaml` with a template.

Then tell Claude the three values from Part 3:

> "Here are my Zoom credentials — Account ID: [paste], Client ID: [paste], Client Secret: [paste]"

Claude will add them to the config file. Or you can open `~/.config/zoom-connect.yaml` in any text editor and paste them yourself under the `main` profile.

**What this step accomplishes:** Saves your credentials locally on your machine in a config file. The credentials never leave your computer — they're used to authenticate directly with Zoom's servers each time you run a command.

---

## Part 7: Test the Connection (1 minute)

Tell Claude:

> "Test the zoom-connect connection"

Claude will run `python3 tools/zoom_client.py --test` and you should see:

```
Connection successful!
  Account: Your Name
  Email: your@email.com
  Plan: Licensed (Pro)
  Scopes: 16
```

**Check these things:**
- **Plan** should show Licensed (Pro) or higher. If it shows Basic (Free), attendance reports won't work.
- **Scopes** should show 16. If it shows fewer, go back to Part 4 and add the missing ones.

To verify all scopes are correct: `python3 tools/zoom_client.py --scopes`

**If you see an error:**
- Double-check the three credentials match exactly what's on marketplace.zoom.us (no trailing spaces)
- Verify the app is activated (Part 5)
- Make sure you're using the right Zoom account (the one with the Pro plan)

---

## Part 8: Test With a Real Meeting (5 minutes)

Test with an actual past Zoom meeting. Any recent meeting works.

### 8a. Find a meeting

> "List my recent Zoom meetings"

You should see a list of your past meetings with IDs. Pick one and note the **Meeting ID**.

### 8b. Pull attendance

> "Get attendance for Zoom meeting [ID]"

You should see participant names, join/leave times, and duration. If the meeting ended less than 15 minutes ago, data may not be available yet.

### 8c. Check recordings

> "List recordings for Zoom meeting [ID]"

You should see recording files listed (MP4, TRANSCRIPT, CHAT, etc.). If cloud recording wasn't enabled for that meeting, there won't be any — it only works for meetings recorded after you turned it on in Part 2.

### 8d. Download a transcript (optional)

> "Download the transcript for Zoom meeting [ID]"

This saves the VTT transcript file to `~/Downloads/zoom-recordings/`.

---

## What Success Looks Like

After all eight parts, you should have:

- [ ] Zoom plan confirmed as Pro or higher
- [ ] Cloud recording + chat saving enabled
- [ ] S2S OAuth app created and activated with 16 scopes
- [ ] Credentials saved in `~/.config/zoom-connect.yaml`
- [ ] Connection test passes (shows 16 scopes)
- [ ] Real meeting data pulls successfully (attendance + recordings)

Once this works, every future meeting will have its data available for automated processing.

---

## Python Dependencies

The zoom-connect tools need two Python packages. If they're not already installed:

```bash
pip3 install requests pyyaml
```

Most systems already have these. If you get "ModuleNotFoundError: No module named 'requests'" when running a tool, this is the fix.

---

## Multiple Zoom Accounts

If you have more than one Zoom account (e.g., personal + team), you can add multiple profiles to the config:

```yaml
default_profile: "main"

profiles:
  main:
    account_id: "..."
    client_id: "..."
    client_secret: "..."
    user_email: "me"
    download_dir: "~/Downloads/zoom-recordings"
    timezone: "Australia/Melbourne"

  team:
    account_id: "..."
    client_id: "..."
    client_secret: "..."
    user_email: "team@yourcompany.com"
    download_dir: "~/Downloads/zoom-recordings"
    timezone: "US/Eastern"
```

Use `--profile main` or `--profile team` on any command to select which account.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Config file not found" | Run `scripts/setup.sh` then edit `~/.config/zoom-connect.yaml` |
| "OAuth token request failed" | Triple-check Account ID, Client ID, and Client Secret. Copy-paste fresh from marketplace.zoom.us |
| "Resource not found" | Meeting may not have ended yet, or the meeting ID is wrong |
| No attendance data | Wait 15 minutes after the meeting ends. Zoom needs processing time |
| No recordings listed | Cloud recording wasn't enabled for that meeting. Enable it now — it'll work for future meetings |
| Plan shows as "Basic" | You need to upgrade to Zoom Pro for attendance reports and cloud recordings |
| Scopes show fewer than 16 | Go back to marketplace.zoom.us and add the missing scopes from Part 4 |
| "ModuleNotFoundError" | Run `pip3 install requests pyyaml` |
| Attendance data expires | Zoom keeps attendance reports for 1 month only. Pull data promptly after sessions |

---

## Data Timing Reference

| Data | Available After Meeting Ends | Retention |
|------|------------------------------|-----------|
| Attendance (participants) | ~15 minutes | 1 month |
| Cloud recordings (video) | 1+ hours (processing time) | Until deleted |
| Chat logs | With cloud recording | Until deleted |
| Transcripts (VTT) | 30 min to 24+ hours (unpredictable) | Until deleted |

**Transcripts are the slowest.** Don't wait for them — check back later. Chat logs are usually available much faster.
