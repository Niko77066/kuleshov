# Seedance 提示词总表 · 800V 热失控

骨架:2-2-video(SUBJECTS/ENVIRONMENT/STYLE/CONTINUITY/AUDIO RULE/TIMELINE + 硬切收尾帧)。
本片 5–8s 短镜 → beats 收到 3–4 个 + 收尾硬切帧。`generate_audio:false`(旁白走 TTS 轨),AUDIO RULE 仅作稳妥声明。
模型 `doubao-seedance-2-0-260128`,`resolution:1080p`,`ratio:16:9`(显式下发,铁律)。

## 固定引用图(公网 URL)

- 包 hero: https://storage.neodrop.ai/kuleshov/800v-thermal-runaway/a02_pack.png
- 剖切芯: https://storage.neodrop.ai/kuleshov/800v-thermal-runaway/a03_module.png
- 风格帧: https://storage.neodrop.ai/kuleshov/800v-thermal-runaway/a01_styleframe.png

## 统一 STYLE 块(所有镜复用)

Forensic engineering-documentary cinematography. Deep carbon-black (#0C0F14) environment, low-key dramatic raking light. Heat reads as ONE color ramp only — amber #FFB02E to orange #FF5A1F to white-hot #FFF3E0; cool coolant-blue #3D9DF6 only on still-normal parts. Bone-white crisp edge highlights. Physically real brushed-metal and matte materials, shallow depth of field, subtle volumetric haze. NO text, NO logos, NO on-screen labels, NO rainbow colors, NO sci-fi HUD, NO blue particle FX, NO cartoon look.

## 统一 AUDIO RULE

No BGM, no music, no score. Diegetic ambience and synchronized physical SFX only. No dialogue or narration.

---

## s01 · 开场 hero(双候选,请求 8s,refs: @Image1=包, @Image2=风格帧)

意图:演播室里的 800V 电池包,一颗电芯已泛琥珀微光,立题"热量怎么传开"。收尾硬切帧交给 s02 剖面 handoff。

### s01-A(宽→中,建立感)
SUBJECTS: An 800V lithium battery pack @Image1 (a row of dark prismatic cells with metal terminal posts in a dark-metal tray); one central cell faintly glowing amber from within, a thin vapor wisp at its vent. Style/lighting reference @Image2.
ENVIRONMENT: Pitch-black forensic investigation studio, matte floor, single soft key from upper-left, faint haze catching the light.
STYLE: [统一 STYLE 块]
CONTINUITY: Keep @Image1 pack and cell design exact. One and only one cell is heating; the rest read cool-blue normal. Damage state: earliest onset, no flame yet.
AUDIO RULE: [统一]
TIMELINE
0:00-0:03 Wide establishing, slow dolly-in on the whole pack in darkness. Only faint blue rim on cells; the central cell just beginning to warm. SFX: deep room tone, faint electrical hum.
0:03-0:06 Medium, continued dolly-in, the one amber cell brightening subtly, vapor thread rising. SFX: low hum, a faint tick of expanding metal.
0:06-0:08 HARD-CUT END FRAME: locked medium-close on the glowing cell centered, camera fully settled, amber core steady, vapor frozen mid-rise, cool-blue neighbors. Hold 0.5s. No fade/dissolve/drift. SFX: hum resolves into room tone.

### s01-B(低角推进,单芯聚焦)
SUBJECTS: same as s01-A.
ENVIRONMENT: same, lower camera height, stronger haze, more negative space above the pack.
STYLE: [统一 STYLE 块]
CONTINUITY: same as s01-A.
AUDIO RULE: [统一]
TIMELINE
0:00-0:03 Low-angle wide, slow push-in along the tray toward the pack, silhouettes rimmed cool-blue. SFX: deep room tone.
0:03-0:06 Rack focus lands on the single amber cell as the push continues; internal glow pulses once, vapor rising. SFX: faint hum, soft crackle.
0:06-0:08 HARD-CUT END FRAME: locked close on the amber cell, off-center right, camera settled, glow steady, haze drifting, neighbors cool-blue. Hold 0.5s. No fade/dissolve/drift. SFX: settles to room tone.

---

## s05 · 喷阀 hero(双候选,请求 8s,refs: @Image1=剖切芯, @Image2=风格帧)

意图:一颗方形电芯泄压阀喷出高速烟气射流(可燃气),"高压锅"喷发。slow-mo 质感。

### s05-A(侧面 tracking,射流为主)
SUBJECTS: A single 800V prismatic battery cell @Image1 in thermal runaway, its top safety vent rupturing; a high-velocity jet of hot grey-white gas and sparks blasts out. Style/lighting reference @Image2.
ENVIRONMENT: Dark forensic studio, cell isolated on a matte stage, deep black background, volumetric haze lit from the side.
STYLE: [统一 STYLE 块]
CONTINUITY: Keep @Image1 cell design exact. The cell body glows orange (#FF5A1F) intensifying to white-hot at the vent; jet is pressurized, directional, not a soft puff. No open flame, hot gas only.
AUDIO RULE: [统一]
TIMELINE
0:00-0:02 Medium side view, locked; the vent bulges, first spurt of gas escapes, cell body reddening. SFX: rising metallic groan, pressure hiss building.
0:02-0:05 Slow-motion side tracking; the vent ruptures fully, a violent directional gas jet with sparks blasts sideways, body glowing orange-to-white. SFX: sharp explosive hiss, spark spatter.
0:05-0:08 HARD-CUT END FRAME: locked medium-close, camera settled, jet sustained and readable, white-hot vent centered, glowing cell body, gas streaming. Hold 0.5s. No fade/dissolve/drift. SFX: sustained roaring hiss into steady jet noise.

### s05-B(3/4 俯,喷发向上冲)
SUBJECTS: same as s05-A.
ENVIRONMENT: same; three-quarter high angle looking slightly down at the vent so the jet climbs toward camera.
STYLE: [统一 STYLE 块]
CONTINUITY: same as s05-A.
AUDIO RULE: [统一]
TIMELINE
0:00-0:02 Three-quarter high, locked; vent seams glowing, pressure swelling under the cap. SFX: metallic groan, hiss building.
0:02-0:05 Slow-motion, slight crash-zoom in as the vent bursts and a gas-and-spark jet erupts upward toward camera, body flashing white-hot. SFX: explosive rupture, sparks.
0:05-0:08 HARD-CUT END FRAME: locked three-quarter close, camera settled, jet plume readable rising out of frame top, white-hot vent, orange body. Hold 0.5s. No fade/dissolve/drift. SFX: roaring jet into steady hiss.

---

## (批 2,待 hero 通过后填参数并生成)

- **s04** 微距膜熔(7s, refs 剖切芯+风格帧):extreme macro, molten separator, anode/cathode touch, short-circuit spark burst, heat glow spreading; end on white-hot micro-arc frozen.
- **s08** 蔓延(7s, refs 包+风格帧):in-pack view, heat color propagating cell-to-cell along the row, neighbors igniting in sequence; end on 3 cells hot, next one just starting.
- **s11** 电弧(6s, refs 风格帧):macro dark, HV busbar insulation charring, a blinding electric arc snaps across the gap igniting gas; end on arc flash frozen (白炽闪帧 handoff).
- **s12** 消防实景(9s, 纯文生视频, LUT 写进 STYLE):firefighters hosing thousands of litres onto a smoking car underbody at night, smoke refuses to relent; end on water sheeting off, smoke persisting.
- **s15** 收尾 hero(7s, refs 包+风格帧,呼应 s01):same pack now calm, the single cell's glow contained/fading, slow pull-out; end on whole pack settled, one faint sealed glow.
