#!/usr/bin/env python3
"""TTSForFree REST helper for Claude skills (stdlib only).

Reads the API key from the TTSFORFREE_API_KEY environment variable.
Commands: voices, favorites, custom, tts, srt, status, mux, upload, transcribe, localize. Run with -h for options.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = os.environ.get("TTSFORFREE_API_BASE", "https://api.ttsforfree.com")
POLL_SECONDS = 5
TIMEOUT_SECONDS = 15 * 60
TIMING = re.compile(r"((?:\d{1,2}:)?\d{1,2}:\d{1,2}(?:[.,]\d{1,3})?)\s*-->\s*((?:\d{1,2}:)?\d{1,2}:\d{1,2}(?:[.,]\d{1,3})?)")


def die(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def api_key():
    key = os.environ.get("TTSFORFREE_API_KEY", "").strip()
    if not key:
        die("set TTSFORFREE_API_KEY (get a key at https://ttsforfree.com/en/profile/)")
    return key


def request(method, path, body=None, retries=4):
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"X-API-Key": api_key(), "Accept": "application/json", "User-Agent": "ttsforfree-claude-skill/1.0"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    for attempt in range(retries + 1):
        req = urllib.request.Request(API + path, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                text = resp.read().decode("utf-8")
                return json.loads(text) if text else {}
        except urllib.error.HTTPError as err:
            detail = err.read().decode("utf-8", "replace")[:300]
            if err.code == 429 or err.code >= 500:
                if attempt < retries:
                    wait = int(err.headers.get("Retry-After") or 0) or min(60, 2 ** (attempt + 2))
                    print(f"HTTP {err.code}, retrying in {wait}s: {detail}", file=sys.stderr)
                    time.sleep(wait)
                    continue
            die(f"HTTP {err.code}: {detail}")
        except urllib.error.URLError as err:
            if attempt < retries:
                time.sleep(2 ** (attempt + 1))
                continue
            die(f"network error: {err.reason}")
    die("request failed")


def parse_ms(value):
    parts = value.replace(",", ".").split(":")
    hours = int(parts[0]) if len(parts) == 3 else 0
    minutes = int(parts[-2])
    seconds = float(parts[-1])
    return int(round(((hours * 60 + minutes) * 60 + seconds) * 1000))


def parse_srt(path):
    lines = open(path, encoding="utf-8-sig").read().replace("\r\n", "\n").split("\n")
    cues, i = [], 0
    while i < len(lines):
        match = TIMING.search(lines[i])
        if not match:
            i += 1
            continue
        text, j = [], i + 1
        while j < len(lines) and lines[j].strip() and not TIMING.search(lines[j]):
            text.append(lines[j].strip())
            j += 1
        if j < len(lines) and TIMING.search(lines[j]) and text and text[-1].isdigit():
            text.pop()
        clean = re.sub(r"\s+", " ", re.sub(r"<[^>]+>|\{\\[^}]*\}", " ", " ".join(text))).strip()
        start, end = parse_ms(match.group(1)), parse_ms(match.group(2))
        if clean and end > start:
            cues.append({"text": clean, "start": start, "end": end})
        i = j
    return cues


def wait_for(job_id, multi):
    path = f"/api/TTS/Multi/Status/{job_id}" if multi else f"/api/TTS/Status/{job_id}"
    deadline = time.time() + TIMEOUT_SECONDS
    while time.time() < deadline:
        status = request("GET", path)
        state = str(status.get("Status") or "").upper()
        if state == "SUCCESS":
            return status.get("Data") or status.get("ExpectUrl")
        if state == "ERROR":
            die(f"job {job_id} failed: {status.get('Message')}")
        print(f"job {job_id}: {state or 'PENDING'}...", file=sys.stderr)
        time.sleep(POLL_SECONDS)
    die(f"job {job_id} still rendering; run: ttsforfree.py status --id {job_id}{' --multi' if multi else ''}")


def download(url, out):
    if not out:
        return
    with urllib.request.urlopen(url, timeout=120) as resp, open(out, "wb") as fh:
        shutil.copyfileobj(resp, fh)
    print(f"saved {out}", file=sys.stderr)


def finish(created, multi, out):
    job_id = created.get("Id")
    if not isinstance(job_id, int) or job_id <= 0:
        die(created.get("Message") or "job was not created")
    print(f"job_id={job_id}", file=sys.stderr)
    url = created.get("Data") if str(created.get("Status") or "").upper() == "SUCCESS" else wait_for(job_id, multi)
    print(url)
    download(url, out)


def cmd_voices(args):
    query = urllib.parse.urlencode({"lang": args.language, "provider": args.provider or ""})
    voices = request("GET", f"/api/Common/GetListVoice?{query}&details={'true' if args.query else 'false'}").get("Data") or []
    terms = [t.lower() for t in (args.query or "").split()]
    rows = []
    for v in voices:
        if args.gender and str(v.get("Gender", "")).lower() != args.gender:
            continue
        haystack = " ".join(str(v.get(k) or "") for k in ("FreindlyName", "StyleList", "VoicePersonalities", "Persona", "UseCase", "Description")).lower()
        if terms and not any(t in haystack for t in terms):
            continue
        if v.get("CanUse") is False and not args.all:
            continue
        rows.append({"voice": v.get("VoiceName"), "name": v.get("FreindlyName"), "gender": v.get("Gender"), "locale": v.get("Locale"), "credits_per_char": v.get("BaseCreditsPerCharacter")})
    print(json.dumps(rows[: args.limit], ensure_ascii=False, indent=2))


def cmd_favorites(_):
    data = request("GET", "/api/FavoriteVoices/GetMyFavorites").get("Data") or []
    print(json.dumps([{"voice": f.get("Voice"), "name": f.get("FriendlyName"), "language": f.get("LanguageCode")} for f in data], ensure_ascii=False, indent=2))


def cmd_custom(_):
    data = request("GET", "/api/CustomVoices/GetMyVoices").get("Data") or {}
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_tts(args):
    text = open(args.text_file, encoding="utf-8").read() if args.text_file else args.text
    if not text:
        die("--text or --text-file is required")
    finish(request("POST", "/api/TTS/CreateBy", {"Texts": text, "Voice": args.voice, "Pitch": 0}), False, args.out)


def cmd_srt(args):
    cues = parse_srt(args.srt)
    if not cues:
        die("no cues found in the SRT file")
    blocks = [{"Texts": c["text"], "Voice": args.voice, "Volume": 1, "Speed": 1, "Pitch": 0, "StartMs": c["start"], "EndMs": c["end"]} for c in cues]
    body = {"ConnectionId": f"skill-{int(time.time())}", "MinSpeechRate": args.min_rate, "MaxSpeechRate": args.max_rate, "Blocks": blocks}
    print(f"{len(blocks)} cues, {sum(len(c['text']) for c in cues)} characters", file=sys.stderr)
    finish(request("POST", "/api/TTS/CreateSrt", body), True, args.out)


def cmd_status(args):
    url = wait_for(args.id, args.multi)
    print(url)
    download(url, args.out)


def upload_file(path):
    name = os.path.basename(path)
    size = os.path.getsize(path)
    category = "tts" if name.lower().endswith((".mp4", ".mov", ".webm", ".mkv", ".m4v")) else "mp3"
    presigned = request("POST", "/api/uploads/request-presigned", {"category": category, "files": [{"fileName": name, "contentType": "application/octet-stream", "fileSize": size}]})
    item = presigned[0]
    with open(path, "rb") as fh:
        req = urllib.request.Request(item["UploadUrl"], data=fh, method="PUT", headers={"Content-Length": str(size)})
        with urllib.request.urlopen(req, timeout=600) as resp:
            if resp.status >= 300:
                die(f"upload failed: HTTP {resp.status}")
    print(f"uploaded {name} ({size} bytes)", file=sys.stderr)
    return item["PublicUrl"]


def cmd_upload(args):
    print(upload_file(args.file))


def cmd_transcribe(args):
    url = args.url or upload_file(args.file)
    # Với API key, server tự đo thời lượng; Duration chỉ để qua validate.
    created = request("POST", "/api/Stt/ConvertLinkMp3ToSrt", {"FileUrl": url, "Duration": 1, "SourceLang": args.language, "ConnectionId": "skill"})
    job_id = created.get("Id")
    if not isinstance(job_id, int) or job_id <= 0:
        die(created.get("Message") or "transcription was not created")
    deadline = time.time() + TIMEOUT_SECONDS
    while time.time() < deadline:
        detail = request("GET", f"/api/Stt/Get/{job_id}") or {}
        status = (detail.get("jobInfo") or {}).get("StatusId")
        if status == 200:
            srt = detail.get("srtContent") or ""
            if args.out:
                open(args.out, "w", encoding="utf-8").write(srt)
                print(f"saved {args.out}", file=sys.stderr)
            else:
                print(srt)
            return
        if status == -100:
            die(f"transcription {job_id} failed")
        print(f"transcription {job_id}: processing...", file=sys.stderr)
        time.sleep(POLL_SECONDS)
    die(f"transcription {job_id} still running")


def cmd_localize(args):
    url = args.video_url or upload_file(args.file)
    targets = []
    for item in args.target:
        language, _, voice = item.partition("=")
        if not language or not voice.startswith("v1:"):
            die(f"--target must look like en=v1:..., got {item}")
        targets.append({"targetLanguage": language, "voiceId": voice})
    body = {"sourceVideoUrl": url, "sourceLanguage": args.source, "targets": targets, "connectId": "skill", "sourceDurationSeconds": 1}
    if args.keep_original is not None:
        body["originalAudioVolumePercent"] = int(args.keep_original)
    created = request("POST", "/api/video-localization", body)
    data = created.get("Data") or {}
    jobs = data.get("jobs") or ([{"jobGuid": data.get("jobGuid"), "targetLanguage": targets[0]["targetLanguage"]}] if data.get("jobGuid") else [])
    if not jobs:
        die(created.get("Message") or "dubbing job was not created")
    pending = {j["jobGuid"]: j["targetLanguage"] for j in jobs}
    results = []
    deadline = time.time() + 3 * TIMEOUT_SECONDS
    while pending and time.time() < deadline:
        for guid in list(pending):
            status = (request("GET", f"/api/video-localization/{guid}").get("Data") or {})
            state = status.get("status")
            if state in ("Completed", "Failed"):
                results.append({"language": pending.pop(guid), "status": state, "audio_url": status.get("audioUrl"), "video_url": status.get("finalVideoUrl"), "srt_url": status.get("translatedSrtUrl"), "error": status.get("errorMessage")})
        if pending:
            print(f"dubbing: {len(pending)} language(s) still processing...", file=sys.stderr)
            time.sleep(POLL_SECONDS * 3)
    print(json.dumps({"done": results, "still_processing": list(pending)}, ensure_ascii=False, indent=2))


def cmd_mux(args):
    if not shutil.which("ffmpeg"):
        die("ffmpeg is not installed")
    if args.keep_original is None:
        cmd = ["ffmpeg", "-y", "-i", args.video, "-i", args.audio, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-af", "apad", "-shortest", args.out]
    else:
        mix = f"[0:a]volume={args.keep_original}[bg];[1:a]volume=1.0[vo];[bg][vo]amix=inputs=2:duration=first:dropout_transition=0[a]"
        cmd = ["ffmpeg", "-y", "-i", args.video, "-i", args.audio, "-filter_complex", mix, "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", args.out]
    subprocess.run(cmd, check=True)
    print(args.out)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("voices", help="search voices for a language")
    p.add_argument("--language", required=True)
    p.add_argument("--query")
    p.add_argument("--gender", choices=["male", "female"])
    p.add_argument("--provider")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--all", action="store_true", help="include voices the plan cannot use")
    p.set_defaults(func=cmd_voices)

    sub.add_parser("favorites", help="list favorite voices").set_defaults(func=cmd_favorites)
    sub.add_parser("custom", help="list custom (designed/cloned) voices").set_defaults(func=cmd_custom)

    p = sub.add_parser("tts", help="one text, one voice")
    p.add_argument("--voice", required=True)
    p.add_argument("--text")
    p.add_argument("--text-file")
    p.add_argument("--out")
    p.set_defaults(func=cmd_tts)

    p = sub.add_parser("srt", help="timeline-aligned voiceover from an SRT/VTT file")
    p.add_argument("--voice", required=True)
    p.add_argument("--srt", required=True)
    p.add_argument("--min-rate", type=float, default=0.95)
    p.add_argument("--max-rate", type=float, default=1.5)
    p.add_argument("--out")
    p.set_defaults(func=cmd_srt)

    p = sub.add_parser("status", help="wait for a job and print its audio URL")
    p.add_argument("--id", type=int, required=True)
    p.add_argument("--multi", action="store_true", help="multi-voice or SRT job")
    p.add_argument("--out")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("mux", help="put the voiceover into a video with ffmpeg")
    p.add_argument("--video", required=True)
    p.add_argument("--audio", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--keep-original", type=float, help="keep original audio at this volume (e.g. 0.2)")
    p.set_defaults(func=cmd_mux)

    p = sub.add_parser("upload", help="upload a local video/audio file, print its public URL")
    p.add_argument("--file", required=True)
    p.set_defaults(func=cmd_upload)

    p = sub.add_parser("transcribe", help="video/audio -> SRT")
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument("--file")
    source.add_argument("--url", help="public URL of a file already uploaded to TTSForFree")
    p.add_argument("--language", required=True, help="spoken language code, e.g. vi")
    p.add_argument("--out")
    p.set_defaults(func=cmd_transcribe)

    p = sub.add_parser("localize", help="dub a video into several languages in one job")
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument("--file")
    source.add_argument("--video-url")
    p.add_argument("--source", required=True, help="spoken language of the video, e.g. vi")
    p.add_argument("--target", action="append", required=True, help="language=voice token, repeat per language")
    p.add_argument("--keep-original", type=int, help="original audio volume percent in the dubbed video (0-100)")
    p.set_defaults(func=cmd_localize)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
