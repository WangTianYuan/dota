"""Read-only OpenDota collection; local cache -> auditable novel research files.

Python 3.12 standard library. Run with --cache PATH. No upload, replay request,
video download, current hero/item stats, or fiction generation is performed.
"""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "05_matches/classics-2021-2023"
BASE = "https://api.opendota.com/api/"
UTC = dt.timezone.utc
CN = dt.timezone(dt.timedelta(hours=8))
START = int(dt.datetime(2021, 10, 18, tzinfo=CN).timestamp())
END = int(dt.datetime(2023, 10, 31, tzinfo=CN).timestamp())

# Names describe the event at the time, not the mutable team registry.
EVENTS = {
    13647: "英特尔世界公开赛北京站（含资格阶段）",
    13717: "DPC中国2021/22冬季A级",
    13716: "DPC中国2021/22冬季S级",
    13738: "DPC西欧2021/22冬季S级",
    13804: "OGA Dota PIT欧洲/独联体第5赛季",
    13937: "DPC中国2021/22冬季地区决赛",
    13960: "DPC西欧2021/22冬季地区决赛",
    13978: "OGA Dota PIT中国2022",
    13994: "Gamers Galaxy迪拜2022",
    14040: "DPC中国2021/22春季A级",
    14041: "DPC中国2021/22春季S级",
    14196: "DPC中国2021/22春季地区决赛",
    14173: "斯德哥尔摩Major2022",
    14248: "DPC中国2021/22夏季S级",
    14391: "利雅得大师赛2022",
    14417: "阿灵顿Major2022",
    14388: "ESL One马来西亚2022",
    14572: "TI11中国区预选（实际进行的42局）",
    14642: "TI11最终突围赛",
    14268: "TI11小组赛与主赛事",
    14859: "DPC中国2023冬季S级",
    15089: "利马Major2023",
    15140: "DPC中国2023春季S级",
    15196: "DreamLeague第19赛季",
    15251: "柏林Major2023",
    15383: "DPC中国2023夏季S级",
    15439: "DreamLeague第20赛季",
    15438: "巴厘岛Major2023",
    15475: "利雅得大师赛2023（API列表缺末两日）",
    15739: "DreamLeague第21赛季",
    15728: "TI12",
}

