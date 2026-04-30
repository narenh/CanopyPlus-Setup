<h1>
  <img src="assets/cplus-logo-sq.png" alt="Canopy+ Logo" height="24" style="vertical-align: middle;" />
  Canopy+
</h1>

A Plex frontend for tvOS, human-written* in SwiftUI. Meant for integrating with CoreELEC (Ugoos AM6B+) or Nvidia Shield.

<p align="center">
  <img src="assets/hero.jpg" alt="Canopy+" width="800" />
</p>

## Download

<a href='https://apps.apple.com/us/app/canopy/id6742864890'><img height='60' alt='Download on the App Store' src='assets/app-store-badge.png'/></a>


## Setup Instructions

### Login
- Login with the same Plex account that you use to sign in on your Apple TV. This is required for deeplinking to function.
- Supports standard accounts and managed Home users, along with PIN enforcement.

### External Player Integration
- Home Assistant (HASS) HIGHLY recommended. This will allow you to tweak things based on your own setup.
#### Nvidia Shield
- This one's by far the easiest. 
- HASS → Install Android Debug Bridge
- HASS → Settings → Automations → Create Automation From Scratch. 
- Add trigger → Webhook (can customize this if you'd like)
- Under "Then do", wake up your shield, Delay for 3 seconds, then run this ADB command: 
```am start --ez "android.intent.extra.START_PLAYBACK" '{{
    trigger.json.startPlaying }}' -a android.intent.action.VIEW
    'plex://server://{{ trigger.json.serverId
    }}/com.plexapp.plugins.library/library/metadata/{{ trigger.json.ratingKey
    }}'
```
- Get the full webhook URL. Generally will be http://[HASS_HOST]:[HASS_PORT]/api/webhook/[WEBHOOK_ID]
- Copy the URL on your iPhone, open Canopy+ → Settings → External Player → and paste the URL into the URL field.


### AI Disclosure
- Canopy+ is almost entirely human-coded with one major exception: the schema, networking, and data models for Plex's Discover and Metadata endpoints.
- All UI and app logic is human-written.