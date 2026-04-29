"""GRPO shape: vid_subtitle — IntakeVideo → Transcription → Compositor.

30 samples (target_n=30, no long_story_n). Monolingual subtitle overlay
on uploaded video. Topics span many languages so the LoRA sees the full
language spectrum where same-language captions fit. Rationale style
mirrors SFT: medium flow narrative + explicit reject list.
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Add Spanish subtitles to this cooking class recording — the chef is already teaching in Spanish, I just need the captions burned onto the video.",
        "rationale": (
            "Spanish-spoken cooking class + monolingual Spanish subtitle overlay. "
            "IntakeVideoAgent ingests the recording; TranscriptionAgent produces "
            "timestamped Spanish SRT segments from the chef's instruction; CompositorAgent "
            "burns the SRT onto the frames. Reject TranslationAgent (same-language ask, "
            "not bilingual), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "VideoAnalysisAgent / HighlightAgent (no analysis or trim), StyleTransferAgent "
            "/ VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the Spanish-spoken cooking-class recording into the workspace.",
            "Transcribe the chef's Spanish-language instruction into timestamped SRT segments.",
            "Burn the Spanish SRT subtitles onto the cooking video and output the final captioned file.",
        ],
    },
    {
        "user_goal": "I recorded a 90-minute podcast interview, please add English captions to it. Same language, no translation needed.",
        "rationale": (
            "90-minute English-spoken podcast interview + monolingual English captions. "
            "IntakeVideoAgent loads the recording; TranscriptionAgent produces timestamped "
            "English SRT lines; CompositorAgent burns the captions onto the video. Reject "
            "TranslationAgent (no bilingual ask), HighlightAgent / VideoAnalysisAgent "
            "(full interview wanted, not trimmed), MusicAgent / AmbienceAgent / "
            "AudioMixAgent (no audio overlay), StyleTransferAgent / VideoExtendAgent (no "
            "restyle / length change)."
        ),
        "intents": [
            "Ingest the 90-minute podcast interview recording into the workspace.",
            "Transcribe the English podcast dialogue into timestamped caption segments.",
            "Burn the English captions onto the podcast video and deliver the captioned final cut.",
        ],
    },
    {
        "user_goal": "Got a gym tutorial video I shot of myself doing deadlift form. Please add English subtitles so my online clients can follow the cues.",
        "rationale": (
            "User-recorded English deadlift gym tutorial + same-language English subtitle "
            "overlay. IntakeVideoAgent loads the tutorial; TranscriptionAgent transcribes "
            "the English form cues into timestamped SRT; CompositorAgent overlays the "
            "captions. Reject TranslationAgent (English-only, not bilingual), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), VideoAnalysisAgent / "
            "HighlightAgent (no analysis or trim), StyleTransferAgent / VideoExtendAgent "
            "(no restyle / length change)."
        ),
        "intents": [
            "Ingest the deadlift gym-tutorial recording into the workspace.",
            "Transcribe the English form cues into timestamped SRT lines.",
            "Burn the English captions onto the deadlift tutorial and output the final captioned video.",
        ],
    },
    {
        "user_goal": "Please add Mandarin subtitles to this DIY craft tutorial I filmed. The host speaks Mandarin throughout, I just need the words on screen.",
        "rationale": (
            "Mandarin-spoken DIY craft tutorial + same-language Mandarin subtitle overlay. "
            "IntakeVideoAgent ingests the tutorial; TranscriptionAgent transcribes the "
            "Mandarin host narration into timestamped SRT; CompositorAgent burns the "
            "Mandarin captions onto the frames. Reject TranslationAgent (no bilingual "
            "ask), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "HighlightAgent / VideoAnalysisAgent (no trim), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the Mandarin DIY craft tutorial into the workspace.",
            "Transcribe the Mandarin host narration into timestamped SRT segments.",
            "Burn the Mandarin captions onto the craft tutorial and deliver the final captioned video.",
        ],
    },
    {
        "user_goal": "I have a French-language travel vlog from my Provence trip. Add French captions to it for accessibility.",
        "rationale": (
            "French-language Provence travel vlog + French accessibility-caption overlay "
            "in the same language. IntakeVideoAgent ingests the vlog; TranscriptionAgent "
            "produces timestamped French SRT segments from the narration; CompositorAgent "
            "burns the captions onto the video. Reject TranslationAgent (single-language "
            "ask), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "VideoAnalysisAgent / HighlightAgent (no trim or content analysis), "
            "StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the French-language Provence travel vlog into the workspace.",
            "Transcribe the French narration into timestamped accessibility-caption segments.",
            "Burn the French captions onto the travel vlog and output the final captioned file.",
        ],
    },
    {
        "user_goal": "Add English captions to this 5-minute startup pitch I recorded for the demo day. Just the captions burned in, nothing else.",
        "rationale": (
            "5-minute English-spoken startup pitch + English captions burned in. "
            "IntakeVideoAgent loads the pitch recording; TranscriptionAgent transcribes "
            "the English pitch speech into timestamped SRT; CompositorAgent burns the "
            "captions onto the frames. Reject TranslationAgent (single language asked), "
            "HighlightAgent / VideoAnalysisAgent (full pitch wanted, not trimmed), "
            "MusicAgent / AmbienceAgent / AudioMixAgent (no BGM / ambient / audio mixing), "
            "StyleTransferAgent / VideoExtendAgent (user explicitly said 'nothing else')."
        ),
        "intents": [
            "Ingest the 5-minute startup-pitch recording into the workspace.",
            "Transcribe the English pitch speech into timestamped caption segments.",
            "Burn the English captions onto the pitch video and output the final captioned demo file.",
        ],
    },
    {
        "user_goal": "I have a Japanese cooking show I recorded — please add Japanese subtitles to match what the chef is saying.",
        "rationale": (
            "Japanese-spoken cooking show + same-language Japanese subtitle overlay. "
            "IntakeVideoAgent ingests the show; TranscriptionAgent transcribes the "
            "Japanese chef's narration into timestamped SRT; CompositorAgent burns the "
            "Japanese captions onto the frames. Reject TranslationAgent (no bilingual "
            "ask), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "VideoAnalysisAgent / HighlightAgent (no trim), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the Japanese cooking show recording into the workspace.",
            "Transcribe the Japanese chef's narration into timestamped SRT segments.",
            "Burn the Japanese captions onto the cooking show and output the final captioned file.",
        ],
    },
    {
        "user_goal": "Got a 50-minute German university lecture recording. Please add German captions for my study group.",
        "rationale": (
            "50-minute German university lecture + German captions for study group. "
            "IntakeVideoAgent loads the lecture; TranscriptionAgent transcribes the "
            "German lecturer's speech into timestamped SRT; CompositorAgent burns the "
            "German captions onto the video. Reject TranslationAgent (same-language "
            "ask), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "HighlightAgent / VideoAnalysisAgent (full lecture wanted, not trimmed), "
            "StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 50-minute German university lecture recording into the workspace.",
            "Transcribe the German lecturer speech into timestamped SRT lines.",
            "Burn the German captions onto the lecture video and deliver the captioned file.",
        ],
    },
    {
        "user_goal": "Please add Korean subtitles to this 30-minute fitness video I shot. The trainer speaks Korean throughout.",
        "rationale": (
            "30-minute Korean-spoken fitness video + same-language Korean subtitle "
            "overlay. IntakeVideoAgent ingests the video; TranscriptionAgent transcribes "
            "the Korean trainer's instruction into timestamped SRT; CompositorAgent "
            "burns the Korean captions onto the frames. Reject TranslationAgent (no "
            "bilingual ask), MusicAgent / AmbienceAgent / AudioMixAgent (no audio "
            "overlay), VideoAnalysisAgent / HighlightAgent (no trim), StyleTransferAgent "
            "/ VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 30-minute Korean fitness video into the workspace.",
            "Transcribe the Korean trainer's instruction into timestamped SRT segments.",
            "Burn the Korean captions onto the fitness video and output the captioned final cut.",
        ],
    },
    {
        "user_goal": "I have an Italian art museum tour recording — please add Italian captions so I can share it with my Italian-speaking relatives.",
        "rationale": (
            "Italian-spoken art museum tour + same-language Italian subtitle overlay. "
            "IntakeVideoAgent loads the tour recording; TranscriptionAgent transcribes "
            "the Italian guide's narration into timestamped SRT; CompositorAgent burns "
            "the Italian captions onto the frames. Reject TranslationAgent (relatives "
            "speak Italian, no bilingual ask), MusicAgent / AmbienceAgent / "
            "AudioMixAgent (no audio overlay), VideoAnalysisAgent / HighlightAgent (no "
            "trim), StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the Italian art museum tour recording into the workspace.",
            "Transcribe the Italian guide's narration into timestamped SRT segments.",
            "Burn the Italian captions onto the museum tour and output the final captioned file.",
        ],
    },
    {
        "user_goal": "Please add Portuguese subtitles to this 45-minute dance-lesson video. The instructor speaks Portuguese.",
        "rationale": (
            "45-minute Portuguese-spoken dance-lesson video + same-language Portuguese "
            "subtitle overlay. IntakeVideoAgent ingests the lesson; TranscriptionAgent "
            "transcribes the Portuguese instructor's cues into timestamped SRT; "
            "CompositorAgent burns the Portuguese captions onto the frames. Reject "
            "TranslationAgent (no bilingual ask), MusicAgent / AmbienceAgent / "
            "AudioMixAgent (no audio overlay), HighlightAgent / VideoAnalysisAgent "
            "(no trim), StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 45-minute Portuguese dance-lesson video into the workspace.",
            "Transcribe the Portuguese instructor's cues into timestamped SRT segments.",
            "Burn the Portuguese captions onto the dance-lesson video and deliver the final captioned cut.",
        ],
    },
    {
        "user_goal": "Got a Russian programming tutorial — please add Russian captions to it. The instructor narrates in Russian throughout.",
        "rationale": (
            "Russian-spoken programming tutorial + same-language Russian subtitle "
            "overlay. IntakeVideoAgent loads the tutorial; TranscriptionAgent transcribes "
            "the Russian instructor's narration into timestamped SRT; CompositorAgent "
            "burns the Russian captions onto the frames. Reject TranslationAgent (no "
            "bilingual ask), MusicAgent / AmbienceAgent / AudioMixAgent (no audio "
            "overlay), VideoAnalysisAgent / HighlightAgent (no trim), StyleTransferAgent "
            "/ VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the Russian programming tutorial into the workspace.",
            "Transcribe the Russian instructor's narration into timestamped SRT segments.",
            "Burn the Russian captions onto the tutorial and output the final captioned file.",
        ],
    },
    {
        "user_goal": "I have a Hindi yoga class recording — please add Hindi captions to it.",
        "rationale": (
            "Hindi-spoken yoga class + same-language Hindi subtitle overlay. "
            "IntakeVideoAgent ingests the class; TranscriptionAgent transcribes the "
            "Hindi instructor's cues into timestamped SRT; CompositorAgent burns the "
            "Hindi captions onto the frames. Reject TranslationAgent (no bilingual "
            "ask), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "VideoAnalysisAgent / HighlightAgent (no trim), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the Hindi yoga class recording into the workspace.",
            "Transcribe the Hindi instructor's cues into timestamped SRT segments.",
            "Burn the Hindi captions onto the yoga class video and deliver the final captioned cut.",
        ],
    },
    {
        "user_goal": "Please add Cantonese subtitles to this short Cantonese drama clip. Same language, just captions on screen.",
        "rationale": (
            "Cantonese-spoken drama clip + same-language Cantonese subtitle overlay. "
            "IntakeVideoAgent loads the clip; TranscriptionAgent transcribes the "
            "Cantonese dialogue into timestamped SRT; CompositorAgent burns the "
            "Cantonese captions onto the frames. Reject TranslationAgent (no bilingual "
            "ask), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "VideoAnalysisAgent / HighlightAgent (no trim), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the Cantonese drama clip into the workspace.",
            "Transcribe the Cantonese dialogue into timestamped SRT segments.",
            "Burn the Cantonese captions onto the drama clip and output the final captioned video.",
        ],
    },
    {
        "user_goal": "Got an Arabic news commentary recording. Please add Arabic captions so deaf viewers can follow along.",
        "rationale": (
            "Arabic-spoken news commentary + Arabic accessibility-caption overlay in "
            "the same language. IntakeVideoAgent ingests the commentary; "
            "TranscriptionAgent transcribes the Arabic narrator's commentary into "
            "timestamped SRT; CompositorAgent burns the Arabic captions onto the "
            "frames. Reject TranslationAgent (no bilingual ask), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), VideoAnalysisAgent / "
            "HighlightAgent (no trim), StyleTransferAgent / VideoExtendAgent (no restyle "
            "/ length change)."
        ),
        "intents": [
            "Ingest the Arabic news commentary recording into the workspace.",
            "Transcribe the Arabic commentary into timestamped accessibility-caption segments.",
            "Burn the Arabic captions onto the commentary and output the final accessible captioned file.",
        ],
    },
    {
        "user_goal": "Please add Turkish subtitles to this Turkish recipe video — the cook speaks Turkish throughout.",
        "rationale": (
            "Turkish-spoken recipe video + same-language Turkish subtitle overlay. "
            "IntakeVideoAgent loads the video; TranscriptionAgent transcribes the Turkish "
            "cook's narration into timestamped SRT; CompositorAgent burns the Turkish "
            "captions onto the frames. Reject TranslationAgent (no bilingual ask), "
            "MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "VideoAnalysisAgent / HighlightAgent (no trim), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the Turkish recipe video into the workspace.",
            "Transcribe the Turkish cook's narration into timestamped SRT segments.",
            "Burn the Turkish captions onto the recipe video and deliver the final captioned cut.",
        ],
    },
    {
        "user_goal": "I have a Vietnamese travel vlog — please add Vietnamese captions so my Vietnamese friends can follow along easily.",
        "rationale": (
            "Vietnamese-spoken travel vlog + same-language Vietnamese subtitle overlay. "
            "IntakeVideoAgent ingests the vlog; TranscriptionAgent transcribes the "
            "Vietnamese narration into timestamped SRT; CompositorAgent burns the "
            "Vietnamese captions onto the frames. Reject TranslationAgent (friends "
            "speak Vietnamese, no bilingual ask), MusicAgent / AmbienceAgent / "
            "AudioMixAgent (no audio overlay), VideoAnalysisAgent / HighlightAgent "
            "(no trim), StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the Vietnamese travel vlog into the workspace.",
            "Transcribe the Vietnamese narration into timestamped SRT segments.",
            "Burn the Vietnamese captions onto the travel vlog and output the final captioned file.",
        ],
    },
    {
        "user_goal": "Please add Thai subtitles to this Thai street food tour I filmed. Host speaks Thai throughout.",
        "rationale": (
            "Thai-spoken street food tour + same-language Thai subtitle overlay. "
            "IntakeVideoAgent loads the tour; TranscriptionAgent transcribes the Thai "
            "host's narration into timestamped SRT; CompositorAgent burns the Thai "
            "captions onto the frames. Reject TranslationAgent (no bilingual ask), "
            "MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "VideoAnalysisAgent / HighlightAgent (no trim), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the Thai street food tour video into the workspace.",
            "Transcribe the Thai host narration into timestamped SRT segments.",
            "Burn the Thai captions onto the tour video and output the final captioned file.",
        ],
    },
    {
        "user_goal": "Got a Polish history lecture recording. Please add Polish captions to it.",
        "rationale": (
            "Polish-spoken history lecture + same-language Polish subtitle overlay. "
            "IntakeVideoAgent ingests the lecture; TranscriptionAgent transcribes the "
            "Polish lecturer's speech into timestamped SRT; CompositorAgent burns the "
            "Polish captions onto the frames. Reject TranslationAgent (no bilingual "
            "ask), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "VideoAnalysisAgent / HighlightAgent (no trim), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the Polish history lecture recording into the workspace.",
            "Transcribe the Polish lecturer speech into timestamped SRT segments.",
            "Burn the Polish captions onto the lecture and deliver the final captioned cut.",
        ],
    },
    {
        "user_goal": "Please add Dutch subtitles to this Dutch programming workshop I recorded — speaker uses Dutch throughout.",
        "rationale": (
            "Dutch-spoken programming workshop + same-language Dutch subtitle overlay. "
            "IntakeVideoAgent loads the workshop; TranscriptionAgent transcribes the "
            "Dutch speaker's narration into timestamped SRT; CompositorAgent burns the "
            "Dutch captions onto the frames. Reject TranslationAgent (no bilingual "
            "ask), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "VideoAnalysisAgent / HighlightAgent (no trim), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the Dutch programming workshop recording into the workspace.",
            "Transcribe the Dutch speaker's narration into timestamped SRT segments.",
            "Burn the Dutch captions onto the workshop video and output the final captioned file.",
        ],
    },
    {
        "user_goal": "I have a Swedish hiking guide video — please add Swedish captions for accessibility.",
        "rationale": (
            "Swedish-spoken hiking guide + Swedish accessibility-caption overlay in the "
            "same language. IntakeVideoAgent ingests the guide; TranscriptionAgent "
            "transcribes the Swedish guide's narration into timestamped SRT; "
            "CompositorAgent burns the Swedish captions onto the frames. Reject "
            "TranslationAgent (no bilingual ask), MusicAgent / AmbienceAgent / "
            "AudioMixAgent (no audio overlay), VideoAnalysisAgent / HighlightAgent "
            "(no trim), StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the Swedish hiking guide video into the workspace.",
            "Transcribe the Swedish narration into timestamped accessibility-caption segments.",
            "Burn the Swedish captions onto the hiking guide and output the final accessible captioned file.",
        ],
    },
    {
        "user_goal": "Please add Greek subtitles to this Greek cooking show — same language, just captions burned on screen.",
        "rationale": (
            "Greek-spoken cooking show + same-language Greek subtitle overlay. "
            "IntakeVideoAgent loads the show; TranscriptionAgent transcribes the Greek "
            "chef's narration into timestamped SRT; CompositorAgent burns the Greek "
            "captions onto the frames. Reject TranslationAgent (no bilingual ask), "
            "MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "VideoAnalysisAgent / HighlightAgent (no trim), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the Greek cooking show recording into the workspace.",
            "Transcribe the Greek chef's narration into timestamped SRT segments.",
            "Burn the Greek captions onto the cooking show and deliver the final captioned cut.",
        ],
    },
    {
        "user_goal": "Got a recording of an English wedding speech I gave — please add English captions so guests with hearing aids can follow along.",
        "rationale": (
            "English-spoken wedding speech + English accessibility-caption overlay in "
            "the same language. IntakeVideoAgent ingests the speech recording; "
            "TranscriptionAgent transcribes the English speech into timestamped SRT; "
            "CompositorAgent burns the captions onto the frames. Reject TranslationAgent "
            "(same-language accessibility ask, not bilingual), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), VideoAnalysisAgent / "
            "HighlightAgent (full speech wanted, not trimmed), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the wedding speech recording into the workspace.",
            "Transcribe the English speech into timestamped accessibility-caption segments.",
            "Burn the English captions onto the speech video for hearing-aid guests and output the final accessible file.",
        ],
    },
    {
        "user_goal": "Please add English captions to this 60-minute company all-hands recording for our deaf and hard-of-hearing employees.",
        "rationale": (
            "60-minute English-spoken company all-hands + English accessibility-caption "
            "overlay in the same language. IntakeVideoAgent loads the recording; "
            "TranscriptionAgent transcribes the all-hands dialogue into timestamped "
            "SRT; CompositorAgent burns the English captions onto the frames. Reject "
            "TranslationAgent (single-language accessibility ask), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), HighlightAgent / "
            "VideoAnalysisAgent (full all-hands wanted, not trimmed), StyleTransferAgent "
            "/ VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 60-minute company all-hands recording into the workspace.",
            "Transcribe the all-hands English dialogue into timestamped accessibility-caption segments.",
            "Burn the English captions onto the all-hands video for accessibility and output the final accessible file.",
        ],
    },
    {
        "user_goal": "Got an English science explainer video I recorded for my YouTube channel. Please burn English captions onto it.",
        "rationale": (
            "English-spoken science explainer + same-language English captions burned "
            "in. IntakeVideoAgent ingests the explainer; TranscriptionAgent transcribes "
            "the English science narration into timestamped SRT; CompositorAgent burns "
            "the English captions onto the frames. Reject TranslationAgent (no "
            "bilingual ask), MusicAgent / AmbienceAgent / AudioMixAgent (no audio "
            "overlay), VideoAnalysisAgent / HighlightAgent (full explainer wanted), "
            "StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the English science explainer video into the workspace.",
            "Transcribe the English science narration into timestamped SRT segments.",
            "Burn the English captions onto the explainer and output the final captioned video for the channel.",
        ],
    },
    {
        "user_goal": "Please add Mandarin subtitles to this Mandarin business presentation I gave for the Shanghai office.",
        "rationale": (
            "Mandarin-spoken business presentation + same-language Mandarin subtitle "
            "overlay. IntakeVideoAgent loads the presentation; TranscriptionAgent "
            "transcribes the Mandarin presentation speech into timestamped SRT; "
            "CompositorAgent burns the Mandarin captions onto the frames. Reject "
            "TranslationAgent (no bilingual ask), MusicAgent / AmbienceAgent / "
            "AudioMixAgent (no audio overlay), VideoAnalysisAgent / HighlightAgent "
            "(no trim), StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the Mandarin business presentation recording into the workspace.",
            "Transcribe the Mandarin presentation speech into timestamped SRT segments.",
            "Burn the Mandarin captions onto the presentation and output the final captioned file for the Shanghai office.",
        ],
    },
    {
        "user_goal": "Got a Mandarin tea ceremony tutorial I filmed. Please add Mandarin captions to it for clarity.",
        "rationale": (
            "Mandarin-spoken tea ceremony tutorial + same-language Mandarin subtitle "
            "overlay. IntakeVideoAgent ingests the tutorial; TranscriptionAgent "
            "transcribes the Mandarin tea-ceremony narration into timestamped SRT; "
            "CompositorAgent burns the Mandarin captions onto the frames. Reject "
            "TranslationAgent (no bilingual ask), MusicAgent / AmbienceAgent / "
            "AudioMixAgent (no audio overlay), VideoAnalysisAgent / HighlightAgent "
            "(no trim), StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the Mandarin tea ceremony tutorial into the workspace.",
            "Transcribe the Mandarin tea-ceremony narration into timestamped SRT segments.",
            "Burn the Mandarin captions onto the tea ceremony tutorial and output the final captioned file.",
        ],
    },
    {
        "user_goal": "Please add Spanish subtitles to this Spanish home renovation video — host narrates in Spanish throughout.",
        "rationale": (
            "Spanish-spoken home renovation video + same-language Spanish subtitle "
            "overlay. IntakeVideoAgent loads the video; TranscriptionAgent transcribes "
            "the Spanish host's narration into timestamped SRT; CompositorAgent burns "
            "the Spanish captions onto the frames. Reject TranslationAgent (no "
            "bilingual ask), MusicAgent / AmbienceAgent / AudioMixAgent (no audio "
            "overlay), VideoAnalysisAgent / HighlightAgent (no trim), StyleTransferAgent "
            "/ VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the Spanish home renovation video into the workspace.",
            "Transcribe the Spanish host's renovation narration into timestamped SRT segments.",
            "Burn the Spanish captions onto the renovation video and output the final captioned file.",
        ],
    },
    {
        "user_goal": "I have a French cheese-making tutorial — please add French subtitles to match the chef's narration.",
        "rationale": (
            "French-spoken cheese-making tutorial + same-language French subtitle "
            "overlay. IntakeVideoAgent ingests the tutorial; TranscriptionAgent "
            "transcribes the French chef's narration into timestamped SRT; "
            "CompositorAgent burns the French captions onto the frames. Reject "
            "TranslationAgent (no bilingual ask), MusicAgent / AmbienceAgent / "
            "AudioMixAgent (no audio overlay), VideoAnalysisAgent / HighlightAgent "
            "(no trim), StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the French cheese-making tutorial into the workspace.",
            "Transcribe the French chef's narration into timestamped SRT segments.",
            "Burn the French captions onto the cheese-making tutorial and deliver the final captioned cut.",
        ],
    },
    {
        "user_goal": "Got an English veterinary case-study recording for my CME credit. Please add English captions for accessibility.",
        "rationale": (
            "English-spoken veterinary case-study recording + English accessibility-"
            "caption overlay in the same language. IntakeVideoAgent loads the case "
            "study; TranscriptionAgent transcribes the English clinical narration into "
            "timestamped SRT; CompositorAgent burns the English captions onto the "
            "frames. Reject TranslationAgent (no bilingual ask), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), VideoAnalysisAgent / "
            "HighlightAgent (full case-study wanted, not trimmed), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the veterinary case-study recording into the workspace.",
            "Transcribe the English clinical narration into timestamped accessibility-caption segments.",
            "Burn the English captions onto the case-study video and output the final accessible captioned file.",
        ],
    },
]
