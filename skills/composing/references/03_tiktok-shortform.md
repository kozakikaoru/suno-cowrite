# 03 TikTok・ショート動画 プレイブック — 15 秒の切り抜きから逆算する

ショート動画での拡散を想定する曲・バイラル狙いの曲で読む。単一ジャンルではなく**流通形態の技法**なので、かわいい連呼系ポップ等では主として単独で、それ以外の曲では主ジャンルのプレイブックに副として重ねて使う (主 1 + 副 1 の運用内)。

> - 例 (Style 記述・スケルトン・フレーズ) はすべてこの資料のための自作。実在曲の歌詞は引用していない
> - 実在アーティスト・作品への言及は §7「研究出典」のみ。本文は系統として抽象化してある
> - BPM・数値は目安。字数上限・タグ語彙・スライダーの実務値は suno-spec が正

## 1. シーンの前提

- ストリーミング + ショート動画がポップスの形を変えた (High): イントロは平均約 20 秒 → 約 5 秒 (78% 減)、ヒット曲の平均尺は 90 年代の 4 分超 → 約 3 分 15 秒、ブリッジは削除傾向。**冒頭 15 秒が実質のサビ**になった
- チャートの前段がショート動画になった (Med): グローバルヒットの多くが先にバイラルを経る。曲は 1 本の完成品ではなく**「切り抜き素材 + 複数バージョン群」**として設計される (High)
- 単位は「曲」ではなく「ループする素材」(High): 最初の 3 秒で認知され、15 秒で完結するフックが本体。視聴判断は 3〜10 秒で下る
- 拡散する曲の共通項 3 点: **ドライで前に出るボーカル / 一聴で真似できるリズムのキメ / 同じ言葉の連呼**
- 日本と海外は別レイヤーで動く (Med-High): 日本 = 振り付け動画文化が最強で、かわいい・連呼・ネタ性が軸。海外 = sped-up/slowed リミックス、phonk、ミーム音源、シネマティック edit、旧曲の再発掘
- 揺り戻しも進行中 (Med): sped-up 一辺倒からエモーショナル/シネマティック edit 音源・ニッチ直撃ハイブリッドへ。「速くすれば伸びる」は既に古い
- 年単位で残る骨格は **頭フック・ループ耐性・切り抜き点の設計**の 3 つ。個別の流行音色は :trend 調査で補完する (2 速度モデル)

## 2. サウンド署名の早見表

| サブスタイル | BPM 目安 | 質感 | Style 記述子の例 |
|---|---|---|---|
| ダンスチャレンジ系 | 120〜140 (125 が汎用) | 明確で一定のビート + 予測可能なフレージング = 振付が作りやすい (High) | `catchy pop, 125 bpm feel, instant hook, punchy drums, bright synths, dry upfront vocals, danceable` |
| かわいい連呼系 (日本) | 125〜130 目安 | バブルガムシンセ + グループチャント + ネタ性ひとつまみ | `j-pop, kawaii, 128 bpm feel, repetitive catchy hook, group chant vocals, bubblegum synths, playful energy` |
| ミーム/リズムネタ系 | 自由 (キメ優先) | ワンフレーズ + キメの反復。音数少なく、笑いの余白を残す | `novelty pop, quirky, minimal beat, rhythmic chant hook, comedic timing, dry vocals` |
| シネマティック edit 系 (海外) | スロー〜ミッド | 感情的なビルドと余白。slowed + reverb で映える設計 | `emotional cinematic pop, atmospheric synths, deep sub bass, intimate breathy vocals, spacious mix, melancholic` |

- どのサブスタイルも**ドラムはシンプルに**: ±20% のテンポ変化 (sped-up/slowed) に耐えるパターンが前提 (§4)
- 振付適性の中心帯は 120〜140 BPM (Med-High)。外すなら外す理由 (ネタ系・edit 系) を持って外す

## 3. 構成慣習 — 標準の器との差分

標準の Verse–Chorus 型 (songwriting の 01_song-structure が正) からの差分は 3 点:

1. **フックファースト** (High): イントロを削るか、いきなりサビで始める。冒頭 5 秒に「この曲」と分かる署名音を置く
2. **15〜30 秒の切り抜き区間を 1 箇所、意図的に設計する** (High): 単体で成立するループをフル尺の中に仕込む。他セクションはフックへの復帰導線として最小限に
3. **ブリッジは原則置かない** (High)。総尺も短く (2 分台目安)

書き始めの手順 (フックファースト設計): (1) 15 秒で完結するフレーズ + キメを先に作る → (2) それをサビ兼イントロに配置する → (3) 残りのセクションを復帰導線として埋める。頭から順に書かない。

標準スケルトン (迷ったらこれ):

```text
[Chorus]
(2〜4 行。連呼フック = 切り抜き区間。冒頭 5 秒の署名音を兼ねる)

[Verse 1]
(4 行。短く、フックへの助走)

[Chorus]
(1 回目と同一歌詞)

[Verse 2]
(4 行)

[Chorus: layered vocals, ad-libs]
(最後は厚く)

[Outro: hook fragment repeating]
(フックの断片 1〜2 行で終わる)

[End]
```

