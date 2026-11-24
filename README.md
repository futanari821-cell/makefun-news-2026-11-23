# THE WORLD — 23 November 2026 (make.fun trial entry, ready to submit)

Bounty: **"Sum up 23 November's world news in one image"** ($100, top 50 split:
1st $20, 11th–50th $1.20). Entries close **2026-11-25 00:00 UTC = 09:00 JST**.

## What is ready
- `main.py` — Python 3.13 / stdlib + Pillow only, fully offline and deterministic.
  Renders `world-23-nov-2026.png` (1600×2200): masthead with the date,
  hero story (Nvidia reinstates Jensen Huang), 8 more stories across war,
  climate, US politics, UK/EU, markets, Middle East/Asia and sport, plus a
  footer strip. Verified: two runs produce byte-identical output
  (`--check` asserts the sha256 match); output image visually checked for
  legibility (no overflow, no overlap).
- `world-23-nov-2026.png` — the rendered entry image.
- Stories are real 23 Nov 2026 headlines (BBC, Al Jazeera, Daily Mirror,
  Economic Times, CoinDesk via web search 2026-11-24).

## What the user still has to do (nothing done here)
1. Answer: do you have a GitHub account? (asked 2026-11-23, still unanswered)
2. Register a make.fun account yourself.
3. Create a **public GitHub repo** (created after the competition opened),
   put `main.py` at the root, add an OSI-approved licence (MIT suggested),
   and submit via make.fun. A Solana wallet + ~0.0025 SOL rent is needed
   only at claim time, not to enter.
4. Entry is free. Expected payout if placed 11th–50th is $1.20; this is a
   trial run to learn the mechanics, not income.