# Explicit match ids avoid relying on erroneous/split upstream series_id groups.
# Every set is ordered by actual start_time again at export.
# kind: 名局 = identified celebrated case; 对照 = editorial teaching selection.
SERIES = [
    ("aries-xg-winter", "Aries—XG，冬季A级", "对照", "初入职业的真实强度：同级与晋级队伍", [6318181592,6318234034]),
    ("pit5-final", "Tundra—Spirit，Dota PIT第5赛季决赛", "对照", "TI10后早期版本的强队交锋，避免只拿2023当教材", [6331896376,6332020917,6332139754,6332245360]),
    ("lgd-aster-winter", "LGD—Aster，冬季S级", "对照", "中单与双辅助的职业配合基准", [6356694527,6356788698,6356868459]),
    ("iwo-lgd-aster", "LGD—Aster，IWO北京站", "对照", "同版本重复对抗：比较变化而非只看输赢", [6390424153,6390481538,6390571192]),
    ("weu-winter-final", "GG—Liquid，西欧冬季地区决赛", "对照", "新队成名的整轮系列赛，不以单个反杀解释成功", [6430229342,6430334629,6430424062,6430522522]),
    ("cn-winter-final", "LGD—RNG，中国冬季地区决赛", "对照", "国内顶尖对抗与连续调整；修正平台拆分的系列ID", [6440951394,6441031610,6441125886,6441263629]),
    ("dubai-final", "BOOM—Tundra，迪拜决赛", "对照", "五局比赛中的变化与英雄池", [6463558810,6463683911,6463778395,6463870718,6463952563]),
    ("aries-dec", "Aries—DEC，春季A级", "对照", "晋级赛季的失利样本：防止把对手写成陪练", [6481319135,6481353456]),
    ("aries-ig", "Aries—iG，春季A级", "对照", "职业起点素材；三局而非孤立一场", [6528301524,6528354531,6528431121]),
    ("cn-spring-final", "LGD—Aster，中国春季地区决赛", "对照", "优势方怎样连续取胜，不先假设每局均势", [6560731135,6560862720,6560977239]),
    ("stockholm-final", "TSM—OG，斯德哥尔摩决赛", "对照", "人员背景与比赛执行；替补条件须随局核验", [6582012262,6582140888,6582249405,6582379623]),
    ("aries-aster-summer", "Aries—Aster，夏季S级", "对照", "从次级到顶级对手的真实差距与同门交锋", [6605582209,6605630445]),
    ("aries-lgd-summer", "Aries—LGD，夏季S级", "对照", "强队稳定取胜教材，不给常规处理虚加光环", [6632414079,6632461072]),
    ("riyadh22-final", "LGD—Spirit，利雅得2022决赛", "对照", "与阿灵顿同对手的前后比较", [6676393091,6676488286]),
    ("arlington-upper-final", "LGD—Spirit，阿灵顿胜者组决赛", "对照", "与次日决赛成对保存：同一批选手的有效解法与再应对", [6705859209,6705943008]),
    ("arlington-final", "LGD—Spirit，阿灵顿决赛", "名局", "75分钟拉锯及此后三局关系；胜者组与决赛反转", [6707542480,6707633683,6707714718,6707754788]),
    ("malaysia-final", "Aster—OG，马来西亚决赛", "对照", "领先赛事进程与赢下最终系列是两件事", [6728333090,6728463079,6728572058]),
    ("cnq-fusion-saiyan", "Fusion—Saiyan，TI11中国预选", "对照", "预选首轮BO1：小队对抗也保留真实样本", [6746385664]),
    ("cnq-rng-ybb", "RNG—Ybb，TI11中国预选", "对照", "头号队伍的第一轮，不默认小队毫无抵抗", [6746425134,6746471021]),
    ("cnq-vg-aries", "VG—Aries，TI11中国预选", "对照", "Aries真实晋级首轮：63分钟长局与35分钟次局", [6746509252,6746573621]),
    ("cnq-cdec-ehome", "CDEC—EHOME，TI11中国预选", "对照", "预选中段队伍的有效竞争", [6746620244,6746684278]),
    ("cnq-xg-ig", "XG—iG，TI11中国预选", "对照", "XG胜者组起点，与最终决赛合读", [6746739403,6746805851]),
    ("cnq-magma-ybb", "Magma—Ybb，TI11中国预选", "对照", "败者组三局：保留同层队伍的反制", [6748032069,6748095913,6748146454]),
    ("cnq-fusion-vg", "Fusion—VG，TI11中国预选", "对照", "VG败者组起点", [6748208449,6748244943]),
    ("cnq-sz-ehome", "深圳—EHOME，TI11中国预选", "对照", "长局胜利后的系列兑现", [6748294251,6748362878]),
    ("cnq-lbzs-ig", "LBZS—iG，TI11中国预选", "对照", "iG三局生存战，与随后击败Aries比较", [6748448382,6748544248,6748621592]),
    ("cnq-rng-aries", "RNG—Aries，TI11中国预选", "对照", "Aries对直接晋级队伍的现实检验", [6749824546,6749870836]),
    ("cnq-cdec-xg", "CDEC—XG，TI11中国预选", "对照", "XG进入胜者组决赛的真实过程", [6749931110,6749988311]),
    ("cnq-ybb-vg", "Ybb—VG，TI11中国预选", "对照", "VG连续淘汰赛的阵容变化", [6750060151,6750140853]),
    ("cnq-sz-ig", "深圳—iG，TI11中国预选", "对照", "iG对Aries之前的两局基准", [6750250583,6750314405]),
    ("cnq-cdec-vg", "CDEC—VG，TI11中国预选", "对照", "VG打进关键资格对抗的前一轮", [6751775817,6751834824]),
    ("cnq-ig-aries", "iG—Aries，TI11中国预选", "对照", "Aries真实淘汰点：小说改写资格路径的直接对照", [6751890098,6751948451,6752024325]),
    ("cnq-upper-final", "XG—RNG，TI11中国预选胜者组决赛", "对照", "与次日总决赛配对：XG曾取得一局的有效方案", [6752116128,6752195021,6752271552]),
    ("cnq-ig-vg", "iG—VG，TI11中国预选", "对照", "锁定前三与LCQ资格的比赛", [6752392642,6752498546]),
    ("cnq-lower-final", "XG—VG，TI11中国预选败者组决赛", "对照", "争取直通TI的最后机会，不混同LCQ资格战", [6753802120,6753851077]),
    ("cnq-final", "RNG—XG，TI11中国预选总决赛", "对照", "中单强表现的团队条件；3:0不等于三局同一种赢法", [6753917157,6753967144,6754052082]),
    ("lcq-xg-liquid", "XG—Liquid，TI11最终突围赛", "对照", "中国队被淘汰的具体对抗，避免抽象归因", [6800460632,6800515392]),
    ("lcq-vg-liquid", "VG—Liquid，TI11最终突围赛", "对照", "争夺出线前的三局压力与适应", [6801647391,6801689673,6801743954]),
    ("ti11-rng-entity", "RNG—Entity，TI11淘汰赛", "名局", "107分钟守高与终结；巨大经济差为何不等于立即获胜", [6814073054]),
    ("ti11-bc-lgd", "beastcoast—LGD，TI11淘汰赛", "对照", "连续三局取舍及Ame团队角色", [6818469926,6818528391,6818576227]),
    ("ti11-lgd-aster", "LGD—Aster，TI11淘汰赛", "对照", "中国强队之间的有效压制；不靠国籍替代分析", [6818781180,6818876789]),
    ("ti11-ta-liquid", "Thunder Awaken—Liquid，TI11淘汰赛", "名局", "一血救援、买活与拆家期限：个人和团队价值同时成立", [6818958825,6819093598,6819203954]),
    ("ti11-liquid-aster", "Liquid—Aster，TI11淘汰赛", "对照", "系列BP与核心英雄变化", [6829184970,6829266295,6829345218]),
    ("ti11-upper-final", "Secret—Tundra，TI11胜者组决赛", "对照", "与总决赛合读，保留双方此前有效的解法", [6829521976,6829692346,6829836531]),
    ("ti11-final", "Tundra—Secret，TI11总决赛", "对照", "稳定冠军打法：地图、阵容与结束比赛的条件", [6832008209,6832140410,6832287527]),
    ("lima-final", "Liquid—GG，利马决赛", "对照", "跨赛事比较GG；必须记录Liquid替补背景", [7046266928,7046340157,7046378132]),
    ("dl19-final", "GG—Liquid，DreamLeague19决赛", "对照", "五局调整及7.33发布后的适应；赛事客户端另核", [7121740499,7121895328,7122028845,7122163122,7122259749]),
    ("berlin-final", "GG—Liquid，柏林决赛", "对照", "7.33新地图后的重建能力；旧版本解法不能直接沿用", [7143520855,7143645211,7143762860,7143863711]),
    ("dl20-lgd-gg", "GG—LGD，DreamLeague20淘汰赛", "对照", "2023中国队与冠军队伍的直接对话", [7215158468,7215250692,7215341696]),
    ("dl20-final", "BB—GG，DreamLeague20决赛", "对照", "另一对手如何与GG打满五局", [7215525382,7215645607,7215744447,7215817409,7215906831]),
    ("bali-final", "GG—Liquid，巴厘岛决赛", "对照", "反复交手后的适应与冠军连续性", [7234263112,7234394896,7234512983,7234584339]),
    ("riyadh23-talon-liquid", "Talon—Liquid，利雅得2023胜者组", "名局", "正面团战与拆家竞速的两个胜负目标", [7258880345,7259007705,7259126761]),
    ("riyadh23-bb-spirit", "BB—Spirit，利雅得2023胜者组", "名局", "两次大逆转候选：核对经济曲线与真正转折", [7259277705,7259371344,7259457478]),
    ("riyadh23-aster-9p", "Aster—9Pandas，利雅得2023", "对照", "中单变化后的中国队样本，关系与指挥另核", [7260344376,7260418930,7260520464]),
    ("dl21-final", "Spirit—Shopify，DreamLeague21决赛", "对照", "TI12前的稳定胜利，对照高波动名局", [7350256732,7350448037,7350558475]),
    ("ti12-talon-bb", "Talon—BB，TI12淘汰赛", "对照", "重复对手之外的淘汰赛形态", [7395201088,7395260041,7395312177]),
    ("ti12-spirit-liquid", "Spirit—Liquid，TI12淘汰赛", "对照", "冠军队如何应对顶尖团队的三局挑战", [7402900929,7402943509,7402993316]),
    ("ti12-bb-ar", "BB—Azure Ray，TI12淘汰赛", "对照", "老将三人组在高水平淘汰赛中的不同职责", [7404577536,7404668056,7404713057]),
    ("ti12-upper-final", "LGD—Spirit，TI12胜者组决赛", "对照", "换人后的LGD与Spirit：不能照搬2022人物分工", [7404763579,7404828649]),
    ("ti12-gg-ar", "GG—Azure Ray，TI12淘汰赛", "对照", "同一队伍能赢下一轮却在下一轮受限", [7404889653,7404938247]),
    ("ti12-lower-final", "GG—LGD，TI12败者组决赛", "对照", "打穿不同对手所需的团队执行", [7406129687,7406249246]),
    ("ti12-final", "GG—Spirit，TI12总决赛", "对照", "三连冠Major队与TI冠军的直接对抗，不以结局倒推全程", [7406424070,7406482053,7406531302]),
]

