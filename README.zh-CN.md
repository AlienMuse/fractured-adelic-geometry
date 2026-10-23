<p align="center">
  <a href="https://doi.org/10.5281/zenodo.23585887"><img src="assets/hero.svg" alt="Fractured Adelic Geometry — 四卷、随书代码与附录环绕基本线的 D6 adelic 蜂巢" width="100%"></a>
</p>

<p align="center">
  <a href="https://doi.org/10.5281/zenodo.23585887"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.23585887.svg" alt="DOI"></a>
  <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/deed.zh-hans"><img src="https://img.shields.io/badge/license-CC%20BY--NC--ND%204.0-0A131E?style=flat" alt="许可：CC BY-NC-ND 4.0"></a>
  <a href="https://github.com/AlienMuse/fractured-adelic-geometry/releases/tag/v1.0.0"><img src="https://img.shields.io/badge/release-1.0.0-1E5A88?style=flat" alt="版本 1.0.0"></a>
  <img src="https://img.shields.io/badge/pages-571-536372?style=flat" alt="571 页">
  <img src="https://img.shields.io/badge/obstructions-14-536372?style=flat" alt="14 个障碍">
  <img src="https://img.shields.io/badge/series-04-536372?style=flat" alt="系列 04">
  <a href="VERIFY.md"><img src="https://img.shields.io/badge/OpenPGP-signed-B8913B?style=flat" alt="OpenPGP 签名"></a>
  <a href="VERIFY.md"><img src="https://img.shields.io/badge/timestamps-RFC%203161%20%C2%B7%20Bitcoin-B8913B?style=flat" alt="RFC 3161 与比特币时间戳"></a>
</p>

<p align="center">
  <b><a href="https://github.com/AlienMuse/fractured-adelic-geometry/releases/download/v1.0.0/Fractured-Adelic-Geometry-v1.0.0-Preview.pdf">阅读预览版</a></b>（73 页，72.0 MB）·
  <a href="#下载">下载</a> ·
  <a href="#四卷">四卷</a> ·
  <a href="#引用">引用</a> ·
  <a href="VERIFY.md">校验</a> ·
  <a href="README.md">English</a>
</p>

<br>

# Fractured Adelic Geometry

Vincent Liu · Research Architecture Edition 1 · 2026 · [English](README.md)

> *难题不在原地强攻；而是在它周围建起理论，直到问题变得自然而自行化解。*
> <br>— Series Note

《Fractured Adelic Geometry — A Foundational Framework for the Birch and Swinnerton-Dyer Conjecture》是一部四卷合一的
专著（正文为英文），共 571 页。它是 WiseMotif Monograph of Mathematical Intelligence 的第四部著作，属于
Grothendieckian Programme，但自成独立体系：它是该 Programme 的研究课题之一——在一个问题上把 Programme 的方法，即递归式
数学发现（recursive mathematical discovery），完整地走一遍：提出结构，用答案已知的情形检验它，把经受住检验的部分
抽象出来，再在新的层次上重新提出问题，正如 Grothendieck 的"上涨的海"（rising sea）。

所选的问题是 Birch–Swinnerton-Dyer 猜想（BSD 猜想）。本书追问：**为什么六十年的工作只在解析秩不超过一时得到定理？
什么样的对象能让这个猜想成为一个陈述，而不是两个互不相关的量之间的比较？**

**Birch–Swinnerton-Dyer 猜想仍未解决。本书没有证明它，没有证明任何此前未知的情形，也没有对任何一条曲线证明
Tate–Shafarevich 群的有限性。** 本书给出的是：把方法毫不让步地用到底之后问题所处的状态——这个框架会给出什么、
需要什么、每条通往它的路线停在哪里。

<table>
  <tr>
    <td align="center"><b>4</b><br><sub>卷，<br>合为一册</sub></td>
    <td align="center"><b>10 · 56</b><br><sub>部 ·<br>章</sub></td>
    <td align="center"><b>571</b><br><sub>页</sub></td>
    <td align="center"><b>12</b><br><sub>条公理<br>F1–F12</sub></td>
    <td align="center"><b>12 · 14</b><br><sub>个猜想 ·<br>个障碍</sub></td>
    <td align="center"><b>1</b><br><sub>Master Identity，<br>猜想</sub></td>
    <td align="center"><b>30 · 364</b><br><sub>幅矢量图 ·<br>条参考文献</sub></td>
  </tr>
