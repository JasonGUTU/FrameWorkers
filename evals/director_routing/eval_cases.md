# director_agent 路由评测用例

> Source: `evals/director_routing/eval_cases.json` · **115** cases / **9** categories  
> Chain 记法: `→` 分步；`{A\|B\|C}` = 这一步任一命中即可；`×N` = 连续 N 步同一组；末尾 `Agent` 后缀省略（`Story` = `StoryAgent`）。

## 目录

- [创作类 (creative — brief → finished film)](#cr) · 15
- [输入类 (intake — 图片参考素材)](#intake) · 5
- [字幕类 (subtitles — 单语字幕)](#sub) · 9
- [双语字幕 (bilingual subtitles)](#bilingual) · 5
- [讲故事类 (illustrated storytelling — slideshow + narrator)](#storytelling) · 15
- [风格迁移 (style transfer)](#style) · 5
- [视频续写 (video extend)](#extend) · 5
- [精彩片段 (highlight)](#highlight) · 4
- [复杂组合 (complex)](#complex) · 52


## <a id="cr"></a>创作类 (creative — brief → finished film)

| # | name | input | expected chain |
|---:|---|---|---|
| 1 | `cr_01` | Make a cultivation-fantasy animated drama about a washed-up young man who awakens an ancient bloodline and rises through the ranks of his sect | Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 2 | `cr_02` | Make a CEO romance mini-drama about a struggling waitress who discovers her rude regular customer is the billionaire she saved years ago | Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 3 | `cr_03` | Make a supernatural-thriller mini-drama where the female lead moves into a haunted house and finds a videotape left by the previous tenant that reveals an unsolved murder | Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 4 | `cr_04` | Make a 3-minute rebirth-revenge animated drama where the female lead is framed by her best friend and falls to her death, then is reborn three years earlier to strike back | Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 5 | `cr_05` | Create a post-apocalyptic animated drama where the last survivors discover a hidden sanctuary guarded by an awakened AI | Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 6 | `cr_06` | Make a sweet costume-drama mini-drama where the female lead transmigrates into the chancellor's legitimate daughter and moves from mutual loathing to mutual redemption with a cold-faced prince | Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 7 | `cr_07` | I want a romance mini-drama where a young woman wins a dating-app lottery and ends up fake-married to a reclusive tech mogul | Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 8 | `cr_08` | Make a sci-fi animated drama about the last awakened AI falling in love with the only human engineer left | Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 9 | `cr_09` | Make an urban romance mini-drama where the female lead runs into her ex-boyfriend — missing for five years — in a rainy-night Paris café | Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 10 | `cr_10` | Make a workplace revenge mini-drama where an overlooked analyst exposes her boss's insider trading by rising to CEO at a rival firm | Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 11 | `cr_11` | Make a palace-intrigue costume-drama mini-drama where a real and a fake princess swap places, exploit each other, and ultimately team up to expose the empress's ambitions | Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 12 | `cr_12` | Make a martial-arts animated drama about a young swordsman who, to avenge his sect, ventures alone into the demonic cult's seven-layered killing formation | Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 13 | `cr_13` | Make an urban underdog-comeback mini-drama where the live-in son-in-law thrown out of the rich family is secretly the heir of a top conglomerate | Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 14 | `cr_14` | Make an epic-battle scene for a fantasy animated drama: seven ancient divine beasts gather to face a demon god returning to the mortal realm | Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 15 | `cr_15` | Make a suspense-twist mini-drama where a therapist realizes her new patient is the man who murdered her sister years ago | Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |

## <a id="intake"></a>输入类 (intake — 图片参考素材)

| # | name | input | expected chain |
|---:|---|---|---|
| 16 | `intake_img_01` | Using this uploaded image as the story's protagonist, produce an inspirational cultivation-fantasy animated drama | IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 17 | `intake_img_02` | Using this uploaded photo as the city backdrop, make a 3-minute urban-suspense mini-drama with an oppressive atmosphere | IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 18 | `intake_img_03` | Use the character in this uploaded image as the hero of a one-minute cultivation-fantasy animated-drama trailer | IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 19 | `intake_img_04` | Set in the seaside town from this uploaded photo, make a tragic costume-drama mini-drama: the female lead dies under the sea to save the male lead | IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 20 | `intake_img_05` | Take the person in this photo as the protagonist and make a rebirth-themed mini-drama about them waking up ten years before their lover's death | IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |

## <a id="sub"></a>字幕类 (subtitles — 单语字幕)

| # | name | input | expected chain |
|---:|---|---|---|
| 21 | `sub_01` | Make an English-subtitled campus sweet-romance mini-drama: the top-student class president and a transferred-in delinquent girl redeem each other | Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription\|AudioMix} → {AudioMix\|Transcription} → Compositor → done |
| 22 | `sub_02` | Make a subtitled costume-drama culinary animated drama where the female lead, a junior imperial-kitchen maid, rises through her cooking skills | Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription\|AudioMix} → {AudioMix\|Transcription} → Compositor → done |
| 23 | `sub_03` | Create a mini-drama with English subtitles about a rebirth revenge story set in modern Shanghai | Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription\|AudioMix} → {AudioMix\|Transcription} → Compositor → done |
| 24 | `sub_04` | Make a subtitled children's cultivation-fantasy animated drama whose protagonist is a seven-year-old divine-beast boy fighting to protect a deep-sea forbidden zone | Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription\|AudioMix} → {AudioMix\|Transcription} → Compositor → done |
| 25 | `sub_05` | Make a subtitled sci-fi mini-drama where the male lead, a top tech-reviewer blogger, suddenly discovers he is actually an AI | Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription\|AudioMix} → {AudioMix\|Transcription} → Compositor → done |
| 26 | `sub_vid_01` | Add English subtitles to this interview-style mini-drama | IntakeVideo → Transcription → Compositor → done |
| 27 | `sub_vid_02` | Add English subtitles to this speech mini-drama | IntakeVideo → Transcription → Compositor → done |
| 28 | `sub_vid_03` | Generate Chinese subtitles for this English mini-drama episode | IntakeVideo → Transcription → Translation → Compositor → done |
| 29 | `sub_vid_05` | Batch-generate English burned-in subtitles for this 30-episode cultivation-fantasy animated drama | IntakeVideo → Transcription → Compositor → done |

## <a id="bilingual"></a>双语字幕 (bilingual subtitles)

| # | name | input | expected chain |
|---:|---|---|---|
| 30 | `bilingual_01` | Make an English-Chinese bilingual costume-drama animated drama about a nine-generation tea-ceremony lineage reconnected with a modern female lead through reincarnation | Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription\|Translation} → {Music\|Ambience\|Transcription\|Translation\|AudioMix} → {Music\|Ambience\|Transcription\|Translation\|AudioMix} → {AudioMix\|Translation} → Compositor → done |
| 31 | `bilingual_02` | Make an English-Japanese bilingual CEO-romance mini-drama where the male lead is a Japan-returned, hidden-identity conglomerate heir | Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription\|Translation} → {Music\|Ambience\|Transcription\|Translation\|AudioMix} → {Music\|Ambience\|Transcription\|Translation\|AudioMix} → {AudioMix\|Translation} → Compositor → done |
| 32 | `bilingual_03` | Create a mini-drama with English and Chinese subtitles about a martial-arts prodigy seeking revenge across ancient and modern timelines | Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription\|Translation} → {Music\|Ambience\|Transcription\|Translation\|AudioMix} → {Music\|Ambience\|Transcription\|Translation\|AudioMix} → {AudioMix\|Translation} → Compositor → done |
| 33 | `bilingual_04` | Make an English-Spanish bilingual cultivation-fantasy animated drama, targeting Latin American market release | Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription\|Translation} → {Music\|Ambience\|Transcription\|Translation\|AudioMix} → {Music\|Ambience\|Transcription\|Translation\|AudioMix} → {AudioMix\|Translation} → Compositor → done |
| 34 | `bilingual_05` | Make an English-Chinese bilingual urban mini-drama where the female lead, a Chinese-American prodigy doctor, gets pulled into a family-inheritance battle | Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription\|Translation} → {Music\|Ambience\|Transcription\|Translation\|AudioMix} → {Music\|Ambience\|Transcription\|Translation\|AudioMix} → {AudioMix\|Translation} → Compositor → done |

