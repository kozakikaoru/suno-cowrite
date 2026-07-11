# 08 アニソン・アイドル プレイブック — 「場」から逆算する機能設計

ジャンルがアニソン的文脈 (キャラソン・タイアップ・OP/ED・TV サイズ) またはアイドル曲 (グループ・コール&レスポンス・かわいい系) の曲で読む。合本なのは、どちらも**曲が置かれる「場」(映像の尺 / ライブの客席) から逆算する機能設計**だから。ダンスブレイクやキリングパートが主導する K-POP 的グループ曲は 04_kpop.md へ、高速・情報量過多のネット発文脈は 05_vocaloid-net.md へ。

> - 例 (Style 記述・スケルトン・フレーズ) はすべてこの資料のための自作。実在曲の歌詞は引用していない
> - 実在アーティスト・作品・番組への言及は §7「研究出典」のみ。本文は系統として抽象化してある
> - BPM・数値は目安。字数上限・タグ語彙・スライダーの実務値は suno-spec が正

## 1. シーンの前提

- アニソンは単一ジャンルではなく「作品の世界観を背負う機能」。ロックでも管弦でも電子でも器になるが、**TV サイズ 89 秒 (放送枠由来の定数) が OP の設計思想を規定**する: 89 秒で世界観提示 → 高揚 → サビ完結 (High)
- フル尺は 89 秒の拡張として作る。「前半 1 コーラスだけ切り出しても成立するか」が設計の検算になる (Med-High)
- 転調・劇的展開が様式として期待される、ポップスでは珍しい領域 (Med)。恥ずかしがらずにドラマを盛る
- キャラソンはアニソン文脈の派生で、歌い手は「キャラクター」。本プラグインでは **character.md の人物設定が仕様書** — 声質・性格・世界観を Style のボーカル記述とムードに写す
- アイドル曲の機能要件は「ライブで場が上がる」: アップテンポ + キャッチー + ダンス映え (Med-High)。**コール&レスポンス設計** = 合いの手が入る空白をアレンジ側に用意するのが、このジャンル固有の作法 (Med-High)
- 現在の主流は「かわいい」を宣言するタイトル + 連呼フック + 振り付けの kawaii 系。ワンフレーズ切り抜き型の男性アイドル曲も同構造 (High)。切り抜き・バイラル特化の設計は 03_tiktok-shortform.md が副読候補
- 両者の共通哲学: **王道進行・様式美を忠実になぞることが快感の源泉** (Med-High)。逸脱を顔にする 07 系と正反対の文法で、「ベタ」は褒め言葉

## 2. サウンド署名の早見表

| サブスタイル | BPM 目安 | 何がそう聴こえさせるか | Style 記述子の例 |
|---|---|---|---|
| アニメ OP ロック (疾走系) | 150〜180 (疾走の定番 160 前後) (Med-High) | 刻むギター + オーケストラヒット + 張りのある高音 + 劇的転調 | `anime opening theme, j-rock, 160 bpm feel, driving guitar riff, orchestral hits, soaring female vocals, dramatic key change, epic and hopeful` |
| アニメ ED バラード系 | 70〜90 (Med-High) | 余韻で世界観を閉じる。ピアノ/ストリングス主体、声は近く | `anime ending theme, emotional ballad, warm piano and strings, intimate female vocals, gentle afterglow, wistful` |
| キャラソン | キャラ次第 | 曲調より「声の性格」が署名。character.md の性格をボーカル演技に写す (Med) | `bright bouncy j-pop, cheerful cute female vocals, playful delivery, colorful synths, upbeat and lovable` |
| 王道アイドル (kawaii 系) | 120〜135 (128 が目安) (Med) | きらきらシンセ + ユニゾン + 連呼フック + 合いの手の隙間 | `j-pop idol group, super kawaii, bright and bubbly, 128 bpm feel, catchy repetitive hook, unison group vocals, sparkling synths, lovable energy` |
| クール系アイドル (ダンス) | 120〜140 (目安) | エッジの立ったビート + キメ + ワンフレーズフック (Med) | `j-pop idol dance track, sharp punchy beat, sleek synth riff, confident unison group vocals, one-phrase hook, stylish and cool` |

- アニソンの声の既定値は「クリアで張りのある高音、サビでロングトーン」(Med)。07 系の「上手すぎない」とは逆に、**上手さを堂々と出す**
- アイドルのボーカル加工は薄めの「生っぽいかわいさ」が通説 (Low、推定) — 迷ったら加工系の語を足さない
- BPM 数値は単独で書かず `bpm feel` 表記 + エネルギー語で (表記の正は suno-spec §5)