# Translation labels only. Never use present-day constants for historical stats.
HERO_CN = {
1:"敌法师",2:"斧王",3:"祸乱之源",4:"血魔",5:"水晶室女",6:"卓尔游侠",7:"撼地者",8:"主宰",9:"米拉娜",10:"变体精灵",11:"影魔",12:"幻影长矛手",13:"帕克",14:"帕吉",15:"剃刀",16:"沙王",17:"风暴之灵",18:"斯温",19:"小小",20:"复仇之魂",21:"风行者",22:"宙斯",23:"昆卡",25:"莉娜",26:"莱恩",27:"暗影萨满",28:"斯拉达",29:"潮汐猎人",30:"巫医",31:"巫妖",32:"力丸",33:"谜团",34:"修补匠",35:"狙击手",36:"瘟疫法师",37:"术士",38:"兽王",39:"痛苦女王",40:"剧毒术士",41:"虚空假面",42:"冥魂大帝",43:"死亡先知",44:"幻影刺客",45:"帕格纳",46:"圣堂刺客",47:"冥界亚龙",48:"露娜",49:"龙骑士",50:"戴泽",51:"发条技师",52:"拉席克",53:"先知",54:"噬魂鬼",55:"黑暗贤者",56:"克林克兹",57:"全能骑士",58:"魅惑魔女",59:"哈斯卡",60:"暗夜魔王",61:"育母蜘蛛",62:"赏金猎人",63:"编织者",64:"杰奇洛",65:"蝙蝠骑士",66:"陈",67:"幽鬼",68:"远古冰魄",69:"末日使者",70:"熊战士",71:"裂魂人",72:"矮人直升机",73:"炼金术士",74:"祈求者",75:"沉默术士",76:"殁境神蚀者",77:"狼人",78:"酒仙",79:"暗影恶魔",80:"德鲁伊",81:"混沌骑士",82:"米波",83:"树精卫士",84:"食人魔魔法师",85:"不朽尸王",86:"拉比克",87:"干扰者",88:"司夜刺客",89:"娜迦海妖",90:"光之守卫",91:"艾欧",92:"维萨吉",93:"斯拉克",94:"美杜莎",95:"巨魔战将",96:"半人马战行者",97:"马格纳斯",98:"伐木机",99:"钢背兽",100:"巨牙海民",101:"天怒法师",102:"亚巴顿",103:"上古巨神",104:"军团指挥官",105:"工程师",106:"灰烬之灵",107:"大地之灵",108:"孽主",109:"恐怖利刃",110:"凤凰",111:"神谕者",112:"寒冬飞龙",113:"天穹守望者",114:"齐天大圣",119:"邪影芳灵",120:"石鳞剑士",121:"天涯墨客",123:"森海飞霞",126:"虚无之灵",128:"电炎绝手",129:"玛尔斯",135:"破晓辰星",136:"玛西",137:"兽",138:"琼英碧灵"
}

