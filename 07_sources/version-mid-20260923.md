# 二号位版本研究：本轮来源与证据边界

ID: sources:version-mid-20260923
读取日期：2026-09-23（America/Los_Angeles；数据文件保留UTC时间，部分为09-24）。F为规则事实，Q为来源表达，O为数据观察，I为推断，H为待验证；不使用这些标记掩盖证据缺口。

## 官方规则（F）

实际通过公开JSON接口读取相关条目；网页入口供人工复查。接口元数据时间不作为上线秒级时间，中文文章日期也不自动等于全球客户端切换日期。

| ID | 原始来源与定位 | 本轮支持的结论 |
|---|---|---|
| V30E | [7.30e接口](https://www.dota2.com/datafeed/patchnotes?version=7.30e&language=english)，hero 90/17 | 光法炎阳之缚削减魔抗改为16/22/28/34%；灵魂形态冲击波治疗比例改为40/50/60%；蓝猫基础攻击-2、电子涡流冷却调整 |
| V31 | [7.31接口](https://www.dota2.com/datafeed/patchnotes?version=7.31&language=english)，item ability_id 77/176，hero 90/17；[中文发布页](https://www.dota2.com.cn/article/details/20220224/220244.html) | 挂件失去3%法强、获得4%减蓝耗和25分钟属性翻倍；虚灵刀改为慧光参与合成；光法冲击波前摇0.3→0、半径375→400；蓝猫基础回蓝等调整 |
| V31B | [7.31b接口](https://www.dota2.com/datafeed/patchnotes?version=7.31b&language=english)，hero 17 | 蓝猫电子涡流冷却改为20/18/16/14秒；接口无某英雄条目不能证明不存在未编号热修 |
| V31C | [7.31c接口](https://www.dota2.com/datafeed/patchnotes?version=7.31c&language=english)，hero 90/17/137 | 光法基础移速330→320、查克拉补魔降低；獸“踏”（践踏）、“咤”的参数削弱，“突”的音效可在战争迷雾中被听见；不据此假设对手有全图坐标 |
| V31D | [7.31d接口](https://www.dota2.com/datafeed/patchnotes?version=7.31d&language=english)，item 77、hero 90、general_notes | 挂件减蓝耗被3%最大魔量替换；光法冲击波前三档伤害降低；玛西进入队长模式 |
| V32 | [7.32接口](https://www.dota2.com/datafeed/patchnotes?version=7.32&language=english)，general_notes、hero 90；[中文完整页](https://www.dota2.com.cn/article/details/20220825/220274.html) | 獸进入队长模式；中路附近小野点移除、经验曲线变化；光法灵魂形态冷却65→85；每等级首塔刷新防御符的改动不能提前写进7.30e |

规则解释边界：冲击波施法前摇归零≠满蓄力瞬发；新增施法收益≠所有英雄都该堆挂件；官方削弱某英雄≠官方证明某打法是唯一最优解。各来源只摘与本轮结论有关的规则，未完成所有热修考古。

## 历史采用与当期讨论

**Q-HIST：** [ONE Esports：Nine中单光法报道](https://www.oneesports.gg/dota2/keeper-of-the-light-mid-tundra-esports/)，署期2021-08-23，已读相关段落。报道记载Nine在ESL One Fall对T1使用中单光法。用途仅为“TI10前已有公开中单光法实例”的历史报道依据；不是最早发明者证明，未据此采用文中的技能数值或整场过程，也未观看嵌入视频。精确局号尚未回接原始赛事数据。

**Q-COM：** [2022年3月的光法中单讨论](https://www.reddit.com/r/DotA2/comments/ts4auj/)，检索元数据日期2022-03-30，正文页面现显示相对日期，精确到日不用于小说事件排序。已读相关评论：Atramhasis指出旧多挂件路线不能照搬到7.31，讨论飞鞋、虚灵刀与大骨灰；I_Am_A_Pumpkin描述清线、叠野及装备转抓人的思路；其他用户提到侧站避波、封野、突进和阵容拆塔问题。

这直接证明当期社区已经讨论这些方案和反制，不证明评论者排名、Nine每场出装、所有数值正确或英雄必胜。评论中有相互冲突及可能不准确的技能说法，本轮不把整帖当规则源。主角不能因采用这些常见方案就被写成发明者。

## 比赛数据（O）

定点读取`05_matches/classics-2021-2023/data/`内已提交OpenDota派生记录。本轮没有重新向API下载这些比赛；记录保留上游URL、旧缓存元数据、当前文件SHA256和所选字段，见[数据摘录](version-mid-20260923-data.json)。

| ID | 来源 | 直接观察 | 不能证明 |
|---|---|---|---|
| M-STORM-C | [6582379623](https://api.opendota.com/api/matches/6582379623)，TSM—OG，2022-05-22 UTC | 数据署名bzm的蓝猫多次购买挂件，17:00购买BKB；时间属于购买日志 | 六个挂件同时生效、全部交易细节、每次购买动机、单件装备导致获胜 |
| M-STORM-D | [6705943008](https://api.opendota.com/api/matches/6705943008)，LGD—Spirit，2022-08-13 UTC | 数据署名NothingToSay的蓝猫有慧光、慧夜对剑、BKB购买记录 | 不同选手/阵容的两局构成因果实验，或新版本再无人购买挂件 |
| M-KOTL-D | [6707633683](https://api.opendota.com/api/matches/6707633683)，Spirit—LGD，2022-08-14 UTC | 数据署名NothingToSay的光法有13:35大骨灰、22:14 BKB记录，中路线标签及10分钟66补刀 | 飞鞋缺失于本次筛选即代表整局没飞鞋；光法为何转BKB；连续抓人、视野、沟通过程 |

7.30e最低基线另外保存8条英雄使用案例，只用于避免把既有中单写成新位置。过滤方法：既有选局语料、日期候选7.30e、`lane_role=2`、指定公开选手署名，再人工检查补刀和上下文线索；不是全量职业样本。署名是API字段，不冒充逐局选手身份核验；版本字母仍为日期推定，赛事客户端尚未独立确认。

## 本轮受限与复查方法

- Spectral `.stats.spectral.gg`与`.stats.ru.spectral.gg`相应页面返回403；搜索摘要不足以复原完整中路生态，未引用胜率/排名。
- 没有本轮视频观看、原始Replay解析或实机测试结果；不需要安装新环境才能交付当前规则与数据结论。
- 复核购买摘录：按`match_id`和`player_slot`回到仓库原JSON，对照`purchase_log`；购买秒数÷60显示为分秒。
- 复核版本事实：打开表中官方接口，查对应`hero_id`或物品的`ability_id`；不要误用`item_id`或把光法认作hero 97。
- 未来进入精确场景时，只补涉及的连续画面、玩家可见信息、物品实际在身状态与机制交互；不把所有字段全核当作开始创作的先决条件。