## 3. 構成慣習 — 標準の器との差分

標準の Verse–Chorus 型 (songwriting の 01_song-structure が正) からの差分:

**アニソン OP 型 — 89 秒の設計 4 点**

1. **イントロは 4〜8 小節でシグネチャー音を提示し、エネルギーはサビより必ず低く** (High)。冒頭全開はサビの天井を消す最悪手
2. **エネルギーカーブは右肩上がりの一方向** (Med-High) — 音数・音域・ダイナミクス・コード感の「密度の総合量」を 89 秒枠で単調増加させる。谷を掘る暇はない (密度設計の一般則は 01_arrangement-craft.md。本型ではそれを単調増加に制約する)
3. **サビ 1 本目を早く完結させる** — Suno は秒数を直接指定できないため、「イントロ短め + A/B を刻んでサビへ急ぐ」構成指示で 89 秒感覚を近似する (Med)
4. **転調はストーリーの装置** (Med) — 「場面が変わった」を和声で言う。`[Key Change]` はラスサビ前が定石で、疾走系は B メロ→サビ境界に置くのも様式内

**アイドル型 — 様式美 3 点**

1. **1・2 コーラスは同型を守る** (Med-High)。展開の意外性より「みんなで踊れる・歌える」予測可能性が価値
2. **3 コーラス目は落ちサビ → 転調ラスサビ** (Med-High)。`[Bridge: stripped down]` → `[Key Change]` → 全開サビが定番の写像
3. **合いの手の空白を先に設計する** (Med-High) — フック行の直後 1〜2 拍とサビ前のキメに「客席が入る隙間」を空ける。詰めすぎたアレンジはライブ機能を殺す

標準スケルトン (アイドル型。迷ったらこれ):

```text
[Intro: sparkling synths, energetic kickoff]

[Verse 1]
(4〜6 行。ユニゾンとソロを交互に)

[Pre-Chorus: building, handclaps and chant]
(2〜4 行。掛け声で助走)

[Chorus: unison group vocals, catchy hook]
(4 行。タイトル連呼。行間に合いの手の隙間)

[Verse 2]
(1 番と同型)

[Pre-Chorus]

[Chorus]
(1 回目と同一歌詞)

[Bridge: stripped down, tender solo vocals]
(2〜4 行。落ちサビ)

[Key Change]

[Chorus: full energy, layered vocals, ad-libs]
(転調ラスサビ。曲中最大密度)

[Outro: chant and handclaps]

[End]
```

アニソン OP 型は前半を「89 秒 1 本勝負」に圧縮する: `[Intro]` 短め → `[Verse]` → `[Pre-Chorus: rising intensity]` → `[Chorus: full band, soaring vocals]` の 4 区画を先に完成させ、2 コーラス目・間奏・ラスサビは拡張として後から足す。

## 4. ボーカル演出

- アニソン: `soaring vocals` `powerful high notes` 系を臆さず使う。感情はまっすぐ張る — 屈折・脱力は 07 系の文法で、ここでは事故になる
- キャラソン: character.md の性格語彙を演技記述子へ翻訳する — 元気 → `cheerful, energetic delivery` / クール → `composed, cool delivery` / おっとり → `soft, airy, gentle delivery`。声の同一性を Persona で固定する運用は 02_style-assembly.md に従う
- アイドル: **ユニゾンが主役、ソロは差し色** (Med)。Style のボーカル枠は `unison group vocals` を筆頭に置き、パート割りの質感は `[Duet]` `[Backing Vocals]` で足す。全編ソロにするとアイドル感が消える
- 合いの手・掛け声は `[Backing Vocals]` `[Ad-lib]` で背景側に置く (タグ語彙は suno-spec §4)。括弧書き行がリフレイン/レスポンス側として歌われやすい挙動 (suno-spec §4) を合いの手に転用できるが、読み上げ事故もあるため使ったら判断メモに書く
- ラップパートを混ぜるアイドル曲の作法は songwriting/references/10_hiphop-genre-ja.md §6 (アイドルラップ) が正 — 本書では扱わない

## 5. Suno 写像の組み立て例

Style 完成例 (自作):

