# Research · Samsung Health AI 同意条款

**抓取时间：2026-07-14**（事件发生于 2026-07-10 前后，属进行中新闻；出厂前建议复核 F08 监管动态）

## 核心事实

- **F01 · 事件与时间**：2026 年 7 月上旬起，Samsung Health 用户在更新后的隐私设置中收到新同意项，标题 **"Consent to the Use of Health Data for AI Training and Modelling"**；与 Samsung Health 大改版及 Galaxy Watch 9（7 月 22 日发售）同期推出。首发报道 How-To Geek（2026-07-10）。
  来源：https://www.howtogeek.com/samsung-health-requires-ai-training-consent/ ；https://9to5google.com/2026/07/13/samsung-health-ai-training-data-consent/

- **F02 · 官方用途表述（原文）**："The health data you have allowed us to collect and process will be used for AI training and modelling, **including human review**, to improve Samsung Health, including algorithms to analyse health conditions and our AI features." —— 明确包含人工审看。
  来源：官方同意页 https://samsunghealth.com/shd/gen-ai?cc=US&lc=en （2026-07-14 浏览器实录，全文存档见 `research-raw/official-consent-page.md`）

- **F03 · 覆盖的四类数据（官方原文分类）**：
  1. 健康与身心数据：身体测量、营养、步数与活动、睡眠；
  2. 用药数据：药物，**含处方与剂量**；
  3. 健康记录：医疗与临床数据——**诊断、预后、检验结果、既往病史与治疗**；
  4. 经期数据：月经周期，含身体状况与生理指标（如心率）。
  来源：同 F02（官方页实录）

- **F04 · 拒绝的代价（弹窗原文）**：拒绝或退出时弹窗警告："You will not be able to sync health data with your Samsung account and your health data **will be deleted** unless retained pursuant to applicable law." —— 不同意 = 关云同步 + 删除已同步数据。
  来源：https://9to5google.com/2026/07/13/samsung-health-ai-training-data-consent/ ；https://www.gsmarena.com/samsung_health_data_ai_training_consent-news-73683.php （2026-07-11）

- **F05 · 删除范围是云端同步数据**：删除针对 Samsung 账户已同步数据；设备本地数据不受同意选择影响（多家报道一致口径）。**准确性关键：不能说"删除你所有健康数据"。**
  来源：https://www.gsmarena.com/samsung_health_data_ai_training_consent-news-73683.php ；https://cybernews.com/news/samsung-health-ai-training-delete-user-data/

- **F06 · 撤回机制（官方原文）**："You may withdraw your consent at any time in the Samsung Health settings > Privacy. If you withdraw your consent, we will stop using your data for AI training and modelling." 同意跨设备生效（同一 Samsung 账户）。但据报道，事后撤回同样触发关同步+删数据逻辑（F04）。
  来源：官方页实录（同 F02）；GSMArena（同 F04）

- **F07 · 官方页的沉默处**：同意详情页**只字未提**拒绝会删数据——删除警告只出现在拒绝动作后的弹窗里；也未说明：人工审看前是否匿名化、谁执行审看、训练数据保留多久、撤回是否影响已训练完的模型。
  来源：官方页实录比对（2026-07-14，本项目自查）；缺口指认另见 https://www.gadgetreview.com/samsung-health-will-delete-your-data-if-you-refuse-ai-training-consent

- **F08 · GDPR 张力**：GDPR 要求对健康数据（Art. 9 特殊类别）的同意"自由给出"（freely given，Art. 7(4) 反捆绑）；"不同意 AI 训练就关云同步删数据"被用户与媒体质疑构成功能捆绑；三星社区论坛已有欧洲用户主张违规。**截至 2026-07-14 无监管机构正式表态**——脚本措辞用"被质疑"，不用"违反"。
  来源：https://www.androidcentral.com/apps-software/want-samsung-health-cloud-sync-you-may-have-to-agree-to-ai-training-first ；论坛反应综合自多家报道

- **F09 · 舆论定性**：Android Authority 读者投票 **86% 表示会拒绝**；媒体标题普遍用 "ultimatum" / "consumer-hostile" / "requirement, not a choice" 定性。
  来源：https://www.androidauthority.com/samsung-health-train-ai-data-3686684/ （2026-07-13）

- **F10 · 机制定性（防标题党）**：这是一次 **opt-in 同意请求**，不是默认开启偷跑；争议点不在"偷偷用"，而在**拒绝的代价**——把与 AI 训练无关的云同步功能作为同意的对价。
  来源：机制综合 F02/F04/F05；对照 https://www.androidpolice.com/dont-want-to-help-samsung-train-its-ai-no-health-data-for-you/

## 可实录的真实页面（供 anchors/实录声部）

1. 官方同意详情页 `samsunghealth.com/shd/gen-ai`（已验证可访问，正文完整）——F02/F03/F06 的证据画面
2. 媒体报道页（9to5Google / GSMArena，内含拒绝弹窗截图）——F04 弹窗画面的出处引用
