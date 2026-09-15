# Batch 012：TI10 G5来源与取证记录

ID: sources:batch-012-ti10-evidence
retrieved_at：2026-09-14
event_time：2021-10-17（赛事日）；中国观赛场景跨至10月18日。
状态：原始回放已完整取得并解析；精确入口状态部分可用，完整视频观看/选手POV未完成。

## 来源登记

| ID | 来源 | 本轮实际读取与可支持范围 |
|---|---|---|
| S12-01 | [OpenDota比赛API](https://api.opendota.com/api/matches/6227492909) | 已取得JSON；Match ID、开始时间字段、时长、阵容、购买日志、分钟经验和目标事件。不是玩家视角；购买时间不等于持有时间；公开显示名可变，不用于复原当年ID |
| S12-02 | [Valve官方回放](http://replay273.valve.net/570/6227492909_1934613958.dem.bz2) | HEAD200，完整下载124472677字节，bzip2校验解压成功，得到150460311字节Source 2回放；内部Match ID一致。原文件保存在本地临时取证目录，不将整场回放放进公开仓库 |
| S12-03 | [Valve编号补丁接口](https://www.dota2.com/datafeed/patchnoteslist) | 已读7.30d/e条目，编号日期不等于客户端精确推送秒数 |
| S12-04 | [Valve 7.30d数据](https://www.dota2.com/datafeed/patchnotes?version=7.30d&language=schinese) | 已读完整JSON，并筛本场英雄相关改动；不是全部机制手册 |
| S12-05 | [构建5061历史元数据](https://github.com/SteamDatabase/GameTracking-Dota2/blob/211b4bb05f3607d1597833d028d15853ef91154d/game/dota/steam.inf) | 已读ClientVersion/ServerVersion=5061，与回放构建一致。镜像提交时间2021-10-17 04:00:24 UTC；客户端VersionDate仍标Oct16，保留时区/构建日期差异 |
| S12-06 | [构建5061技能配置](https://github.com/SteamDatabase/GameTracking-Dota2/blob/211b4bb05f3607d1597833d028d15853ef91154d/game/dota/scripts/npc/npc_abilities.txt) | 已读天怒四技能定义；与2021-09-26提交e33c80190789d90d7fb275e2677bd84b595dd83a同文件哈希一致。客户端文件镜像，不把未公开引擎实现当作已知 |
| S12-07 | [构建5061物品配置](https://github.com/SteamDatabase/GameTracking-Dota2/blob/211b4bb05f3607d1597833d028d15853ef91154d/game/dota/pak01_dir/scripts/npc/items.txt) | 已读树枝、圆环、智力斗篷、鞋、传送和海洋之心相关字段；传送目标限制、基础施法/冷却与入口装备属性可核 |
| S12-08 | [中国官方7.30公告](https://www.dota2.com.cn/article/details/20210818/220130.html) | 已读天怒段落；当期中文名“奥法鹰隼”、震荡光弹减速改40%、神秘之耀持续2.2秒。不能写作“奥术鹰隼” |
| S12-09 | [中文总决赛录像](https://www.bilibili.com/video/BV11F411Y7bk/) | 浏览器读到五个分P；第五分P时长01:11:19。切换分P操作超时，随后浏览连接失败；未取得比赛画面、未观看全场、未复原队内语音 |
| S12-10 | [Dotabuff日志](https://www.dotabuff.com/matches/6227492909/log) | 本轮网页工具访问失败；旧数据沿用仓库Batch 004已核摘录，不冒充本轮重新读取 |
| S12-T01 | [Manta解析器](https://github.com/dotabuff/manta/tree/v1.5.0) | Dotabuff维护的MIT开源Source 2解析器；本轮临时使用v1.5.0，读取实体、字符串表、文件信息 |
| S12-T02 | [OpenDota解析源码](https://github.com/odota/parser/blob/master/src/main/java/opendota/Parse.java) | 本轮只读实体物品和坐标处理等相关代码，用于核对字段含义；不是运行了OpenDota完整后端 |

## 完整性与方法

压缩回放SHA256：`ca897c1a7229b1a19c92e4c71ea92682bf26c3b1e8584b9e89793d52cafe9f15`。

技能配置SHA256：`efa51e0d1584d07d3d7ab04eb7481a54110a80133acc6844f8f3b89e20b79779`。

回放完整解析至tick93145；FileInfo记录playback_ticks=93145、playback_time=3104.8335秒。按39个目标时刻取样，实际时间为每个目标之后第一个已解析实体包时间，未用线性插值伪造精确帧。所列540秒样本实际为540.0348秒。

选手本体必须由`CDOTA_PlayerResource`的`m_hSelectedHero`定位，并同时匹配entity index和serial。对全部390个选手样本验证玩家槽位一致。原始回放含有同类英雄复制体；初步按类名首匹配会混入XP=0的复制体，已经修正并重新提取全部样本，早期调试输出不作为证据。英雄本体、幻象/复制体和当前API昵称不得混为一谈。

提取保留物品槽位：主栏、背包、储藏、传送、中立物品必须分开。字段中的可见团队标记只作为局部线索，不宣称完成整个战争迷雾或真人注意力重建。

## 复现与依赖边界

本轮因现有API不足以回答在身装备/冷却问题，临时使用Go官方便携运行时与Manta v1.5.0读取原始回放。运行时来自go.dev，压缩包SHA256与官方元数据核对通过；依赖安装在本地临时取证目录，没有修改系统PATH或小说仓库的运行依赖。

仓库只收少量派生快照、原创提取代码与来源说明。复现用文件见`batch-012-replay-extractor/`；原始回放、完整客户端配置与完整中间实体输出不入库。维护代价仅是后续需要重现时运行隔离的提取工具，不能将解析器成功等同于全部事实或视觉核验完成。

## 失败/限制记录

- OpenDota parser未发现可直接使用的latest release资产，未运行其服务。
- 起初尝试历史`game/dota/scripts/npc/items.txt`返回404；通过该提交树定位到真正的`game/dota/pak01_dir/scripts/npc/items.txt`后读到物品定义。
- B站播放器控制不可用，本轮未取得视频画面。
- 终局比分字段29—12与选手击杀合计28—12分歧尚未完全解释；原片终局计分牌未核。
- 9分钟OpenDota经济差与回放净资产求和不一致；未混合字段形成精确经济结论。
- FileInfo结束时间为文件元数据，不等于中国直播GG墙钟；未用API开始时间加比赛时长作结。

## 结果入口

- 人可读：[接管状态卡](../05_matches/ti10-gf-g5/batch-012-entry-state.md)。
- 派生摘要：`batch-012-ti10-extract.json`（39目标时刻的筛选摘录，不是逐帧全量数据库）。
- 创作分离：`06_story/batch-012-first-simulation-working-draft.md`。
