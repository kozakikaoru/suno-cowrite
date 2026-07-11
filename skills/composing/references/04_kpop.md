# 04 K-POP プレイブック — キリングパートから逆算する

ジャンルが K-POP 系の曲で読む。composer 向けだが dual-audience: **lyricist はこの資料を渡されたら §6「ことば側への申し送り」を必読** (余力があれば §3 も)。

> - 例 (Style 記述・スケルトン・フレーズ) はすべてこの資料のための自作。実在曲の歌詞は引用していない
> - 実在アーティスト・作品への言及は §7「研究出典」のみ。本文は系統として抽象化してある
> - BPM・数値は目安。字数上限・タグ語彙・スライダーの実務値は suno-spec が正

## 1. シーンの前提

- **制作体制が曲の形を規定している** (High): ソングキャンプ文化 — プロデューサー 1 + トップライナー 2〜3 人を、A&R がハイパースペシフィックなブリーフでマッチングする。プロデューサーは 8/16 小節の **song starter** (ビートとコードの種) を持ち込み、トップラインは**グルーヴ・ファースト**で乗せる
- 帰結: **「セクションごとに独立に強いパーツを作って縫合する」構造** (High)。1 曲に 3〜4 ジャンルを縫い込む曲中ジャンルスイッチが平常運転で、セクションの継ぎ目が「驚き」の演出装置になる
- パフォーマンス前提 (High): 曲はステージ・振付とワンセット。**キリングパート** = 曲中で最も記憶される 4〜8 拍、という概念がシーンの共通語。ポイント振付 + フックの頂点 + レイヤー最大化をこの 1 点に同時に当てる
- サウンドの基調: 明るくラウドで glossy (光沢仕上げ)。洗練されたシンセリフ + EDM 系ベース + 808。中心帯は 120〜140 BPM (High)。メジャー ⇔ マイナーのモーダルシフトが常套
- ソロアーティストの曲でも「セクション積層 + 見せ場からの逆算」は設計術としてそのまま流用できる

## 2. サウンド署名の早見表

| サブスタイル | BPM 目安 | 質感 | Style 記述子の例 |
|---|---|---|---|
| ガールクラッシュ系 | 130〜140 | アグレッシブな EDM/トラップ、太いドロップ、強気の態度 | `K-pop girl group, aggressive edm trap beat, sassy vocals, powerful chant chorus, heavy bass drop, confident attitude, glossy production` |
| 爽やかポップ系 | 115〜125 | 明るいシンセポップ + ファンキーなギターカッティング、清涼感 | `K-pop boy group, bright synth pop, funky guitar riff, youthful vocals, layered harmonies, refreshing energy` |
| 実験系/パフォーマンス特化 | 135〜145 | インダストリアル・ダブステップ・急転換。ダークで複雑 | `experimental K-pop, industrial sounds, dubstep breakdown, aggressive rap-singing, complex structure, dark energy` |

- 有効語彙 (コミュニティ検証 High): `glossy production / maximalist / layered harmonies / mixed group vocals / gang vocals / high note belt / rap-singing / clear enunciation`
- どのサブスタイルでも仕上げは glossy。lo-fi 系の質感とは原則相容れない (混ぜるなら意図を判断メモに残す)

## 3. 構成慣習 — 標準の器との差分

標準の Verse–Chorus 型 (songwriting の 01_song-structure が正) からの差分は 4 点 (High):

1. **Pre-Chorus がビルド専用の独立セクションとして必須級**。`[Pre-Chorus]` で明示し、Verse と地続きにしない
2. **サビは「アンセミック」か「アンチドロップ」の二択で設計する** (下の技法カード)
3. **Post-Chorus / Dance Break がバイラル発生点**。歌の後に「踊るための器楽区間」を置く
4. **セクション数が多い**: Rap Verse、ストリップダウンした Bridge、終盤の転調 (またはテンポシフト) 付きラストサビまで積み上げる

技法カード:

- **アンチドロップ・コーラス**: (1) Pre-Chorus で最大までビルド → (2) サビ頭でドラムか上物を抜き、フックとベースだけ残す → (3) サビ 2 周目 (または 2 回目のサビ) でフル編成に戻す。「開く」代わりに「空ける」ことで頂点を作る
- **キリングパート設計 (最重要)**: 曲を頭から書かない。(1) 「全部盛り」の 4〜8 拍を 1 箇所決める → (2) 前後のセクションは助走と余韻として密度を下げる → (3) その 1 点へ向けて構成全体を逆算する

標準スケルトン (迷ったらこれ):

```text
[Intro: signature synth riff]

[Verse 1]
(4 行。ミニマル or ラップ寄り)

[Pre-Chorus: building energy]
(2〜4 行)

[Chorus: anthemic, layered vocals]
(4 行)

[Post-Chorus: chant hook]
(1〜2 行の連呼)

[Verse 2: rap, rhythmic delivery]
(4〜8 行)

[Pre-Chorus]

[Chorus]

[Dance Break: instrumental, heavy beat]

[Bridge: stripped down, emotional]
(2〜4 行)

[Key Change]

[Chorus: maximum layers, ad-libs, high note belt]

[Outro]
[End]
```