## <a id="storytelling"></a>讲故事类 (illustrated storytelling — slideshow + narrator)

| # | name | input | expected chain |
|---:|---|---|---|
| 101 | `storytelling_01` | Turn this children's bedtime tale into an illustrated audiobook video — calm narration with one soft watercolor picture per scene: Once upon a time, a little rabbit named Pip found a tiny glowing seed in the meadow... | Narration → {Illustration\|Narrator} → {Narrator\|Illustration} → Compositor → done |
| 102 | `storytelling_02` | Make a narrated picture-book video of this Aesop's fable about the ant and the grasshopper | Narration → {Illustration\|Narrator} → {Narrator\|Illustration} → Compositor → done |
| 103 | `storytelling_03` | Read this classical Chinese Tang-dynasty poem aloud and show a matching ink-painting illustration for each verse, slideshow-style | Narration → {Illustration\|Narrator} → {Narrator\|Illustration} → Compositor → done |
| 104 | `storytelling_04` | Produce a narrated picture-book science storytime about how emperor penguins raise their chicks in Antarctica; one cute cartoon image per behavior | Narration → {Illustration\|Narrator} → {Narrator\|Illustration} → Compositor → done |
| 105 | `storytelling_05` | Create an illustrated audiobook of this Greek myth about Persephone returning from the underworld every spring, storybook style | Narration → {Illustration\|Narrator} → {Narrator\|Illustration} → Compositor → done |
| 106 | `storytelling_music_01` | Make an illustrated audiobook of this lullaby-style bedtime story with a gentle, slow piano score playing softly under the narrator | Narration → {Illustration\|Narrator\|Music} → {Narrator\|Illustration\|Music} → {Music\|Narrator\|Illustration} → AudioMix → Compositor → done |
| 107 | `storytelling_ambience_01` | Narrate this forest-adventure children's story as an illustrated audiobook with a gentle forest-ambience bed (wind through leaves, distant birds) | Narration → {Illustration\|Narrator\|Ambience} → {Narrator\|Illustration\|Ambience} → {Ambience\|Narrator\|Illustration} → AudioMix → Compositor → done |
| 108 | `storytelling_bilingual_01` | Make an English-Chinese bilingual illustrated audiobook of this short fairytale — narrate in English, burn both English and Chinese subtitles on the slideshow | Narration → {Illustration\|Narrator} → {Narrator\|Illustration} → Translation → Compositor → done |
| 109 | `storytelling_imgref_01` | Using the uploaded character portrait as the heroine, turn this short folktale into an illustrated audiobook where every picture keeps her appearance consistent with the reference | IntakeImage → BriefEnricher → Narration → {Illustration\|Narrator} → {Narrator\|Illustration} → Compositor → done |
| 110 | `storytelling_full_01` | Using the uploaded character portrait of the fox protagonist, produce an English-Chinese bilingual illustrated audiobook of this folk tale, narrated in English with a gentle koto-and-flute background score | IntakeImage → BriefEnricher → Narration → {Illustration\|Narrator\|Music} → {Narrator\|Illustration\|Music} → {Music\|Narrator\|Illustration} → AudioMix → Translation → Compositor → done |
| 111 | `storytelling_music_ambience_01` | Make an illustrated audiobook of this ocean-themed children's story with a gentle piano lullaby playing under the narrator AND ambient wave sounds in the background | Narration → {Illustration\|Narrator\|Music\|Ambience} → {Narrator\|Illustration\|Music\|Ambience} → {Music\|Ambience\|Illustration\|Narrator} → {Ambience\|Music} → AudioMix → Compositor → done |
| 112 | `storytelling_music_bilingual_01` | Create an English-Chinese bilingual illustrated audiobook of this Hans Christian Andersen fairytale with a gentle harp-and-celesta BGM | Narration → {Illustration\|Narrator\|Music} → {Narrator\|Illustration\|Music} → {Music\|Narrator\|Illustration} → AudioMix → Translation → Compositor → done |
| 113 | `storytelling_imgref_music_01` | Using this uploaded portrait of the protagonist as the main character, turn this short myth into an illustrated audiobook with a soft guzheng score under the narration | IntakeImage → BriefEnricher → Narration → {Illustration\|Narrator\|Music} → {Narrator\|Illustration\|Music} → {Music\|Narrator\|Illustration} → AudioMix → Compositor → done |
| 114 | `storytelling_imgref_bilingual_01` | Using this uploaded character portrait of the storyteller grandmother, produce an English-Spanish bilingual illustrated audiobook of this folk tale | IntakeImage → BriefEnricher → Narration → {Illustration\|Narrator} → {Narrator\|Illustration} → Translation → Compositor → done |
| 115 | `storytelling_ultra_01` | Using this uploaded fox-protagonist portrait, make a bilingual English-Chinese illustrated audiobook of the fox-and-crow fable with both a gentle flute score AND forest-ambience sounds under the narrator | IntakeImage → BriefEnricher → Narration → {Illustration\|Narrator\|Music\|Ambience} → {Narrator\|Illustration\|Music\|Ambience} → {Music\|Ambience\|Illustration\|Narrator} → {Ambience\|Music} → AudioMix → Translation → Compositor → done |

