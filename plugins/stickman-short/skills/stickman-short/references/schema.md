# story.json schema

```jsonc
{
  "id": "eiffel", "lang": "en", "title": "The man who sold the Eiffel Tower",
  "useCase": "history",              // history | motivation | fight | whatif | storytime | psychology
  "voiceTier": "premium",            // budget | hybrid | premium
  "scenes": [
    {
      "text": "A man sold the Eiffel Tower.",          // narration = caption
      "highlight": ["Eiffel"],                         // words shown in yellow
      "narration": { "voice": "Concierge 10 Gemini (East Coast)" },  // filled by scripts/voice.mjs: url, file, durationSec, credits
      "background": "paris",
      "actors": [ { "id": "lustig", "pose": "point", "x": 0.25, "hat": "top", "expression": "smug", "speaking": true } ],
      "props": [ { "kind": "tower", "x": 0.64 } ],
      "effects": [ { "kind": "question", "x": 0.8, "y": 0.36, "at": 0.5 } ],
      "camera": "punchIn",
      "bubble": { "actor": "lustig", "text": "Top secret…" },
      "bigText": "SCRAP?"
    }
  ]
}
```

## Values

- **pose**: stand, walk, run, point, talk, cheer, shock, think, sad, sit, punch, kick, block, fall, give, lift, phone, type, sleep, pushup
- **expression**: neutral, happy, shock, angry, sad, determined, smug
- **hat**: top, cap, crown, headband, hair, bun · **color**: any CSS color for the stroke (use it to tell actors apart)
- **prop** (in hand): money, phone, book, sword, dumbbell, trophy, paper, coffee, flag
- **actor position**: `x` 0..1 across the frame; `enter: "left" | "right"` walks in; `x2` moves during the scene (walk / run); `y` 0..1 for feet off the ground; `face: -1` looks left; `scale` (default 1.3)
- **background**: paris, city, room, office, gym, dojo, space, night, classroom (`boardText` on the board), street, void, earth
- **props** (scene): tower, desk, sign (`label`), clock, chart (`label`), door, bed, podium, calendar (`label`), hole, trophy, box, phoneBig (`label`)
- **effects**: pow, speedlines, sweat, question, sparkle, moneyRain, rain, zzz, hearts, fire, arrowUp (`x`, `y` 0..1, `at` seconds into the scene)
- **camera**: push (default on even scenes), pan, punchIn, shake, flash
- Scene length = narration length (+0.2 s). Without narration set `durationSec`.
