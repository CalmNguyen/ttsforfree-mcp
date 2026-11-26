---
name: ttsforfree
description: Generate natural AI speech with TTSForFree - narration, multi-voice podcasts and timeline-synced voiceovers for video editing (SRT/WebVTT to speech, dubbing, translated subtitles), using the user's favorite and custom (cloned/designed) voices. Use when the user wants text read aloud, an MP3 voiceover, a podcast, to dub or voice over a video, or to add audio to subtitles.
---

# TTSForFree text-to-speech

TTSForFree turns text into speech with thousands of AI voices in 100+ languages and returns hosted MP3 URLs.
Two ways to reach it - prefer the first that is available:

1. **MCP tools** (connector `https://api.ttsforfree.com/mcp`): `list_voices`, `list_favorite_voices`, `list_my_custom_voices`,
   `get_voice_details`, `text_to_speech`, `multi_voice_to_speech`, `srt_to_speech`, `get_job_status`, `get_job_detail`,
   `list_recent_jobs`, `get_account_status`, `design_custom_voice`, `add_favorite_voice`, `remove_favorite_voice`, `list_languages`,
   and for media files `create_upload_url`, `transcribe_media`, `get_transcription`, `estimate_video_localization`,
   `localize_video`, `get_localization_status`.
   If a tool answers "Sign-in required", ask the user to open Settings > Connectors > TTSForFree and click Connect
   (OAuth sign-in with their TTSForFree account, no API key). In Claude Code: `/mcp` > ttsforfree > Authenticate.
2. **REST API** with `scripts/ttsforfree.py` (Python 3 stdlib only) and the key in env `TTSFORFREE_API_KEY`.
   Never print, hard-code or commit the key. Get one at https://ttsforfree.com/en/profile/ (API Key).

## Rules

1. **Voice first.** If the user did not name a voice: favorites → custom voices → `list_voices(language, query=...)`.
   Tell the user which voice you picked and why (gender, accent, style). Pass the exact `voice` token (`v1:...`); never build or edit it.
2. **Pick the tool by who owns the timeline.**
   - `text_to_speech` - one voice; audio length can follow the speech (narration, article, lesson, new video whose scenes follow the audio).
   - `multi_voice_to_speech` - several speakers in order, no fixed timestamps (podcast, dialogue, interview, audio drama).
   - `srt_to_speech` - an existing video/subtitle timeline must be kept (voiceover, dubbing, translated subtitles, tutorials).
3. **Jobs are asynchronous.** A `PENDING` result is normal: call `get_job_status` with the same `job_id` and `job_type`.
   Never create the same job twice, never invent an `audio_url`, never download before `SUCCESS`.
4. **Credits are real money.** For long scripts (> ~5,000 characters) or many cues, call `get_account_status` first and tell the user the size.
   On a retry, check `list_recent_jobs` before creating a new job. On 429, wait and retry later instead of looping.
5. **Report errors verbatim** and suggest the fix (different voice, shorter text, upgrade link from `get_account_status`).
6. **Respect consent.** Only clone voices the user has the right to use; `design_custom_voice` uses a quota slot - confirm first.

## Video and audio files

- Only files uploaded to TTSForFree are processed. **Never try to download from YouTube or other sites**; ask the user for the original file
  (creators can download their own videos from YouTube Studio).
- `create_upload_url(file_name)` → `curl -sS --fail -T <file> "<upload_url>"` (expires in 15 min) → use `public_url`.
  If you cannot run commands, ask the user to upload on https://ttsforfree.com/en/video-localization/ and paste the file link.
  If the upload or a download fails with "Could not resolve host", "blocked by network policy" or 403 on
  `*.r2.cloudflarestorage.com` / `cdn.ttsforfree.com`, your environment limits network access. Ask the user to allow
  `ttsforfree.com`, `*.ttsforfree.com` and `*.r2.cloudflarestorage.com`, then retry with the same file:
  normal chat on claude.ai: Settings → Capabilities → turn on Allow network egress → Additional allowed domains;
  Claude Code: conversation menu → Edit cloud environment → Network access → Allowed domains.
  Do not guess the content of a file you could not upload. Guide: https://ttsforfree.com/en/claude-tts-connector/#network-allowlist