- 末尾をフック断片で終えると、ループ再生時に頭のサビへ自然につながる (ループ耐性)
- タグは suno-spec §4 の語彙だけ使う。**`[Intro]` を書かない**ことが最初の設計判断になる

## 4. ボーカル演出

- 原則は**聞き取りやすく、口ずさめる** (High)。技巧・装飾より明瞭度。ドライで前に出る声がジャンルの声 (`dry upfront vocals`)
- 連呼とチャント: 同じ言葉の反復とグループチャント (`group chant vocals`) が日本系の主武器。掛け声はキメ拍に置く
- **マルチバージョン前提設計** (High: レーベルが公式に複数バージョンを出す慣行が定着) — sped-up (+10〜30% 速 + ピッチ上げ) と slowed + reverb の両方で成立させる:
  1. ±20% のテンポ変化で破綻しないシンプルなドラム
  2. ピッチ変化で映える主旋律域 (上げても刺さらず、下げてもこもらない中域中心)
  3. リバーブ余白を残すドライ気味ミックス (slowed 側で足される残響の席を空けておく)
- edit 系はブレス多めの親密な声 (`intimate breathy vocals`) で、slowed 化したときの感情量を先に仕込む

## 5. Suno 写像の組み立て例

Style 完成例 (自作):

1. 日本・振り付け系: `j-pop, kawaii, 128 bpm feel, repetitive catchy hook, group chant vocals, danceable, bubblegum synths, dry upfront vocals, playful energy`
2. 汎用ダンスチャレンジ系: `catchy pop, 125 bpm feel, instant hook, chant-along chorus, punchy drums, bright synths, dry upfront vocals, playful confident energy`
3. 海外 edit 系: `emotional cinematic pop, slow build, atmospheric synth pads, deep sub bass, intimate breathy female vocals, spacious clean mix, melancholic night mood`

Exclude 定番: `progressive rock, jam band, muddy reverb` — 長尺化・展開の迷走・声のこもりを防ぐ (運用は suno-spec §3)。

よくある事故と対処:

| 症状 | 対処 |
|---|---|
| イントロが長く生成される | スケルトンの頭を `[Chorus]` にし、`[Intro]` タグを書かない。Style の先頭側に `instant hook` |
| フックが 15 秒で完結しない | フック行を削って連呼に寄せる (§6)。1 フレーズ 1 呼吸 × 反復に単純化する |
| sped-up / slowed にすると破綻しそうな音数 | 速いフィル・厚い装飾を削る。Exclude に `orchestral, busy drum fills` |
| edit 系が賑やかになりすぎる | `spacious, minimal` を足す。slowed で映えるのは派手さではなく余白 |
| ボーカルが奥に引っ込む | `dry upfront vocals` を明示し、Exclude に `heavy reverb` |

## 6. ことば側への申し送り

- **武器は「口ずさめるワンフレーズ」ただ 1 つ**: タイトル語 (または決め台詞) を短く連呼するフックが曲の本体。意味の説明より音の快感を優先する
- 切り抜き区間は単体で意味が完結させる: その 15 秒だけ聴いて「何の曲か」が伝わる (前後の文脈に依存させない)
- 連呼ワードは母音の開いた語・撥音のキメで: 真似しやすさ = 発音のしやすさ
- 日本向けは振り付けを誘発する動作語 (振る・回す・上げる系) をフックに置くと強い
- 同型フレーズの反復は正義。韻の技巧より反復の設計に力を使う
- バースは短くフックへの助走に徹する。情報を詰めない (情報量で聴かせたい曲はこのプレイブックの外)

## 7. 研究出典

技法は 2026-07-11 取得の下記調査に基づく。実在アーティスト・作品への言及はこの欄のみ。歌詞原文は引用していない。確度: High = 複数ソース一致または研究 / Med = 単一ソースまたはコミュニティ知。

- イントロ短縮の研究 (約 20 秒 → 約 5 秒): https://news.osu.edu — High
- 平均尺の短縮・ブリッジ削除傾向: https://www.prsformusic.com / https://joebennett.net — High
- ショート動画とチャートの関係・切り抜き設計: https://musicpulse.app / https://blog.recordjet.com — Med
- バイラル曲の共通項とフックファースト: https://blog.push.fm/24094 / https://www.thebandcampdiaries.com/post/794800251360968704 — Med
- sped-up / slowed リミックスの慣行: https://hmc.chartmetric.com/nightcore-slowed-reverb-tiktok-remix — High
- 2023 → 2025 のトレンド変遷 (edit 文化への移行): https://fanraizd.com — Med
- ダンスチャレンジ適性 BPM: https://songbrain.ai — Med
- 日本のバイラル文化 (振り付け・かわいい・連呼): https://www.kkbox.com (2025 邦楽バイラル) / https://studio15.co.jp — Med
