---
name: stickman-short
description: Make a narrated stick-figure animated Short (9:16 MP4) from an idea, a script or existing audio. Writes a viral-style script, voices it with TTSForFree (budget Azure, hybrid or Gemini voices), lays out scenes as JSON and renders the animation with Remotion. Use when the user asks for a stickman / stick figure / cartoon Short, TikTok or Reel, or a story/explainer animation with voiceover.
---

# Stickman Short

Turn an idea into a finished vertical video: script → voice (TTSForFree) → `story.json` → Remotion render.
Everything is drawn in code (stick figures, props, backgrounds), so characters look the same in every scene and a re-render costs nothing.

## Needs

- **TTSForFree** for the voice: the TTSForFree connector in Claude (`https://api.ttsforfree.com/mcp`, no key needed), or an API key from ttsforfree.com/en/profile (env `TTSFORFREE_API_KEY`).
- **Rendering** needs Node 18+ and a folder you can run commands in (Claude Code, Claude Desktop with a local folder, or the user's own terminal). In a chat without code execution, produce `story.json` + audio and give the user the three commands from step 6.

## Workflow

1. **Ask where we start** (one question, offer choices): ideas from scratch / I have a script / I have audio. Then length: 15–25 s, 25–40 s, 40–60 s. Then the use case (see `references/use-cases.md`): history twist, motivation, fight / action, what-if science, storytime, psychology tip, or "surprise me".
2. **Ideas**: give 10 numbered ideas for the chosen use case. Each = a one-line hook that creates a question in the first 2 seconds. Prefer true, checkable facts for history / science; say so if a famous story is disputed and tell the honest version.
3. **Script**: one short sentence per scene (5–14 words), 6–12 scenes. Structure: hook (scene 1–2) → setup → escalation → twist → one-line CTA. Show the script and let the user edit it.
4. **Voice tier** (show the cost from `references/voices.md` before generating):
   - *budget*: one Azure Natural voice (0.5 credit / character): ~100–200 credits per Short.
   - *hybrid*: Gemini voice for the hook and the twist, Azure for the rest: ~1,000–1,500 credits.
   - *premium*: Gemini voice for every scene (8 credits / character): ~4,000+ credits for 45 s.
   Ask for favorite voices first if the connector is available (`list_favorite_voices`), otherwise suggest from `references/voices.md`.
5. **story.json**: write `template/story.json` following `references/schema.md`: one scene per sentence with background, actors (pose, position, expression, hat, color, prop), props, effects, camera, optional speech bubble or big number. Vary the camera and poses scene to scene; put the big reveal on a `bigText` + `flash` or `shake` scene.
6. **Voice + render** (in `template/`):
   ```bash
   npm install
   TTSFORFREE_API_KEY=... node scripts/voice.mjs story.json     # one TTS block per scene, downloads public/audio/*
   npx remotion render short out/short.mp4
   ```
   With the connector instead of a key: call `multi_voice_to_speech` with one segment per scene (`pause_after_ms: 0`), then `get_job_detail` and download each block's audio into `public/audio/`; set every scene's `narration.file` (`audio/<name>.mp3`) and `narration.durationSec` (ffprobe), then render.
7. **Deliver** the MP4 path, total credits used, and 2–3 title + hashtag ideas.

## Rules

- Caption text = the narration sentence; mark 1–2 key words per scene in `highlight`.
- Keep characters consistent: same `hat` and `color` for the same actor in every scene.
- Never claim one voice "sounds best"; offer a 3-voice preview when the user is unsure.
- No copyrighted characters, logos or real people's likeness beyond a plain stick figure with a hat.