PERIOD_TEAMS = {15:"PSG.LGD",7119388:"Team Spirit",2163:"Team Liquid",8291895:"Tundra",1838315:"Team Secret",6209166:"Team Aster",7453020:"Aster.Aries",6209804:"RNG",8605863:"Entity",7391077:"Thunder Awaken",8255888:"BetBoom",9131584:"BetBoom",8599101:"Gaimin Gladiators",8597976:"Talon",8261500:"Xtreme Gaming",726228:"Vici Gaming",2586976:"OG",8260983:"TSM",7732977:"BOOM",8254400:"beastcoast",8255756:"Evil Geniuses",7422789:"9Pandas",8894818:"Quest",8724984:"Virtus.pro",8728920:"nouns",4:"EHOME",5:"Invictus Gaming",8582076:"Dandelion Esport Club"}
ITEM_CN = {"blink":"跳刀","overwhelming_blink":"力量跳刀","swift_blink":"敏捷跳刀","arcane_blink":"智力跳刀","black_king_bar":"黑皇杖","aghanims_shard":"魔晶","ultimate_scepter":"阿哈利姆神杖","ultimate_scepter_2":"神杖祝福","refresher":"刷新球","sheepstick":"邪恶镰刀","orchid":"紫怨","bloodthorn":"血棘","sphere":"林肯法球","manta":"幻影斧","skadi":"斯嘉蒂之眼","satanic":"撒旦之邪力","rapier":"圣剑","butterfly":"蝴蝶","monkey_king_bar":"金箍棒","greater_crit":"代达罗斯之殇","assault":"强袭胸甲","heart":"恐鳌之心","shivas_guard":"希瓦的守护","bloodstone":"血精石","octarine_core":"玲珑心","kaya_and_sange":"慧夜对剑","sange_and_yasha":"散夜对剑","yasha_and_kaya":"慧光对剑","nullifier":"否决挂饰","ethereal_blade":"虚灵之刃","abyssal_blade":"深渊之刃","basher":"碎颅锤","desolator":"黯灭","radiance":"辉耀","bfury":"狂战斧","maelstrom":"漩涡","mjollnir":"雷神之锤","gungir":"缚灵索","hurricane_pike":"飓风长戟","dragon_lance":"魔龙枪","force_staff":"原力法杖","glimmer_cape":"微光披风","aeon_disk":"永恒之盘","lotus_orb":"清莲宝珠","pipe":"洞察烟斗","crimson_guard":"赤红甲","wraith_pact":"怨灵契约","helm_of_the_dominator":"支配头盔","helm_of_the_overlord":"统御头盔","vladmir":"弗拉迪米尔的祭品","travel_boots":"远行鞋","travel_boots_2":"远行鞋升级","hand_of_midas":"迈达斯之手","meteor_hammer":"陨星锤","diffusal_blade":"净魂之刃","disperser":"散失之刃升级（当期中文名另核）","mage_slayer":"法师克星","meme_hammer":"陨星锤"}

