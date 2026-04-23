# Channel Adapters Registry

Channel adapters connect LibreFang agents to external messaging platforms. Each adapter in this directory is a flat `.toml` file describing the platform, its communication protocol, and any credentials required to operate.

Once a channel is configured, agents can receive messages from and send messages to that platform without any code changes — the adapter handles protocol translation.

## File Format

Each channel is a single `.toml` file. The filename (without `.toml`) must match the `id` field.

```toml
id = "telegram"
name = "Telegram"
description = "Telegram Bot API adapter for sending and receiving messages"
category = "messaging"             # messaging | enterprise | social | developer | iot
tags = ["popular"]
icon = "lucide:smartphone"
protocol = "bot-api"               # see Protocol Reference below

[i18n.zh]
name = "Telegram"
description = "Telegram Bot API 适配器，收发消息"

[metadata]
url = "https://telegram.org"
docs = "https://core.telegram.org/bots/api"
```

## Protocol Reference

| Protocol | Description |
|----------|-------------|
| `bot-api` | Platform-specific bot HTTP API (e.g. Telegram Bot API) |
| `websocket` | Long-lived WebSocket connection (e.g. Slack RTM, Discord Gateway) |
| `webhook` | Agent receives POST requests from the platform |
| `rest-api` | Polling or push via generic HTTP REST |
| `imap` | Email protocols (IMAP for receive, SMTP for send) |
| `irc` | Internet Relay Chat protocol |
| `matrix` | Matrix client-server API |
| `mqtt` | MQTT pub/sub protocol for IoT messaging |
| `xmpp` | Extensible Messaging and Presence Protocol |

## Configuring a Channel

```bash
# List all available channel adapters
librefang catalog channels

# Install a channel adapter
librefang channel install telegram

# Configure credentials for a channel
librefang channel configure telegram

# Attach a channel to an agent
librefang channel attach telegram --agent assistant

# List configured channels
librefang channel list

# Remove a channel
librefang channel remove telegram
```

## All Channel Adapters (45 total)

### Messaging

| ID | Name | Protocol | Description |
|----|------|----------|-------------|
| discord | Discord | websocket | Discord bot adapter for sending and receiving messages in Discord servers and channels |
| email | Email | imap | Email adapter for sending and receiving messages via SMTP and IMAP protocols |
| irc | IRC | irc | IRC adapter for connecting to Internet Relay Chat networks and channels |
| keybase | Keybase | rest-api | Keybase adapter for encrypted messaging via the Keybase chat API |
| line | LINE | webhook | LINE Messaging API adapter for sending and receiving messages on the LINE platform |
| matrix | Matrix | matrix | Matrix adapter for decentralized messaging via the Matrix client-server API |
| messenger | Facebook Messenger | webhook | Facebook Messenger adapter for sending and receiving messages via the Messenger Platform |
| nostr | Nostr | websocket | Nostr adapter for publishing and reading events on the Nostr decentralized protocol |
| qq | QQ | websocket | QQ bot adapter for messaging within Tencent QQ groups and channels |
| signal | Signal | rest-api | Signal adapter for secure end-to-end encrypted messaging via Signal CLI |
| telegram | Telegram | bot-api | Telegram Bot API adapter for sending and receiving messages |
| threema | Threema | rest-api | Threema Gateway adapter for secure messaging via the Threema platform |
| viber | Viber | webhook | Viber bot adapter for sending and receiving messages via the Viber Bot API |
| wechat | WeChat | rest-api | WeChat Official Account adapter for messaging on the WeChat platform |
| whatsapp | WhatsApp | rest-api | WhatsApp Business API adapter for sending and receiving messages on WhatsApp |
| xmpp | XMPP | xmpp | XMPP adapter for messaging via the Extensible Messaging and Presence Protocol |

### Enterprise

| ID | Name | Protocol | Description |
|----|------|----------|-------------|
| dingtalk | DingTalk | webhook | DingTalk bot adapter for sending messages to DingTalk groups and conversations |
| feishu | Feishu (Lark) | webhook | Feishu (Lark) bot adapter for messaging within the Feishu collaboration platform |
| flock | Flock | webhook | Flock bot adapter for team messaging and notifications in Flock workspaces |
| google_chat | Google Chat | webhook | Google Chat adapter for sending messages and cards to Google Workspace conversations |
| guilded | Guilded | websocket | Guilded bot adapter for messaging in Guilded servers and channels |
| mattermost | Mattermost | websocket | Mattermost adapter for team messaging and notifications in Mattermost workspaces |
| pumble | Pumble | webhook | Pumble adapter for team messaging and notifications in Pumble workspaces |
| rocketchat | Rocket.Chat | rest-api | Rocket.Chat adapter for messaging in self-hosted Rocket.Chat instances |
| slack | Slack | websocket | Slack bot adapter for sending and receiving messages in Slack workspaces |
| teams | Microsoft Teams | webhook | Microsoft Teams adapter for messaging and notifications in Teams channels |
| twist | Twist | rest-api | Twist adapter for async team communication in Twist workspaces |
| webex | Cisco Webex | webhook | Cisco Webex adapter for messaging and notifications in Webex spaces |
| wecom | WeCom (WeChat Work) | webhook | WeCom (WeChat Work) adapter for enterprise messaging within WeCom organizations |
| zulip | Zulip | rest-api | Zulip adapter for topic-based team messaging in Zulip organizations |

### Social

| ID | Name | Protocol | Description |
|----|------|----------|-------------|
| bluesky | Bluesky | rest-api | Bluesky AT Protocol adapter for posting and reading from the decentralized social network |
| linkedin | LinkedIn | rest-api | LinkedIn adapter for posting updates and messages via the LinkedIn API |
| mastodon | Mastodon | rest-api | Mastodon adapter for posting toots and reading timelines on Mastodon instances |
| reddit | Reddit | rest-api | Reddit adapter for posting and reading content via the Reddit API |
| twitch | Twitch | irc | Twitch adapter for reading and sending messages in Twitch stream chats |

### Developer

| ID | Name | Protocol | Description |
|----|------|----------|-------------|
| discourse | Discourse | rest-api | Discourse forum adapter for posting topics and replies via the Discourse API |
| gitter | Gitter | rest-api | Gitter adapter for developer chat rooms linked to GitHub repositories |
| revolt | Revolt | websocket | Revolt adapter for messaging in the open-source Revolt chat platform |
| webhook | Webhook | webhook | Generic webhook adapter for sending and receiving messages via HTTP callbacks |

### IoT / Self-Hosted

| ID | Name | Protocol | Description |
|----|------|----------|-------------|
| gotify | Gotify | rest-api | Gotify adapter for sending push notifications to a self-hosted Gotify server |
| mqtt | MQTT | mqtt | MQTT adapter for publishing and subscribing to messages on MQTT brokers |
| mumble | Mumble | websocket | Mumble adapter for text messaging in Mumble voice communication servers |
| nextcloud | Nextcloud Talk | rest-api | Nextcloud Talk adapter for messaging within self-hosted Nextcloud instances |
| ntfy | ntfy | rest-api | ntfy adapter for sending push notifications via the ntfy pub-sub service |

## Adding a New Channel Adapter

1. Create `channels/<name>.toml` — the filename must match the `id` field.
2. Set `category` to one of: `messaging`, `enterprise`, `social`, `developer`, `iot`.
3. Set `protocol` to the appropriate value from the Protocol Reference table above.
4. Add `[metadata]` with `url` and `docs` links.
5. Add `[i18n.*]` blocks for supported locales.
6. Run `python scripts/validate.py`.
7. Submit a PR.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full guide.