- `[Dance Break]` (コミュニティは `[Rap Verse]` 表記も使う) は suno-spec §4 の標準語彙外だが、K-POP 文脈ではコミュニティ検証済み (High)。効きが揺れる場合は `[Instrumental Break: dance break, heavy beat]` / `[Verse: rap delivery]` に差し替える (語彙の正は suno-spec §4)
- キリングパートの置き所は Dance Break 直前のサビ末尾か、ラスサビ頭が定石

## 4. ボーカル演出 — スタックが「K-POP の声」を作る

- **サビは 6〜12 トラックのボーカルスタック** (High): リード + オクターブ重ね + 3 度/5 度ハモ + ブレスレイヤー + ワイドコーラス。この厚みがジャンルの署名
  - Suno 写像: Style に `layered harmonies, stacked vocals`、サビ側に `[Chorus: layered harmonies, wide backing vocals]`
- **ギャングボーカル**でキメを強調する (High): キメ拍の短い掛け声を全員声で。`gang vocals`
- バースの標準話法は **rap-singing** (歌とラップの中間)。`rap-singing, smooth rhythmic delivery`
- パート割りの感覚を 1 ボーカルでも再現する: セクションごとに声の温度を変える (`[Verse 2: deep sultry delivery]` のようなパラメータ付きタグ)。グループ感が欲しければ `mixed group vocals`
- **high note belt は 1 曲 1〜2 回**: キリングパートかラスサビ専用の装置。乱発すると頂点が消える
- 発音は明瞭に: `clear enunciation` はダンスポップの聞き取りやすさを支える定番記述子 (§6 の言葉選びとセット)

## 5. Suno 写像の組み立て例

Style 完成例 (自作。語彙は §2 の有効語彙から構成):

1. ガールクラッシュ系: `K-pop girl group, aggressive edm trap beat, 135 bpm feel, sassy vocals, powerful chant chorus, heavy bass drop, confident attitude, glossy production`
2. 爽やかポップ系: `K-pop boy group, bright synth pop, funky guitar riff, 120 bpm feel, youthful clear vocals, layered harmonies, refreshing energy, polished modern mix`
3. 実験系: `experimental K-pop, industrial sounds, dubstep breakdown, aggressive rap-singing, complex structure, 140 bpm feel, dark charismatic energy, maximalist glossy production`

Exclude 定番: `lo-fi, acoustic folk, garage rock` — glossy な仕上げを守る 3 点 (運用は suno-spec §3)。

よくある事故と対処:

| 症状 | 対処 |
|---|---|
| Pre-Chorus が立たず Verse からサビに直行して聴こえる | `[Pre-Chorus: rising tension, drum build]` とパラメータで上昇を明示し、行数を 2〜4 行確保する |
| アンチドロップが「音の薄いサビ」にしかならない | 直前のビルドが弱いと成立しない。Pre-Chorus 側を最大化してから抜く (§3 技法カードの順序) |
| Dance Break が歌で埋まる | `[Dance Break: instrumental, heavy beat]` と instrumental を明記し、タグ直下に歌詞行を置かない |
| ジャンルスイッチで散らかる | 縫い込みは 3〜4 ジャンルまで。骨格を 1 つ決めて Style の先頭に置く (組み立ては 02_style-assembly.md) |
| ボーカルが単声で平板 | Style に `layered harmonies, gang vocals`、サビにパラメータ付きタグ (§4)。それでも薄ければ `[Choir]` `[Backing Vocals]` を重ねる |

## 6. ことば側への申し送り (lyricist 必読)

- **言語ミックスが様式** (High): 日本語主体の曲でも、フックに短い英語のパンチフレーズを混ぜるのが K-POP の文法。英語行は誰でも歌える単純さでよい (難しい英語は事故のもと)
- **掛け声・チャントの席を空ける**: ギャングボーカル用の 1〜2 語 (曲固有の合言葉が理想) をキメ拍に。合いの手も地の行として書く (入稿の括弧規則は songwriting 側の規約が正)
- **clear enunciation を言葉側から支える**: 子音の立つ語・開いた母音を選ぶ。もごもごした連語や詰まる音の連続はサビに置かない
- **キリングパートの 1 行はコピーの文法**: 短く・断定・反復可能。曲名やコンセプト語をここに埋め込むのが定石
- **Pre-Chorus は「上昇の言葉」**: 意味の上でも高度を上げる (疑問 → 確信、静 → 動)。サビ頭の宣言に着地させる
- Rap Verse は rap-singing 前提で詰め込みすぎない。歌に戻れる語数で書く
- 1 番と 2 番で同じ構文の言い換えを使うと、セクション積層の反復美に言葉が同期する

## 7. 研究出典

技法は 2026-07-11 取得の下記調査に基づく。実在アーティスト・作品への言及はこの欄のみ。歌詞原文は引用していない。確度: High = 複数ソース一致または当事者取材 / Med = 単一ソースまたはコミュニティ知。

- ソングキャンプと song starter 文化 (当事者取材): https://www.billboard.com (UMPG ソングキャンプ) / https://laist.com (Making of a K-pop hit) — High
- 曲構成の類型 (Pre-Chorus・アンチドロップ・Dance Break・キリングパート): https://medium.com/@fortytwoaisles / https://kpopalypse.com — Med〜High
- ボーカルスタックの実務 (6〜12 トラック): https://beatkey.app — Med
- プロデューサー視点の制作解説: https://www.loopcloud.com — Med
- Suno での K-POP 記述子と構成タグ: https://openmusicprompt.com — High (コミュニティ検証)