- `transcribe_media(media_url, language)` → SRT with timestamps (billed per second, measured by the server).
- **Many languages at once (YouTube multi-language audio):** `estimate_video_localization` → confirm the credits → one
  `localize_video(video_url, source_language, targets=[{language, voice}, ...])` → poll `get_localization_status(job_guids)`.
  Each language returns `audio_url` (upload in YouTube Studio → Languages → Add dub), `final_video_url` and `translated_srt_url`.
- Remotion / captions: after `multi_voice_to_speech` or `srt_to_speech`, `get_job_detail(job_id)` lists every segment's audio URL.

## Writing good subtitles for `srt_to_speech`

- One sentence (or clause) per cue. Keep cue duration ≥ characters / 15 seconds; otherwise split the text or extend the cue.
- Keep gaps between cues for breaths (≥ 150 ms). Never overlap cues.
- When translating, keep every start/end time and adapt wording to fit the duration (target languages are often longer than English).
- Multiple speakers: prefix cue text with `[Name]` or `Name:` and pass `speaker_voices: {"Name": "v1:..."}`; set `voice` as the default.
- `min_speech_rate` / `max_speech_rate` (default 0.95 / 1.5) bound the auto-fit speed; set both equal for a fixed speed.

## Video editing workflow (automatic voiceover)

1. Get the timeline: existing SRT/VTT, a transcript with timestamps, or write cues from the script and scene lengths.
2. (Optional) translate the cues, keeping times.
3. `srt_to_speech` with the SRT text → wait for `SUCCESS` → `audio_url`. The MP3 starts at 00:00 of the video timeline.
4. Merge with ffmpeg (the tool result's `video_merge` field has the same commands):

```bash
curl -L -o voiceover.mp3 "$AUDIO_URL"
# replace the original audio
ffmpeg -i input.mp4 -i voiceover.mp3 -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -af apad -shortest output.mp4
# or keep music/effects under the voice (original at 20%)
ffmpeg -i input.mp4 -i voiceover.mp3 -filter_complex "[0:a]volume=0.2[bg];[1:a]volume=1.0[vo];[bg][vo]amix=inputs=2:duration=first:dropout_transition=0[a]" -map 0:v:0 -map "[a]" -c:v copy -c:a aac -b:a 192k output.mp4
# optional: burn subtitles
ffmpeg -i output.mp4 -vf subtitles=subtitles.srt -c:a copy output_subtitled.mp4
```

For a **new** video from a script: generate audio first (`text_to_speech` or `multi_voice_to_speech`), measure its duration
(`ffprobe -v error -show_entries format=duration -of csv=p=0 voiceover.mp3`), then size scenes to the audio.

Save `job_id`s with the project. When the user edits a few lines, re-render only those cues instead of the whole video.

## REST fallback (no MCP connector)

```bash
export TTSFORFREE_API_KEY=...            # ask the user to set it; never echo it
python3 scripts/ttsforfree.py voices --language en --query narrator
python3 scripts/ttsforfree.py favorites
python3 scripts/ttsforfree.py tts --voice "v1:..." --text "Hello world" --out hello.mp3
python3 scripts/ttsforfree.py srt --voice "v1:..." --srt subtitles.srt --out voiceover.mp3
python3 scripts/ttsforfree.py mux --video input.mp4 --audio voiceover.mp3 --out output.mp4 [--keep-original 0.2]
python3 scripts/ttsforfree.py upload --file input.mp4                       # prints the public URL
python3 scripts/ttsforfree.py transcribe --file input.mp4 --language vi --out input.srt
python3 scripts/ttsforfree.py localize --file input.mp4 --source vi --target "en=v1:..." --target "ja=v1:..."
```

REST endpoints (header `X-API-Key`): `GET /api/Common/GetListVoice?lang=en`, `GET /api/FavoriteVoices/GetMyFavorites`,
`GET /api/CustomVoices/GetMyVoices`, `POST /api/TTS/CreateBy`, `POST /api/TTS/CreateMulti`, `POST /api/TTS/CreateSrt`,
`GET /api/TTS/Status/{id}`, `GET /api/TTS/Multi/Status/{id}`, `POST /api/uploads/request-presigned`, `POST /api/Stt/ConvertLinkMp3ToSrt`,
`GET /api/Stt/Get/{id}`, `POST /api/video-localization`, `GET /api/video-localization/{jobGuid}`. Full docs: https://ttsforfree.com/en/docs/