</table>

## 核心想法：一个对象，两种描述

每一个已证明的情形，都是靠一座"桥"从解析的一侧跨到算术的一侧——Heegner 点、Kolyvagin 系统、Kato 的 Euler 系统——
每座桥只沿一个方向运送一个类，而这些桥都止步于解析秩一。本书的论点是：**桥是症状，不是解答。** 之所以需要桥，是因为
把算术概形描述成 Spec ℤ 上的局部环化空间，能极好地看见 Zariski 局部化与平展下降，却完全看不见 Frobenius 动力学、
阿基米德完备化、整 *p*-进 Hodge 结构和正则化行列式。在这种语言里，猜想的两边是不同种类的对象，它们之间的比较只能
是一座桥。

本书提出改换对象本身。**Frobenius–Arakelov–Prismatic（FAP）空间**的范畴把凝聚解析结构、每个素数处的整棱柱
F-gauge、Fargues–Fontaine 实现、Arakelov 边界、绝对分圆结构和一个算术流，作为基础而非附加的数据同时携带，并由
十二条公理 F1–F12 约束。它为 ℚ 上的椭圆曲线 *E* 配上一个算术谱 *X*<sub>E</sub> 和一条行列式线
Δ(*X*<sub>E</sub>)，带有一个解析的、一个代数的两种平凡化。**Master Identity**（Conjecture A）断言这两种平凡化
在整数意义下一致。零点阶成为一个核的维数，首项系数成为一个行列式。

| 方法 | 本书做了什么 |
|---|---|
| **诊断** | 把秩二障碍刻画为外代数作用在导出形变环上的一个结构性陈述，而不是技术上的偶然（第 27 章） |
| **构造** | 给出 FAP 空间、算术谱 *X*<sub>E</sub>、范畴化的 Lefschetz–Verdier 迹公式和基本线（fundamental line）的规格 |
| **检验** | 在有限域上逐条审核十二条公理，并对照 ℤ 上的 𝔾<sub>m</sub>——即答案已知的情形 |
| **下降** | 由 Master Identity 与公理证明秩公式和首项系数公式 |
| **定价** | 按五级刻度给十二个猜想评级，并给出十四个障碍的图谱与攻克方案 |
| **认证** | 给出七层计算架构：带认证的引擎、证书层级和证明义务账本 |
| **反驳** | 用一章专门反对本书，写明什么会推翻这个框架 |

## 四卷

四卷与附录装订为一册。下面每张封面把对应的卷放在 D₆ adelic 蜂巢的中心，格中是该卷在本书封面上的公式。