## <a id="style"></a>风格迁移 (style transfer)

| # | name | input | expected chain |
|---:|---|---|---|
| 35 | `style_01` | Convert this mini-drama clip to a Studio Ghibli animated-drama style | IntakeVideo → StyleTransfer → done |
| 36 | `style_02` | Make this mini-drama clip look like a cyberpunk animated drama with neon and rainy-night atmosphere | IntakeVideo → StyleTransfer → done |
| 37 | `style_03` | Apply a Van Gogh oil-painting style to this cultivation-drama clip | IntakeVideo → StyleTransfer → done |
| 38 | `style_04` | Convert this live-action mini-drama entirely to a Japanese anime style, preserving plot and camera work | IntakeVideo → StyleTransfer → done |
| 39 | `style_05` | Convert this costume-drama mini-drama to a Chinese ink-wash animated-drama style | IntakeVideo → StyleTransfer → done |

## <a id="extend"></a>视频续写 (video extend)

| # | name | input | expected chain |
|---:|---|---|---|
| 40 | `extend_01` | Extend this CEO-romance confrontation scene to 15 seconds, adding the male lead's inner monologue and slow-motion close-ups | IntakeVideo → VideoExtend → done |
| 41 | `extend_03` | Extend this cultivation-duel clip by adding a slow-motion reversal where the underdog awakens a forbidden bloodline | IntakeVideo → VideoExtend → done |
| 42 | `extend_04` | Extend this tragic costume-drama farewell scene to 20 seconds, adding snow-scene cutaways and flashbacks of the female lead recalling her past life | IntakeVideo → VideoExtend → done |
| 43 | `extend_05` | Extend this scene of the female lead confessing and crying by 8 seconds, adding rain sound effects and close-ups of her trembling hands | IntakeVideo → VideoExtend → done |
| 44 | `extend_06` | Extend this reincarnation awakening scene by 10 seconds with ghostly overlays of the character's past life flashing back | IntakeVideo → VideoExtend → done |