1. アニメ OP ロック: `anime opening theme, j-rock, 160 bpm feel, driving guitar riff, orchestral hits, soaring female vocals, dramatic key change, high-energy build, epic and hopeful`
2. kawaii 系アイドル: `j-pop idol group, super kawaii, bright and bubbly, 128 bpm feel, catchy repetitive hook, unison group vocals, call-and-response chants, sparkling synths, key change finale, lovable energy`
3. キャラソン (元気で天然な妹分キャラの例): `bright bouncy j-pop, upbeat, cheerful cute female vocals, playful delivery, colorful sparkling synths, clean pop production, sunny and lovable`

Exclude 定番 (運用は suno-spec §3):

- アニソン OP: `lo-fi, chill, downtempo` — 疾走の腰を折る質感を防ぐ
- kawaii 系アイドル: `dark, aggressive, heavy metal` — ムード反転防止
- ED バラード系: `edm, heavy drums` — 余韻を守る

よくある事故と対処:

| 症状 | 対処 |
|---|---|
| 冒頭からサビ級の音圧で始まる | `[Intro: restrained, building]` で局所的に抑える。Style の `high-energy` 系が全域を支配しているときの定石 |
| 前半で盛り上がりきらない (89 秒感覚が出ない) | `[Pre-Chorus: rising intensity]` を明示し、サビに `full band, soaring` 系を足す。§3 の右肩カーブをタグで段階化する |
| 転調が起きない | `[Key Change]` をラスサビ直前の単独行に置き、Style 側にも `dramatic key change` を書いて二重に誘導する (Med) |
| ユニゾンがソロに化ける | ボーカル枠の筆頭を `unison group vocals` にし、`[Chorus: unison group vocals]` とセクション側からも押す |
| 合いの手が主旋律を上書きする | 合いの手行を減らして `[Backing Vocals]` を明示する。直らなければ合いの手は消し、アレンジの隙間 (拍の空白) だけ残す |
| アイドル曲が K-POP 化する (グロッシーで強い) | `glossy` `edm trap` 系の語を外して `bright and bubbly, lovable` へ寄せる。密度の作法ごと寄せたいなら本書ではなく 04_kpop.md で組み直す |

## 6. ことば側への申し送り

- アニソン: **世界観の核になる語をサビ 1 本目までに出し切る**。89 秒で「この作品の歌」と分からせる — タイトル・キーワードはサビ頭が定位置
- アニソンの A/B メロは「情景 → 決意」のような**一方向の感情設計**が構成と噛み合う。谷 (諦め・停滞) を作る歌詞は OP 型に不向きで、入れるならフル尺の 2 コーラス目以降へ
- キャラソン: character.md の一人称・口癖・語尾をフックに埋め込む。**キャラが言わない語彙を 1 語でも使うと世界観が破れる** — 語彙の照合を推敲の第一項目にする
- アイドル: **フックは宣言型 + 連呼**。「かわいい」「好き」を言い切る短文を、タイトルの音列ごと反復する
- 合いの手は歌詞側の設計物 — フック行の後ろに 2〜4 音の短い掛け声を置く。本文行と混ざらない配置は composer と併せて決める
- ユニゾン前提の行はモーラを揃えて割りやすくする。ソロの差し色行にだけ字余りの感情を許す
- フック末尾は母音の開いた音 (a/o 段) が声を張りやすい。作詞の一般則は songwriting 側が正

## 7. 研究出典

技法は 2026-07-11 取得の下記調査に基づく。実在アーティスト・作品への言及はこの欄のみ (本書は個別名を参照していない)。歌詞原文は引用していない。確度: High = 複数ソース一致 / Med = 単一ソースまたはコミュニティ知 / Low = 推定。

- アニメ OP の 89 秒設計思想とエネルギーカーブ: https://note.com/aug_is_the_tonic / https://core-ms.net — Med-High
- アニソンの BPM 帯・コード進行・多転調の様式: https://core-ms.net / https://wellen.jp / https://khufrudamonotes.com — Med
- アイドル曲の構成様式 (王道進行・落ちサビ転調)・コール&レスポンス: https://i-me.media / https://coconala.com/magazine/4673 — Med-High
- kawaii 系・連呼フック・日本のバイラル文脈: https://kkbox.com / https://ragnet.co.jp / https://studio15.co.jp — Med〜High
- Suno のメタタグ・Style 実務: https://blakecrosley.com/guides/suno / https://sunoaiwiki.com — High (コミュニティ検証)
