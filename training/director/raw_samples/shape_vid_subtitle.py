"""Shape: vid_subtitle — IntakeVideo → Transcription → Compositor.

User uploaded a video and asks for monolingual subtitles ONLY — no audio
overlay, no style change, no highlight extraction, no translation.

Reject biases:
  - VideoAnalysisAgent / HighlightAgent (no analysis or highlight ask)
  - TranslationAgent (monolingual request, not bilingual)
  - MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay ask)
  - StyleTransferAgent / VideoExtendAgent (no style / length change)

Rationale style mix: standard "reject bucket" (~60%), positive-only
framing (~20%), more narrative (~20%) — prevents the LoRA from learning a
single rationale template.
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Add English subtitles to this lecture recording — the speaker is already speaking English, I just need the captions burned onto the video.",
        "rationale": (
            "User uploaded a video and asks only for monolingual English subtitles — same language "
            "as the spoken audio. IntakeVideoAgent ingests the uploaded recording. TranscriptionAgent "
            "extracts timestamped English segments from the speech. CompositorAgent burns the SRT "
            "onto the frames. Reject VideoAnalysisAgent (no analysis requested), TranslationAgent "
            "(user explicitly wants English-only, not bilingual), MusicAgent / AmbienceAgent / "
            "AudioMixAgent (no audio overlay mentioned), and StyleTransferAgent / VideoExtendAgent "
            "(no style change or length change asked for)."
        ),
        "intents": [
            "Ingest the uploaded lecture recording into the workspace as the source video artifact.",
            "Transcribe the English-language lecturer speech into timestamped SRT segments.",
            "Burn the English SRT captions onto the lecture video and output the final subtitled file.",
        ],
    },
    {
        "user_goal": "I have a cooking demo clip I shot on my phone — please burn Chinese subtitles onto it so my relatives can follow along. The chef speaks Mandarin already.",
        "rationale": (
            "User uploaded a Mandarin-spoken cooking clip and only wants Mandarin (Chinese) "
            "subtitles added — no language change, no audio swap, no style. IntakeVideoAgent loads "
            "the phone-shot clip. TranscriptionAgent produces timestamped Mandarin segments from "
            "the chef's narration. CompositorAgent burns the Chinese SRT onto the clip. Reject "
            "TranslationAgent (same-language subtitles, no bilingual request), MusicAgent / "
            "AmbienceAgent (user didn't ask for BGM or ambient), HighlightAgent / VideoAnalysisAgent "
            "(no trimming / analysis ask)."
        ),
        "intents": [
            "Ingest the phone-shot cooking demo clip into the workspace.",
            "Transcribe the chef's Mandarin narration into timestamped SRT lines.",
            "Burn the Mandarin subtitles onto the cooking video and deliver the final captioned cut.",
        ],
    },
    {
        "user_goal": "Please add captions to this interview I did last week. Just English captions that match what we said, no translation.",
        "rationale": (
            "User wants same-language English captions on an existing interview recording. "
            "IntakeVideoAgent loads the interview. TranscriptionAgent extracts English segments "
            "from the dialogue. CompositorAgent overlays the SRT. Reject TranslationAgent (no "
            "bilingual), reject VideoAnalysisAgent / HighlightAgent (no edit / highlight ask), "
            "reject MusicAgent and AmbienceAgent (no audio overlay), reject StyleTransferAgent "
            "(no visual style change)."
        ),
        "intents": [
            "Ingest the interview recording into the workspace.",
            "Transcribe the English interview dialogue into timestamped caption segments.",
            "Compose the final video with English captions burned onto the interview frames.",
        ],
    },
    {
        "user_goal": "Here's a TED-style talk I gave. Can you auto-caption it in English? I want the captions permanently rendered on the video, not a separate SRT file.",
        "rationale": (
            "User has a talk video and wants hard-burned English captions (not a sidecar SRT). "
            "IntakeVideoAgent loads the talk. TranscriptionAgent produces timestamped English "
            "segments. CompositorAgent renders the captions permanently onto the frames. Reject "
            "TranslationAgent (single language requested), VideoAnalysisAgent (no content analysis "
            "needed to caption), HighlightAgent (user wants the full talk captioned, not trimmed), "
            "MusicAgent / AmbienceAgent / AudioMixAgent (no audio changes)."
        ),
        "intents": [
            "Ingest the TED-style talk recording into the workspace.",
            "Transcribe the English talk into timestamped SRT segments.",
            "Burn the English captions permanently onto the talk video and export the hard-subbed cut.",
        ],
    },
    {
        "user_goal": "I recorded a 15-minute company all-hands in Japanese. Please transcribe it and burn Japanese subtitles onto the video.",
        "rationale": (
            "Japanese-spoken all-hands + request for same-language Japanese subtitles burned in. "
            "IntakeVideoAgent ingests the 15-minute recording. TranscriptionAgent transcribes the "
            "Japanese speech into timestamped SRT. CompositorAgent burns Japanese captions on the "
            "frames. Reject TranslationAgent (no bilingual request), VideoAnalysisAgent (no "
            "summarization / highlight ask), MusicAgent / AmbienceAgent (no audio layer), "
            "StyleTransferAgent (no look change)."
        ),
        "intents": [
            "Ingest the 15-minute Japanese all-hands recording into the workspace.",
            "Transcribe the Japanese speech into timestamped SRT caption segments.",
            "Compose the final video with Japanese captions burned onto the all-hands footage.",
        ],
    },
    {
        "user_goal": "My grandma's oral history interview is in Cantonese. Please add Cantonese subtitles so the family can read along while she speaks.",
        "rationale": (
            "Cantonese-spoken oral history + request for Cantonese (same-language) subtitles for "
            "family viewing. IntakeVideoAgent loads the interview. TranscriptionAgent transcribes "
            "the Cantonese speech to timestamped SRT. CompositorAgent burns Cantonese captions "
            "onto the video. Reject TranslationAgent (same language requested, not bilingual), "
            "VideoAnalysisAgent / HighlightAgent (no trimming), MusicAgent / AmbienceAgent (no "
            "audio overlay), StyleTransferAgent (no visual change)."
        ),
        "intents": [
            "Ingest grandma's Cantonese oral history interview into the workspace.",
            "Transcribe the Cantonese speech into timestamped SRT segments.",
            "Compose the final video with Cantonese subtitles burned onto the interview frames.",
        ],
    },
    {
        "user_goal": "Please add Spanish subtitles to this vlog — the vlogger is speaking Spanish, I just need captions for accessibility.",
        "rationale": (
            "Spanish-spoken vlog + request for Spanish (same-language) subtitles for accessibility. "
            "IntakeVideoAgent ingests the vlog. TranscriptionAgent transcribes Spanish speech into "
            "timestamped SRT. CompositorAgent overlays the captions. Reject TranslationAgent (no "
            "language pivot wanted), VideoAnalysisAgent / HighlightAgent (no content analysis "
            "required for simple captioning), MusicAgent / AmbienceAgent (no audio bed), "
            "StyleTransferAgent / VideoExtendAgent (no visual change or length adjustment)."
        ),
        "intents": [
            "Ingest the Spanish vlog into the workspace as the source video.",
            "Transcribe the vlogger's Spanish speech into timestamped SRT.",
            "Compose the final vlog with Spanish accessibility subtitles burned onto the frames.",
        ],
    },
    {
        "user_goal": "I have a podcast episode I recorded as video. Transcribe it and burn English captions — the hosts speak English.",
        "rationale": (
            "Video-podcast recording (English speech) + request for English captions burned in. "
            "IntakeVideoAgent ingests the video-podcast file. TranscriptionAgent extracts English "
            "dialogue into timestamped SRT. CompositorAgent burns captions. Reject "
            "TranslationAgent (single-language request), VideoAnalysisAgent / HighlightAgent (no "
            "segmenting / clip extraction), MusicAgent / AmbienceAgent / AudioMixAgent (no audio "
            "overlay), StyleTransferAgent (no look change)."
        ),
        "intents": [
            "Ingest the video-podcast recording into the workspace.",
            "Transcribe the English host dialogue into timestamped caption segments.",
            "Burn the English captions onto the podcast video and export the captioned version.",
        ],
    },
    {
        "user_goal": "Add French subtitles to this street-interview clip. The interviewer and respondents are all speaking French — I just need matching French captions.",
        "rationale": (
            "French street interview + request for same-language French subtitles. "
            "IntakeVideoAgent ingests the clip. TranscriptionAgent transcribes French speech to "
            "timestamped SRT. CompositorAgent burns French captions onto the clip. Reject "
            "TranslationAgent (no bilingual ask), HighlightAgent / VideoAnalysisAgent (no trimming "
            "or summarization), MusicAgent / AmbienceAgent (no audio change), StyleTransferAgent "
            "(no visual restyling)."
        ),
        "intents": [
            "Ingest the French street-interview clip into the workspace.",
            "Transcribe the French interviewer and respondent dialogue into timestamped SRT.",
            "Compose the final clip with French subtitles burned onto the street-interview footage.",
        ],
    },
    {
        "user_goal": "Please add Korean subtitles to this variety show clip — the hosts speak Korean, I only need Korean captions for deaf viewers.",
        "rationale": (
            "Korean-spoken variety clip + accessibility request for Korean-only subtitles. "
            "IntakeVideoAgent ingests the clip. TranscriptionAgent transcribes the Korean host "
            "banter into timestamped SRT. CompositorAgent burns Korean captions for deaf-viewer "
            "accessibility. Reject TranslationAgent (same-language request), VideoAnalysisAgent / "
            "HighlightAgent (no trimming), MusicAgent / AmbienceAgent / AudioMixAgent (no audio "
            "overlay), StyleTransferAgent / VideoExtendAgent (no visual / length change)."
        ),
        "intents": [
            "Ingest the Korean variety-show clip into the workspace.",
            "Transcribe the Korean hosts' speech into timestamped SRT caption segments.",
            "Burn Korean accessibility subtitles onto the variety clip and deliver the captioned cut.",
        ],
    },
    {
        "user_goal": "Could you add German subtitles to this kitchen-tutorial I shot for my YouTube channel? The instructor speaks German throughout.",
        "rationale": (
            "German-spoken kitchen tutorial + request for German captions to aid viewers. The "
            "flow is IntakeVideoAgent → TranscriptionAgent → CompositorAgent. TranscriptionAgent "
            "handles German speech natively into a timestamped SRT; CompositorAgent renders "
            "those captions onto the tutorial. Translation is not needed since the author wants "
            "German captions on German audio. No audio, style, or length modification was asked "
            "for, so Music / Ambience / AudioMix / StyleTransfer / VideoExtend stay out."
        ),
        "intents": [
            "Ingest the German-spoken kitchen tutorial into the workspace.",
            "Transcribe the instructor's German speech into timestamped SRT caption lines.",
            "Compose the final tutorial with German captions burned onto the footage.",
        ],
    },
    {
        "user_goal": "Please caption this Italian stand-up comedy set in Italian. The comedian speaks Italian — burn Italian subtitles directly onto the footage.",
        "rationale": (
            "Italian stand-up footage + request for Italian (same-language) captions burned in. "
            "IntakeVideoAgent loads the comedy set. TranscriptionAgent transcribes Italian speech "
            "including comedic timing into SRT. CompositorAgent burns captions. No translation "
            "since the author wants Italian-on-Italian; no audio edits since there's no BGM / "
            "ambient ask; no style transfer or highlight extraction since the whole set should "
            "remain intact."
        ),
        "intents": [
            "Ingest the Italian stand-up comedy set into the workspace.",
            "Transcribe the comedian's Italian monologue into timestamped SRT caption segments.",
            "Burn the Italian subtitles onto the full stand-up set and export the captioned cut.",
        ],
    },
    {
        "user_goal": "Add Portuguese subtitles to this soccer commentary video. The announcer speaks Brazilian Portuguese. Same-language captions, please.",
        "rationale": (
            "Brazilian-Portuguese soccer commentary + Portuguese captioning request. "
            "IntakeVideoAgent ingests the commentary video. TranscriptionAgent captures the "
            "announcer's Portuguese narration into timestamped SRT. CompositorAgent burns captions "
            "for viewer accessibility. TranslationAgent is unneeded (author specified same-language "
            "captions). No audio overlay, no highlight extraction, no visual restyle."
        ),
        "intents": [
            "Ingest the Brazilian-Portuguese soccer commentary video into the workspace.",
            "Transcribe the announcer's Portuguese commentary into timestamped SRT segments.",
            "Compose the final video with Portuguese subtitles burned onto the commentary footage.",
        ],
    },
    {
        "user_goal": "I need Arabic subtitles added to this mosque sermon recording. The imam speaks Arabic — please match the captions to his spoken words.",
        "rationale": (
            "Arabic-spoken sermon + request for Arabic-matching captions. IntakeVideoAgent loads "
            "the sermon recording. TranscriptionAgent transcribes Arabic speech to a timestamped "
            "SRT, preserving the imam's delivery. CompositorAgent burns the Arabic captions onto "
            "the video. No translation, no audio edits, no trimming, no visual restyle — the "
            "sermon is presented in full with added captions only."
        ),
        "intents": [
            "Ingest the Arabic mosque sermon recording into the workspace.",
            "Transcribe the imam's Arabic spoken words into timestamped SRT caption lines.",
            "Burn the Arabic subtitles onto the sermon video and export the captioned recording.",
        ],
    },
    {
        "user_goal": "Hindi subtitles on this Bollywood-style dance tutorial, please. The instructor narrates in Hindi — match the captions to her narration.",
        "rationale": (
            "Hindi-narrated dance tutorial + Hindi captioning request. IntakeVideoAgent ingests "
            "the tutorial. TranscriptionAgent transcribes the instructor's Hindi narration into "
            "timestamped SRT. CompositorAgent overlays the captions on the tutorial. Reject "
            "TranslationAgent (same-language ask), reject MusicAgent / AmbienceAgent (the "
            "tutorial already has its original music baked into the video and no overlay was "
            "requested), reject StyleTransferAgent / VideoExtendAgent (no visual or length change)."
        ),
        "intents": [
            "Ingest the Hindi Bollywood-style dance tutorial video into the workspace.",
            "Transcribe the instructor's Hindi narration into timestamped SRT lines.",
            "Compose the tutorial with Hindi captions burned onto the dance footage.",
        ],
    },
    {
        "user_goal": "Russian subtitles needed on this documentary clip. The narrator speaks Russian; I'd like Russian captions under the narration.",
        "rationale": (
            "Russian-narrated documentary + Russian captioning. Flow: IntakeVideo → Transcription "
            "→ Compositor. TranscriptionAgent captures the Russian narration as timestamped SRT; "
            "CompositorAgent places Russian captions under the frame. No translation (matching "
            "language), no audio layer added, no trimming, no look change."
        ),
        "intents": [
            "Ingest the Russian documentary clip into the workspace.",
            "Transcribe the Russian narrator's speech into timestamped SRT caption segments.",
            "Burn Russian captions onto the documentary footage and export the captioned version.",
        ],
    },
    {
        "user_goal": "Please add Vietnamese subtitles on this travel-vlog clip from Hanoi. The vlogger speaks Vietnamese throughout — Vietnamese captions only, no translation.",
        "rationale": (
            "Vietnamese-spoken travel vlog + Vietnamese (monolingual) captioning. "
            "IntakeVideoAgent ingests the Hanoi vlog. TranscriptionAgent transcribes Vietnamese "
            "speech into timestamped SRT. CompositorAgent burns the Vietnamese captions onto the "
            "vlog. Reject TranslationAgent (monolingual requested), VideoAnalysisAgent / "
            "HighlightAgent (no trimming), MusicAgent / AmbienceAgent (no audio overlay), "
            "StyleTransferAgent (no restyling)."
        ),
        "intents": [
            "Ingest the Vietnamese Hanoi travel-vlog clip into the workspace.",
            "Transcribe the vlogger's Vietnamese speech into timestamped SRT segments.",
            "Compose the vlog with Vietnamese captions burned onto the travel footage.",
        ],
    },
    {
        "user_goal": "Add Thai subtitles on this Muay Thai training video. The trainer speaks Thai — match the Thai captions to his coaching cues.",
        "rationale": (
            "Thai-coached Muay Thai training video + Thai-on-Thai captioning. IntakeVideoAgent "
            "loads the training clip. TranscriptionAgent transcribes Thai coaching cues into "
            "timestamped SRT. CompositorAgent renders Thai captions onto the training footage. "
            "No translation, no audio overlay, no analysis or highlight reel, no style transfer."
        ),
        "intents": [
            "Ingest the Thai Muay Thai training video into the workspace.",
            "Transcribe the trainer's Thai coaching cues into timestamped SRT segments.",
            "Burn Thai captions onto the training clip and export the final captioned footage.",
        ],
    },
    {
        "user_goal": "I need English subtitles on this nature-documentary clip — the narrator speaks English, just want the captions burned in.",
        "rationale": (
            "English-narrated nature documentary + English caption request. IntakeVideoAgent "
            "ingests the clip. TranscriptionAgent transcribes the narrator into timestamped SRT. "
            "CompositorAgent burns the English captions into the clip. Reject TranslationAgent "
            "(English-on-English), VideoAnalysisAgent / HighlightAgent (full clip wanted), "
            "Music / Ambience / AudioMix (no audio overlay), Style / Extend (no visual or length "
            "change)."
        ),
        "intents": [
            "Ingest the nature-documentary clip into the workspace.",
            "Transcribe the English narration into timestamped SRT caption segments.",
            "Burn the English captions into the documentary footage and export the final cut.",
        ],
    },
    {
        "user_goal": "Please subtitle this Turkish wedding speech in Turkish — it's my uncle's toast, just need Turkish captions added for the deaf relatives.",
        "rationale": (
            "Turkish wedding toast + Turkish (monolingual) captioning for accessibility. "
            "IntakeVideoAgent ingests the toast recording. TranscriptionAgent transcribes the "
            "Turkish speech into timestamped SRT. CompositorAgent burns Turkish captions onto "
            "the recording so deaf relatives can follow. Reject TranslationAgent (same-language "
            "request), reject audio / visual / trimming agents — the toast should stay intact."
        ),
        "intents": [
            "Ingest the Turkish wedding-toast recording into the workspace.",
            "Transcribe the uncle's Turkish speech into timestamped SRT lines.",
            "Burn Turkish accessibility captions onto the toast video and deliver the captioned cut.",
        ],
    },
    {
        "user_goal": "Add Dutch subtitles to this museum guided-tour recording. The guide speaks Dutch — burn Dutch captions matching her narration.",
        "rationale": (
            "Dutch-guided museum tour + Dutch captioning ask. IntakeVideoAgent loads the tour "
            "recording. TranscriptionAgent transcribes Dutch narration into timestamped SRT. "
            "CompositorAgent burns Dutch captions onto the tour footage. No translation, no "
            "audio layer, no restyling, no highlighting or trimming — the full tour is captioned "
            "and delivered as-is."
        ),
        "intents": [
            "Ingest the Dutch museum guided-tour recording into the workspace.",
            "Transcribe the guide's Dutch narration into timestamped SRT caption segments.",
            "Compose the tour video with Dutch captions burned onto the museum footage.",
        ],
    },
    {
        "user_goal": "Polish captions on this Polish stand-up special, please. Same language — Polish speaker, Polish captions.",
        "rationale": (
            "Polish stand-up + Polish-on-Polish captions. IntakeVideoAgent ingests the special. "
            "TranscriptionAgent transcribes the Polish monologue to timestamped SRT including "
            "comedic cadence. CompositorAgent burns captions. Reject TranslationAgent (no pivot), "
            "VideoAnalysisAgent / HighlightAgent (no trimming requested), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / "
            "VideoExtendAgent (no visual or length change)."
        ),
        "intents": [
            "Ingest the Polish stand-up special video into the workspace.",
            "Transcribe the Polish stand-up monologue into timestamped SRT segments.",
            "Burn Polish captions onto the stand-up video and export the captioned version.",
        ],
    },
    {
        "user_goal": "Please add Swedish captions to this IKEA-style assembly walkthrough. The narrator speaks Swedish and I want Swedish subtitles underneath.",
        "rationale": (
            "Swedish-narrated assembly walkthrough + Swedish captioning. IntakeVideoAgent loads "
            "the walkthrough. TranscriptionAgent transcribes the Swedish narration into "
            "timestamped SRT. CompositorAgent burns Swedish subtitles under the frame. No "
            "translation, no audio layer, no restyle, no trimming or highlighting."
        ),
        "intents": [
            "Ingest the Swedish assembly walkthrough video into the workspace.",
            "Transcribe the narrator's Swedish instructions into timestamped SRT lines.",
            "Compose the walkthrough with Swedish captions burned onto the assembly footage.",
        ],
    },
    {
        "user_goal": "Hebrew subtitles on this bar-mitzvah speech video, please. The speaker speaks Hebrew — Hebrew-on-Hebrew captions.",
        "rationale": (
            "Hebrew bar-mitzvah speech + Hebrew-matching captions. IntakeVideoAgent ingests the "
            "recording. TranscriptionAgent transcribes the Hebrew speech into timestamped SRT. "
            "CompositorAgent burns the Hebrew captions onto the ceremonial footage. No "
            "translation (matching language), no audio overlay, no highlight extraction, no "
            "visual style change — the speech is delivered intact with captions added."
        ),
        "intents": [
            "Ingest the Hebrew bar-mitzvah speech video into the workspace.",
            "Transcribe the Hebrew speech into timestamped SRT caption segments.",
            "Burn Hebrew captions onto the bar-mitzvah recording and export the final captioned video.",
        ],
    },
    {
        "user_goal": "Please caption this online Q&A panel in English — all panelists speak English, just burn captions in.",
        "rationale": (
            "English-spoken Q&A panel + English captioning. IntakeVideoAgent ingests the panel "
            "recording. TranscriptionAgent transcribes all panelist dialogue including Q&A turns "
            "into timestamped SRT. CompositorAgent burns English captions onto the panel video. "
            "Reject TranslationAgent (English-on-English), VideoAnalysisAgent / HighlightAgent "
            "(no trimming or Q&A extraction ask — full panel captioned), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent (no visual "
            "change)."
        ),
        "intents": [
            "Ingest the English Q&A panel recording into the workspace.",
            "Transcribe all panelist dialogue across Q&A turns into timestamped SRT segments.",
            "Burn English captions onto the full Q&A panel video and export the captioned recording.",
        ],
    },
    {
        "user_goal": "Add subtitles in English to this conference keynote. The speaker presents in English — just caption it for the live-stream replay.",
        "rationale": (
            "English keynote + English captioning for live-stream replay. IntakeVideoAgent loads "
            "the keynote file. TranscriptionAgent captures the speaker's English presentation "
            "into timestamped SRT. CompositorAgent burns captions onto the keynote video for "
            "replay viewers. No translation, no audio edits, no trimming, no visual restyle."
        ),
        "intents": [
            "Ingest the English conference keynote recording into the workspace.",
            "Transcribe the speaker's English presentation into timestamped SRT captions.",
            "Burn English captions onto the keynote video and export the replay-ready captioned cut.",
        ],
    },
    {
        "user_goal": "Please add Greek captions to this Greek-Orthodox church service recording. The priest speaks Greek; Greek-matching captions please.",
        "rationale": (
            "Greek-spoken church service + Greek captioning. IntakeVideoAgent ingests the "
            "recording. TranscriptionAgent transcribes the priest's Greek liturgy into "
            "timestamped SRT. CompositorAgent burns Greek captions onto the service video. "
            "Reject TranslationAgent (Greek-on-Greek), VideoAnalysisAgent / HighlightAgent "
            "(whole service retained), MusicAgent / AmbienceAgent / AudioMixAgent (no audio "
            "overlay — the original chanting is preserved), StyleTransferAgent (no visual "
            "change)."
        ),
        "intents": [
            "Ingest the Greek-Orthodox church service recording into the workspace.",
            "Transcribe the priest's Greek liturgy into timestamped SRT caption segments.",
            "Burn Greek captions onto the full church service video and export the captioned recording.",
        ],
    },
    {
        "user_goal": "Please transcribe this Indonesian news broadcast and burn Indonesian subtitles into it. Same-language captions only.",
        "rationale": (
            "Indonesian news broadcast + Indonesian captioning request. IntakeVideoAgent loads "
            "the broadcast file. TranscriptionAgent captures the anchor's Indonesian delivery "
            "into timestamped SRT. CompositorAgent burns Indonesian captions onto the broadcast "
            "for same-language viewers. No translation, no audio overlay, no trimming, no visual "
            "restyle."
        ),
        "intents": [
            "Ingest the Indonesian news broadcast recording into the workspace.",
            "Transcribe the anchor's Indonesian delivery into timestamped SRT caption segments.",
            "Compose the broadcast with Indonesian captions burned onto the anchor's footage.",
        ],
    },
    {
        "user_goal": "Could you caption this Czech puppet-theatre performance in Czech? The puppeteer narrates in Czech.",
        "rationale": (
            "Czech-narrated puppet theatre + Czech captioning. IntakeVideoAgent ingests the "
            "performance recording. TranscriptionAgent transcribes the puppeteer's Czech "
            "narration into timestamped SRT. CompositorAgent burns Czech captions onto the "
            "performance. Reject TranslationAgent (same-language captioning), reject all audio / "
            "style / trimming / highlight agents — the full performance is captioned and "
            "presented as-is."
        ),
        "intents": [
            "Ingest the Czech puppet-theatre performance into the workspace.",
            "Transcribe the puppeteer's Czech narration into timestamped SRT caption segments.",
            "Compose the performance video with Czech captions burned onto the stage footage.",
        ],
    },
    {
        "user_goal": "Add Finnish captions to this Finnish cooking-challenge episode. Same-language, chef's dialogue only.",
        "rationale": (
            "Finnish cooking-challenge + Finnish captioning request. IntakeVideoAgent ingests "
            "the episode. TranscriptionAgent transcribes the chef's Finnish dialogue into "
            "timestamped SRT. CompositorAgent burns Finnish captions onto the challenge footage. "
            "No translation (same language), no audio overlay, no trimming, no style transfer."
        ),
        "intents": [
            "Ingest the Finnish cooking-challenge episode into the workspace.",
            "Transcribe the chef's Finnish dialogue into timestamped SRT caption segments.",
            "Burn Finnish captions onto the cooking-challenge episode and export the captioned cut.",
        ],
    },
]