<table>
  <tr>
    <td width="33%" valign="top" align="center">
      <a href="docs/contents/volume-i.md"><img src="assets/covers/volume-1.jpg" alt="卷 I 封面 — Problem and Foundations" width="200"></a><br>
      <b>I · Problem and Foundations</b><br>
      <sub>Part 0–II · 17 章 · 第 1–135 页</sub><br><br>
      <sub>以完整精度陈述猜想，剖析障碍的结构；由各组成部分构造 FAP 空间的范畴——凝聚与棱柱基底、算术分裂图、十二条公理 F1–F12、六函子运算、下降——以及可对偶性、核性、迹与正则化行列式的范畴机器。</sub><br><br>
      <a href="docs/contents/volume-i.md">目录</a> · <a href="https://github.com/AlienMuse/fractured-adelic-geometry/releases/download/v1.0.0/Fractured-Adelic-Geometry-v1.0.0-Complete.pdf">PDF</a>
    </td>
    <td width="33%" valign="top" align="center">
      <a href="docs/contents/volume-ii.md"><img src="assets/covers/volume-2.jpg" alt="卷 II 封面 — The Arithmetic Spectrum and the Rank-Two Barrier" width="200"></a><br>
      <b>II · The Arithmetic Spectrum and the Rank-Two Barrier</b><br>
      <sub>Part III–V · 19 章 · 第 136–279 页</sub><br><br>
      <sub>把理论用于一条曲线：算术谱 X<sub>E</sub>、作为流的不动点集的 Selmer 群、Arakelov 边界上的高度、每一个局部因子；Euler 系统的机制与秩二诊断；模性、Gross–Zagier 及其后续、Kudla 纲领、相对迹公式与 murmurations。</sub><br><br>
      <a href="docs/contents/volume-ii.md">目录</a> · <a href="https://github.com/AlienMuse/fractured-adelic-geometry/releases/download/v1.0.0/Fractured-Adelic-Geometry-v1.0.0-Complete.pdf">PDF</a>
    </td>
    <td width="33%" valign="top" align="center">
      <a href="docs/contents/volume-iii.md"><img src="assets/covers/volume-3.jpg" alt="卷 III 封面 — The Master Identity and the Engine" width="200"></a><br>
      <b>III · The Master Identity and the Engine</b><br>
      <sub>Part VI–VII · 11 章 · 第 280–366 页</sub><br><br>
      <sub>完整陈述 Conjecture A；下降到秩公式与首项系数公式；验证退化情形；全书的逻辑依赖图。随后是七层架构：带认证的算术内核，下降、Selmer、L 函数与 p-进引擎，发现层与证书格式。</sub><br><br>
      <a href="docs/contents/volume-iii.md">目录</a> · <a href="https://github.com/AlienMuse/fractured-adelic-geometry/releases/download/v1.0.0/Fractured-Adelic-Geometry-v1.0.0-Complete.pdf">PDF</a>
    </td>
  </tr>
  <tr>
    <td width="33%" valign="top" align="center">
      <a href="docs/contents/volume-iv.md"><img src="assets/covers/volume-4.jpg" alt="卷 IV 封面 — Formalisation and the Programme" width="200"></a><br>
      <b>IV · Formalisation and the Programme</b><br>
      <sub>Part VIII–IX · 9 章 · 第 367–442 页</sub><br><br>
      <sub>形式化库今天能表达和不能表达什么；自动形式化与证明搜索；多 Agent 架构；证明义务账本与信任模型。然后是剩下的部分：十四个障碍的图谱、分九个阶段的构造纲领、专门反对本书的一章，以及前景评估。</sub><br><br>
      <a href="docs/contents/volume-iv.md">目录</a> · <a href="https://github.com/AlienMuse/fractured-adelic-geometry/releases/download/v1.0.0/Fractured-Adelic-Geometry-v1.0.0-Complete.pdf">PDF</a>
    </td>
    <td width="33%" valign="top" align="center">
      <a href="docs/contents/apparatus.md"><img src="assets/covers/volume-5.jpg" alt="附录封面 — Appendices A–H" width="200"></a><br>
      <b>The Apparatus · 附录 A–H</b><br>
      <sub>8 个附录 · 参考文献 · 三个索引 · 第 443–525 页</sub><br><br>
      <sub>正文不宜中断去补充的内容：椭圆曲线、Galois 上同调与对偶、∞-范畴、凝聚与棱柱工具箱、证明义务账本、数值表和 Lean 4 源码；符号、人名与主题三个索引。</sub><br><br>
      <a href="docs/contents/apparatus.md">目录</a> · <a href="https://github.com/AlienMuse/fractured-adelic-geometry/releases/download/v1.0.0/Fractured-Adelic-Geometry-v1.0.0-Complete.pdf">PDF</a>
    </td>
    <td width="33%" valign="top" align="center">
      <a href="https://github.com/AlienMuse/fractured-adelic-geometry/releases/download/v1.0.0/Fractured-Adelic-Geometry-v1.0.0-Complete.pdf"><img src="assets/covers/complete.jpg" alt="合卷封面 — 环绕基本线的 D6 adelic 蜂巢" width="200"></a><br>
      <b>合卷</b><br>
      <sub>卷 I–IV · 附录 A–H · 571 页</sub><br><br>
      <sub>四卷与附录合为一册，环绕基本线 Δ(X<sub>E</sub>)：一个对象，两种描述。页码与参考文献连续编排，因为逻辑依赖跨越了卷的划分。</sub><br><br>
      <a href="https://github.com/AlienMuse/fractured-adelic-geometry/releases/download/v1.0.0/Fractured-Adelic-Geometry-v1.0.0-Complete.pdf">PDF</a> · <a href="docs/contents/apparatus.md">附录</a> · 80.7 MB
    </td>
  </tr>
