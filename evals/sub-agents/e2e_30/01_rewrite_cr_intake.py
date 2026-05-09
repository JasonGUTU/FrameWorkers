#!/usr/bin/env python3
"""Rewrite cr (10) + intake_img (10) user_goal as Chinese mass-appeal short-drama topics.

storytelling (10) is left untouched — its current goals are appropriate for
the illustrated-audiobook audience (Inuit grandmother / Greek shepherd /
forest river / etc. fit the genre).

Each new user_goal is written so its trigger keywords match the GT chain's
audio / subtitle capability hints:
  - Ambience layer  -> 提"加 X 环境音"
  - Music layer     -> 提"加 X BGM / 配乐"
  - Transcription   -> 提"加中文字幕"
  - Translation     -> 提"加中英双语字幕"

Original user_goal is preserved in `_meta.original_user_goal` for audit.
"""
from __future__ import annotations
import json
from pathlib import Path

# 20 new user_goals keyed by case name.
# Topic mapping -> chain shape:
#   6L (cr type A, no audio)        — pure story → video
#   8L cr+Ambience                  — env-sound-driven scenes
#   8L cr+Music                     — emotion-driven scenes (BGM)
#   9L cr+Music+Ambience parallel   — epic scenes (BGM + env)
#   8L intake_img (no audio)        — pure portrait → drama
#  10L intake_img+Music             — portrait → drama + BGM
#  10L intake_img+Trans+Translation — portrait → drama + bilingual subs
#   9L intake_img+Transcription     — portrait → drama + Chinese subs
#  11L intake_img+Trans+Music       — portrait → drama + subs + BGM
NEW_GOALS: dict[str, str] = {
    # === cr Type A: 6 layers, no audio ===
    "cr_042": (
        "做一部修真飞升题材动画短剧——天才少年被同门师兄陷害废了丹田，"
        "他以家传一柄废剑重新筑基，斩万古妖魔，最后突破九重天劫飞升神界。"
    ),
    "cr_023": (
        "做一部古装重生宫斗题材动画短剧——前世被亲姐姐陷害打入冷宫赐毒酒的废后柳如烟，"
        "重生回入宫前一日，这次她要让背叛她的所有人一个一个跪在她脚下。"
    ),
    "cr_049": (
        "做一部都市重生复仇题材动画短剧——金牌律师被合伙人构陷锒铛入狱，"
        "出来时妻女已死；天降重生回十年前那个改变一切的雨夜，"
        "他要把当年背叛过他的每一个人一个不漏地拉下水。"
    ),

    # === cr Type B: 8 layers, +Ambience ===
    "cr_064": (
        "做一部末日丧尸题材动画短剧——病毒爆发第七天，一支由前特种兵队长和女医生组成的小队，"
        "穿越被丧尸群占领的城市地下隧道去寻找传说中的疫苗实验室。"
        "记得加丧尸嘶吼、防空警报、风扫过废墟的环境音。"
    ),
    "hard_004": (
        "做一部仙侠复仇题材动画短剧——魔教余孽屠门后唯一幸存的少年道士，"
        "背着师傅头颅一路血战重返昆仑山，要在血月当晚祭旗复仇。"
        "记得加山风呼啸、剑鸣破空、远雷滚动的环境音。"
    ),
    "cr_016": (
        "做一部灵异悬疑题材动画短剧——午夜的精神病院旧楼里，新来的男实习医生发现"
        "304 病房每晚都在自动播放一段三十年前的录音；当他终于推开那扇门，"
        "看见的却是十岁的自己。记得加电流杂音、空荡走廊回响、远处啜泣声的环境音。"
    ),

    # === cr Type C: 9 layers, +Music+Ambience parallel ===
    "hard_007": (
        "做一部古装战争史诗题材动画短剧——大将军慕容戎之子镇守西北十年未归，"
        "最后一战他孤身一骑冲入十万敌军中，只为给死去的父亲讨回那柄祖传青龙偃月刀。"
        "记得加战马嘶鸣、弓弦绷紧、雪原寒风的环境音，再配一段悲壮的古风战鼓 BGM。"
    ),
    "cr_072": (
        "做一部神话改编玄幻题材动画短剧——封神大战末年，从苦肉计中活下来的小妖九尾狐"
        "被姜子牙押解上封神台，临死前她忽然想起一个总在梦里出现的男人。"
        "记得加九重天雷劫的环境音 + 一段悲怆古风 BGM。"
    ),

    # === cr Type D: 8 layers, +Music ===
    "cr_059": (
        "做一部校园修罗场题材动画短剧——成绩永远第一的冷面转校生顾修宁，"
        "第一天就被发现是十年前那场校园纵火案唯一的幸存者；"
        "而新来的班主任林老师，正是当年把他从火里拖出来的人。配一段克制压抑的钢琴 BGM。"
    ),
    "cr_030": (
        "做一部总裁追妻题材动画短剧——契约老婆苏念三年后带着一对双胞胎儿女回国，"
        "向霍家继承人递上离婚协议，那个曾经把她当替身的男人，第一次跪在她面前。"
        "配一段揪心的弦乐 BGM。"
    ),

    # === intake_img Type A: 8 layers, no audio ===
    "intake_img_019": (
        "以这张上传的人物照片作为重生女主的脸，做一部古装重生宫斗题材动画短剧——"
        "她是被皇帝赐毒酒的前世废后，重生回到入宫选秀的那一日，"
        "这一次她要把欠她一条命的人，一个个亲手送进黄泉。"
    ),
    "intake_img_018": (
        "以这张上传的人物照片为豪门男主，做一部都市豪门虐恋题材动画短剧——"
        "七年前他亲眼看着她从游艇上跳下大海，七年后她以另一个名字回来，"
        "成了他最大的商业对手，也成了他这辈子最想抓住又抓不住的影子。"
    ),
    "intake_img_005": (
        "以这张上传的人物照片作为修真男主的样子，做一部修真重生题材动画短剧——"
        "他上一世曾是镇压万古的天帝，被九大圣地联手陨落；这一世他重生在被全宗门嘲笑的"
        "废材小师弟身上，所有当年踩过他的人，都不知道自己已经站在末日边缘。"
    ),
    "intake_img_008": (
        "以这张上传的人物照片作为玄幻女主，做一部末日异能题材动画短剧——"
        "病毒爆发那天她在地铁里觉醒了操纵金属的异能，从此带着一群幸存者，"
        "在被丧尸潮淹没的城市里和军方异能小组周旋，找出真正释放病毒的人。"
    ),

    # === intake_img Type B: 10 layers, +Music ===
    "intake_img_046": (
        "以这张上传的人物照片为古装女主，做一部宫斗逆袭题材动画短剧——"
        "她是从冷宫一路爬回坤宁宫的废后，复仇路上唯一还记得她真名的，"
        "只有当年那个为她挡过一刀的小太监。配一段大气磅礴的古风 BGM。"
    ),
    "intake_img_039": (
        "以这张上传的人物照片为校园修罗场女主，做一部都市校园甜虐题材动画短剧——"
        "传闻她是江北最大私立高中的隐秘校董之女，转学第一天就和全校最难缠的"
        "校霸男主杠上了。配一段轻快又揪心的钢琴 BGM。"
    ),

    # === intake_img Type C: 10 layers, +Transcription+Translation ===
    "intake_img_036": (
        "以这张上传的人物照片作为霸总男主的样子，做一部都市豪门虐恋题材动画短剧——"
        "三年前那场车祸后失忆的小娇妻苏念，三年后带着一个长相和霍总一模一样的"
        "小男孩重新出现在他面前。要加中英双语字幕方便海外观众观看。"
    ),
    "intake_img_037": (
        "以这张上传的人物照片为玄幻女主，做一部魔尊重生题材动画短剧——"
        "前世她是镇守人间界的魔尊，被自己最信任的徒弟联合天界众神陨落；"
        "重生回到入魔前一日，她要把那群伪善天人一个个亲手拉下神坛。"
        "记得加中英双语字幕方便外网短视频平台分发。"
    ),

    # === intake_img Type D: 9 layers, +Transcription ===
    "intake_img_030": (
        "以这张上传的人物照片为悬疑男主，做一部都市悬疑刑侦题材动画短剧——"
        "刑警队新来的副队长接的第一桩案子，是一起沉默了十五年的连环抛尸案；"
        "当他追到真相边缘时，发现自己父亲的名字赫然出现在当年的嫌疑人名单上。"
        "记得加中文字幕方便短视频平台分发。"
    ),

    # === intake_img Type E: 11 layers, +Transcription+Music ===
    "intake_img_049": (
        "以这张上传的人物照片为豪门虐恋女主，做一部都市豪门替身题材动画短剧——"
        "她是被找来代替死去白月光的替身娇妻，三年契约期满那天她递上离婚协议，"
        "可那个三年来从没正眼看过她的男人，却开始疯了一样在全城找她。"
        "记得加中文字幕方便短视频平台分发，再配一段悲伤的钢琴 BGM。"
    ),
}


