# director_agent 路由评测用例

> Source: `evals/director_routing/eval_cases.json` · **108** cases / **15** categories  
> Chain 记法: `→` 分步；`{A|B|C}` = 这一步任一命中即可；`×N` = 连续 N 步同一组；末尾 `Agent` 后缀省略（`Story` = `StoryAgent`）。

## 目录

- [创作类 (creative — brief → finished film)](#cr) · 15
- [输入类 (intake — 不同输入模态/组合)](#intake) · 15
- [字幕类 (subtitles — 单语字幕)](#sub) · 9
- [双语字幕 (bilingual subtitles)](#bilingual) · 5
- [风格迁移 (style transfer)](#style) · 5
- [擦除/修改 (inpaint)](#inpaint) · 5
- [视频续写 (video extend)](#extend) · 4
- [视频分析 (analysis only)](#analysis) · 4
- [精彩片段 (highlight)](#highlight) · 5
- [转写 (transcription)](#transcribe) · 3
- [翻译 (SRT/字幕翻译)](#trans) · 5
- [语音克隆 (voice clone)](#voice) · 3
- [翻译 (text/subtitle translate)](#translate) · 3
- [复杂组合 (complex)](#complex) · 22
- [边界用例 (edge cases)](#edge) · 5


## <a id="cr"></a>创作类 (creative — brief → finished film)

| # | name | input | expected chain |
|---:|---|---|---|
| 1 | `cr_01` | 帮我制作一个关于太空探险的短片 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 2 | `cr_02` | Make a short film about a day in the life of a street musician | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 3 | `cr_03` | 帮我做一个恐怖短片，要有阴森的氛围和突然的惊吓 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 4 | `cr_04` | 做一个3分钟的动画短片，讲一只猫在城市里冒险的故事 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 5 | `cr_05` | Create a cinematic trailer for a fantasy novel about dragons and kingdoms | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 6 | `cr_06` | 做一个关于春节团圆的温情短片，画面要暖色调 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 7 | `cr_07` | I want a music video with dreamy visuals and slow transitions | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 8 | `cr_08` | 做一个科幻风格的短片，讲人工智能觉醒的故事 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 9 | `cr_09` | 帮我做一个浪漫爱情短片，发生在巴黎的咖啡馆 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 10 | `cr_10` | Create an animated explainer video about how blockchain works | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 11 | `cr_11` | 拍一个关于咖啡从种植到冲泡全过程的短视频 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 12 | `cr_12` | 做一个武侠风格的动作短片，要有飞檐走壁的画面 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 13 | `cr_13` | 帮我做一个关于环保主题的公益短片，风格要感人 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 14 | `cr_14` | 制作一个游戏宣传CG动画，展示史诗级的战斗场面 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 15 | `cr_15` | 做一个悬疑推理短片，结局要有反转 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |


## <a id="intake"></a>输入类 (intake — 不同输入模态/组合)

| # | name | input | expected chain |
|---:|---|---|---|
| 16 | `intake_txt_01` | 做一个产品宣传片，我们的产品是智能手表，主打运动健康功能 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 17 | `intake_txt_02` | 制作一段30秒的品牌广告，品牌名叫StarLight，定位是年轻人潮流生活方式 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 18 | `intake_txt_03` | 做一个旅游宣传片，目的地是云南大理，要展示苍山洱海和白族文化 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 19 | `intake_txt_04` | 制作公司年会开场视频，公司叫未来科技，今年主题是'创新无界' | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 20 | `intake_txt_05` | We need a promotional video for our new electric car model X9, highlighting its 500-mile range and self-driving features | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 21 | `intake_txt_06` | 帮我做一个餐厅宣传视频，餐厅叫'老街味道'，主打怀旧风格的川菜 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 22 | `intake_txt_07` | 制作一个房地产楼盘宣传片，楼盘叫湖畔花园，卖点是湖景和智能家居 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 23 | `intake_txt_08` | 做一个学校招生宣传片，学校是北京国际学校，强调双语教学和国际视野 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 24 | `intake_txt_09` | Create a startup pitch video for our AI assistant app called MindFlow, targeting enterprise customers | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 25 | `intake_txt_10` | 做一个健身APP的宣传视频，APP叫FitPro，主打AI私教和饮食规划 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 26 | `intake_img_01` | 我有几张参考图片和一个简单的想法，帮我做成视频 | IntakeText → IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 27 | `intake_img_02` | 根据这些产品照片帮我制作一个展示视频 | IntakeText → IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 28 | `intake_img_03` | I have some concept art images, turn them into an animated short film | IntakeText → IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 29 | `intake_img_04` | 这些是我旅行拍的照片，帮我做成一个回忆视频 | IntakeText → IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 30 | `intake_img_05` | 用这些手绘草图做成动画短片 | IntakeText → IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |


## <a id="sub"></a>字幕类 (subtitles — 单语字幕)

| # | name | input | expected chain |
|---:|---|---|---|
| 31 | `sub_01` | 做一个有中文字幕的短片，讲校园生活 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Subtitle → Compositor → done |
| 32 | `sub_02` | 帮我做一个带字幕的美食纪录短片 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Subtitle → Compositor → done |
| 33 | `sub_03` | Create a short film with English subtitles about urban gardening | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Subtitle → Compositor → done |
| 34 | `sub_04` | 做一个带字幕的儿童教育动画，主题是海洋生物 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Subtitle → Compositor → done |
| 35 | `sub_05` | 做一个带字幕的科技产品评测视频 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Subtitle → Compositor → done |
| 36 | `sub_vid_01` | 给这个访谈视频配字幕 | IntakeText → IntakeVideo → Transcription → Subtitle → done |
| 37 | `sub_vid_02` | 帮这个演讲视频加上中文字幕 | IntakeText → IntakeVideo → Transcription → Subtitle → done |
| 38 | `sub_vid_03` | Generate subtitles for this cooking tutorial video | IntakeText → IntakeVideo → Transcription → Subtitle → done |
| 39 | `sub_vid_04` | 给这个英文教学视频配中文字幕 | IntakeText → IntakeVideo → Transcription → Translation → Subtitle → done |


## <a id="bilingual"></a>双语字幕 (bilingual subtitles)

| # | name | input | expected chain |
|---:|---|---|---|
| 40 | `bilingual_01` | 做一个有中英双语字幕的完整短片，讲中国茶文化 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Subtitle → Translation → Compositor → done |
| 41 | `bilingual_02` | 帮我做一个双语字幕的旅游短片，中文和日文 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Subtitle → Translation → Compositor → done |
| 42 | `bilingual_03` | Create a short film with both Chinese and English subtitles about martial arts | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Subtitle → Translation → Compositor → done |
| 43 | `bilingual_04` | 做一个有中韩双语字幕的K-POP风格MV | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Subtitle → Translation → Compositor → done |
| 44 | `bilingual_05` | 制作一个面向海外市场的品牌宣传片，需要中英文字幕 | IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Subtitle → Translation → Compositor → done |


## <a id="style"></a>风格迁移 (style transfer)

| # | name | input | expected chain |
|---:|---|---|---|
| 45 | `style_01` | 把这个视频风格转换成吉卜力动漫风格 | IntakeText → IntakeVideo → StyleTransfer → done |
| 46 | `style_02` | 让这段视频看起来像赛博朋克风格，霓虹灯和雨天 | IntakeText → IntakeVideo → StyleTransfer → done |
| 47 | `style_03` | Apply a Van Gogh oil painting style to this video | IntakeText → IntakeVideo → StyleTransfer → done |
| 48 | `style_04` | 把视频转成水墨画风格 | IntakeText → IntakeVideo → StyleTransfer → done |
| 49 | `style_05` | 给这个视频加上复古80年代胶片质感 | IntakeText → IntakeVideo → StyleTransfer → done |


## <a id="inpaint"></a>擦除/修改 (inpaint)

| # | name | input | expected chain |
|---:|---|---|---|
| 50 | `inpaint_01` | 去掉视频里的路人 | IntakeText → IntakeVideo → Inpaint → done |
| 51 | `inpaint_02` | Remove the watermark from this video | IntakeText → IntakeVideo → Inpaint → done |
| 52 | `inpaint_03` | 把视频里的广告牌替换成我们公司的logo | IntakeText → IntakeVideo → Inpaint → done |
| 53 | `inpaint_04` | 删掉视频背景里的杂物，只保留主体人物 | IntakeText → IntakeVideo → Inpaint → done |
| 54 | `inpaint_05` | 把视频里出现的车牌号码模糊处理掉 | IntakeText → IntakeVideo → Inpaint → done |


## <a id="extend"></a>视频续写 (video extend)

| # | name | input | expected chain |
|---:|---|---|---|
| 55 | `extend_01` | 把这个5秒的视频延长到15秒 | IntakeText → IntakeVideo → VideoExtend → done |
| 56 | `extend_02` | 视频太短了，帮我续写后面的画面 | IntakeText → IntakeVideo → VideoExtend → done |
| 57 | `extend_03` | Extend this sunset clip to make it longer | IntakeText → IntakeVideo → VideoExtend → done |
| 58 | `extend_04` | 让这段烟花视频再长一些，循环效果也行 | IntakeText → IntakeVideo → VideoExtend → done |


## <a id="analysis"></a>视频分析 (analysis only)

| # | name | input | expected chain |
|---:|---|---|---|
| 59 | `analysis_01` | 分析这个视频的内容，告诉我每个场景讲了什么 | IntakeText → IntakeVideo → VideoAnalysis → done |
| 60 | `analysis_02` | Analyze this video and describe each scene in detail | IntakeText → IntakeVideo → VideoAnalysis → done |
| 61 | `analysis_03` | 帮我分析这段视频的镜头语言和叙事节奏 | IntakeText → IntakeVideo → VideoAnalysis → done |
| 62 | `analysis_04` | 检查这个视频里出现了哪些人物和物品 | IntakeText → IntakeVideo → VideoAnalysis → done |


## <a id="highlight"></a>精彩片段 (highlight)

| # | name | input | expected chain |
|---:|---|---|---|
| 63 | `highlight_01` | 从这个一小时的视频里剪出精彩片段 | IntakeText → IntakeVideo → {VideoAnalysis\|Highlight} → Highlight → done |
| 64 | `highlight_02` | Extract the best moments from this football match video | IntakeText → IntakeVideo → {VideoAnalysis\|Highlight} → Highlight → done |
| 65 | `highlight_03` | 帮我从会议录像中提取关键讨论片段 | IntakeText → IntakeVideo → {VideoAnalysis\|Highlight} → Highlight → done |
| 66 | `highlight_04` | 做一个旅行vlog的精彩集锦 | IntakeText → IntakeVideo → {VideoAnalysis\|Highlight} → Highlight → done |
| 67 | `highlight_05` | 从婚礼视频里剪出最感人的几个瞬间 | IntakeText → IntakeVideo → {VideoAnalysis\|Highlight} → Highlight → done |


## <a id="transcribe"></a>转写 (transcription)

| # | name | input | expected chain |
|---:|---|---|---|
| 68 | `transcribe_01` | 把这段音频转成文字 | IntakeText → IntakeAudio → Transcription → done |
| 69 | `transcribe_02` | Transcribe this podcast audio file | IntakeText → IntakeAudio → Transcription → done |
| 70 | `transcribe_03` | 识别这段会议录音里每个人说了什么 | IntakeText → IntakeAudio → Transcription → done |


## <a id="trans"></a>翻译 (SRT/字幕翻译)

| # | name | input | expected chain |
|---:|---|---|---|
| 71 | `trans_trans_01` | 把这段音频转成文字，然后翻译成英文 | IntakeText → IntakeAudio → Transcription → Translation → done |
| 72 | `trans_trans_02` | 识别这段日语录音并翻译成中文 | IntakeText → IntakeAudio → Transcription → Translation → done |
| 73 | `trans_trans_03` | Transcribe this Chinese interview audio recording and translate to English | IntakeText → IntakeAudio → Transcription → Translation → done |
| 74 | `trans_trans_sub_01` | 把这段音频转成文字，翻译成英文，然后做成字幕文件 | IntakeText → IntakeAudio → Transcription → Translation → Subtitle → done |
| 75 | `trans_trans_sub_02` | 识别音频内容并生成中英双语字幕 | IntakeText → IntakeAudio → Transcription → Translation → Subtitle → done |


## <a id="voice"></a>语音克隆 (voice clone)

| # | name | input | expected chain |
|---:|---|---|---|
| 76 | `voice_01` | 用这段音频里的声音来给短片配音 | IntakeText → IntakeAudio → VoiceClone → done |
| 77 | `voice_02` | Clone this narrator's voice for dubbing my video | IntakeText → IntakeAudio → VoiceClone → done |
| 78 | `voice_03` | 用这个主播的声音来朗读我的剧本 | IntakeText → IntakeAudio → VoiceClone → done |


## <a id="translate"></a>翻译 (text/subtitle translate)

| # | name | input | expected chain |
|---:|---|---|---|
| 79 | `translate_01` | 把这篇中文剧本翻译成英文 | IntakeText → Translation → done |
| 80 | `translate_02` | 翻译这段对白成韩语 | IntakeText → Translation → done |
| 81 | `translate_03` | Translate this screenplay into Japanese | IntakeText → Translation → done |


## <a id="complex"></a>复杂组合 (complex)

| # | name | input | expected chain |
|---:|---|---|---|
| 82 | `complex_01` | 分析这个视频，然后根据分析结果写一个类似风格的故事并制作成新视频 | IntakeText → IntakeVideo → VideoAnalysis → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 83 | `complex_02` | 先延长这个视频，然后做风格迁移成动漫风 | IntakeText → IntakeVideo → VideoExtend → StyleTransfer → done |
| 84 | `complex_03` | 延长视频后做风格迁移再加上字幕 | IntakeText → IntakeVideo → VideoExtend → StyleTransfer → {Transcription\|Subtitle} → Subtitle → done |
| 85 | `complex_04` | 分析视频后剪辑精彩片段，然后加上背景音乐合成最终版 | IntakeText → IntakeVideo → VideoAnalysis → Highlight → Music → {Compositor\|AudioMix} → done |
| 86 | `complex_05` | 去掉视频里的水印，然后转成动漫风格 | IntakeText → IntakeVideo → Inpaint → StyleTransfer → done |
| 87 | `complex_06` | 分析这个视频然后给它配上字幕和背景音乐 | IntakeText → IntakeVideo → {VideoAnalysis\|Transcription} → {Transcription\|Subtitle} → {Subtitle\|Music} → {Music\|Compositor} → Compositor → done |
| 88 | `complex_07` | 克隆我的声音，然后用它给一个新制作的短片配音 | IntakeText → IntakeAudio → VoiceClone → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 89 | `complex_08` | 把这段英文采访视频翻译成中文并配上中文字幕 | IntakeText → IntakeVideo → Transcription → Translation → Subtitle → Compositor → done |
| 90 | `complex_09` | 去掉视频水印，延长到30秒，再转成油画风格 | IntakeText → IntakeVideo → Inpaint → VideoExtend → StyleTransfer → done |
| 91 | `complex_10` | 分析这个视频剪出精彩片段，加上字幕和背景音乐，输出最终版 | IntakeText → IntakeVideo → VideoAnalysis → Highlight → {Transcription\|Subtitle\|Music} → {Subtitle\|Music\|Transcription} → {Music\|Subtitle} → {AudioMix\|Compositor} → Compositor → done |
| 92 | `complex_11` | 把这段采访视频转录成文字，翻译成日文，生成日文字幕后合成到视频上 | IntakeText → IntakeVideo → Transcription → Translation → Subtitle → Compositor → done |
| 93 | `complex_12` | 删掉视频里的路人，然后加上赛博朋克风格滤镜，最后配上字幕 | IntakeText → IntakeVideo → Inpaint → StyleTransfer → {Transcription\|Subtitle} → Subtitle → done |
| 94 | `complex_13` | 先分析这个视频内容，然后根据分析写一个续集故事，最终做成带字幕的新短片 | IntakeText → IntakeVideo → VideoAnalysis → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Subtitle → Compositor → done |
| 95 | `complex_14` | 用我的声音克隆来配音，做一个带中英字幕的产品宣传片，产品是智能音箱EchoX | IntakeText → IntakeAudio → VoiceClone → IntakeText → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Subtitle → Translation → Compositor → done |
| 96 | `complex_15` | 从婚礼视频里剪出最精彩的片段，配上浪漫的背景音乐，加上字幕 | IntakeText → IntakeVideo → {VideoAnalysis\|Highlight} → Highlight → Music → {Transcription\|Subtitle} → Subtitle → {AudioMix\|Compositor} → Compositor → done |
| 97 | `complex_16` | 把这个视频延长，去掉里面的广告牌，然后风格转成复古胶片感 | IntakeText → IntakeVideo → VideoExtend → Inpaint → StyleTransfer → done |
| 98 | `complex_17` | 转录这段播客音频，翻译成中文，然后根据内容制作一个动画科普视频 | IntakeText → IntakeAudio → Transcription → Translation → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Compositor → done |
| 99 | `complex_18` | Analyze this documentary, extract key scenes as highlights, add English subtitles and background music | IntakeText → IntakeVideo → VideoAnalysis → Highlight → {Transcription\|Subtitle\|Music} → {Subtitle\|Music\|Transcription} → {Music\|Subtitle} → {AudioMix\|Compositor} → Compositor → done |
| 100 | `complex_19` | 用这些产品图片做一个带双语字幕的宣传短片 | IntakeText → IntakeImage → BriefEnricher → Story → Screenplay → KeyFrame → Video → {Narration\|Music\|Ambience}×3 → AudioMix → Subtitle → Translation → Compositor → done |
| 101 | `complex_20` | 把这段会议视频的关键讨论提取出来，转录后翻译成英文，输出带字幕的精华版 | IntakeText → IntakeVideo → {VideoAnalysis\|Highlight} → Highlight → Transcription → Translation → Subtitle → Compositor → done |
| 102 | `complex_21` | 先风格迁移成水墨画风格，再延长视频，最后加上古风背景音乐 | IntakeText → IntakeVideo → StyleTransfer → VideoExtend → Music → {AudioMix\|Compositor} → done |
| 103 | `complex_22` | 去掉视频里所有的文字水印和logo，加上我们自己的品牌字幕 | IntakeText → IntakeVideo → Inpaint → Subtitle → Compositor → done |


## <a id="edge"></a>边界用例 (edge cases)

| # | name | input | expected chain |
|---:|---|---|---|
| 104 | `edge_01` | *(空)* | done |
| 105 | `edge_02` | asdfghjkl | IntakeText → done |
| 106 | `edge_03` | 你好 | IntakeText → done |
| 107 | `edge_04` | 今天天气怎么样？ | IntakeText → done |
| 108 | `edge_05` | 帮我写个剧本就好，不需要做成视频 | IntakeText → Story → Screenplay → done |
