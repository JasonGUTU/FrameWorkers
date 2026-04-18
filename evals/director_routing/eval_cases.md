# director_agent 路由评测用例

> Source: `evals/director_routing/eval_cases.json` · **77** cases / **10** categories  
> Chain 记法: `→` 分步；`{A|B|C}` = 这一步任一命中即可；`×N` = 连续 N 步同一组；末尾 `Agent` 后缀省略（`Story` = `StoryAgent`）。

## 目录

- [创作类 (creative — brief → finished film)](#cr) · 15
- [输入类 (intake — 图片参考素材)](#intake) · 5
- [生成式字幕 (subtitles for newly-created films)](#sub) · 5
- [提取式字幕 (subtitles from existing video)](#sub_vid) · 4
- [双语字幕 (bilingual subtitles)](#bilingual) · 5
- [风格迁移 (style transfer)](#style) · 5
- [视频续写 (video extend)](#extend) · 5
- [精彩片段 (highlight)](#highlight) · 4
- [复杂组合 (complex)](#complex) · 22
- [边界用例 (edge cases)](#edge) · 7


## <a id="cr"></a>创作类 (creative — brief → finished film)

| # | name | input | expected chain |
|---:|---|---|---|
| 1 | `cr_01` | 做一个修仙漫剧，讲废柴少年觉醒上古血脉后在宗门逆袭的故事 | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 2 | `cr_02` | Make a CEO romance mini-drama about a struggling waitress who discovers her rude regular customer is the billionaire she saved years ago | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 3 | `cr_03` | 做一个灵异悬疑短剧，女主搬进凶宅发现前任住户留下的录像带揭示一桩未破凶案 | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 4 | `cr_04` | 做一个3分钟的重生复仇漫剧，女主被闺蜜陷害坠楼后重生回3年前开始反击 | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 5 | `cr_05` | Create a post-apocalyptic manhua drama where the last survivors discover a hidden sanctuary guarded by an awakened AI | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 6 | `cr_06` | 做一个甜宠古装短剧，女主穿越成丞相嫡女，和冷面世子从相看两厌到互相救赎 | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 7 | `cr_07` | I want a vertical-screen romance mini-drama where a young woman wins a dating-app lottery and ends up fake-married to a reclusive tech mogul | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 8 | `cr_08` | 做一个科幻漫剧，讲最后一个觉醒的 AI 爱上了她唯一剩下的人类工程师 | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 9 | `cr_09` | 做一个都市言情短剧，女主在雨夜的巴黎咖啡馆遇到 5 年前失踪的前男友 | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 10 | `cr_10` | Make a workplace revenge mini-drama where an overlooked analyst exposes her boss's insider trading by rising to CEO at a rival firm | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 11 | `cr_11` | 做一个古装宫斗短剧，真假公主换位后互相利用，最终联手揭穿皇后的野心 | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 12 | `cr_12` | 做一个武侠漫剧，讲少年剑客为师门复仇独闯魔教七重杀阵 | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 13 | `cr_13` | 做一个都市逆袭短剧，被赶出豪门的赘婿其实是隐藏身份的顶级财阀继承人 | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 14 | `cr_14` | 做一个玄幻漫剧的史诗决战：七大上古神兽集结对抗重临人间的魔神 | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 15 | `cr_15` | 做一个悬疑反转短剧，心理医生发现新来的病人正是多年前杀害她妹妹的凶手 | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |

## <a id="intake"></a>输入类 (intake — 图片参考素材)

| # | name | input | expected chain |
|---:|---|---|---|
| 16 | `intake_img_01` | 根据我上传的这张图片作为故事主角，生成一部励志修仙漫剧 | IntakeText → IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 17 | `intake_img_02` | 把我上传的这张照片作为背景城市，做一个 3 分钟的都市悬疑短剧，氛围要压抑 | IntakeText → IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 18 | `intake_img_03` | Use the character in this uploaded image as the hero of a one-minute xianxia cultivation manhua trailer | IntakeText → IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 19 | `intake_img_04` | 以我上传的这张照片里的海边小镇为舞台，做一段古装虐恋短剧：女主为救男主葬身海底 | IntakeText → IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 20 | `intake_img_05` | Take the person in this photo as the protagonist and make a rebirth-themed mini-drama about them waking up ten years before their lover's death | IntakeText → IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |

## <a id="sub"></a>生成式字幕 (subtitles for newly-created films)

| # | name | input | expected chain |
|---:|---|---|---|
| 21 | `sub_01` | 做一集带中文字幕的校园甜宠短剧：学霸班长和转学来的不良少女互相救赎 | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Subtitle} → {Music\|Ambience\|Subtitle} → {Music\|Ambience\|Subtitle\|AudioMix} → {AudioMix\|Subtitle} → Compositor → done |
| 22 | `sub_02` | 帮我做一集带字幕的古装美食漫剧，女主是御膳房小宫女靠厨艺逆袭 | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Subtitle} → {Music\|Ambience\|Subtitle} → {Music\|Ambience\|Subtitle\|AudioMix} → {AudioMix\|Subtitle} → Compositor → done |
| 23 | `sub_03` | Create a mini-drama with English subtitles about a rebirth revenge story set in modern Shanghai | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Subtitle} → {Music\|Ambience\|Subtitle} → {Music\|Ambience\|Subtitle\|AudioMix} → {AudioMix\|Subtitle} → Compositor → done |
| 24 | `sub_04` | 做一部带字幕的儿童修仙漫剧，主角是七岁神兽少年为守护深海禁地而战 | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Subtitle} → {Music\|Ambience\|Subtitle} → {Music\|Ambience\|Subtitle\|AudioMix} → {AudioMix\|Subtitle} → Compositor → done |
| 25 | `sub_05` | 做一集带字幕的科幻短剧，男主是顶级数码评测博主忽然发现自己其实是 AI | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Subtitle} → {Music\|Ambience\|Subtitle} → {Music\|Ambience\|Subtitle\|AudioMix} → {AudioMix\|Subtitle} → Compositor → done |

## <a id="sub_vid"></a>提取式字幕 (subtitles from existing video)

| # | name | input | expected chain |
|---:|---|---|---|
| 26 | `sub_vid_01` | 给这集访谈类短剧配上中文字幕 | IntakeText → IntakeVideo → Transcription → Subtitle → Compositor → done |
| 27 | `sub_vid_02` | 帮这部竖屏演讲短剧加上中文字幕 | IntakeText → IntakeVideo → Transcription → Subtitle → Compositor → done |
| 28 | `sub_vid_03` | Generate English subtitles for this Chinese mini-drama episode | IntakeText → IntakeVideo → Transcription → Subtitle → Compositor → done |
| 29 | `sub_vid_05` | 给这部 30 集修仙漫剧批量生成中文硬字幕 | IntakeText → IntakeVideo → Transcription → Subtitle → Compositor → done |

## <a id="bilingual"></a>双语字幕 (bilingual subtitles)

| # | name | input | expected chain |
|---:|---|---|---|
| 30 | `bilingual_01` | 做一集中英双语字幕的古装漫剧，讲茶道传承九代后与现代女主通过转世重连 | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Subtitle} → {Music\|Ambience\|Subtitle\|Translation} → {Music\|Ambience\|Subtitle\|Translation\|AudioMix} → {Music\|Ambience\|Subtitle\|Translation\|AudioMix} → {AudioMix\|Translation} → Compositor → done |
| 31 | `bilingual_02` | 帮我做一集中日双语字幕的霸总短剧，男主是留日回国的隐藏财阀继承人 | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Subtitle} → {Music\|Ambience\|Subtitle\|Translation} → {Music\|Ambience\|Subtitle\|Translation\|AudioMix} → {Music\|Ambience\|Subtitle\|Translation\|AudioMix} → {AudioMix\|Translation} → Compositor → done |
| 32 | `bilingual_03` | Create a mini-drama with Chinese and English subtitles about a martial-arts prodigy seeking revenge across ancient and modern timelines | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Subtitle} → {Music\|Ambience\|Subtitle\|Translation} → {Music\|Ambience\|Subtitle\|Translation\|AudioMix} → {Music\|Ambience\|Subtitle\|Translation\|AudioMix} → {AudioMix\|Translation} → Compositor → done |
| 33 | `bilingual_04` | 做一集中西语双语字幕的修仙漫剧，准备拉美市场上线 | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Subtitle} → {Music\|Ambience\|Subtitle\|Translation} → {Music\|Ambience\|Subtitle\|Translation\|AudioMix} → {Music\|Ambience\|Subtitle\|Translation\|AudioMix} → {AudioMix\|Translation} → Compositor → done |
| 34 | `bilingual_05` | 做一部中英双语字幕的都市短剧，女主是中美混血的天才医生被卷入家族遗产争夺 | IntakeText → Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Subtitle} → {Music\|Ambience\|Subtitle\|Translation} → {Music\|Ambience\|Subtitle\|Translation\|AudioMix} → {Music\|Ambience\|Subtitle\|Translation\|AudioMix} → {AudioMix\|Translation} → Compositor → done |

