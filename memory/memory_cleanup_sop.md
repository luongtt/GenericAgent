# Memory Cleanup SOP

L1 unique purpose: **Existence** index: know what related memory to check under what circumstances.

## ROI Model
L1 pays a token cost per word per turn, but prevents mistakes (insurance). ROI = (Probability of mistake × Cost) / Cost of words.

## What to keep (High ROI)
- Red lines: Irreversible if violated, e.g. "forbid killing python" → 5 words prevents -100k
- Counter-intuitive triggers: Won't think of reading SOP without a prompt, e.g. "HttpOnly" → 4 words prevents task failure.
- Routing pointers: Minimize SOP locating, e.g. "vision_sop+vision_api.py"

## What to delete (Low ROI)
- Implementation details: The "how-to" already in SOP → only keep trigger words
- Intuitive abilities: Can think of it without a reminder → 0 gain
- Redundancy: Rules already covered in L3 / fragments already in other L1 lines → paying tax for duplicates is not worth it

## 4 Questions per Item
1. If deleted, does the probability of making mistakes really increase? → If not, delete it.
2. Is it already covered in L3 SOP? → If yes, only keep trigger words.
3. Without these words, can you think of reading the SOP yourself? → If yes, delete it.
4. For the same gain, can you use fewer words? → If yes, compress it.

## L1 Write Verification (Must pass before writing)
- "What scenario do these words trigger?" → If you can't answer, don't write it; Trigger word = scenario name (video content understanding) not tool name (yt-dlp).
- Compress by scenario value, not word count: Trigger scenario words shouldn't be deleted at all; implementation details without an independent scenario are the targets for compression.
- Level matching: Red lines → RULES, SOP index → L3 filename is sufficient (forbid adding description words); self-explanatory names do not need additional trigger words, do not stuff tools into L0.
- Memory modification is persistent damage, errors compound in subsequent turns → Cleanup requires more caution than daily tasks.

## Cleanup Process
0. Deliver task before depositing, forbid writing memory before completion.
1. Read insight line by line, split fragments by |, label each fragment: red line / trigger word / routing / implementation detail.
2. Low ROI fragments → delete after confirming L3 coverage; RULES ask per item "Does it blow up if violated or is it just a good habit?"
3. Check recent mistake experiences, supplement omitted high ROI trigger words.
4. Verify total lines ≤ 30.