def main() -> None:
    here = Path(__file__).parent.resolve()
    src = here / "selection.json"
    data = json.loads(src.read_text())

    if not (here / "selection.original.json").exists():
        raise SystemExit("selection.original.json missing — backup must exist before rewrite")

    rewritten = 0
    for c in data:
        if c["name"] in NEW_GOALS:
            c["_meta"]["original_user_goal"] = c["user_goal"]
            c["user_goal"] = NEW_GOALS[c["name"]]
            c["_meta"]["rewritten"] = True
            rewritten += 1
        else:
            c["_meta"]["rewritten"] = False

    src.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    # Regenerate selection.md
    md: list[str] = [
        "# 30-case selection (seed=42, cr+intake_img rewritten 2026-05-09)\n\n",
        "Source: `eval_cases_v4500_balanced.json`\n",
        "Total: 30 (10 per category × 3 categories)\n",
        f"Rewritten: cr (10) + intake_img (10) = {rewritten} → 中文短剧爆款; storytelling (10) untouched\n\n",
    ]
    for cat in ["cr", "intake_img", "storytelling"]:
        cat_picks = [c for c in data if c["category"] == cat]
        shape_set = sorted({c["_meta"]["shape_layers_str"] for c in cat_picks})
        rw_count = sum(1 for c in cat_picks if c["_meta"].get("rewritten"))
        md.append(f"## {cat} ({len(cat_picks)}, rewritten={rw_count})\n")
        md.append(f"- unique shapes: **{len(shape_set)}**\n\n")
        md.append("| name | layers | user_goal |\n|---|---|---|\n")
        for c in cat_picks:
            m = c["_meta"]
            goal = c["user_goal"][:140].replace("|", r"\|")
            if len(c["user_goal"]) > 140:
                goal += "..."
            md.append(f"| `{c['name']}` | {m['shape_layer_count']} | {goal} |\n")
        md.append("\n")
    (here / "selection.md").write_text("".join(md))

    print(f"Rewrote {rewritten} cases (cr + intake_img)")
    print(f"  selection.json updated; selection.original.json kept")
    print(f"  selection.md regenerated")


if __name__ == "__main__":
    main()