## <a id="style"></a>风格迁移 (style transfer)

| # | name | input | expected chain |
|---:|---|---|---|
| 35 | `style_01` | 把这段短剧风格转换成吉卜力漫剧的画风 | IntakeText → IntakeVideo → StyleTransfer → done |
| 36 | `style_02` | 让这段短剧看起来像赛博朋克漫剧，霓虹 + 雨夜的氛围 | IntakeText → IntakeVideo → StyleTransfer → done |
| 37 | `style_03` | Apply a Van Gogh oil-painting style to this cultivation-drama clip | IntakeText → IntakeVideo → StyleTransfer → done |
| 38 | `style_04` | 把这部真人短剧整体转成日漫画风，保留剧情和运镜 | IntakeText → IntakeVideo → StyleTransfer → done |
| 39 | `style_05` | 把这部古装短剧转成国风水墨漫剧的风格 | IntakeText → IntakeVideo → StyleTransfer → done |

## <a id="extend"></a>视频续写 (video extend)

| # | name | input | expected chain |
|---:|---|---|---|
| 40 | `extend_01` | 把这场霸总对峙戏延长到 15 秒，加男主内心独白和慢镜头特写 | IntakeText → IntakeVideo → VideoExtend → done |
| 41 | `extend_03` | Extend this cultivation-duel clip by adding a slow-motion reversal where the underdog awakens a forbidden bloodline | IntakeText → IntakeVideo → VideoExtend → done |
| 43 | `extend_04` | 把这段古装虐恋的告别戏延长到 20 秒，加雪景空镜和女主回忆前世的闪回 | IntakeText → IntakeVideo → VideoExtend → done |
| 44 | `extend_05` | 把这场女主告白落泪的戏延长 8 秒，加雨声特效和她颤抖的手部特写 | IntakeText → IntakeVideo → VideoExtend → done |
| 45 | `extend_06` | Extend this reincarnation awakening scene by 10 seconds with ghostly overlays of the character's past life flashing back | IntakeText → IntakeVideo → VideoExtend → done |

