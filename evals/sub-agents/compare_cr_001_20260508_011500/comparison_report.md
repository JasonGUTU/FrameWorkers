# Comparison report — case `cr_001`

- generated: `2026-05-08 01:14:54`

## Per-mp4 metrics

| metric | framework | baseline |
|---|---|---|
| duration_sec | 65.62 | 70.42 |
| resolution | 1948x1064 | 1920x1080 |
| has_audio_track | True | True |
| filesize_bytes | 37705414 | 157330882 |
| shot_segment_count | — | 9 |
| audio_lufs.input_i (LUFS) | -27.41 | -18.68 |
| audio_lufs.input_lra (LRA) | 6.90 | 16.90 |
| audio_lufs.input_tp (dBTP) | -4.53 | -3.56 |

## Gemini-3 vision judge (per video)

| metric | framework | baseline |
|---|---|---|
| character_consistency_score (0-10) | 0 | 2 |
| subtitle_burnin_present | False | False |

### Judge reasoning
- **framework**: The frames depict completely different characters across varying settings and eras, such as modern soldiers, a young man in armor, and an older man in a tunic, with no consistent protagonist.
- **baseline**:  The video displays a montage of different scenes featuring several distinct warriors with entirely different faces, ages, facial hair, and armor, lacking a single consistent protagonist.