## <a id="highlight"></a>精彩片段 (highlight)

| # | name | input | expected chain |
|---:|---|---|---|
| 45 | `highlight_01` | Cut the most thrilling twist moments from this mini-drama episode into promotional material | IntakeVideo → VideoAnalysis → Highlight → done |
| 46 | `highlight_03` | Extract the sweetest lead-couple interactions from this mini-drama into a promo short | IntakeVideo → VideoAnalysis → Highlight → done |
| 47 | `highlight_04` | Cut the palace-intrigue iconic scenes from this costume-drama animated drama into a 30-second viral promo | IntakeVideo → VideoAnalysis → Highlight → done |
| 48 | `highlight_05` | Cut a compilation of face-slapping payback moments from this rebirth mini-drama episode | IntakeVideo → VideoAnalysis → Highlight → done |

## <a id="complex"></a>复杂组合 (complex)

| # | name | input | expected chain |
|---:|---|---|---|
| 49 | `complex_01` | Analyze this hit mini-drama, then write a new story in the same genre and produce it as a new animated drama | IntakeVideo → VideoAnalysis → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 50 | `complex_02` | First extend this mini-drama clip, then style-transfer it into a Japanese anime look | IntakeVideo → VideoExtend → StyleTransfer → done |
| 51 | `complex_03` | Extend this mini-drama episode, then style-transfer it into an animated-drama look, and add English subtitles | IntakeVideo → VideoExtend → StyleTransfer → Transcription → Compositor → done |
| 52 | `complex_04` | Analyze the pacing of this 12-episode mini-drama, cut the best twist moments, add background music, and composite the final | IntakeVideo → VideoAnalysis → Highlight → Music → AudioMix → Compositor → done |
| 53 | `complex_06` | Analyze this mini-drama's emotional arc, then add subtitles and background music to it | IntakeVideo → {VideoAnalysis\|Transcription} → {Transcription\|VideoAnalysis} → {Transcription\|Music} → {Music\|Transcription} → AudioMix → Compositor → done |
| 54 | `complex_08` | Translate this Chinese interview video to English and add English subtitles | IntakeVideo → Transcription → Translation → Compositor → done |
| 55 | `complex_10` | Analyze this mini-drama, cut the climactic twist moments, add English subtitles and background music, and output the final promo | IntakeVideo → VideoAnalysis → Highlight → {Transcription\|Music} → {Transcription\|Music} → {Music\|Transcription} → AudioMix → Compositor → done |
| 56 | `complex_11` | Transcribe this mini-drama EP01's English dub, translate it to Japanese, generate Japanese subtitles, and burn them onto the video | IntakeVideo → Transcription → Translation → Compositor → done |
| 57 | `complex_13` | First analyze this hit mini-drama, then write a sequel story based on the analysis, and produce it as a new subtitled animated drama | IntakeVideo → VideoAnalysis → Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription\|AudioMix} → {AudioMix\|Transcription} → Compositor → done |
| 58 | `complex_15` | Cut the lead-couple highlight interactions from this urban sweet-romance mini-drama, add romantic background music and English subtitles | IntakeVideo → VideoAnalysis → Highlight → {Music\|Transcription} → {Transcription\|Music} → {Transcription\|Music} → AudioMix → Compositor → done |
| 59 | `complex_18` | Analyze this English mini-drama season, extract the high-tension climax moments, and add Chinese subtitles plus emotional background score | IntakeVideo → VideoAnalysis → Highlight → Transcription → {Translation\|Transcription\|Music} → {Music\|Translation} → AudioMix → Compositor → done |
| 60 | `complex_19` | Using this uploaded animated-drama character image, make an English-Chinese bilingual CEO-romance mini-drama trailer | IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription\|Translation} → {Music\|Ambience\|Transcription\|Translation\|AudioMix} → {Music\|Ambience\|Transcription\|Translation\|AudioMix} → {AudioMix\|Translation} → Compositor → done |
| 61 | `complex_20` | Extract the key dialogue from this mini-drama's meeting scenes, transcribe and translate them to Chinese, and output a subtitled highlight edit | IntakeVideo → VideoAnalysis → Highlight → Transcription → Translation → Compositor → done |
| 62 | `complex_21` | First style-transfer to an ink-wash animated-drama look, then extend the key scene, finally add traditional-style background music | IntakeVideo → StyleTransfer → VideoExtend → Music → AudioMix → Compositor → done |
| 63 | `complex_23` | Using this uploaded female-lead character portrait as the protagonist, make a 3-minute cyberpunk sci-fi dystopian mini-drama: she leads an underground hacker coalition raiding a clone corporation and finally discovers she is also a clone. Extend the climactic identity-reveal confrontation scene by 10 seconds, adding slow-motion close-ups and shots of her trembling hands. | IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → VideoExtend → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 64 | `complex_24` | Add a sad piano background score to this mini-drama clip | IntakeVideo → Music → AudioMix → Compositor → done |
| 65 | `complex_25` | Add rain ambience and a piano background score to this rainy-night scene | IntakeVideo → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 66 | `complex_26` | Convert this clip to an animated-drama look and add English subtitles | IntakeVideo → StyleTransfer → Transcription → Compositor → done |
| 67 | `complex_27` | Convert this costume-drama mini-drama clip to an ink-wash style and add a traditional-style background score | IntakeVideo → StyleTransfer → Music → AudioMix → Compositor → done |
| 68 | `complex_28` | Extend this confrontation scene by 10 seconds and add English subtitles | IntakeVideo → VideoExtend → Transcription → Compositor → done |
| 69 | `complex_29` | Extend this fight scene by 8 seconds and add a tense, intense background score | IntakeVideo → VideoExtend → Music → AudioMix → Compositor → done |
| 70 | `complex_30` | Cut the highlight moments from this mini-drama and add English subtitles to produce a promo | IntakeVideo → VideoAnalysis → Highlight → Transcription → Compositor → done |
| 71 | `complex_31` | Add an upbeat electronic ambient background score to this urban-nightscape vlog clip | IntakeVideo → Music → AudioMix → Compositor → done |
| 72 | `complex_32` | Add a cinematic orchestral score to this costume-drama fight scene | IntakeVideo → Music → AudioMix → Compositor → done |
| 73 | `complex_33` | Add ocean-wave ambience and a lyrical piano background score to this seaside farewell scene | IntakeVideo → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 74 | `complex_34` | Add thunder-and-wind ambience and an epic percussion background score to this cultivation-fantasy final-battle clip | IntakeVideo → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 75 | `complex_35` | Convert this urban-romance clip to a cyberpunk look and add a synth-driven electronic score | IntakeVideo → StyleTransfer → Music → AudioMix → Compositor → done |
| 76 | `complex_36` | Turn this martial-arts clip into traditional ink-painting style with a guqin score | IntakeVideo → StyleTransfer → Music → AudioMix → Compositor → done |
| 77 | `complex_37` | Convert this workplace-confrontation scene to a Japanese anime look and add English subtitles | IntakeVideo → StyleTransfer → Transcription → Compositor → done |
| 78 | `complex_38` | Convert this interview clip to a Van Gogh oil-painting look and add English subtitles | IntakeVideo → StyleTransfer → Transcription → Compositor → done |
| 79 | `complex_39` | Extend this CEO-romance confession scene by 12 seconds and add a romantic piano background score | IntakeVideo → VideoExtend → Music → AudioMix → Compositor → done |
| 80 | `complex_40` | Extend this ancient sword-duel scene by 15 seconds and layer in an epic battle score | IntakeVideo → VideoExtend → Music → AudioMix → Compositor → done |
| 81 | `complex_41` | Extend this rebirth-awakening scene by 10 seconds and add English subtitles | IntakeVideo → VideoExtend → Transcription → Compositor → done |
| 82 | `complex_42` | Extend this cultivation awakening scene by 8 seconds and add English subtitles | IntakeVideo → VideoExtend → Transcription → Compositor → done |
| 83 | `complex_43` | Cut the palace-intrigue showdown iconic scenes from this mini-drama into a promo reel and add English subtitles | IntakeVideo → VideoAnalysis → Highlight → Transcription → Compositor → done |
| 84 | `complex_44` | Cut the top tear-jerker moments from this romance drama into a 30-second promo with English subtitles | IntakeVideo → VideoAnalysis → Highlight → Transcription → Compositor → done |
| 85 | `complex_45` | Extend this tragic costume-drama scene by 10 seconds and convert the whole thing to an ink-wash animated-drama look | IntakeVideo → VideoExtend → StyleTransfer → done |
| 86 | `complex_46` | Extend this martial-arts fight scene by 8 seconds, convert it to an animated-drama look, and add English subtitles | IntakeVideo → VideoExtend → StyleTransfer → Transcription → Compositor → done |
| 87 | `complex_47` | First convert this urban car-chase scene to a cyberpunk look, then extend the climax by 12 seconds, finally add a synth-driven score | IntakeVideo → StyleTransfer → VideoExtend → Music → AudioMix → Compositor → done |
| 88 | `complex_48` | Analyze this 20-episode cultivation drama and cut the most epic reveal moments with an orchestral score | IntakeVideo → VideoAnalysis → Highlight → Music → AudioMix → Compositor → done |
| 89 | `complex_49` | Translate this Japanese-language interview mini-drama into English subtitles and burn them onto the video | IntakeVideo → Transcription → Translation → Compositor → done |
| 90 | `complex_50` | Extract the highlight dialogue from this Chinese-language business-warfare mini-drama, translate it to English, and add subtitles | IntakeVideo → VideoAnalysis → Highlight → Transcription → Translation → Compositor → done |
| 91 | `complex_51` | Analyze this CEO-romance mini-drama's pacing, then add English subtitles and a background score | IntakeVideo → {VideoAnalysis\|Transcription} → {Transcription\|VideoAnalysis} → {Transcription\|Music} → {Music\|Transcription} → AudioMix → Compositor → done |
| 92 | `complex_52` | Cut the climactic scenes from this costume-drama mini-drama into a trailer, with English subtitles and an epic score | IntakeVideo → VideoAnalysis → Highlight → {Transcription\|Music} → {Transcription\|Music} → {Music\|Transcription} → AudioMix → Compositor → done |
| 93 | `complex_53` | Cut the face-slapping iconic scenes from this urban rebirth mini-drama, add rousing music and English subtitles | IntakeVideo → VideoAnalysis → Highlight → {Music\|Transcription} → {Transcription\|Music} → {Transcription\|Music} → AudioMix → Compositor → done |
| 94 | `complex_54` | Analyze the tropes of this hit sci-fi mini-drama and rewrite a new story in the same style as a new animated drama | IntakeVideo → VideoAnalysis → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 95 | `complex_55` | Write a sequel based on the plotline of this palace-intrigue mini-drama and produce it as a new English-subtitled animated drama | IntakeVideo → VideoAnalysis → Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription\|AudioMix} → {AudioMix\|Transcription} → Compositor → done |
| 96 | `complex_56` | Study this cultivation-fantasy drama's character arcs and generate a prequel animated drama with English subtitles | IntakeVideo → VideoAnalysis → Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription\|AudioMix} → {AudioMix\|Transcription} → Compositor → done |
| 97 | `complex_57` | Using these uploaded costume-drama character images as the protagonists, make an English-Chinese bilingual palace-intrigue mini-drama promo | IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription\|Translation} → {Music\|Ambience\|Transcription\|Translation\|AudioMix} → {Music\|Ambience\|Transcription\|Translation\|AudioMix} → {AudioMix\|Translation} → Compositor → done |
| 98 | `complex_58` | Use these uploaded cyberpunk character portraits to produce a bilingual (English/Chinese) sci-fi mini-drama trailer | IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Transcription} → {Music\|Ambience\|Transcription\|Translation} → {Music\|Ambience\|Transcription\|Translation\|AudioMix} → {Music\|Ambience\|Transcription\|Translation\|AudioMix} → {AudioMix\|Translation} → Compositor → done |
| 99 | `complex_59` | Using this uploaded female-swordsman character portrait as the protagonist, make a martial-arts mini-drama; extend the sect-massacre opening scene by 15 seconds with slow-motion | IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → VideoExtend → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 100 | `complex_60` | Use this uploaded medical-drama character portrait as the lead and produce a rebirth mini-drama with the climax reveal extended by 10 seconds | IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → VideoExtend → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |

