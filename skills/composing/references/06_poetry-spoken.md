# 06 ポエトリー/スポークンワード プレイブック — 語りをトラックに乗せる

ジャンルが語り主導 (ポエトリーリーディング/スポークンワード/ポエトリーラップ) の曲で読む。composer 向けだが dual-audience: **lyricist はこの資料を渡されたら §6「ことば側への申し送り」を必読** (余力があれば §1・§3 も)。韻の技巧が主役のラップなら本書ではなく songwriting/references/10_hiphop-genre-ja.md へ。

> - 例 (Style 記述・スケルトン・フレーズ) はすべてこの資料のための自作。実在曲の歌詞は引用していない
> - 実在アーティスト・作品への言及は §7「研究出典」のみ。本文は系統として抽象化してある
> - BPM・数値は目安。字数上限・タグ語彙・スライダーの実務値は suno-spec が正

## 1. シーンの前提

- 定義: ポエトリーリーディング ≒ スポークンワード。**ポエトリーラップ** = 韻の技巧より物語・感情の伝達を優先し、詩の朗読のようにリズムへ言葉を乗せる系統 (High)
- ジャンルの存在理由: **「メロディに合わせて言葉を削らなくてよい」**。情報量と生々しい熱量をそのまま運べることが、歌に対する優位性 (Med-High)
- 基本形は打ち込みトラック + マイク 1 本の独白。声が主役で、トラックは「語りの場」を作る背景 (Med-High)
- 日本のシーンの系譜 (Med-High): ①日常のリアル派 (生活の実感を等身大の言葉で) / ②文学的で感情の重い派 (詩としての強度) / ③ハードコア越境派 (ラップシーンとの往復)
- 聴かせどころは「声の存在感」と「熱量の変化」。コード進行やフックの強さで聴かせる文法ではない

## 2. サウンド署名の早見表

トラックは幅が広いが、共通原則は**声の帯域を空けた引き算のアレンジ** (Med)。迷ったら楽器を 1 つ減らす。

| サブスタイル | テンポ感 | トラックの質感 | Style 記述子の例 |
|---|---|---|---|
| ピアノ/アンビエント系 (文学派) | スロー | エモーショナルなピアノ、パッド、徹底して疎 | `emotional piano, ambient pads, sparse arrangement, spacious` |
| lo-fi ビート系 (日常リアル派) | 70〜90 目安 | 埃っぽいドラム、温かいベース、ざらつき | `lo-fi beat, dusty drums, warm bass, intimate` |
| バンド/ポストロック系 (熱量派) | ミッド | 静→轟音のビルド、生ドラム | `post-rock build, clean guitar arpeggios, live drums, dynamic` |
| ハードコア越境系 | ミッド〜アップ | ラップ寄りのビート、太い低音 | `boom bap influenced beat, heavy bass, raw, aggressive undertone` |

- 声の処理: **ドライ〜軽いルームリバーブで「近い」**のがジャンルの声 (Med)。深いリバーブは語りの生々しさを殺す
- 密度の下限を恐れない: ビートレス (ピアノ + 声だけ) でも成立する。「音が足りない」と感じたら、音を足す前に §4 の熱量設計を疑う

## 3. 構成慣習 — 標準の器との差分

標準の Verse–Chorus 型 (songwriting の 01_song-structure が正) からの差分は 3 点:

1. **ヴァース = `[Spoken Word]` の語り、フックだけ歌 (または連呼)** が最頻出形 (High)。`[Spoken Word]` はこのジャンル最大の武器で、語りセクションの頭に必ず置く
2. **サビの高揚を「語りの熱量エスカレーション」で作る** (Med) — 声量・言葉の密度・ピッチの上ずりを段階的に上げる。コードや音量のビルドは従属変数
3. **曲末に向けて言葉が加速・過熱する** (Med)。感情の頂点はラスサビではなく最終ブロックの語りに置く

標準スケルトン (迷ったらこれ):

```text
[Intro: sparse piano, vinyl texture]

[Spoken Word]
(語り 8〜12 行。静かに、近く)

[Chorus: sung, soft melodic hook]
(歌 2〜4 行。張らない)

[Spoken Word: more intense, denser delivery]
(語り 8〜12 行。密度を上げる)

[Chorus]
(1 回目と同一歌詞)

[Bridge: spoken, urgent, drums drop out]
(語り 4〜6 行。最熱点。楽器を減らして声だけ前へ)

[Chorus: full arrangement, layered vocals]
(最後だけ厚く)

[Outro: whispered spoken word]
(1〜2 行の余韻)

[End]
```

- サビを持たない AABA 型 (語りが進み続ける) も文学派では有効。その場合も熱量カーブの設計 (右肩上がり + 最終ブロックで最大) は同じ
- タグは suno-spec §4 の語彙だけ使う。`[Spoken Word]` と `[Whisper]` が主戦力

## 4. ボーカル演出 — 熱量の 3 段階設計

語りは放っておくと平板になる。**3 段階の熱量を先に決めて**からパラメータ付きタグに落とす:

| 段階 | 声の状態 | タグ・記述子の例 |
|---|---|---|
| 1. 静 (導入) | 近く、囁くように、間が多い | `[Spoken Word: calm, close mic, intimate]` |
| 2. 動 (展開) | 言葉が増え、前のめりに | `[Spoken Word: more intense, urgent delivery]` |
| 3. 熱 (頂点) | 声量とピッチが上がり、叫びの手前 | `[Spoken Word: impassioned, almost shouting]` |

- 歌フックは語りとの温度差で聴かせる: 語りが熱い曲ほどフックは柔らかく (対比)、語りが静かな曲ならフックはチャント連呼で上げる
- `[Whisper]` は導入と結末の演出に効く。全編囁きは単調のもと
- 声の性別・基本質感は Style 欄で固定し (§5)、セクションごとの演技はタグで動かす — この役割分担を崩さない

## 5. Suno 写像の組み立て例

Style 完成例 (自作):

1. 文学派 (ピアノ): `japanese poetry reading, spoken word over emotional piano, ambient pads, sparse arrangement, intimate close-mic female voice, dry vocals, slow tempo, literary and confessional, quiet intensity`
2. 日常リアル派 (lo-fi): `japanese poetry rap, spoken word verses with sung hook, lo-fi beat, dusty drums, warm bass, close-mic male voice, raw and honest, building intensity, mid-slow tempo`
3. 熱量派 (バンド): `spoken word over post-rock, clean guitar arpeggios swelling to distorted wall, live drums, impassioned male voice, dynamic quiet-loud contrast, cathartic climax`

Exclude 定番: `auto-tune, edm, polished pop vocals` — 語りの生々しさを守る 3 点 (運用は suno-spec §3)。

よくある事故と対処:

| 症状 | 対処 |
|---|---|
| 語りが歌になってしまう | `[Spoken Word]` を各語りセクションの頭に置き直し、Style に `spoken word` を明記する。**歌詞側の行長を不揃いに崩す** (行が揃うほど歌と解釈される。§6) |
| 語りが平板で退屈 | §4 の 3 段階をパラメータ付きタグで明示する。トラック側も段階ごとに 1 要素ずつ足す |
| トラックが賑やかで声が沈む | Style に `sparse, minimal` を足し、Exclude に `orchestral`。楽器を減らす方向で解決する (声を大きくする方向ではない) |
| フックが語りに引きずられて歌わない | `[Chorus: sung, melodic]` と歌唱を明示する。フック行はモーラを揃えて歌の文法に寄せる |

## 6. ことば側への申し送り (lyricist 必読)

- **哲学**: このジャンルは「情報量を削らない」ことが存在理由。歌モノの推敲 (字数を詰める・削る) とは逆方向で、具体と量をそのまま運んでよい
- **行の長さは不揃いでよい。むしろ揃えない**: 行のモーラが揃うほど Suno は歌として解釈する (§5 の事故)。長短の落差そのものが語りのリズムになる
- **1 行 = 1 呼吸**: 行の切れ目が息継ぎであり「間」。聴かせたい 1 語は単独行に置き、畳みかけたい所は行を長くする
- **行間の呼吸を並びで設計する**: 空行や記号に頼らず、行の長短の並びで加速・減速を作る (短→短→長 = タメてから流す、の型)
- **エスカレーションの逆算**: 曲末ブロックほど行を長く・密度を濃く。§3 の熱量カーブと行密度を一致させる
- **フックだけは歌の文法**: 短く・反復・母音の開いた語。語りとフックで 2 つの文法を 1 曲に共存させる
- **韻は義務ではない**: 踏むなら意味優先で、音の一致を主張しない。韻の技巧を前に出したい曲は本書ではなく 10_hiphop 系へ
- **生々しさは固有の具体から**: 一般論を書いた瞬間に「詩」ではなく「標語」になる。半径 5 メートルの名詞と数字で描く

## 7. 研究出典

技法は 2026-07-11 取得の下記調査に基づく。実在アーティスト・作品への言及はこの欄のみ。歌詞原文は引用していない。確度: High = 複数ソース一致 / Med = 単一ソースまたはコミュニティ知。

- ポエトリーリーディングの定義とスポークンワードとの関係: https://ja.wikipedia.org/wiki/ポエトリーリーディング — High
- 日本のポエトリーラップの系譜と「情報量」論: https://note.com/pon_wtw — Med
- トラックの質感と声処理の慣習: https://sawanoguitarlab.com — Med
- GOMESS (文学的で感情の重い系統の代表例として): https://rude-alpha.com — Med
- ポエトリーと歌の境界の分析: https://qjweb.jp/column/132044 — Med
- 春ねむり (ハードコア越境系統の代表例として): https://www.cinra.net — Med
- Suno の `[Spoken Word]` タグ実務: https://blakecrosley.com/guides/suno / https://sunoaiwiki.com — High (コミュニティ検証)