# Editorial identity annotations are kept separate from mutable API names.
# These resolve common missing labels using period roster/hero context; they do
# not assert that the nickname displayed in the original replay was inspected.
NAME_NOTES = {
    137193239:("Paparazi","03_teams/2022-cn-roster-ledger.md：2021冬季及2022 XG中单；与本局英雄对应"),
    134276083:("old eLeVeN","03_teams/2022-cn-roster-ledger.md：2022 XG三号位；与本局英雄对应"),
    166458146:("J","03_teams/2022-cn-roster-ledger.md：2021冬季XG一号位；与本局英雄对应"),
    156662698:("Srf","03_teams/2022-cn-roster-ledger.md：2021冬季XG三号位；与本局英雄对应"),
    73562326:("zai","C03/C04/C10：Liquid当期名单及本局英雄对应"),
    72312627:("MATUMBAMAN","C03/C04：TI11 Liquid当期名单及本局英雄对应"),
    339235645:("Pakazs","C04：TA—Liquid G3阵容及账户对应"),
    106863163:("Somnus","C15及03_teams/2022-cn-roster-ledger.md：RNG/AR当期阵容"),
    94738847:("Chalice","C15及03_teams/2022-cn-roster-ledger.md：RNG/AR当期阵容"),
    118134220:("Faith_bian","03_teams/2022-cn-roster-ledger.md：2022 LGD；不使用后来Bach昵称"),
    136177710:("圣子华炼","03_teams/2022-cn-roster-ledger.md：RNG冬季阵容及核心英雄对应"),
    119535307:("FelixCiaoBa","03_teams/2022-cn-roster-ledger.md：RNG冬季阵容及辅助英雄对应"),
    162926943:("TK","03_teams/2022-cn-roster-ledger.md：Aries当期阵容"),
    373520478:("White丶Album","02_tournaments/2022-aries-ti11-path.md：3月18日出场记录"),
    121769650:("Nisha","C13：TI11 Secret当期核心英雄对应"),
    94786276:("Nine","TI11当期Tundra名单及中单英雄对应；回放显示ID未核"),
}


def period_team(raw, side):
    tid=raw.get(side+"_team_id")
    if raw.get('leagueid') == 14572:
        # C18: these ids have since been renamed; override only this event.
        cnq_names={8725475:'Team Fusion',7407260:'Team Saiyan',8582076:'Ybb Gaming',1520578:'CDEC',8126892:'Team Magma',7356881:'ShenZhen',8124688:'LBZS'}
        if tid in cnq_names:
            return cnq_names[tid]
    if tid==39:
        return "Evil Geniuses" if raw["start_time"]<1672531200 else "Shopify Rebellion"
    if tid==15:
        return "PSG.LGD" if raw["start_time"]<1696118400 else "LGD Gaming"
    if tid==8574561 and raw["start_time"]>=1682899200:
        return "Azure Ray"
    return PERIOD_TEAMS.get(tid,raw.get(side+"_name") or f"team#{tid}")