</table>

## 主要结果

- **下降（第 38–39 章）。** 由 Master Identity 与公理 F1–F12 推出秩公式 ord<sub>s=1</sub> L(E, s) = rank E(ℚ) 和完整的
  首项系数公式——这是对条件命题的完整证明，每个假设都与定理一并写出。
- **阶等于重数。** 正则化行列式在一个特征值处的零点阶等于它的代数重数；秩成为一个指标。
- **退化情形（第 40 章）。** 在有限域上，十二条公理中有九条成为定理，形式化体系特化为 Tate 与 Milne 的定理；对 ℤ 上的
  𝔾<sub>m</sub>，它特化为显式公式与类数公式。
- **秩二诊断（第 27 章）。** 说明为什么现有的每一个证明都止步于解析秩一，并把原因刻画为外代数作用在导出形变环上的一个
  结构性陈述。
- **登记册与图谱（第 3、41、53 章）。** 十二个猜想 A–M，其中十一个评为最高两级难度，只有一个——Conjecture H——用现有
  技术可以处理；十四个障碍 I–XIV，其中五个包含已知的重大公开问题。
- **两项自认（第 53 章）。** Conjecture A 是 BSD 公式的转写；行列式形式体系预设了 Tate–Shafarevich 群的有限性，而不是
  推出它。

## 本书是什么，不是什么

**它是**一个附有完整代价的基础性提议：一个给出规格的框架、完整证明的条件定理、一套计算与形式化验证架构，以及精确到
可以被攻克、定价或推翻的障碍。每个实质性断言在提出之处都带有四种标签之一：**[KNOWN]** 文献中的定理，
**[CONDITIONAL]** 在所述假设下成立，**[NEW]** 本书提出并证明，**[OPEN]** 猜想或障碍，不声称有证明。

**它不是** Birch–Swinnerton-Dyer 猜想的证明。框架的核心对象只给出了规格，没有构造出来；公理仅有的模型是 ℤ 上的
𝔾<sub>m</sub> 和有限域上的曲线——恰好是答案事先已知的两种情形。Lean 源码陈述了理论，但没有编译过。

## 从哪里读起

四条路线出自 *Leitfaden*。

| 路线 | 章 |
|---|---|
| 基础路线 | 1–3、4–10、11–17、37、53–54 |
| 算术路线 | 1–3、18–23、24–30、38、41 |
| 解析路线 | 1–3、31–36、39–40 |
| 计算路线 | 1–3、42–47、48–52、55，以及 [`code/`](code/) 目录 |

持怀疑态度的审稿人应当先读 §41.9《What the book has actually proved》：这一节就是为这样的读者写的。

