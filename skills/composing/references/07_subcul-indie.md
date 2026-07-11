# 07 サブカル・インディー プレイブック — 質感の系譜と効かせ方 (hyperpop 含む)

ジャンルがインディー/オルタナ系 — 渋谷系・下北沢系・シューゲイザー/ドリームポップ・音響系・hyperpop — の曲で読む。ボカロ文化・ネット発シーンが主軸の曲は隣接系統の 05_vocaloid-net.md へ。

> - 例 (Style 記述・スケルトン・フレーズ) はすべてこの資料のための自作。実在曲の歌詞は引用していない
> - 実在アーティスト・作品への言及は §7「研究出典」のみ。本文は系統として抽象化してある
> - BPM・数値は目安。字数上限・タグ語彙・スライダーの実務値は suno-spec が正

## 1. シーンの前提

- 「サブカルっぽい」は単一ジャンルではなく**質感の系譜の束**。系譜をまたぐ共通項は 3 つ (Med):
  1. **コード** — ダイアトニックから半歩外す (テンション・借用・転調)
  2. **録音** — ハイファイを避ける。宅録感・テープ感、または過剰なリバーブ
  3. **声** — **上手すぎない・近すぎない** (囁き・等身大・脱力)
- 現在形はネット発オルタナ: 宅録 → SNS 集合で、アニソン・J-POP・渋谷系を等価に参照する雑食性が標準 (Med)
- 日本のオルタナがアルゴリズム経由で英語圏リスナーに発見される流れが継続 (Med)。`japanese shoegaze` のような英語圏タグがそのまま通じる
- hyperpop はこの文脈の最若層: クリップ・歪み・ビットクラッシュを「修正でなく美学」として使う、デジタル過剰の引き受け (High)。SoundCloud/TikTok/Discord 発で、日本勢は歌モノに寄る (Med)

## 2. サウンド署名の早見表 — 系譜別

| 系譜 | BPM 目安 | 何がそう聴こえさせるか | Style 記述子の例 |
|---|---|---|---|
| 渋谷系 | ミッド (目安) | 60s ソフトロック参照のオーケストラル・ポップ。dim/aug/分数コードと頻繁な転調が「おしゃれで不思議」の正体。ブラス・ストリングス・オルガン・ボッサギター (Med) | `shibuya-kei, 60s soft rock influence, jazzy tension chords, bossa nova guitar, strings and horns, sweet airy female vocals, stylish, retro-futuristic` |
| 下北沢系 | ミッド (目安) | 等身大の歌詞 + 装飾の少ないバンドサウンド + ざらついた録音。日本語フォークロック直系の系譜 (Med) | `japanese indie rock, jangly guitars, raw home-recording texture, understated male vocals, nostalgic, mid-tempo` |
| シューゲイザー/ドリームポップ | スロー〜ミッド | **「歪み」と「残響」が 2 大要素** (High)。轟音の壁 + ミニマルなリフ反復 + 甘いメロディ + 埋もれる声。J-POP 由来のメロを轟音に沈める国内型が現代主流 | `japanese shoegaze, dream pop, wall of distorted guitars, heavy reverb, hazy whispery vocals buried in the mix, slow tempo, melancholic and dreamy` |
| 音響系/ダブ系 | スロー (目安) | 空間処理が主役。レゲエ/ダブ基調の浮遊するミックス (Med) | `dub-influenced japanese alternative, spacious floating mix, deep dub bass, sparse guitar, ambient textures, hazy late-night mood` |
| hyperpop | 150+ (Med) | 派手なシンセ・過剰コンプと歪み・金属的パーカッション・ピッチシフト声・短い曲尺。光沢のあるシンセコード (bubblegum bass 系譜) が記号 (High) | `hyperpop, glitchy, pitched-up autotuned vocals, distorted 808s, metallic synths, bitcrushed textures, chaotic maximalist energy, 160 bpm feel` |

- glitchcore 派生 (hyperpop の高速側): 高速チョップボーカル・高ピッチ声・鋭い 808 (High)。`glitchcore, chopped vocals` を hyperpop 記述子に重ねる
- 系譜は混ぜてよいが骨格は 1 つ: 「渋谷系 × シューゲイザー」のような掛け合わせは、どちらの署名を骨格にするかを先に決める (Style の組み立ては 02_style-assembly.md)

## 3. 構成慣習 — 標準の器との差分

標準の Verse–Chorus 型 (songwriting の 01_song-structure が正) からの逸脱そのものがジャンルの顔になる。系譜別の差分:

- **シューゲイザー**: サビの「開き」を音量ではなく**音の厚み** (ギターのレイヤー数) で作る。轟音の間奏がサビと等価の聴かせ場になり、Bridge は省略しがち
- **渋谷系**: 転調が展開の主装置。`[Key Change]` を B メロやラスサビ前に置き、「おしゃれな違和感」を構成で保つ
- **音響系**: セクション概念が薄い。`[Instrumental Break]` を長く取り、歌が空間に「浮かぶ」配置にする。Verse–Chorus に無理に畳まない
- **hyperpop**: 短尺 (1:30〜2:30 目安)・イントロほぼゼロ・Bridge 削除。サビはドロップ的に扱う (`[Drop]` 併用可)。歌詞量を絞ることで尺を短く誘導する

標準スケルトン (シューゲイザー例):

```text
[Intro: clean guitar arpeggio, distant and hazy]

[Verse 1]
(4〜6 行)

[Chorus: wall of sound, layered distorted guitars]
(4 行)

[Verse 2]
(4〜6 行)

[Chorus]
(1 回目と同一歌詞)

[Instrumental Break: guitar feedback, massive reverb]

[Chorus: maximum layers, vocals buried]

[Outro: feedback slowly dissolving]

[Fade Out]
```

