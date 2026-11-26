# Voices and cost (TTSForFree)

Cost = characters × the voice's `BaseCreditsPerCharacter` (shown in the Voice Library and `GetListVoice`).

| Tier | Example voices (English) | Credits / char | Measured on our sample Shorts |
|---|---|---|---|
| budget | Andrew, Guy, Brian, Ava, Emma (Natural, Azure) | 0.5 | 100–175 credits per 16–22 s Short |
| hybrid | Gemini (e.g. Concierge 10 Gemini) on hook + twist, Azure elsewhere | mixed | 1,213 credits for a 28 s Short |
| premium | Gemini voices (Concierge, Sadaltager, Algenib…) | 8 | 4,184 credits for a 45 s Short |

Plan prices (ttsforfree.com/pricing, Basic monthly): US$2.99 / 69,000 VND for 300,000 credits.
So a budget Short costs well under one US cent, a premium Gemini Short about US$0.04.

Other languages: pick a voice with `list_voices(language)`; Gemini voices are multilingual.
