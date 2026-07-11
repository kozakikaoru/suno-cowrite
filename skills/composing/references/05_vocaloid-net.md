# 05 ボカロ・ネット発 プレイブック — 高速高密度の文法を人間の声へ

ジャンルがボカロ系・ネット発シーンの曲で読む (Suno の人間声で「ボカロっぽさ」を出す手順まで含む)。hyperpop などネット発の隣接系統は 07_subcul-indie.md へ。ニコラップ (動画サイト発の HIPHOP 文化) は songwriting/references/10_hiphop-genre-ja.md §7 が正。

> - 例 (Style 記述・スケルトン・フレーズ) はすべてこの資料のための自作。実在曲の歌詞は引用していない
> - 実在アーティスト・作品への言及は §7「研究出典」のみ。本文は系統として抽象化してある
> - BPM・数値は目安。字数上限・タグ語彙・スライダーの実務値は suno-spec が正

## 1. シーンの前提

- 出自は歌声合成ソフト + 動画サイトの投稿文化。合成音声には息継ぎ・音域・滑舌の人間的制約がなく、**その「制約のなさ」がそのまま様式になった** — 高速・高密度・広音域 (Med-High)
- 計量研究でも確認されている (High): 人気ボカロ曲は「発声時間が短く、テンポが速く、早口」
- 3 系統とその混血 (Med-High): ①高速・情報量過多系 (BPM 170〜185 が標準帯) / ②ロック系 (16 分早口をバンドサウンドで) / ③エレクトロ/ポップ系。近年は 3 系統の混血が標準形
- **ボカロ文法は現代 J-POP の基礎教養になった** (High): ボカロ出身の作家がメジャーへ持ち込んだ質感 — 高密度な言葉数・跳躍の多いメロディ・物語主導のコンセプト・DTM で完結する緻密なアレンジ — が、現代 J-POP のヒット文法そのものになった。ボカロ系と明示されない曲でも、現代的な J-POP を組むときの参照点として本書は機能する
- 物語主導: 曲を世界観・キャラクター・連作の器として設計する文化。character.md / world.md を持つ本プラグインの前提と相性が良い

## 2. サウンド署名の早見表

| 系統 | BPM 目安 | 質感 | Style 記述子の例 |
|---|---|---|---|
| 高速・情報量過多系 | 170〜185 (極端例 240) | 16 分早口 + ピアノ連打 + シンセリード。隙間を埋め尽くす音数 | `high-speed j-pop, rapid-fire vocals, frantic piano riffs, bright synth lead, dry upfront vocals, hyperactive` |
| ロック系 | 155〜165 目安 | バンドサウンドで 16 分早口。非ダイアトニックな音階選択の毒気 | `japanese rock, fast articulate vocals, aggressive guitar riffs, relentless drums, dark tension, dry vocals` |
| エレクトロ/ポップ系 | 128〜150 目安 | クォンタイズ感の強いシンセとタイトな打ち込み | `japanese electropop, tight synth arpeggios, punchy programmed beat, deadpan female vocals, bittersweet, danceable` |

ミックスの署名 (Med) — 「ボカロっぽさ」は音色より処理に宿る:

- ボーカルに 1〜3kHz を譲る / キック 60〜80Hz / **リバーブは薄くドライ** (最重要成分) / シンセはアタック重視 / ハイハットは 16 分
- Style 写像: `dry upfront vocals, minimal reverb, bright mix, tight percussive synths`

## 3. 構成慣習 — 標準の器との差分

器は標準の Verse–Chorus 型 (songwriting の 01_song-structure が正) に近いが、和声と密度の運用に署名がある:

1. **借用和音、特に ♭VII で疾走感を注入する** (Med-High)。Suno はコード進行の直接指定が不安定なので、`driving, propulsive` 系のムード語 + ロック/エレクトロ記述子で近似する (組み立ての一般則は 02_style-assembly.md)
2. **サビ手前の半音上転調が頻出** (Med-High): ラスサビ限定ではなく、曲中のサビ前でも使う。`[Key Change]` をサビ直前に置いて近似する (最も安定して効く置き所はラスサビ前)
3. **間奏が聴かせ場**: ピアノ連打・高速シンセリフの器楽区間がサビと等価の見せ場になる。`[Instrumental Break]` や `[Piano Solo]` で確保する
4. **密度差で展開を作る**: 静のセクションを長く取るより、詰め (16 分) ⇔ 開き (8 分) の切り替えで景色を変える。全編 16 分は逆にのっぺりする (目安)

標準スケルトン (迷ったらこれ):

```text
[Intro: frantic piano riff, fast synth arpeggio]

[Verse 1]
(4〜8 行。密度高め)

[Pre-Chorus]
(2〜4 行。さらに詰める)

[Chorus]
(4 行。音域の頂点、開母音)

[Verse 2]
(4〜8 行)

[Pre-Chorus]

[Chorus]

[Instrumental Break: rapid piano and synth lead]

[Bridge: sudden quiet, sparse]
(2〜4 行。唯一の減速点)

[Key Change]

[Chorus: highest intensity, soaring melody]

[Outro: abrupt cut or short piano tag]
[End]
```

- タグは suno-spec §4 の語彙だけ使う。尺は短めが文化 (3 分前後目安)。長い後奏を置かず、切り落とすように終わる曲が多い