hyperpop はこの逆で「詰めて短く」: `[Intro]` を外し、`[Verse]` → `[Chorus]` → `[Verse]` → `[Chorus]` → `[Outro]` の 5 区画に絞ると尺が寄る (目安)。

## 4. ボーカル演出 — 「上手すぎない・近すぎない」の質感論

声を楽器の一枚として扱い、**ミックス上の距離感**で系譜を分ける。「歌唱力の高さ」を演出から意図的に外すのがこのライブラリで本書だけの流儀:

| 系譜 | 声の距離と質感 | 記述子の例 |
|---|---|---|
| 渋谷系 | 前にいるが軽い。甘く風通しよく | `sweet airy vocals, light, effortless` |
| 下北沢系 | 近くて生。話すように | `understated vocals, unpolished, conversational` |
| シューゲイザー | 遠くて埋もれる。楽器と等価 | `hazy whispery vocals buried in the mix` |
| 音響系 | 浮遊。輪郭を残さない | `floating distant vocals, blurred` |
| hyperpop | 加工で人工化。声をシンセの一部に | `pitched-up autotuned vocals, formant-shifted, stacked` |

- `soaring` `powerful` 系の記述子は原則使わない (ジャンルの声の文法に反する)。上手く歌われてしまう事故の対処は §5
- hyperpop の声設計 (High): ピッチ上げ + フォルマントシフト + ハモ重ねの三点で「声のシンセ化」。`[Ad-lib]` や短い行の高速反復 (チョップ風) も相性がよい

## 5. Suno 写像の組み立て例

Style 完成例 (自作):

1. 渋谷系: `shibuya-kei, 60s soft rock influence, jazzy tension chords, bossa nova guitar, strings and horns, organ, sweet airy female vocals, stylish and playful, retro-futuristic pop`
2. シューゲイザー: `japanese shoegaze, dream pop, wall of distorted guitars, heavy reverb, hazy whispery female vocals buried in the mix, slow tempo, melancholic and dreamy`
3. hyperpop: `hyperpop, glitchy maximalist pop, pitched-up autotuned vocals, distorted 808s, metallic percussion, bitcrushed synth textures, chaotic euphoric energy, short and explosive, 160 bpm feel`

Exclude 定番 (系譜別。運用は suno-spec §3):

- シューゲイザー/音響系: `polished pop, edm, auto-tune` — 清潔な現代ポップ化を防ぐ
- 渋谷系: `heavy metal, distorted guitars, trap` — 轟音・現代ビートへの漂流を防ぐ
- hyperpop: `acoustic, ballad, smooth jazz` — 有機的な方向への漂流を防ぐ

よくある事故と対処:

| 症状 | 対処 |
|---|---|
| シューゲイザーで声がクリアに前へ出る | Style の `buried in the mix, hazy` を強調し、Exclude に `clear vocals`。それでも出るなら `[Chorus: vocals buried under guitars]` とセクション側でも押す |
| 渋谷系がただのレトロ歌謡になる | `stylish, retro-futuristic` で「更新された過去」側に引き戻す。ボッサギターと管弦を明示する |
| hyperpop が普通のエレクトロポップに丸まる | `glitchy, bitcrushed, chaotic` を削らない。Weirdness を上げる (数値運用は suno-spec §3) |
| 轟音で全体が濁る | 歪み系記述子を 2 語までに絞り、`minimal repetitive riff` でリフの単純さを明示する (壁は「単純な音の厚積み」で作る) |
| 声が上手すぎる | §4 の距離感記述子に差し替え、Exclude に `powerful vocals` |

## 6. ことば側への申し送り

- 渋谷系: 意味の重さより**音の軽やかさと洒脱**。カタカナ語・外来語の艶が武器になる。深刻な主題も軽く言う
- 下北沢系: 等身大・半径 5 メートル・話し言葉。修辞で飾った瞬間に嘘になる
- シューゲイザー: **声が埋もれる前提で書く** — 文で聴かせず単語の粒で聴かせる。母音の開いた短い語を反復し、聞き取れなくても成立する歌詞にする
- hyperpop: 感情の振幅 (自己否定と多幸感の往復) を短いフレーズの連呼で出す。ネット語彙・口語も可。1 行を短く
- 共通: 「上手い歌詞」より「その人しか書かない歌詞」。整いすぎたらこのジャンルでは負け

## 7. 研究出典

技法は 2026-07-11 取得の下記調査に基づく。実在アーティスト・作品への言及はこの欄のみ。歌詞原文は引用していない。確度: High = 複数ソース一致 / Med = 単一ソースまたはコミュニティ知。

- 渋谷系の様式と和声感: https://ja.wikipedia.org/wiki/渋谷系 / https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q12258054762 — Med
- シューゲイザーの 2 大要素 (歪み・残響) と国内型の分析: https://ja.wikipedia.org/wiki/シューゲイザー / https://www.umbrella-company.jp / https://www.neowing.co.jp/feature/1901shoegaze — High/Med
- 下北沢系・日本インディーの系譜: https://note.com/harusame33 / https://a-girafe.com — Med
- 音響系/ダブ系 (フィッシュマンズを代表例として): https://ja.wikipedia.org/wiki/フィッシュマンズ — Med
- hyperpop の定義と美学 (過剰の引き受け・bubblegum bass 系譜): https://en.wikipedia.org/wiki/Hyperpop / https://blog.native-instruments.com / https://emastered.com — High
- 日本の hyperpop シーン: https://turntokyo.com / https://utaten.com / https://note.com/nodobotokesoft — Med