TOP_KEYS = "match_id start_time duration leagueid series_id series_type radiant_name dire_name radiant_team_id dire_team_id radiant_win radiant_score dire_score first_blood_time patch version game_mode lobby_type cluster replay_url picks_bans draft_timings radiant_gold_adv radiant_xp_adv objectives teamfights pauses tower_status_radiant tower_status_dire barracks_status_radiant barracks_status_dire".split()
PLAYER_KEYS = ("player_slot account_id hero_id name personaname kills deaths assists level last_hits denies net_worth gold gold_spent gold_per_min xp_per_min hero_damage hero_healing tower_damage stuns camps_stacked creeps_stacked obs_placed sen_placed lane lane_role lane_pos is_roaming position_est times gold_t xp_t lh_t dn_t purchase_log buyback_log kills_log runes_log obs_log sen_log obs_left_log sen_left_log ability_upgrades_arr ability_uses ability_targets item_uses damage_targets damage_inflictor damage_inflictor_received damage_taken killed killed_by hero_hits max_hero_hit life_state permanent_buffs additional_units item_0 item_1 item_2 item_3 item_4 item_5 item_neutral backpack_0 backpack_1 backpack_2 aghanims_scepter aghanims_shard moonshard").split()
TRACKED_TOP = "picks_bans draft_timings radiant_gold_adv radiant_xp_adv objectives teamfights pauses".split()
TRACKED_PLAYER = "times gold_t xp_t lh_t dn_t purchase_log buyback_log kills_log runes_log obs_log sen_log ability_upgrades_arr ability_uses item_uses lane_pos".split()


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def get(cache, key, endpoint, offline=False):
    path = cache / (key + ".json")
    if not path.exists():
        if offline:
            raise FileNotFoundError(path)
        req = urllib.request.Request(BASE + endpoint, headers={"User-Agent":"DotaNovelResearch/1.0"})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=45) as response:
                    data = response.read()
                json.loads(data)
                path.write_bytes(data)
                time.sleep(1.05)
                break
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(2 ** (attempt + 1))
    raw = path.read_bytes()
    provenance = {
        "url": BASE + endpoint,
        "cache_file_modified_at_utc": dt.datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat(),
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "raw_bytes": len(raw),
        "cache_timestamp_note": "本地缓存文件时间，不是比赛时间或上游最后解析时间",
    }
    return json.loads(raw.decode("utf-8-sig")), provenance


def date(timestamp, zone=CN):
    return dt.datetime.fromtimestamp(timestamp, zone).isoformat()


def clock(seconds):
    if seconds is None:
        return "缺失"
    s = int(seconds)
    return ("-" if s < 0 else "") + f"{abs(s)//60:02d}:{abs(s)%60:02d}"


def availability(obj, key):
    if key not in obj:
        return "absent_in_source"
    if obj[key] is None:
        return "null_in_source"
    if obj[key] == [] or obj[key] == {}:
        return "empty_in_source_not_proof_of_no_events"
    return "present"


def infer_patch(timestamp, patches):
    eligible = [v for v, t in patches if t <= timestamp]
    return {"candidate": eligible[-1] if eligible else None,
            "basis":"I：按官方补丁索引发布时间推定；未核赛事客户端/延期更新",
            "event_patch_verified":False}


def sample_adv(match):
    arr = match.get("radiant_gold_adv")
    if not arr:
        return {"status":"missing"}
    winner_sign = 1 if match["radiant_win"] else -1
    low = min(enumerate(arr), key=lambda x: x[1]*winner_sign)
    swings = sorted(((i, arr[i]-arr[max(0,i-5)]) for i in range(5,len(arr))), key=lambda x:abs(x[1]),reverse=True)
    return {"status":"parsed_minute_samples", "sign":"正数=天辉领先；负数=夜魇领先",
            "minute_samples":{str(i):arr[i] for i in [0,10,20,30,40,50,60,75,90,100] if i<len(arr)},
            "final_sample":{"minute":len(arr)-1,"radiant_adv":arr[-1]},
            "winner_worst_sample":{"minute":low[0],"winner_adv":low[1]*winner_sign},
            "largest_5minute_changes":[{"end_minute":i,"radiant_delta":d} for i,d in swings[:3]],
            "limitation":"五分钟差值只定位回看片段；不是单波团战收益、实际知情程度或胜负因果"}