## 4. ボーカル演出 — 合成音声の癖を人間の声に写す

ボカロ的メロディの 3 要素 (High) と声の処理 (Med):

- **広音域**: 女声想定で C4〜G5 を常用し、サビで A5/B5 に触れる。`wide vocal range`
- **跳躍**: 長 9 度級の跳躍を平気で入れる。滑らかにつながず、跳ぶこと自体を聴かせる。`wide melodic leaps`
- **16 分詰め込み早口**: `rapid-fire vocals`。ただし実際に速く歌わせる主因は歌詞側の行密度 (§6)
- **声はドライで前に張り付く**: `dry upfront vocals, minimal reverb`。情感過多のビブラートやメリスマはジャンルの声ではない
- **棒読み感の人間的近似**: `deadpan, precise, articulate vocals`。感情を抑えた精密発声が「あの感じ」に最も近い

**人間ボーカルでボカロっぽさを出す 5 手順** (構成 Med。迷ったら上から順に):

1. BPM 170 前後 + 16 分早口で外形を作る (テンポと密度が第一署名)
2. 広い音域と急跳躍をメロディ要件として Style に書く (`wide melodic leaps, wide vocal range`)
3. `dry vocals, minimal reverb, bright mix` で処理の署名を再現する
4. ピアノ連打・高速シンセリフを楽器指定で立てる (`frantic piano riffs, fast synth lead`)
5. `deadpan, precise, articulate vocals` で「歌いすぎない」声にする

## 5. Suno 写像の組み立て例

Style 完成例 (自作):

1. 高速・情報量過多系: `high-speed j-pop, vocaloid-style, 175 bpm feel, rapid-fire 16th-note vocals, frantic piano riffs, bright synth lead, driving rock drums, dry upfront vocals, wide melodic leaps, hyperactive and melancholic`
2. ロック系: `japanese rock, vocaloid-influenced, 160 bpm feel, fast articulate female vocals, aggressive guitar riffs, relentless drums, dry vocals, wide vocal range, dark playful tension`
3. エレクトロ/ポップ系: `japanese electropop, 140 bpm feel, tight synth arpeggios, punchy programmed beat, deadpan precise female vocals, minimal reverb, bittersweet and danceable`

Exclude 定番: `power ballad, gospel choir, heavy reverb, soulful vocal runs` — ウェットで情感過多な歌唱への漂流を防ぐ (運用は suno-spec §3)。

よくある事故と対処:

| 症状 | 対処 |
|---|---|
| 早口にならない | Style だけでは決まらない。歌詞の行あたり文字密度を上げる (§6)。`rapid-fire 16th-note vocals` + BPM 明示を併用 |
| 情感たっぷりに歌われて「らしさ」が消える | `deadpan, precise` を足し、Exclude に `soulful vocal runs` (§4 手順 5) |
| 声が奥に沈む・残響で滲む | `dry upfront vocals, minimal reverb` を明示し、Exclude に `heavy reverb` |
| テンポが遅く生成される | BPM を数値で書き、`driving, relentless` を重ねる。`[Intro: fast tempo]` とタグ側でも押す |
| メロが跳ばずのっぺりする | `wide melodic leaps, wide vocal range` を明示し、サビに `[Chorus: soaring high melody]` |
| ピアノ連打が出ない | 楽器記述をジャンル直後に前置し、`[Instrumental Break: rapid piano]` で器楽区間を確保する |

## 6. ことば側への申し送り

- **言葉数を削らない**: 高密度が様式。1 行のモーラ数を通常の歌モノより多めに積む — 早口は Style 記述子ではなく行密度から誘導される
- 早口区間とサビで語の文法を分ける: 早口区間 = 子音の立つ語・破裂音・畳みかける列挙 / サビ = 開母音でロングトーンと跳躍に耐える語
- **物語主導で書く**: 世界観・キャラクターの一人称。心情の説明より、情景と出来事の速射で感情を運ぶ
- 聞き取れない前提の保険を掛ける: キーフレーズは反復で回収する。1 回しか言わない重要語を早口区間に置かない
- 造語・言葉遊び・体言止めの連打はシーン語彙として許容度が高い。むしろ個性になる
- サビ頭の 1 語は母音の開いた強い語にする (跳躍の頂点に乗る)

## 7. 研究出典

技法は 2026-07-11 取得の下記調査に基づく。実在アーティスト・作品への言及はこの欄のみ。歌詞原文は引用していない。確度: High = 学術・複数ソース一致 / Med = 単一ソースまたはコミュニティ知。

- ボカロ調の作り方 (テンポ・音域・跳躍・ミックス署名): https://core-ms.net — Med
- 人気ボカロ曲の計量分析 (発声時間・テンポ・早口): https://ipsj.ixsq.nii.ac.jp (item_id=112346) — High (学術)
- ボカロ (音楽ジャンル) の系譜と 3 系統: https://ja.wikipedia.org/wiki/ボカロ_(音楽ジャンル) — Med
- 制作視点のボカロ曲分析 (和声・転調・構成): https://ragnet.co.jp / https://note.com/soundwitches — Med
- ボカロ出身作家と J-POP 本流の合流: https://www.billboard-japan.com (special 3483) — High
- シーン解説 (教育機関): https://www.tsm-koutoukatei.jp — Med
