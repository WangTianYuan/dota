# 来源、录像入口与覆盖缺口

检索/获取：2026-09-15。只保存比赛数据、必要元数据和原创研究摘要，不镜像文章全文或视频。来源所述事件时间、来源发布时间和本次读取时间分开。

## 数据源

**C01 · OpenDota公开API。** 读取`/api/leagues`和`/api/leagues/{league_id}/matches`确定比赛列表，再读取入选的`/api/matches/{match_id}`。例如[TA—Liquid G3](https://api.opendota.com/api/matches/6819203954)。每局源URL、缓存时间、字节数、SHA256随数据档保存；赛事源随`event-inventory.json`保存。本轮没有向平台申请付费解析或调用写接口。

完整响应保留在仓库外缓存；库内派生数据去掉皮肤、登录时间、订阅、当前段位/榜单基准等无关字段，保留比赛所需字段。`api_personaname`即便留在数据层，也不用于阅读卡填补当期职业名。平台不提供原始连续玩家视角，不能据此声称看过录像。

**C02 · Valve官方补丁索引。** 使用仓库已保存的[51条编号索引](../../01_versions/patch-index.json)，其原始出处为[patchnoteslist](https://www.dota2.com/datafeed/patchnoteslist)。这只用于生成日期候选；例如DreamLeague19决赛已经处在7.33发布之后，不能把整个4月赛事都写成7.32。赛事服务器是否延期更新、热修与具体参数仍需进一步核验。

## 已实际读取的公开文章与赛事页

| 编号 | 来源与发布日期 | 此次用途及限制 |
|---|---|---|
| C03 | [Liquid：Standing on a 1 HP Event Horizon](https://teamliquid.com/news/2022/10/28/liquid-dota-standing-on-a-1-hp-event-horizon)，2022-10-28 | 队伍发布的1血救援复盘；位置、救援时机与买活意义属于注明来源的复盘，不伪装成本轮亲自逐帧观察 |
| C04 | [ClassicDota：TA—Liquid G3](https://classicdota.com/game/159/)，比赛2022-10-23 | 核对比赛ID、阵容、50:59、页面所标7.32c；该旧站不是覆盖2023的完整经典榜，页面补丁标签也不代替原始客户端 |
| C05 | [Dota官方：阿灵顿甲级联赛冠军](https://www.dota2.com.cn/article/details/20220817/220273.html)，2022-08-17 | 官方确认LGD胜者组2:0、Spirit总决赛3:1及75分钟第二局；不包含每一波的详细成因 |
| C06 | [Negitaku：阿灵顿决赛](https://www.negitaku.org/news/n-25527)，2022-08 | 提供四局ID和录像入口，报道中的局面只作导航，不等于自行观察 |
| C07 | [ONE Esports：利雅得两个胜者组系列](https://www.oneesports.gg/dota2/riyadh-masters-upper-bracket-semifinals/)，2023-07-28 | Talon—Liquid换家及BB—Spirit翻盘的同期报道、完整系列录像链接；具体技能链尚待第一手录像核验 |
| C08 | [Talon：利雅得前三](https://talon.gg/blogs/news/talon-secure-top-3-at-riyadh-masters-2023)，2023-08-01 | 当事队伍确认赛事路径；正文将GG此前胜利称为多个Major的口径不采用，DreamLeague与Major不能混算 |
| C09 | [ONE Esports：RNG—Entity 107分钟](https://www.oneesports.gg/dota2/entity-wins-107-minute-ti11-elimination/)，2022-10-20 | 核对名局背景及主赛事时长纪录的范围；情绪化表述和经济差约数不直接升级成比赛事实 |
| C10 | [Liquid：April 2023 Review](https://teamliquid.com/news/2023/04/05/the-liquid-review-april-2023)，2023-04-05 | 当事队伍说明Boxi离场、Jabbz代打及系列结果；只研究Dota段，不复制整篇跨项目月报 |
| C11 | [ESL：柏林Major冠军](https://eslfaceitgroup.com/press/gaimin-gladiators-continue-win-streak-crowned-champions-at-esl-one-berlin-dota-2-major-powered-by-intel/)，2023-05-07 | 主办方确认GG3:1 Liquid及此前利马、DL19夺冠；不是技能机制文档 |
| C12 | [OG：Misha’s long road to TI](https://ogs.gg/mishas-long-road-to-ti/)，2022年TI前 | 队伍说明斯德哥尔摩等赛事的签证/替补背景；不据此替任何选手设定私下态度 |
| C13 | [Dota官方：TI11结束](https://www.dota2.com.cn/article/details/20221030/220309.html)，2022-10-30 | 官方赛果和当日赛况；“发布新英雄”不等于该英雄当天能被比赛选用 |
| C14 | [DLTV：Spirit—Liquid利雅得决赛](https://dltv.org/matches/408987/team-spirit-vs-team-liquid-riyadh-masters-2023)，赛事2023-07-30 | 页面确认3:1，但此次未取得可与OpenDota关联的游戏ID；不把网站自身页面号408987当比赛ID |
| C15 | [RNG—Entity当期阵容/录像入口](https://game-tournaments.com/en/dota-2/international-2022/playoff/rng-vs-entity-462220)，赛事2022-10-20 | 核对阵容与存在中英文录像入口；第三方赛页，不视为本人采访 |
| C16 | [Valve 7.33中文补丁数据](https://www.dota2.com/datafeed/patchnotes?version=7.33&language=schinese)，补丁2023-04 | 完整JSON已取至本地缓存；定向读取地图重做、双生之门、肉山与减益免疫相关条目，不称为已核全部英雄参数 |
| C17 | [利雅得完整赛程与结果](https://www.oneesports.gg/dota2/riyadh-masters-2023-schedule-results/)，更新2023-07-31 | 与API日期覆盖对照，确认当地最后两天仍有比赛；不把API最后一天当作赛事结束 |
| C18 | [Spectral：TI11中国预选逐局列表](https://stats.ru.spectral.gg/lrg2/?league=ti11_cn_quali&mod=matches)，赛事2022-09-08—12 | 取得42个游戏ID、19组系列、当期双方标签与时长；随后由OpenDota单局确认独立leagueid为14572，42局详情均已获取。17局合计人头与OpenDota不同，保留分歧 |
| C19 | [Esports Charts：中国预选赛程结果](https://escharts.com/tournaments/dota2/international-2022-china-qualifier/schedule)，赛事2022-09-08—12 | 核对19组已比赛系列的赛果、首轮Fusion—Saiyan为BO1及Aries三轮路径；赛程计划时间不代替API实际开始时间 |
| C20 | [Spectral：利雅得逐局列表](https://stats.ru.spectral.gg/lrg2/?league=riyadh_masters_2023&mod=matches)与[决赛四局卡片](https://stats.ru.spectral.gg/lrg2/?gets=0_232&league=riyadh_masters_2023&mod=matches-cards)，赛事2023-07 | 235行事实摘录；与API比较发现15个额外ID。补录决赛40个人次的英雄对应、赛果与时长；卡片无完整过程日志。G3的29000只作来源记录值 |
| C21 | [noxville关于利雅得缺失回放的公开回复](https://www.reddit.com/r/DotA2/comments/15egpw8/why_cant_i_see_the_last_few_games_of_the_riyadh/)，讨论2023-07-31 | 直读其关于迪拜集群及为datdota人工录入15局的陈述（Q）；不视为Valve官方故障公告，也不据此宣布所有数据永久无法恢复 |
| C22 | [利雅得淘汰赛对阵页](https://escorenews.com/en/dota-2/riyadh-masters-2023/playoff)，赛事2023-07 | 与C17对照最后两日的系列阶段及结果；网站自身比赛页号与Dota游戏ID分开，当前队名不直接倒填历史 |

C18/C20通过web工具读取实际表格；直接HTTP请求返回验证页，未取得可称为原站完整HTML的文件。资料库保存的是标明来源的事实摘录。datdota本轮访问403/失败，没有取得其人工补录原表。对C20额外的15个ID逐一请求OpenDota详情均为404，具体结果见补录文件的核查记录。

C07与C09是记者对比赛的描述。本库据此提出回看片段与研究问题；它们**不足以单独批准具体技能交互进入正文**。历史参数仍以Valve资料/当期客户端为主。来源可靠性按具体字段处理，官方文章也可能有术语笔误或宣传性判断。

## 录像入口与读取状态

均为已定位链接，**本轮未播放核片**。第二轮已尝试用浏览器打开TA—Liquid G3官方入口，但创建页超时，随后浏览器连接失败，未看到画面。YouTube网页抓取也多次返回限流/错误；不能从标题声称看过内容。链接可能因地区/平台状态变化而不可播放。

| 对局 | 入口 | 定位与状态 |
|---|---|---|
| TA—Liquid G1 | [dota2官方录像](https://www.youtube.com/watch?v=SH4ZwJAJj04) | 同期索引提供的第一局入口；未核视频内时钟 |
| TA—Liquid G2 | [dota2官方录像](https://www.youtube.com/watch?v=wrykNstiM4c) | 同期索引提供的第二局入口；未核视频内时钟 |
| TA—Liquid G3 | [dota2官方录像](https://www.youtube.com/watch?v=MtioXmRXrq8) | Liquid官方文章嵌入从视频51:26开始的片段；游戏时钟映射未独立确认 |
| RNG—Entity | [dota2官方录像](https://www.youtube.com/watch?v=yLL3N2IkHnA) | 已核频道/标题元数据；游戏时钟92分钟以后为本轮优先回看区 |
| 阿灵顿G1 | [单局录像入口](https://youtu.be/yTKEcBdihTs) | Negitaku赛后页提供；未逐页确认频道与内容 |
| 阿灵顿G2 | [单局录像入口](https://youtu.be/84wu8YaB1cE) | 优先回看游戏43—52、56—60、72:30以后；未映射视频秒数 |
| 阿灵顿G3 | [单局录像入口](https://youtu.be/2ZhvG2aOHuo) | 同上；保留27分钟快局作长盘之后的对照 |
| 阿灵顿G4 | [单局录像入口](https://youtu.be/VXXjP-ZFZzc) | 同上 |
| 利雅得Talon—Liquid全系列 | [Gamers8录像入口](https://www.youtube.com/watch?v=SXWRsd31lMI) | 从同期报道的“Full series”链接取得，页面限流；不是拿集锦代替全局 |
| 利雅得2023决赛 | [官方菲律宾语转播](https://www.youtube.com/watch?v=WhbOFdApFNI) | 频道元数据标注官方转播，含最后一天对局；尚未分割各局 |
| 利雅得2023决赛集锦 | [ESL Dota 2集锦](https://www.youtube.com/watch?v=9VcbDnxfxnw) | 官方频道发布但说明为NoobFromUA集锦，**不是完整BO5录像** |
| 柏林决赛 | [ESL Dota 2入口](https://www.youtube.com/watch?v=RDXFc3u_ScI) | 已检索频道/标题，未核是否完整单日/系列或剪辑，不标为全局已看 |

其他已存数据的系列尚未逐一绑定稳定中文全场录像。可从比赛ID和准确日期定位；不能用2026平台搜索结果的解说身份倒填2021。

## 需要保留的缺口

1. **利雅得2023过程数据仍缺，身份已补。** 与Spectral交叉比较后找到15个缺失ID：14局在当地7月29—30日，另1局是7月25日BB—9Pandas系列的一局。15个API详情均404。最后两日的系列结果、逐局时长及决赛十人阵容已另存[补录](supplements/riyadh23-recovery.md)，不计入171局详细解析。尚无这些局的购买、买活、肉山、经济曲线和连续动作。
2. **TI11中国区预选数据缺口已补。** 独立联赛14572的42局已取得详细数据；19组已比赛系列与C18/C19对照。Aries确为先2:0 VG、再0:2 RNG、最后1:2 iG。小说第三名路线仍属已锁虚构方向，不回写历史；各局具体动作仍待看片。
3. **非Major和地区赛事。** 本次有迪拜、Dota PIT、IWO、DreamLeague及中国DPC，但未穷尽六大区各级联赛、公开预选、BTS等杯赛。IWO索引中含较早公开资格赛、部分队伍ID为空；3329不能被称作3329场顶级强队经典战。
4. **杭州亚运会。** 在时间范围内，且与CN线相关；正式比赛单局/阵容数据未并入本次API库，另补官方成绩册和转播，不用普通DPC规则自动代替该赛制。
5. **2021开篇邻近月份。** 精选只有6局发生在2021年。近期设计优先使用其中的冬季对局以及已有7.30d/e研究；不能因2023案例好看而强迫开篇主角提前发现后来的地图和英雄机制。
6. **实时状态。** 无连续十人坐标、全体当期血蓝/技能冷却/信使物品、完整战争迷雾和私人语音。眼位、终局装备、购买时间和英雄总施法次数不能填满这些空白。
7. **数据异常。** 当前队名污染、职业昵称缺失、系列ID拆分、团战聚类缺项、暂停信息大面积缺失已显式处理。中国预选新增发现Fusion、Ybb、CDEC、Magma、深圳、LBZS等API名称已变；只对该赛事恢复当期编辑标签，原值保留。17局中两站合计人头不同，不能当同一口径拼接。Spectral的Finished列与卡片时间含义不同，且12小时显示缺AM/PM，不能直接转换为精确北京时间。

## 下一步补证的优先级

先围绕作者实际选择的前期代表局，读一组7.30e/7.31比赛和对应英雄机制，再选一个能直观兑现的交锋。与小说近期无关的名局先保留数据和研究问题；进入相应赛季时逐段核片。新来源、看过的具体区间和推翻旧判断的证据写回对应卡，不另开只有“已学习”的空泛总结。
