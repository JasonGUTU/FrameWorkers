"""Shape: vid_bilingual_sub — IntakeVideo → Transcription → Translation → Compositor.

User uploaded a video speaking language A, and asks for bilingual
subtitles (language A + language B) burned onto the video.  No audio
overlay, no style change, no highlight extraction.

Reject biases:
  - VideoAnalysisAgent / HighlightAgent (no analysis or trimming)
  - MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay)
  - StyleTransferAgent / VideoExtendAgent (no visual or length change)
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Please add both English and Chinese subtitles to this Mandarin cooking-show clip — bilingual burn-in on the video.",
        "rationale": (
            "User uploaded a Mandarin-spoken cooking-show and asks for bilingual (Chinese + "
            "English) subtitles burned onto the video. IntakeVideoAgent ingests the clip. "
            "TranscriptionAgent transcribes the Mandarin speech. TranslationAgent produces the "
            "English counterpart. CompositorAgent burns both Chinese and English SRT lines "
            "onto the footage. Reject VideoAnalysisAgent / HighlightAgent (no trimming), "
            "MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent "
            "(no restyle)."
        ),
        "intents": [
            "Ingest the Mandarin cooking-show clip into the workspace as the source video.",
            "Transcribe the chef's Mandarin narration into timestamped SRT segments.",
            "Translate the Mandarin SRT segments into matching English subtitles.",
            "Compose the final video with bilingual Chinese-English subtitles burned onto the cooking footage.",
        ],
    },
    {
        "user_goal": "Add English-Japanese bilingual subtitles to this Japanese anime-convention panel video.",
        "rationale": (
            "Japanese-spoken convention panel + request for Japanese + English bilingual "
            "subtitles. IntakeVideoAgent ingests the panel footage. TranscriptionAgent extracts "
            "Japanese speech. TranslationAgent produces English translations. CompositorAgent "
            "burns both Japanese and English captions onto the panel. No audio / style / "
            "length changes asked for."
        ),
        "intents": [
            "Ingest the Japanese anime-convention panel video into the workspace.",
            "Transcribe the panelists' Japanese dialogue into timestamped SRT segments.",
            "Translate the Japanese SRT segments into matching English subtitles.",
            "Compose the panel video with bilingual Japanese-English subtitles burned onto the frames.",
        ],
    },
    {
        "user_goal": "Please add both French and English subtitles to this interview with a French chef.",
        "rationale": (
            "French-spoken chef interview + request for French + English bilingual subtitles. "
            "IntakeVideoAgent ingests the interview. TranscriptionAgent extracts French speech. "
            "TranslationAgent produces English translations. CompositorAgent burns both language "
            "tracks onto the interview. No audio overlay, no trimming, no restyle requested."
        ),
        "intents": [
            "Ingest the French-chef interview video into the workspace.",
            "Transcribe the chef's French speech into timestamped SRT segments.",
            "Translate the French SRT segments into matching English subtitles.",
            "Compose the final video with bilingual French-English subtitles burned onto the interview footage.",
        ],
    },
    {
        "user_goal": "I need English and Spanish subtitles on this Spanish-language soccer commentary. Both languages burned onto the video.",
        "rationale": (
            "Spanish-spoken soccer commentary + request for Spanish + English bilingual captions. "
            "IntakeVideoAgent ingests the commentary. TranscriptionAgent transcribes Spanish "
            "speech. TranslationAgent produces English translations. CompositorAgent burns both "
            "language subtitles onto the commentary video."
        ),
        "intents": [
            "Ingest the Spanish-language soccer commentary into the workspace.",
            "Transcribe the announcer's Spanish commentary into timestamped SRT segments.",
            "Translate the Spanish SRT segments into matching English subtitles.",
            "Compose the commentary video with bilingual Spanish-English subtitles burned in.",
        ],
    },
    {
        "user_goal": "Please burn Korean and English bilingual captions onto this K-drama trailer.",
        "rationale": (
            "Korean-spoken K-drama trailer + request for Korean + English bilingual captions. "
            "IntakeVideoAgent ingests the trailer. TranscriptionAgent transcribes the Korean "
            "dialogue. TranslationAgent produces English translations. CompositorAgent burns "
            "both languages onto the trailer."
        ),
        "intents": [
            "Ingest the K-drama trailer video into the workspace.",
            "Transcribe the Korean dialogue into timestamped SRT segments.",
            "Translate the Korean SRT segments into matching English subtitles.",
            "Compose the trailer with bilingual Korean-English subtitles burned onto the frames.",
        ],
    },
    {
        "user_goal": "Add Italian-English bilingual subtitles to this Italian wine-making documentary clip.",
        "rationale": (
            "Italian-narrated wine-making doc clip + request for Italian + English bilingual "
            "captions. IntakeVideoAgent ingests the clip. TranscriptionAgent transcribes Italian "
            "speech. TranslationAgent produces English translations. CompositorAgent burns both "
            "languages onto the clip."
        ),
        "intents": [
            "Ingest the Italian wine-making documentary clip into the workspace.",
            "Transcribe the Italian narrator's speech into timestamped SRT segments.",
            "Translate the Italian SRT segments into matching English subtitles.",
            "Compose the doc clip with bilingual Italian-English subtitles burned onto the footage.",
        ],
    },
    {
        "user_goal": "Please add Portuguese and English subtitles to this Brazilian surf-competition broadcast clip.",
        "rationale": (
            "Brazilian-Portuguese surf-broadcast + request for Portuguese + English bilingual "
            "subtitles. IntakeVideoAgent ingests the broadcast clip. TranscriptionAgent "
            "transcribes the Portuguese commentary. TranslationAgent produces English. "
            "CompositorAgent burns both tracks onto the clip."
        ),
        "intents": [
            "Ingest the Brazilian-Portuguese surf-competition broadcast clip into the workspace.",
            "Transcribe the Portuguese surf commentary into timestamped SRT segments.",
            "Translate the Portuguese SRT segments into matching English subtitles.",
            "Compose the broadcast clip with bilingual Portuguese-English subtitles burned in.",
        ],
    },
    {
        "user_goal": "Add German and English bilingual captions to this German tech-demo video.",
        "rationale": (
            "German-spoken tech-demo + request for German + English bilingual captions. "
            "IntakeVideoAgent ingests the demo. TranscriptionAgent transcribes German speech. "
            "TranslationAgent produces English translations. CompositorAgent burns both "
            "languages onto the demo."
        ),
        "intents": [
            "Ingest the German tech-demo video into the workspace.",
            "Transcribe the presenter's German speech into timestamped SRT segments.",
            "Translate the German SRT segments into matching English subtitles.",
            "Compose the demo video with bilingual German-English subtitles burned onto the frames.",
        ],
    },
    {
        "user_goal": "Please add Arabic and English subtitles to this Arabic-language news interview.",
        "rationale": (
            "Arabic-spoken news interview + request for Arabic + English bilingual captions. "
            "IntakeVideoAgent ingests the interview. TranscriptionAgent transcribes Arabic "
            "speech. TranslationAgent produces English translations. CompositorAgent burns "
            "both tracks onto the interview."
        ),
        "intents": [
            "Ingest the Arabic-language news interview into the workspace.",
            "Transcribe the Arabic interview dialogue into timestamped SRT segments.",
            "Translate the Arabic SRT segments into matching English subtitles.",
            "Compose the interview with bilingual Arabic-English subtitles burned onto the footage.",
        ],
    },
    {
        "user_goal": "Please burn Russian and English bilingual subtitles onto this Russian street-vendor interview.",
        "rationale": (
            "Russian-spoken street-vendor interview + request for Russian + English bilingual "
            "captions. IntakeVideoAgent ingests the interview. TranscriptionAgent transcribes "
            "Russian speech. TranslationAgent produces English translations. CompositorAgent "
            "burns both languages onto the footage."
        ),
        "intents": [
            "Ingest the Russian street-vendor interview video into the workspace.",
            "Transcribe the Russian dialogue into timestamped SRT segments.",
            "Translate the Russian SRT segments into matching English subtitles.",
            "Compose the interview with bilingual Russian-English subtitles burned in.",
        ],
    },
    {
        "user_goal": "Add Hindi and English bilingual captions to this Bollywood behind-the-scenes clip.",
        "rationale": (
            "Hindi-spoken Bollywood BTS clip + request for Hindi + English bilingual captions. "
            "IntakeVideoAgent ingests the clip. TranscriptionAgent transcribes Hindi speech. "
            "TranslationAgent produces English translations. CompositorAgent burns both tracks."
        ),
        "intents": [
            "Ingest the Bollywood behind-the-scenes clip into the workspace.",
            "Transcribe the Hindi BTS dialogue into timestamped SRT segments.",
            "Translate the Hindi SRT segments into matching English subtitles.",
            "Compose the BTS clip with bilingual Hindi-English subtitles burned onto the footage.",
        ],
    },
    {
        "user_goal": "Please add Vietnamese and English subtitles to this Vietnamese pho-making tutorial.",
        "rationale": (
            "Vietnamese-spoken pho tutorial + request for Vietnamese + English bilingual "
            "captions. IntakeVideoAgent ingests the tutorial. TranscriptionAgent transcribes "
            "Vietnamese narration. TranslationAgent produces English translations. "
            "CompositorAgent burns both tracks onto the tutorial."
        ),
        "intents": [
            "Ingest the Vietnamese pho-making tutorial video into the workspace.",
            "Transcribe the instructor's Vietnamese narration into timestamped SRT segments.",
            "Translate the Vietnamese SRT segments into matching English subtitles.",
            "Compose the tutorial with bilingual Vietnamese-English subtitles burned onto the cooking footage.",
        ],
    },
    {
        "user_goal": "Add Thai-English bilingual subtitles to this Thai muay-thai training clip.",
        "rationale": (
            "Thai-coached muay-thai clip + request for Thai + English bilingual captions. "
            "IntakeVideoAgent ingests the clip. TranscriptionAgent transcribes Thai coaching "
            "cues. TranslationAgent produces English translations. CompositorAgent burns both "
            "languages onto the training clip."
        ),
        "intents": [
            "Ingest the Thai muay-thai training clip into the workspace.",
            "Transcribe the trainer's Thai coaching cues into timestamped SRT segments.",
            "Translate the Thai SRT segments into matching English subtitles.",
            "Compose the training clip with bilingual Thai-English subtitles burned in.",
        ],
    },
    {
        "user_goal": "Please put Dutch and English bilingual captions on this Dutch tulip-farm tour video.",
        "rationale": (
            "Dutch-narrated tulip-farm tour + request for Dutch + English bilingual captions. "
            "IntakeVideoAgent ingests the tour video. TranscriptionAgent transcribes Dutch "
            "narration. TranslationAgent produces English translations. CompositorAgent burns "
            "both languages onto the tour."
        ),
        "intents": [
            "Ingest the Dutch tulip-farm tour video into the workspace.",
            "Transcribe the guide's Dutch narration into timestamped SRT segments.",
            "Translate the Dutch SRT segments into matching English subtitles.",
            "Compose the tour with bilingual Dutch-English subtitles burned onto the tulip-farm footage.",
        ],
    },
    {
        "user_goal": "Add Turkish and English bilingual subtitles to this Turkish kebab-shop interview.",
        "rationale": (
            "Turkish-spoken kebab-shop interview + request for Turkish + English bilingual "
            "captions. IntakeVideoAgent ingests the interview. TranscriptionAgent transcribes "
            "Turkish speech. TranslationAgent produces English translations. CompositorAgent "
            "burns both tracks."
        ),
        "intents": [
            "Ingest the Turkish kebab-shop interview video into the workspace.",
            "Transcribe the Turkish dialogue into timestamped SRT segments.",
            "Translate the Turkish SRT segments into matching English subtitles.",
            "Compose the interview with bilingual Turkish-English subtitles burned onto the footage.",
        ],
    },
    {
        "user_goal": "Please burn Greek and English bilingual captions onto this Greek-Orthodox wedding ceremony clip.",
        "rationale": (
            "Greek-language wedding ceremony clip + request for Greek + English bilingual "
            "captions. IntakeVideoAgent ingests the ceremony. TranscriptionAgent transcribes "
            "Greek liturgy + vows. TranslationAgent produces English translations. "
            "CompositorAgent burns both tracks onto the ceremony video."
        ),
        "intents": [
            "Ingest the Greek-Orthodox wedding ceremony clip into the workspace.",
            "Transcribe the Greek ceremony dialogue and liturgy into timestamped SRT segments.",
            "Translate the Greek SRT segments into matching English subtitles.",
            "Compose the ceremony with bilingual Greek-English subtitles burned onto the footage.",
        ],
    },
    {
        "user_goal": "Add Polish and English subtitles to this Polish animated short-film clip.",
        "rationale": (
            "Polish-narrated animated short + request for Polish + English bilingual captions. "
            "IntakeVideoAgent ingests the short film. TranscriptionAgent transcribes the "
            "Polish narration. TranslationAgent produces English translations. CompositorAgent "
            "burns both languages onto the short."
        ),
        "intents": [
            "Ingest the Polish animated short-film clip into the workspace.",
            "Transcribe the Polish narration into timestamped SRT segments.",
            "Translate the Polish SRT segments into matching English subtitles.",
            "Compose the short film with bilingual Polish-English subtitles burned onto the animation.",
        ],
    },
    {
        "user_goal": "Please put Finnish and English bilingual captions on this Finnish sauna-culture documentary clip.",
        "rationale": (
            "Finnish-narrated sauna-culture doc + request for Finnish + English bilingual "
            "captions. IntakeVideoAgent ingests the clip. TranscriptionAgent transcribes "
            "Finnish narration. TranslationAgent produces English translations. "
            "CompositorAgent burns both tracks."
        ),
        "intents": [
            "Ingest the Finnish sauna-culture documentary clip into the workspace.",
            "Transcribe the Finnish narration into timestamped SRT segments.",
            "Translate the Finnish SRT segments into matching English subtitles.",
            "Compose the documentary with bilingual Finnish-English subtitles burned onto the sauna footage.",
        ],
    },
    {
        "user_goal": "Add Czech and English bilingual subtitles to this Czech beer-brewery tour video.",
        "rationale": (
            "Czech-narrated brewery tour + request for Czech + English bilingual captions. "
            "IntakeVideoAgent ingests the tour. TranscriptionAgent transcribes Czech narration. "
            "TranslationAgent produces English translations. CompositorAgent burns both tracks."
        ),
        "intents": [
            "Ingest the Czech brewery-tour video into the workspace.",
            "Transcribe the tour guide's Czech narration into timestamped SRT segments.",
            "Translate the Czech SRT segments into matching English subtitles.",
            "Compose the brewery tour with bilingual Czech-English subtitles burned onto the footage.",
        ],
    },
    {
        "user_goal": "Please burn Swedish and English bilingual captions onto this Swedish midsummer-festival video.",
        "rationale": (
            "Swedish-narrated midsummer-festival video + request for Swedish + English bilingual "
            "captions. IntakeVideoAgent ingests the video. TranscriptionAgent transcribes "
            "Swedish narration. TranslationAgent produces English translations. CompositorAgent "
            "burns both tracks onto the festival video."
        ),
        "intents": [
            "Ingest the Swedish midsummer-festival video into the workspace.",
            "Transcribe the Swedish narrator and festival dialogue into timestamped SRT segments.",
            "Translate the Swedish SRT segments into matching English subtitles.",
            "Compose the festival video with bilingual Swedish-English subtitles burned onto the footage.",
        ],
    },
    {
        "user_goal": "Add Indonesian and English bilingual subtitles to this Indonesian beach-vendor documentary.",
        "rationale": (
            "Indonesian beach-vendor doc + request for Indonesian + English bilingual captions. "
            "IntakeVideoAgent ingests the doc. TranscriptionAgent transcribes Indonesian speech. "
            "TranslationAgent produces English translations. CompositorAgent burns both tracks."
        ),
        "intents": [
            "Ingest the Indonesian beach-vendor documentary into the workspace.",
            "Transcribe the Indonesian dialogue into timestamped SRT segments.",
            "Translate the Indonesian SRT segments into matching English subtitles.",
            "Compose the documentary with bilingual Indonesian-English subtitles burned onto the beach footage.",
        ],
    },
    {
        "user_goal": "Please burn Hebrew and English bilingual captions onto this Hebrew-language prayer-service video.",
        "rationale": (
            "Hebrew-spoken prayer-service + request for Hebrew + English bilingual captions. "
            "IntakeVideoAgent ingests the service. TranscriptionAgent transcribes Hebrew "
            "liturgy. TranslationAgent produces English translations. CompositorAgent burns "
            "both tracks onto the prayer-service video."
        ),
        "intents": [
            "Ingest the Hebrew prayer-service video into the workspace.",
            "Transcribe the Hebrew prayer liturgy into timestamped SRT segments.",
            "Translate the Hebrew SRT segments into matching English subtitles.",
            "Compose the prayer service with bilingual Hebrew-English subtitles burned onto the footage.",
        ],
    },
    {
        "user_goal": "Add Ukrainian and English bilingual subtitles to this Ukrainian folk-dance festival clip.",
        "rationale": (
            "Ukrainian-narrated folk-dance festival + request for Ukrainian + English bilingual "
            "captions. IntakeVideoAgent ingests the clip. TranscriptionAgent transcribes "
            "Ukrainian narration. TranslationAgent produces English translations. CompositorAgent "
            "burns both tracks onto the festival clip."
        ),
        "intents": [
            "Ingest the Ukrainian folk-dance festival clip into the workspace.",
            "Transcribe the Ukrainian narration into timestamped SRT segments.",
            "Translate the Ukrainian SRT segments into matching English subtitles.",
            "Compose the festival clip with bilingual Ukrainian-English subtitles burned onto the footage.",
        ],
    },
    {
        "user_goal": "Please put Norwegian and English bilingual captions on this Norwegian fjord-hiking vlog.",
        "rationale": (
            "Norwegian-narrated fjord-hiking vlog + request for Norwegian + English bilingual "
            "captions. IntakeVideoAgent ingests the vlog. TranscriptionAgent transcribes "
            "Norwegian narration. TranslationAgent produces English translations. "
            "CompositorAgent burns both tracks."
        ),
        "intents": [
            "Ingest the Norwegian fjord-hiking vlog into the workspace.",
            "Transcribe the Norwegian vlogger's narration into timestamped SRT segments.",
            "Translate the Norwegian SRT segments into matching English subtitles.",
            "Compose the vlog with bilingual Norwegian-English subtitles burned onto the hiking footage.",
        ],
    },
    {
        "user_goal": "Add Cantonese and English bilingual subtitles to this Cantonese dim-sum-restaurant interview.",
        "rationale": (
            "Cantonese-spoken dim-sum interview + request for Cantonese + English bilingual "
            "captions. IntakeVideoAgent ingests the interview. TranscriptionAgent transcribes "
            "Cantonese speech. TranslationAgent produces English translations. CompositorAgent "
            "burns both tracks onto the interview."
        ),
        "intents": [
            "Ingest the Cantonese dim-sum-restaurant interview video into the workspace.",
            "Transcribe the Cantonese interview dialogue into timestamped SRT segments.",
            "Translate the Cantonese SRT segments into matching English subtitles.",
            "Compose the interview with bilingual Cantonese-English subtitles burned onto the footage.",
        ],
    },
    {
        "user_goal": "Please burn Tagalog and English bilingual captions onto this Filipino street-food vlog.",
        "rationale": (
            "Tagalog-narrated street-food vlog + request for Tagalog + English bilingual "
            "captions. IntakeVideoAgent ingests the vlog. TranscriptionAgent transcribes "
            "Tagalog narration. TranslationAgent produces English translations. CompositorAgent "
            "burns both tracks onto the vlog."
        ),
        "intents": [
            "Ingest the Filipino street-food vlog into the workspace.",
            "Transcribe the Tagalog vlogger narration into timestamped SRT segments.",
            "Translate the Tagalog SRT segments into matching English subtitles.",
            "Compose the vlog with bilingual Tagalog-English subtitles burned onto the street-food footage.",
        ],
    },
    {
        "user_goal": "Add Bengali and English bilingual subtitles to this Bengali cultural-dance performance clip.",
        "rationale": (
            "Bengali-language cultural-dance performance + request for Bengali + English "
            "bilingual captions. IntakeVideoAgent ingests the clip. TranscriptionAgent "
            "transcribes Bengali narration. TranslationAgent produces English. CompositorAgent "
            "burns both tracks onto the performance clip."
        ),
        "intents": [
            "Ingest the Bengali cultural-dance performance clip into the workspace.",
            "Transcribe the Bengali narration into timestamped SRT segments.",
            "Translate the Bengali SRT segments into matching English subtitles.",
            "Compose the performance with bilingual Bengali-English subtitles burned onto the dance footage.",
        ],
    },
    {
        "user_goal": "Please put Malay and English bilingual captions on this Malay nasi-lemak cooking tutorial.",
        "rationale": (
            "Malay-narrated nasi-lemak tutorial + request for Malay + English bilingual captions. "
            "IntakeVideoAgent ingests the tutorial. TranscriptionAgent transcribes Malay "
            "narration. TranslationAgent produces English. CompositorAgent burns both tracks "
            "onto the tutorial."
        ),
        "intents": [
            "Ingest the Malay nasi-lemak cooking tutorial into the workspace.",
            "Transcribe the cook's Malay narration into timestamped SRT segments.",
            "Translate the Malay SRT segments into matching English subtitles.",
            "Compose the tutorial with bilingual Malay-English subtitles burned onto the cooking footage.",
        ],
    },
    {
        "user_goal": "Add Romanian and English bilingual captions to this Romanian traditional-wedding ceremony clip.",
        "rationale": (
            "Romanian wedding-ceremony clip + request for Romanian + English bilingual captions. "
            "IntakeVideoAgent ingests the clip. TranscriptionAgent transcribes Romanian speech "
            "and ceremony dialogue. TranslationAgent produces English. CompositorAgent burns "
            "both tracks onto the ceremony video."
        ),
        "intents": [
            "Ingest the Romanian wedding-ceremony clip into the workspace.",
            "Transcribe the Romanian ceremony dialogue into timestamped SRT segments.",
            "Translate the Romanian SRT segments into matching English subtitles.",
            "Compose the ceremony with bilingual Romanian-English subtitles burned onto the footage.",
        ],
    },
    {
        "user_goal": "Please burn Persian-English bilingual captions onto this Persian-language poetry-reading clip.",
        "rationale": (
            "Persian-spoken poetry reading + request for Persian + English bilingual captions. "
            "IntakeVideoAgent ingests the clip. TranscriptionAgent transcribes the Persian "
            "recitation into SRT. TranslationAgent produces English translations. "
            "CompositorAgent burns both tracks onto the reading."
        ),
        "intents": [
            "Ingest the Persian poetry-reading clip into the workspace.",
            "Transcribe the Persian recitation into timestamped SRT segments.",
            "Translate the Persian SRT segments into matching English subtitles.",
            "Compose the reading with bilingual Persian-English subtitles burned onto the footage.",
        ],
    },
    {
        "user_goal": "Add Hungarian and English bilingual subtitles to this Hungarian goulash-cooking demo.",
        "rationale": (
            "Hungarian-narrated goulash demo + request for Hungarian + English bilingual "
            "captions. IntakeVideoAgent ingests the demo. TranscriptionAgent transcribes "
            "Hungarian narration. TranslationAgent produces English translations. "
            "CompositorAgent burns both tracks onto the demo."
        ),
        "intents": [
            "Ingest the Hungarian goulash-cooking demo into the workspace.",
            "Transcribe the Hungarian cook's narration into timestamped SRT segments.",
            "Translate the Hungarian SRT segments into matching English subtitles.",
            "Compose the demo with bilingual Hungarian-English subtitles burned onto the cooking footage.",
        ],
    },
    {
        "user_goal": "Please put Danish and English bilingual captions on this Danish architecture-tour video.",
        "rationale": (
            "Danish-narrated architecture tour + request for Danish + English bilingual captions. "
            "IntakeVideoAgent ingests the tour. TranscriptionAgent transcribes Danish narration. "
            "TranslationAgent produces English translations. CompositorAgent burns both tracks."
        ),
        "intents": [
            "Ingest the Danish architecture-tour video into the workspace.",
            "Transcribe the Danish narrator's commentary into timestamped SRT segments.",
            "Translate the Danish SRT segments into matching English subtitles.",
            "Compose the tour with bilingual Danish-English subtitles burned onto the architecture footage.",
        ],
    },
    {
        "user_goal": "Add Swahili and English bilingual subtitles to this Swahili safari-guide commentary.",
        "rationale": (
            "Swahili-narrated safari guide + request for Swahili + English bilingual captions. "
            "IntakeVideoAgent ingests the commentary. TranscriptionAgent transcribes the Swahili "
            "narration. TranslationAgent produces English translations. CompositorAgent burns "
            "both tracks onto the safari video."
        ),
        "intents": [
            "Ingest the Swahili safari-guide commentary video into the workspace.",
            "Transcribe the Swahili guide's narration into timestamped SRT segments.",
            "Translate the Swahili SRT segments into matching English subtitles.",
            "Compose the commentary video with bilingual Swahili-English subtitles burned onto the safari footage.",
        ],
    },
    {
        "user_goal": "Please burn Icelandic and English bilingual captions onto this Icelandic glacier-hiking vlog.",
        "rationale": (
            "Icelandic-narrated glacier-hiking vlog + request for Icelandic + English bilingual "
            "captions. IntakeVideoAgent ingests the vlog. TranscriptionAgent transcribes "
            "Icelandic narration. TranslationAgent produces English translations. "
            "CompositorAgent burns both tracks onto the hiking footage."
        ),
        "intents": [
            "Ingest the Icelandic glacier-hiking vlog into the workspace.",
            "Transcribe the Icelandic narration into timestamped SRT segments.",
            "Translate the Icelandic SRT segments into matching English subtitles.",
            "Compose the vlog with bilingual Icelandic-English subtitles burned onto the glacier footage.",
        ],
    },
    {
        "user_goal": "Add Slovak and English bilingual subtitles to this Slovak folk-music performance video.",
        "rationale": (
            "Slovak folk-music performance + request for Slovak + English bilingual captions. "
            "IntakeVideoAgent ingests the performance video. TranscriptionAgent transcribes "
            "Slovak spoken intros / announcements. TranslationAgent produces English. "
            "CompositorAgent burns both tracks."
        ),
        "intents": [
            "Ingest the Slovak folk-music performance video into the workspace.",
            "Transcribe the Slovak introductions and announcements into timestamped SRT segments.",
            "Translate the Slovak SRT segments into matching English subtitles.",
            "Compose the performance with bilingual Slovak-English subtitles burned onto the stage footage.",
        ],
    },
    {
        "user_goal": "Please add Croatian and English bilingual captions to this Croatian coastal-town walking-tour.",
        "rationale": (
            "Croatian-narrated coastal walking-tour + request for Croatian + English bilingual "
            "captions. IntakeVideoAgent ingests the tour. TranscriptionAgent transcribes Croatian "
            "narration. TranslationAgent produces English translations. CompositorAgent burns "
            "both tracks onto the tour video."
        ),
        "intents": [
            "Ingest the Croatian coastal walking-tour video into the workspace.",
            "Transcribe the Croatian guide's narration into timestamped SRT segments.",
            "Translate the Croatian SRT segments into matching English subtitles.",
            "Compose the tour with bilingual Croatian-English subtitles burned onto the coastal footage.",
        ],
    },
    {
        "user_goal": "Add Serbian and English bilingual captions to this Serbian documentary on Belgrade's history.",
        "rationale": (
            "Serbian-narrated Belgrade-history doc + request for Serbian + English bilingual "
            "captions. IntakeVideoAgent ingests the doc. TranscriptionAgent transcribes Serbian "
            "narration. TranslationAgent produces English. CompositorAgent burns both tracks."
        ),
        "intents": [
            "Ingest the Serbian Belgrade-history documentary into the workspace.",
            "Transcribe the Serbian narration into timestamped SRT segments.",
            "Translate the Serbian SRT segments into matching English subtitles.",
            "Compose the documentary with bilingual Serbian-English subtitles burned onto the Belgrade footage.",
        ],
    },
    {
        "user_goal": "Please put Bulgarian and English bilingual captions on this Bulgarian rose-oil-distillery tour clip.",
        "rationale": (
            "Bulgarian-narrated rose-oil distillery tour + request for Bulgarian + English "
            "bilingual captions. IntakeVideoAgent ingests the tour. TranscriptionAgent "
            "transcribes Bulgarian narration. TranslationAgent produces English translations. "
            "CompositorAgent burns both tracks onto the tour."
        ),
        "intents": [
            "Ingest the Bulgarian rose-oil-distillery tour clip into the workspace.",
            "Transcribe the tour guide's Bulgarian narration into timestamped SRT segments.",
            "Translate the Bulgarian SRT segments into matching English subtitles.",
            "Compose the tour clip with bilingual Bulgarian-English subtitles burned onto the distillery footage.",
        ],
    },
    {
        "user_goal": "Add Lithuanian and English bilingual subtitles to this Lithuanian amber-jewelry documentary.",
        "rationale": (
            "Lithuanian-narrated amber-jewelry doc + request for Lithuanian + English bilingual "
            "captions. IntakeVideoAgent ingests the doc. TranscriptionAgent transcribes "
            "Lithuanian narration. TranslationAgent produces English. CompositorAgent burns "
            "both tracks."
        ),
        "intents": [
            "Ingest the Lithuanian amber-jewelry documentary into the workspace.",
            "Transcribe the Lithuanian narration into timestamped SRT segments.",
            "Translate the Lithuanian SRT segments into matching English subtitles.",
            "Compose the doc with bilingual Lithuanian-English subtitles burned onto the amber-jewelry footage.",
        ],
    },
    {
        "user_goal": "Please burn Urdu and English bilingual captions onto this Urdu-poetry-reading clip.",
        "rationale": (
            "Urdu-spoken poetry reading + request for Urdu + English bilingual captions. "
            "IntakeVideoAgent ingests the clip. TranscriptionAgent transcribes the Urdu "
            "recitation. TranslationAgent produces English translations. CompositorAgent burns "
            "both tracks onto the reading."
        ),
        "intents": [
            "Ingest the Urdu poetry-reading clip into the workspace.",
            "Transcribe the Urdu poetry recitation into timestamped SRT segments.",
            "Translate the Urdu SRT segments into matching English subtitles.",
            "Compose the reading with bilingual Urdu-English subtitles burned onto the footage.",
        ],
    },
]