[预览版](https://github.com/AlienMuse/fractured-adelic-geometry/releases/download/v1.0.0/Fractured-Adelic-Geometry-v1.0.0-Preview.pdf)包含前置部分——Series Note、Abstract、Preface、
Statement of Epistemic Status、Leitfaden、符号、目录——以及 Part 0 全文。

## 下载

| 文件 | 页数 | 大小 |
|---|---:|---:|
| [**合卷**](https://github.com/AlienMuse/fractured-adelic-geometry/releases/download/v1.0.0/Fractured-Adelic-Geometry-v1.0.0-Complete.pdf)——卷 I–IV 与附录 | 571 | 80.7 MB |
| [预览版](https://github.com/AlienMuse/fractured-adelic-geometry/releases/download/v1.0.0/Fractured-Adelic-Geometry-v1.0.0-Preview.pdf)——前置部分与 Part 0 | 73 | 72.0 MB |
| [随书代码](https://github.com/AlienMuse/fractured-adelic-geometry/releases/download/v1.0.0/Fractured-Adelic-Geometry-v1.0.0-code.zip)——BSDKit、证书检查器、Lean 4 源码（未编译）；Apache-2.0 | — | 101.9 KB |

同样的文件（校验值相同）存档于 Zenodo：[doi:10.5281/zenodo.23585888](https://doi.org/10.5281/zenodo.23585888)。封面为 600 ppi 全出血，所有字体已
嵌入，PDF 已线性化以便快速打开。随书代码也放在 [`code/`](code/)，与压缩包逐字节一致。

## 引用

> Liu, V. (2026). *Fractured Adelic Geometry — A Foundational Framework for the Birch and Swinnerton-Dyer Conjecture*
> (Research Architecture Edition 1, version 1.0.0). Zenodo. https://doi.org/10.5281/zenodo.23585887

BibTeX 与 *Cite this repository* 按钮见[英文 README](README.md#citation) 与 [CITATION.cff](CITATION.cff)。概念 DOI
10.5281/zenodo.23585887 始终指向最新版本；引用本次的确切文件请用版本 DOI 10.5281/zenodo.23585888。

## 真实性

本次发布的每个文件都列在 `SHA256SUMS` 中，经 OpenPGP 签名，并有两重时间戳（RFC 3161 与比特币上的 OpenTimestamps）。
签名密钥与 Series 01、02、03 相同。

签名密钥指纹：`DA1A 1AEF D8B2 C17C FF3F 1D1B 3905 0F50 7A4F EC17`

本仓库的 GitHub Release 不可更改。从其他渠道获得、与 `SHA256SUMS` 不符的副本不是真本。三级校验方法见 [VERIFY.md](VERIFY.md)。

## 许可与 AI 使用

本书以 [CC BY-NC-ND 4.0](LICENSE) 许可发布：在署名、非商业、不改动的前提下可以分享。书中印出的代码清单与
[`code/`](code/) 中的随书代码另以 Apache License 2.0 提供。翻译及其他用途需书面许可。详见 [NOTICE.md](NOTICE.md) ·
名称使用：[TRADEMARKS.md](TRADEMARKS.md)。

**依欧盟指令 2019/790 第 4(3) 条保留文本与数据挖掘权利。** 未经书面许可，不得用本书训练或微调机器学习模型。读者个人
可以用 AI 工具阅读、检索、解释或翻译本书供自己学习。完整政策：[TDM-AND-AI-POLICY.md](TDM-AND-AI-POLICY.md)。
术语对照：[docs/terminology-zh.md](docs/terminology-zh.md)。

## 参与

一个不可能失败的框架什么也没有告诉读者，而本书写成的方式就是为了让失败容易被报告。最重要的三类贡献：

- **反驳**——一条曲线，在其上局部 Tamagawa 因子的棱柱公式与 Tate 算法不一致；一个退化情形，其中某条公理特化为错误
  陈述；或引擎与某个数值预测相矛盾（第 55 章）。
- **构造**——在十四个障碍中任何一个上取得进展，按第 54 章九个阶段的顺序。
- **复现**——独立运行 BSDKit 与附录 G 的数值表，或编译 Lean 源码。

请通过 [errata issue](https://github.com/AlienMuse/fractured-adelic-geometry/issues/new?template=errata.yml) 报告错误。被采纳的更正将在下一版中署名致谢（见
[ERRATA.md](ERRATA.md)）。

---

<p align="center"><sub>
  <a href="https://wisemotif.ai">WiseMotif Monograph of Mathematical Intelligence</a> · Series 04 · Mathematics and Artificial Intelligence<br>
  Series 01：<a href="https://github.com/AlienMuse/grothendieckian-machine"><i>GAI-MUA: The Grothendieckian Machine</i></a> ·
  Series 02：<a href="https://github.com/AlienMuse/topos-native-intelligence"><i>GM-Omega-Infinity: Topos-Native Intelligence</i></a> ·
  Series 03：<a href="https://github.com/AlienMuse/arithmetic-spectral-descent"><i>Arithmetic Spectral Descent</i></a><br>
  © 2026 Vincent Liu
</sub></p>