def export_match(raw, source, patches):
    result = {"schema_version":1,"evidence":"F：第三方解析数据；非本轮录像观察", "source":source,
              "observation":{"full_vod_watched":False,"scene_vod_watched":False,"original_replay_parsed_locally":False,"player_pov_verified":False,"team_voice_verified":False},
              "patch_precision":infer_patch(raw["start_time"],patches),
              "field_availability":{"match":{k:availability(raw,k) for k in TRACKED_TOP},"players":[]},
              "match":{k:raw[k] for k in TOP_KEYS if k in raw},
              "players":[],"navigation":sample_adv(raw)}
    result["match"]["start_time_beijing"] = date(raw["start_time"])
    result["match"]["start_time_utc"] = date(raw["start_time"],UTC)
    result["period_team_labels"]={"radiant":period_team(raw,"radiant"),"dire":period_team(raw,"dire"),"basis":"当期赛事编辑标签；原API队名保留在match内，API队名可能已更新为后来队名"}
    for p in raw.get("players",[]):
        q = {k:p[k] for k in PLAYER_KEYS if k in p}
        q["hero_name_zh"] = HERO_CN.get(p["hero_id"],f"待译英雄#{p['hero_id']}")
        q["api_name"] = q.pop("name",None)
        q["api_personaname"] = q.pop("personaname",None)
        q["player_name_period_verified"] = False
        if p.get('account_id') in NAME_NOTES:
            label,basis=NAME_NOTES[p['account_id']]
            q['identity_annotation']={'editorial_name':label,'basis':basis,'method':'按当期阵容与英雄对应补充称呼；与原API职业名、回放显示ID分开','replay_display_name_verified':False}
        q["side"] = "radiant" if p["player_slot"]<128 else "dire"
        result["players"].append(q)
        result["field_availability"]["players"].append({"player_slot":p["player_slot"],**{k:availability(p,k) for k in TRACKED_PLAYER}})
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=pathlib.Path, required=True)
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()
    args.cache.mkdir(parents=True,exist_ok=True)
    patches=json.loads((ROOT/"01_versions/patch-index.json").read_text(encoding="utf-8-sig"))["patches"]
    inventory=[]
    events=[]
    for lid,title in EVENTS.items():
        rows,source=get(args.cache,f"league-{lid}",f"leagues/{lid}/matches",args.offline)
        assert isinstance(rows,list), (lid,"not a match list")
        included=[r for r in rows if START<=r["start_time"]<END]
        events.append({"league_id":lid,"title":title,"source":source,"returned_count":len(rows),"in_window_count":len(included),"earliest_beijing":date(min(r["start_time"] for r in included)) if included else None,"latest_beijing":date(max(r["start_time"] for r in included)) if included else None,"coverage_verified_against_full_bracket":False})
        for r in included:
            inventory.append({"event_title":title,**{k:r.get(k) for k in ["match_id","leagueid","start_time","duration","radiant_team_id","dire_team_id","radiant_name","dire_name","radiant_win","series_id","series_type","radiant_score","dire_score"]}})
    inventory.sort(key=lambda m:m["start_time"])
    save(OUT/"event-inventory.json",events)
    save(OUT/"match-inventory.json",inventory)
    event_lines=["# 赛事覆盖表","","这是各API数据集此次返回的实际日期范围，不是已经与完整赛程逐场核对过的覆盖承诺。资格赛可能与主赛共用联赛ID；当地日期与北京时间可能跨日。","","| 赛事 | 比赛索引数 | 最早—最晚（北京） | 数据源 |","|---|---:|---|---|"]
    for e in events:
        event_lines.append(f"| {e['title']} | {e['in_window_count']} | {e['earliest_beijing'][:10]}—{e['latest_beijing'][:10]} | [API]({e['source']['url']}) |")
    (OUT/'events.md').write_text('\n'.join(event_lines)+'\n',encoding='utf-8')
    completed={}
    failures=[]
    ids=list(dict.fromkeys(mid for *_,members in SERIES for mid in members))
    for n,mid in enumerate(ids,1):
        try:
            raw,source=get(args.cache,f"match-{mid}",f"matches/{mid}",args.offline)
            assert raw.get("match_id")==mid and len(raw.get("players",[]))==10, (mid,"identity/player count")
            assert START<=raw["start_time"]<END, (mid,"outside window")
            result=export_match(raw,source,patches)
            save(OUT/f"data/{mid}.json",result)
            completed[mid]=result
            print(f"{n}/{len(ids)} {mid} {clock(raw['duration'])} {raw.get('radiant_name')} / {raw.get('dire_name')}",flush=True)
        except Exception as exc:
            failures.append({"match_id":mid,"error":str(exc)})
            print(f"FAILED {mid} {exc}",flush=True)
    manifest=[]
    index=["# 逐场检索表", "", "自动整理的数据导航；‘名局’与‘对照’是编辑选材分类。所有单局均未在本轮观看录像。球员API显示名可能已变，表内以英雄区分十个位置，不把平台位置推断当作真实指挥分工。", "", "| 系列 | 类型 | 日期（北京） | 单局数 | 研究问题 |", "|---|---|---|---:|---|"]
    for slug,title,kind,question,members in SERIES:
        games=sorted([completed[x] for x in members if x in completed],key=lambda r:r["match"]["start_time"])
        manifest.append({"slug":slug,"title":title,"selection_type":kind,"teaching_question":question,"requested_match_ids":members,"exported_match_ids":[x["match"]["match_id"] for x in games],"series_order_basis":"显式选局；按start_time排序；上游series_id仅保留不作权威分组","vod_status":"not_watched"})
        first=games[0]["match"]["start_time_beijing"][:10] if games else "缺失"
        index.append(f"| [{title}](series/{slug}.md) | {kind} | {first} | {len(games)} | {question} |")
        lines=[f"# {title}","",f"选材：{kind}。研究问题：{question}。","","本页是第三方解析数据卡。不是已经看过录像的战术结论；游戏ID顺序、分钟曲线、日志用于下一步定位。比赛日期为北京时间。",""]
        for number,g in enumerate(games,1):
            m=g["match"];mid=m["match_id"]
            winner=g['period_team_labels']['radiant' if m['radiant_win'] else 'dire']
            lines += [f"## 第{number}局 · {mid}","",f"{m['start_time_beijing']}；时长{clock(m['duration'])}；天辉 {g['period_team_labels']['radiant']} / 夜魇 {g['period_team_labels']['dire']}；胜方 {winner}；人头 {m.get('radiant_score')}:{m.get('dire_score')}。", "",f"版本候选 **{g['patch_precision']['candidate']}**（按发布日期推定，非赛事客户端精确核验）。[数据档](../data/{mid}.json) · [OpenDota](https://www.opendota.com/matches/{mid}) · [Dotabuff入口，未逐页核读](https://www.dotabuff.com/matches/{mid})", "", "选手名带※为根据当期阵容补充的常用称呼，依据存于数据档；其余沿用API职业名。均不等于已核原回放显示ID。", "", "| 阵营 | 英雄 | 选手称呼 | K/D/A | 正补/反补 | 终局净资产 | GPM/XPM |", "|---|---|---|---|---|---:|---|"]
            for p in g["players"]:
                annotation=p.get('identity_annotation')
                name=((annotation['editorial_name']+'※') if annotation else (p.get("api_name") or "待核（账户ID见数据档）")).replace("|","/").replace("\n"," ")
                lines.append(f"| {'天辉' if p['side']=='radiant' else '夜魇'} | {p['hero_name_zh']} | {name} | {p.get('kills')}/{p.get('deaths')}/{p.get('assists')} | {p.get('last_hits')}/{p.get('denies')} | {p.get('net_worth')} | {p.get('gold_per_min')}/{p.get('xp_per_min')} |")
            lines += ["", "关键装备购入与买活（解析日志，不代表装备已经在身或当时能用）：", ""]
            for p in g['players']:
                purchases=[f"{clock(e.get('time'))} {ITEM_CN[e['key']]}" for e in (p.get('purchase_log') or []) if e.get('key') in ITEM_CN]
                buys=[clock(e.get('time')) for e in (p.get('buyback_log') or [])]
                if purchases or buys:
                    lines.append(f"- {p['hero_name_zh']}："+'；'.join(purchases)+(f"。买活：{'、'.join(buys)}" if buys else '')+'。')
            nav=g["navigation"]
            if nav["status"]!="missing":
                samples="；".join(f"{minute}分 {value:+,}" for minute,value in nav["minute_samples"].items())
                low=nav["winner_worst_sample"]
                lines += ["",f"天辉经济差采样：{samples}。",f"最终胜方最差分钟样本：{low['minute']}分，{low['winner_adv']:+,}。这不代表最大瞬时差，也不能单独证明翻盘成因。"]
            obj=m.get("objectives")
            if obj:
                rosh=[o for o in obj if "ROSHAN" in str(o.get("type","")) or "AEGIS" in str(o.get("type",""))]
                if rosh:
                    labels={'CHAT_MESSAGE_ROSHAN_KILL':'肉山被击杀','CHAT_MESSAGE_AEGIS':'神盾被拾取','CHAT_MESSAGE_AEGIS_STOLEN':'神盾被抢夺','CHAT_MESSAGE_AEGIS_DENIED':'神盾被反补'}
                    lines += ["", "肉山/盾的定位日志（归属与争夺过程需回片）："+"；".join(f"{clock(o.get('time'))} {labels.get(o.get('type'),o.get('type'))}" for o in rosh)+"。"]
            lines += ["", "完整BP顺序、购入/买活/击杀/符/插眼日志、分人分钟曲线、团战聚类与终局装备槽见数据档；各字段是否缺失单独记录。购入时间不能视作送到身上的时间，空日志不能直接视作没有发生。", ""]
        path=OUT/f"series/{slug}.md";path.parent.mkdir(parents=True,exist_ok=True);path.write_text("\n".join(lines),encoding="utf-8")
    save(OUT/"selection.json",manifest)
    (OUT/"match-index.md").write_text("\n".join(index)+"\n",encoding="utf-8")
    stats={"generated_at_utc":dt.datetime.now(UTC).isoformat(),"scope_beijing":"2021-10-18 through 2023-10-30 inclusive","events":len(events),"inventory_rows":len(inventory),"unique_inventory_matches":len({m['match_id'] for m in inventory}),"selected_series":len(SERIES),"requested_matches":len(ids),"exported_matches":len(completed),"parsed_objectives_present":sum(bool(x['match'].get('objectives')) for x in completed.values()),"gold_curves_present":sum(bool(x['match'].get('radiant_gold_adv')) for x in completed.values()),"purchase_logs_nonempty_players":sum(bool(p.get('purchase_log')) for x in completed.values() for p in x['players']),"full_vods_watched":0,"failures":failures}
    save(OUT/"collection-status.json",stats)
    print(json.dumps(stats,ensure_ascii=False,indent=2),flush=True)


if __name__=="__main__":
    main()