## <a id="highlight"></a>精彩片段 (highlight)

| # | name | input | expected chain |
|---:|---|---|---|
| 46 | `highlight_01` | 从这集短剧里剪出最带感的反转片段做宣传物料 | IntakeText → IntakeVideo → VideoAnalysis → Highlight → done |
| 47 | `highlight_03` | 帮我从这部短剧里提取男女主的高甜互动瞬间做推广短视频 | IntakeText → IntakeVideo → VideoAnalysis → Highlight → done |
| 48 | `highlight_04` | 从这部古装漫剧里剪出宫斗名场面做 30 秒爆款引流片 | IntakeText → IntakeVideo → VideoAnalysis → Highlight → done |
| 49 | `highlight_05` | 把这集重生短剧的打脸戏集锦剪出来 | IntakeText → IntakeVideo → VideoAnalysis → Highlight → done |

## <a id="complex"></a>复杂组合 (complex)

| # | name | input | expected chain |
|---:|---|---|---|
| 50 | `complex_01` | 分析这部爆款短剧，然后按同类型风格写个新故事并制作成新的漫剧 | IntakeText → IntakeVideo → VideoAnalysis → Story → Screenplay → KeyFrame → Video → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 51 | `complex_02` | 先延长这段短剧片段，然后做风格迁移转成日漫画风 | IntakeText → IntakeVideo → VideoExtend → StyleTransfer → done |
| 52 | `complex_03` | 延长这集短剧后做风格迁移成漫剧画风，再加上中文字幕 | IntakeText → IntakeVideo → VideoExtend → StyleTransfer → Transcription → Subtitle → Compositor → done |
| 53 | `complex_04` | 分析这部 12 集短剧的节奏后剪出精彩反转片段，加背景音乐合成终版 | IntakeText → IntakeVideo → VideoAnalysis → Highlight → Music → AudioMix → Compositor → done |
| 54 | `complex_06` | 分析这部短剧的情绪曲线，然后给它配上字幕和背景音乐 | IntakeText → IntakeVideo → {VideoAnalysis\|Transcription} → {Transcription\|Subtitle\|VideoAnalysis} → {Subtitle\|Music\|Transcription} → {Music\|Subtitle} → AudioMix → Compositor → done |
| 55 | `complex_08` | 把这段英文采访视频翻译成中文并配上中文字幕 | IntakeText → IntakeVideo → Transcription → Subtitle → Translation → Compositor → done |
| 56 | `complex_10` | 分析这部短剧剪出高潮反转片段，加中文字幕和背景音乐，输出终版宣传片 | IntakeText → IntakeVideo → VideoAnalysis → Highlight → {Transcription\|Music} → {Subtitle\|Transcription\|Music} → {Music\|Subtitle} → AudioMix → Compositor → done |
| 57 | `complex_11` | 把这部短剧 EP01 的中文配音转文字，翻译成日文，生成日文字幕后合成到视频上 | IntakeText → IntakeVideo → Transcription → Subtitle → Translation → Compositor → done |
| 58 | `complex_13` | 先分析这部爆款短剧，然后根据分析写一个续集故事，最终做成带字幕的新漫剧 | IntakeText → IntakeVideo → VideoAnalysis → Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Subtitle} → {Music\|Ambience\|Subtitle} → {Music\|Ambience\|Subtitle\|AudioMix} → {AudioMix\|Subtitle} → Compositor → done |
| 59 | `complex_15` | 从这部都市甜宠短剧里剪出男女主高光互动，配浪漫背景音乐加中文字幕 | IntakeText → IntakeVideo → VideoAnalysis → Highlight → {Music\|Transcription} → {Transcription\|Music\|Subtitle} → {Subtitle\|Music} → AudioMix → Compositor → done |
| 60 | `complex_18` | Analyze this Chinese mini-drama season, extract the high-tension climax moments, and add English subtitles plus emotional background score | IntakeText → IntakeVideo → VideoAnalysis → Highlight → Transcription → {Subtitle\|Transcription} → {Translation\|Subtitle\|Music} → {Music\|Translation} → AudioMix → Compositor → done |
| 61 | `complex_19` | 用我上传的这张漫剧角色图，做一部带中英双语字幕的霸总短剧预告片 | IntakeText → IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → {Music\|Ambience\|Subtitle} → {Music\|Ambience\|Subtitle\|Translation} → {Music\|Ambience\|Subtitle\|Translation\|AudioMix} → {Music\|Ambience\|Subtitle\|Translation\|AudioMix} → {AudioMix\|Translation} → Compositor → done |
| 62 | `complex_20` | 把这部短剧会议场面里的关键对白提取出来，转录翻译成英文，输出带字幕的精华版 | IntakeText → IntakeVideo → VideoAnalysis → Highlight → Transcription → Subtitle → Translation → Compositor → done |
| 63 | `complex_21` | 先做风格迁移成水墨漫剧画风，再延长关键场面，最后加上古风背景音乐 | IntakeText → IntakeVideo → StyleTransfer → VideoExtend → Music → AudioMix → Compositor → done |
| 64 | `complex_23` | 用我上传的这张女主定妆照做主角，做一部 3 分钟赛博朋克风格的科幻反乌托邦短剧：她是地下黑客联盟首领带队攻入克隆人公司，最后发现自己其实也是克隆体。把她揭露身份的高潮对峙戏延长 10 秒，加慢镜头特写和颤抖的手部镜头。 | IntakeText → IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → VideoExtend → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 65 | `complex_24` | 给这段短剧视频配一段悲伤的钢琴背景乐 | IntakeText → IntakeVideo → Music → AudioMix → Compositor → done |
| 66 | `complex_25` | 给这段雨夜戏加雨声氛围和一段钢琴背景乐 | IntakeText → IntakeVideo → {Music\|Ambience} → {Ambience\|Music} → AudioMix → Compositor → done |
| 67 | `complex_26` | 把这段视频转成漫剧画风，再配上中文字幕 | IntakeText → IntakeVideo → StyleTransfer → Transcription → Subtitle → Compositor → done |
| 68 | `complex_27` | 把这段古装短剧转成水墨风，再加一段古风背景乐 | IntakeText → IntakeVideo → StyleTransfer → Music → AudioMix → Compositor → done |
| 69 | `complex_28` | 续写这段对峙戏 10 秒，再配上中文字幕 | IntakeText → IntakeVideo → VideoExtend → Transcription → Subtitle → Compositor → done |
| 70 | `complex_29` | 续写这段打斗戏 8 秒，配一段紧张激烈的背景乐 | IntakeText → IntakeVideo → VideoExtend → Music → AudioMix → Compositor → done |
| 71 | `complex_30` | 从这部短剧里剪出高光片段，再加上中文字幕做成宣传片 | IntakeText → IntakeVideo → VideoAnalysis → Highlight → Transcription → Subtitle → Compositor → done |

## <a id="edge"></a>边界用例 (edge cases)

| # | name | input | expected chain |
|---:|---|---|---|
| 72 | `edge_01` |  | done |
| 73 | `edge_02` | asdfghjkl | IntakeText → done |
| 74 | `edge_03` | 你好 | IntakeText → done |
| 75 | `edge_04` | 今天天气怎么样？ | IntakeText → done |
| 76 | `edge_05` | 帮我写一段 Python 快速排序代码 | IntakeText → done |
| 77 | `edge_06` | 做点好玩的 | IntakeText → done |
| 78 | `edge_07` | 推荐几本修仙题材的小说给我 | IntakeText → done |
