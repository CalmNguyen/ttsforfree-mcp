# TTSForFree MCP server

Text-to-speech, multi-voice podcasts, subtitle voiceovers, transcription and video dubbing for Claude and any
other MCP client. Thousands of AI voices in 100+ languages, returned as hosted MP3 URLs.

**[➕ Add to Claude](https://claude.ai/customize/connectors?modal=add-custom-connector&connectorName=TTSForFree&connectorUrl=https%3A%2F%2Fapi.ttsforfree.com%2Fmcp)** · **[Install in VS Code](https://vscode.dev/redirect?url=vscode%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522ttsforfree%2522%252C%2522type%2522%253A%2522http%2522%252C%2522url%2522%253A%2522https%253A%252F%252Fapi.ttsforfree.com%252Fmcp%2522%257D)** · [Claude Code plugin](#claude-code-plugin-mcp--skills)

- **Server URL:** `https://api.ttsforfree.com/mcp` (Streamable HTTP, remote, nothing to install)
- **Sign-in:** OAuth. Click *Connect* and sign in to TTSForFree. No API key needed. An API key (`X-API-Key` header) also
  works for scripts and agents.
- **Registry:** [`io.github.CalmNguyen/ttsforfree`](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.CalmNguyen/ttsforfree)
- **Website:** [ttsforfree.com](https://ttsforfree.com/?utm_source=github&utm_medium=readme&utm_campaign=ttsforfree-mcp) · setup guide:
  [ttsforfree.com/en/claude-tts-connector](https://ttsforfree.com/en/claude-tts-connector/?utm_source=github&utm_medium=readme&utm_campaign=ttsforfree-mcp)

A free plan is included. Paid generation uses your TTSForFree credits.

## Connect

### Claude (claude.ai, Desktop, mobile)

**One click:** [Add to Claude](https://claude.ai/customize/connectors?modal=add-custom-connector&connectorName=TTSForFree&connectorUrl=https%3A%2F%2Fapi.ttsforfree.com%2Fmcp) opens Claude's *Add custom connector* dialog with the name and URL filled in.
Confirm, then click **Connect**, sign in to TTSForFree and allow access.

- Free plan: Claude allows one custom connector.
- Team / Enterprise: an Owner adds it once for the organization with
  [this admin link](https://claude.ai/admin-settings/connectors?modal=add-custom-connector&connectorName=TTSForFree&connectorUrl=https%3A%2F%2Fapi.ttsforfree.com%2Fmcp); members then click **Connect**.

Manual setup, if the link does not open:

1. **Settings → Connectors → Add custom connector**
2. URL: `https://api.ttsforfree.com/mcp`
3. Click **Connect**, sign in to TTSForFree and allow access.

### Claude Code

#### Claude Code plugin (MCP + skills)

This repository is also a Claude Code plugin marketplace. The `ttsforfree` plugin adds the MCP connector and the
`ttsforfree` skill (voice choice, SRT timing and ffmpeg merge rules), so Claude knows how to use the tools well.

```bash
claude plugin marketplace add CalmNguyen/ttsforfree-mcp
claude plugin install ttsforfree@ttsforfree
```

Then run `/mcp` → `plugin:ttsforfree:ttsforfree` → **Authenticate**. Optional: `claude plugin install stickman-short@ttsforfree`
adds a skill that turns an idea into a narrated stick-figure Short (9:16 MP4) rendered with Remotion.

#### MCP server only

```bash
claude mcp add --transport http ttsforfree https://api.ttsforfree.com/mcp
```

Then run `/mcp` → `ttsforfree` → **Authenticate**. With an API key instead:

```bash
claude mcp add --transport http ttsforfree https://api.ttsforfree.com/mcp \
  --header "X-API-Key: YOUR_API_KEY"
```

### Cursor, VS Code and other clients

VS Code: [Install in VS Code](https://vscode.dev/redirect?url=vscode%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522ttsforfree%2522%252C%2522type%2522%253A%2522http%2522%252C%2522url%2522%253A%2522https%253A%252F%252Fapi.ttsforfree.com%252Fmcp%2522%257D), or run

```bash
code --add-mcp '{"name":"ttsforfree","type":"http","url":"https://api.ttsforfree.com/mcp"}'
```

Cursor and other clients: add this to the client's MCP config.

```json
{
  "mcpServers": {
    "ttsforfree": {
      "url": "https://api.ttsforfree.com/mcp"
    }
  }
}
```

Add `"headers": { "X-API-Key": "YOUR_API_KEY" }` if the client does not support OAuth.
Get an API key at [ttsforfree.com/en/profile](https://ttsforfree.com/en/profile/?utm_source=github&utm_medium=readme&utm_campaign=ttsforfree-mcp).

### Claude API (MCP connector)

```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: mcp-client-2025-11-20" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-opus-5-5",
    "max_tokens": 2048,
    "mcp_servers": [{
      "type": "url",
      "name": "ttsforfree",
      "url": "https://api.ttsforfree.com/mcp",
      "authorization_token": "YOUR_TTSFORFREE_API_KEY"
    }],
    "tools": [{ "type": "mcp_toolset", "mcp_server_name": "ttsforfree" }],
    "messages": [{ "role": "user", "content": "Read this in a warm British voice: Welcome to our channel!" }]
  }'
```

## What you can ask

| Ask Claude | Tools it uses |
|---|---|
| "Read this lesson in a calm British voice from my favorites." | `list_favorite_voices` → `text_to_speech` |
| "Turn this article into a 2-host podcast, one MP3." | `multi_voice_to_speech` → `get_job_detail` |
| "Translate this SRT to Spanish, keep the timestamps, voice it, give me the ffmpeg command." | `srt_to_speech` → `get_job_status` |
| "Transcribe this video into an SRT file." | `create_upload_url` → `transcribe_media` |
| "Dub this video into Vietnamese, Spanish and Japanese for YouTube. Cost first." | `create_upload_url` → `estimate_video_localization` → `localize_video` → `get_localization_status` |
| "Make me a young male voice that reviews stories, southern Vietnamese accent." | `design_custom_voice` |

Video walkthroughs: [ttsforfree.com/en/claude-tts-connector](https://ttsforfree.com/en/claude-tts-connector/?utm_source=github&utm_medium=readme&utm_campaign=ttsforfree-mcp).

## Tools (21)

| Tool | Type | What it does |
|---|---|---|
| `list_languages` | read | All supported languages and their codes. |
| `list_voices` | read | Search voices by language, gender, provider and keywords ("warm narrator"). |
| `get_voice_details` | read | Persona, use case, accent, styles, preview audio and credit cost of one voice. |
| `list_favorite_voices` | read | The user's favorite voices, in saved order. |
| `list_my_custom_voices` | read | Personal voices from Voice Design / Voice Clone and the remaining quota. |
| `add_favorite_voice` | write | Save a voice to favorites. |
| `remove_favorite_voice` | write | Remove a voice from favorites. |
| `design_custom_voice` | write | Create a new personal voice from a text description. |
| `get_account_status` | read | Plan, remaining credits, per-request limits and API rate limits. |
| `text_to_speech` | job | One text + one voice → MP3 (narration, articles, lessons). |
| `multi_voice_to_speech` | job | Ordered segments with different voices → one MP3 (podcast, dialogue). |
| `srt_to_speech` | job | SRT/WebVTT or timed segments → timeline-aligned MP3 + ffmpeg merge commands. |
| `get_job_status` | read | Poll a job until SUCCESS and get the audio URL. |
| `list_recent_jobs` | read | Recent jobs with audio URLs, to reuse instead of paying twice. |
| `get_job_detail` | read | Per-segment audio of a multi-voice/SRT job (for Remotion and captions). |
| `create_upload_url` | write | One-time upload URL for a local video/audio file (PUT, up to 2 GB). |
| `transcribe_media` | job | Video/audio → timestamped SRT (speech-to-text). |
| `get_transcription` | read | Status and SRT of a transcription. |
| `estimate_video_localization` | read | Credit estimate to dub a video into several languages. |
| `localize_video` | job | Dub one video into many languages: audio track + dubbed video per language. |
| `get_localization_status` | read | Progress and results (audio URL for YouTube, dubbed video, SRT) per language. |

`job` tools are asynchronous: they return a `job_id`, and the client polls the matching status tool until `SUCCESS`.

**Prompts:** `youtube_multi_language_audio`, `video_voiceover`, `podcast_episode`, `narrate_text`.

## Privacy and data

- OAuth access is scoped to your TTSForFree account and can be revoked any time from your TTSForFree profile
  (Connected apps).
- Text, subtitles and uploaded media are processed only to produce the audio, subtitles or video you asked for.
- Privacy policy: [ttsforfree.com/en/privacy-policy](https://ttsforfree.com/en/privacy-policy/?utm_source=github&utm_medium=readme&utm_campaign=ttsforfree-mcp)

## Support

Open an issue in this repository or contact us via [ttsforfree.com/en/contact](https://ttsforfree.com/en/contact/?utm_source=github&utm_medium=readme&utm_campaign=ttsforfree-mcp).

## Repository layout

| Path | What it is |
|---|---|
| [`server.json`](server.json) | Entry published to the MCP Registry |
| [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) | Claude Code plugin marketplace (`ttsforfree`) |
| [`plugins/ttsforfree`](plugins/ttsforfree) | Plugin: MCP connector (`.mcp.json`) + `ttsforfree` skill |
| [`plugins/stickman-short`](plugins/stickman-short) | Plugin: `stickman-short` skill (Remotion template) |

The skills are copies of the downloads on ttsforfree.com (`/claude/ttsforfree-skill.zip`,
`/downloads/stickman-short-skill.zip`); update both places together. Check changes with `claude plugin validate .`.

## Registry metadata

[`server.json`](server.json) is the entry published to the
[MCP Registry](https://registry.modelcontextprotocol.io). To publish an update, bump `version` in `server.json`
and push a tag `vX.Y.Z` (or run the *Publish to MCP Registry* workflow manually). The workflow signs in with
GitHub OIDC, so no secret is needed.
