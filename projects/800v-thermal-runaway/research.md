# Research · 800V 热失控:热量是怎么一路传开的

抓取日期:2026-07-14(全部条目)。M0-lite:WebSearch 建底座,script 中每个事实主张必须回链编号。

## 事实清单

**F01 · 热失控的起点是负极保护膜分解(~90°C)**
锂电池热失控是链式反应,通常始于负极表面 SEI 膜在 80–120°C 区间分解放热(约 90°C 起明显),膜破坏后负极直接接触电解液继续放热——"越热分解越快"的正反馈。自加热阶段约 50–140°C。
出处:[CM Batteries](https://cmbatteries.com/lithium-battery-thermal-runaway/)、[Large Battery](https://www.large-battery.com/blog/thermal-runaway-in-lithium-batteries-safety-risks-explained/)、[ScienceDirect 建模综述](https://www.sciencedirect.com/science/article/pii/S2352152X25024752)

**F02 · ~130°C 隔膜熔化 → 内短路,进入失控段(140–850°C)**
PE 隔膜约 130°C 开始熔化(文献亦有 140°C 起大面积熔化),正负极直接接触引发大面积内短路与剧烈焦耳热,反应进入不可逆的失控阶段。
出处:同 F01 + [ScienceDirect 隔膜收缩建模](https://www.sciencedirect.com/science/article/abs/pii/S2352152X24036454)

**F03 · 单芯峰值 ~750°C,剧烈喷发持续 10–30 秒**
实测一例热失控峰值 743.8°C(因体系/SOC 而异,三元更高);NMC 电芯失控时有 10–30 秒的剧烈喷发期,液、气、固三态物质从泄压阀喷出。对比锚:电池包壳体常用铝合金熔点约 660°C——峰值温度足以熔铝。
出处:[Envodrive](https://envodrive.com/en-us/blogs/articles/thermal-runaway-in-lithium-ion-batteries-causes-risks-and-prevention)、[Electric & Hybrid Vehicle Technology](https://www.electrichybridvehicletechnology.com/technical-articles/lfp-vs-nmc-thermal-runaway.html)

**F04 · 喷出的是可燃气:CO₂、H₂、CO + 小分子烃**
喷阀气体体积占比前三为 CO₂、H₂、CO,另含 CH₄、C₂H₄ 等,主要来自电解液(有机碳酸酯)高温分解——本身可燃,遇明火/电弧即燃爆。
出处:[MDPI Batteries](https://www.mdpi.com/2313-0105/9/6/300)、[Springer 喷气综述](https://link.springer.com/article/10.1007/s10973-025-14616-8)、[FAA 报告](https://www.fire.tc.faa.gov/pdf/TC-15-59.pdf)

**F05 · 三元正极高温自释氧:这团火自带助燃剂**
高温下 NMC 正极材料分解释放氧气,隔膜失效后直接供燃——反应自持,不依赖外部氧气,窒息式灭火(泡沫/覆盖)基本无效。
出处:[EV FireSafe](https://www.evfiresafe.com/ev-fire-what-is-thermal-runaway)、[Electric & Hybrid Vehicle Technology](https://www.electrichybridvehicletechnology.com/technical-articles/lfp-vs-nmc-thermal-runaway.html)、[Blazestack](https://www.blazestack.com/blog/7-reasons-why-ev-fires-are-hard-to-put-out)

**F06 · 热量传播四条路:芯壁传导、结构件传导、高温喷气、辐射**
芯到芯的热量走:①相邻芯壁直接传导(最主要);②汇流排、液冷板、结构互连件的二次传导;③高温喷气的对流冲刷(可把热能快速甩到远处电芯)+ 喷出气体二次燃烧;④高温下传导切换为辐射主导。
出处:[Charged EVs](https://chargedevs.com/newswire/thermal-runaway-in-ev-battery-packs-designing-a-mitigation-strategy/)、[ASME J. Heat Transfer](https://asmedigitalcollection.asme.org/heattransfer/article/147/5/051501/1211107/Predictions-of-Cell-to-Cell-Propagation-and-Vent)、[ResearchGate 热传模式定量分析](https://www.researchgate.net/publication/352088623)

**F07 · 蔓延速度量级:芯间 ~50 秒/颗,模组间 ~400 秒**
模组级实验推算:芯间蔓延间隔约 50s,模组间约 400s;NMC-811 全链蔓延速度约为 LFP 的 5 倍(单芯反应速度 9 倍)。多米诺是分钟级,不是小时级。
出处:[ScienceDirect NMC-811 vs LFP](https://www.sciencedirect.com/science/article/pii/S2590116823000802)、[Electric & Hybrid Vehicle Technology](https://www.electrichybridvehicletechnology.com/technical-articles/lfp-vs-nmc-thermal-runaway.html)

**F08 · 800V 的额外一层:绝缘失效与电弧**
电压平台从 400V 升至 800V,绝缘面临表面爬电、体击穿、局部放电三类典型失效;常规 FR-4 板 CTI 仅 175–225V,800V 系统要求 CTI ≥ 600V。振动/湿度/高温/碰撞下绝缘退化可直接引发起火;热失控高温本身就是绝缘杀手,高压直流电弧又成为点燃喷出可燃气的新火源。
出处:[捷配 PCB 技术文](https://www.jiepei.com/design/11316.html)、[腾讯新闻·高压绝缘设计](https://news.qq.com/rain/a/20241022A04UB000)、[EET-China](https://www.eet-china.com/mp/a387733.html)

**F09 · 灭火难:上万升水 + 48 小时复燃窗口**
高压电池起火需大量持续水流直接冷却电芯(数千加仑≈上万升量级),表面熄灭后损伤电芯仍在内部产热,24–48 小时甚至更久后可复燃。
出处:[BGR](https://www.bgr.com/2121201/why-electric-car-fires-hard-put-out/)、[Autoblog 消防员访谈](https://www.autoblog.com/news/firefighter-explains-why-ev-battery-fires-can-reignite-after-they-look-extinguished)、[FireRescue1](https://www.firerescue1.com/electric-vehicles/articles/electric-vehicle-fires-where-the-waiting-game-wins-f934UedqIpVqc1k2/)

**F10 · 工程拦截:隔热 + 定向排气 + 监测**
主流热扩散防护:电芯间垫气凝胶隔热垫、模组间与上盖加云母板、给高温喷气修定向排气通道(隔离喷气与邻芯/箱盖)、BMS 监测预警——目标是把热失控封在单芯,拆掉多米诺。
出处:[知乎·PACK 热失控蔓延抑制](https://zhuanlan.zhihu.com/p/28195088436)、[艾邦气凝胶·材料对比](https://www.aibangairgel.com/a/13759)、[搜狐·热扩散防护方法](https://www.sohu.com/a/690777649_121730969)

**F11 · 法规时间锚:5 分钟逃生 → 2 小时不起火不爆炸(2026-07-01 生效)**
旧标 GB 38031-2020:热扩散起火爆炸前 ≥5 分钟提供报警(逃生窗口)。新标 GB 38031-2025 于 2026 年 7 月 1 日对新申报车型生效(已获批车型 2027-07-01):单芯热失控后整包 2 小时不起火、不爆炸,监测点温度 ≤60°C,烟气不得进入乘员舱。时效钩子:本片制作时新国标刚生效两周。
出处:[新华网](https://www.news.cn/fortune/20260629/ecdbb252acf842e7ac2b432d103471dd/c.html)、[中证网](https://jnz.cs.com.cn/app/html/jnz/126508.html)、[武汉商务局转载](https://sw.wuhan.gov.cn/xwdt/mtbd/202606/t20260630_2814825.shtml)

## 时效声明

F11 为强时效事实(新国标生效两周),片尾角标标注"信息截至 2026-07"。其余为机理类事实,时效风险低。

## 未采信/存疑

- "峰值温度可达 1000°C" 的说法常见于科普文但本轮未找到可靠一手出处,剧本采用保守值 ~750°C(F03 有实测例);
- 芯间 50s/模组间 400s 为特定实验构型的推算值,剧本中以"大约每 50 秒沦陷一颗"级别的量级表述,不当作普适常数。
