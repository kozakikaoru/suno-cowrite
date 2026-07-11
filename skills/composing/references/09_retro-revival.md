# 09 レトロ・リバイバル プレイブック — 年代記述子で「あの音」を丸ごと呼び出す

ジャンルがレトロ・リバイバル系 — シティポップ再解釈・昭和歌謡・synthwave / future funk など、**特定の年代の音を現代に召喚する**曲で読む。共通するのは、サウンドの正体が「年代そのもの」である点で、Suno では**年代記述子 (80s 等) が音響全体を最も強く引き寄せるレバー**になる (§5)。過剰にデジタルでグリッチなネット発の質感は 07_subcul-indie.md、ローファイの劣化ノイズを主役にするチル質感はこの器の担当外。

> - 例 (Style 記述・スケルトン・フレーズ) はすべてこの資料のための自作。実在曲の歌詞は引用していない
> - 実在アーティスト・作品への言及は §7「研究出典」のみ。本文は系統として抽象化してある
> - BPM・数値は目安。字数上限・タグ語彙・スライダーの実務値は suno-spec が正

## 1. シーンの前提

- レトロ・リバイバルは単一ジャンルではなく、複数の年代回帰の束。共通哲学は**時代の音色と録音の質感を意匠として現代に呼び戻す**こと。ゆえに署名は構成より和声・音色・プロダクションに宿る
- シティポップ再解釈は pop + disco + funk + R&B + boogie + ジャズフュージョンの交点 (High)。グルーヴィーな (スラップ) ベース + maj7/9th のジャジーなコード + きらめくエレピ + 滑らかなボーカルが器で、「夜のドライブ・ネオン・都会」の美学が受けの軸
- **リバイバルの構造**: 海外の動画サイトのアルゴリズム経由で再発見された文脈 (High)。原曲世代の記憶と、原曲を知らない世代が「新しい音」として聴く新鮮さ — この二重性が消費のエンジン
- 昭和歌謡 (Kayōkyoku) は昭和期の歌謡曲を現代に再構成する系統。**ローマ字表記のマクロン (Kayōkyoku) の有無で出力ジャンルが変わる**という Suno 挙動の知見は skills/suno-spec/references/style-vocab.md が正 — 本書では深掘りせず、Style に書くときはそちらの表記に従う
- synthwave / future funk は隣接する電子系リバイバル。synthwave = 80 年代の映画・ゲーム音楽的なシンセ美学、future funk = シティポップ/ディスコをサンプリング・チョップした四つ打ちダンス
- **質感が本体**: このジャンル群は「録音の古さ」が意匠 (High)。アナログテープ由来の温かみ・飽和が signature で、ハイファイに磨きすぎると年代感が飛ぶ。ただし劣化ノイズを足すローファイとは別物 — 狙うのは清潔で温かい「当時のハイファイ」

## 2. サウンド署名の早見表

| サブスタイル | BPM 目安 | 何がそう聴こえさせるか | Style 記述子の例 |
|---|---|---|---|
| シティポップ再解釈 | ミドルテンポ目安 (Low、数値未確認) | maj7/9th のジャジーなコード + グルーヴィーなスラップベース + きらめくエレピ + アナログテープの温かみ | `japanese city pop, mid-tempo groove, funky slap bass, jazzy maj7 chords, shimmering electric piano, analog tape warmth, smooth vocals, nostalgic night drive` |
| 昭和歌謡 (Kayōkyoku) | バラード〜歌謡ポップで幅広い (目安) | 歌謡的なマイナー旋律 + 生楽器/ストリングス + ドラマティックな歌唱。**マクロン必須** (style-vocab) | `Kayōkyoku, 80s japanese pop, dramatic expressive vocals, lush strings, retro analog production, nostalgic` |
| synthwave | ミドル、80〜118 目安 (Low、注記†) | 太いアナログシンセ + ゲートリバーブのドラム + アルペジオベース + ネオン的メランコリー | `synthwave, 80s retro, warm analog synths, gated reverb drums, arpeggiated bassline, neon melancholy, cinematic` |
| future funk | 四つ打ち、110〜130 目安 (Low、注記†) | シティポップ/ディスコのチョップサンプル + フィルターハウス的四つ打ち + 多幸感 | `future funk, chopped city pop samples, filtered disco house, four-on-the-floor, bright euphoric groove, danceable` |

- **† synthwave / future funk は §7 の City Pop 調査の対象外**。BPM は一般に流通する目安で確度 Low — 数値を断定せず、迷ったら `mid-tempo` 等のエネルギー語 + 年代タグで代替する (表記の正は suno-spec §5)
- 年代タグ (80s 等) は BPM 数値より強く音響全体を決める。骨格の先頭に「ジャンル語 + 年代 + アナログ質感語」の 3 点を置くのが再現性の要 (§5)
- 質感の中心はアナログの温かみ。`lo-fi` の劣化ノイズとは別物なので、濁りを避けたいときは §5 の Exclude で `lo-fi, muddy` を切る

## 3. 構成慣習 — 標準の器との差分

レトロ・リバイバルの署名は構成より**和声・質感・アレンジ**に宿るため、標準の Verse–Chorus 型 (songwriting の 01_song-structure が正) からの差分は小さい。数少ない構成上の勘所:

1. シティポップは**イントロ・間奏にインストの見せ場を置く** (Med) — エレピソロ、ファンキーなギターカッティング、サックス/ブラス。フックへ急ぐショート動画作法とは逆に、groove を聴かせる余裕を作る
2. **ジャジーなコード移動と転調が「おしゃれさ」の装置**。ただし Suno はコード直接指定が不安定なので、`jazzy maj7 chords` 等の記述子とムードで近似する (組み立ての一般則は 02_style-assembly.md)
3. synthwave は展開の起伏より**持続する情景**。反復と shimmer を長く保ち、ボーカルなし (instrumental) でも成立する
4. future funk は**サンプルチョップのループが骨格**。ダンス構成で、歌モノ的な物語展開は要らない

標準スケルトン (シティポップ型。迷ったらこれ):

```text
[Intro: shimmering electric piano, groovy slap bass]
(4〜8 小節。グルーヴとコード感を提示)

[Verse 1]
(4〜8 行。滑らかに歌う)

[Pre-Chorus: rising, lush chords]
(2〜4 行)

[Chorus: smooth soaring vocals, full band groove]
(4 行。エモーショナルな頂点)

[Verse 2]

[Pre-Chorus]

[Chorus]

[Instrumental Break: electric piano solo, funky guitar cutting]
(エレピ or サックスの見せ場)

[Bridge: mellow, jazzy reharmonization]
(2〜4 行)

[Chorus: final, layered harmonies]

[Outro: fading groove, tape warmth]
[End]
```

synthwave はこの器から Verse/Pre-Chorus を抜き、`[Intro]` → 持続する `[Instrumental]` → `[Hook]` の反復に寄せる。future funk はチョップ素材のループを `[Instrumental Break]` 主体で回す。

## 4. ボーカル演出

- シティポップ: **滑らかで都会的な歌唱**。`smooth, warm, silky vocals`。力まず洗練させ、当時の様式としてメロウなハモリ・コーラスワーク (`lush backing harmonies`) を重ねる。男女どちらでも成立する
- 昭和歌謡: よりドラマティックでビブラート豊かな歌謡唱法。`dramatic, expressive vocals with rich vibrato`。シティポップの脱力とは逆に、情感を堂々と込める
- synthwave: 声は控えめか instrumental。`airy, distant vocals with reverb` で情景に溶かすか、完全インストにする
- future funk: チョップされたボーカルサンプルを楽器として扱う (`chopped vocal samples`)。歌モノにするなら明るくファンキーに
- 声の同一性を Persona で固定する運用は 02_style-assembly.md に従う

## 5. Suno 写像の組み立て例

**年代タグの扱いが要**: `80s` / `80s production` などの年代記述子は、このジャンル群で音響全体を最も強く引き寄せる (§1)。「ジャンル語 + 年代 + アナログ質感語」を骨格の先頭に置くと再現性が高い。引きが強い分、現代的な語 (`modern`, `edm`) と衝突すると年代感が壊れるので、そうした語は Exclude か削除する。

Style 完成例 (自作):

1. シティポップ再解釈: `japanese city pop, 80s, mid-tempo groove, funky slap bass, jazzy maj7 chords, shimmering electric piano, analog tape warmth, smooth silky female vocals, lush backing harmonies, nostalgic night drive`
2. 昭和歌謡 (Kayōkyoku): `Kayōkyoku, 80s japanese pop, mid-tempo, dramatic expressive female vocals with vibrato, lush strings, warm analog production, melancholic and nostalgic` — マクロン付き表記が効きを決める (skills/suno-spec/references/style-vocab.md)
3. synthwave: `synthwave, 80s retro, mid-tempo, warm analog synths, gated reverb drums, arpeggiated bassline, neon melancholy, airy distant vocals, cinematic and nostalgic`

Exclude 定番 (運用は suno-spec §3):

- シティポップ: `lo-fi, muddy, distorted, aggressive, modern edm` — アナログの艶を濁らせる質感と、年代を壊す現代語を防ぐ
- synthwave: `acoustic, organic, lo-fi, modern pop` — シンセ美学を守る
- 昭和歌謡: `novelty, comical, edm, trap` — ジャンルドリフト防止 (コミカル化の一次対策はマクロン表記で、Exclude は保険)

よくある事故と対処:

| 症状 | 対処 |
|---|---|
| アナログの温かみが出ず、デジタルで硬い | `analog tape warmth, warm analog production` を明示し、年代タグ `80s` を骨格先頭へ。`80s production` は音響全体を引き寄せる強タグ (§1) |
| 昭和歌謡がコミカル/ノベルティ曲に化ける | Kayōkyoku のマクロンが落ちていないか確認する (Kayokyoku 表記での事故報告あり)。表記の正は skills/suno-spec/references/style-vocab.md |
| ジャジーなコード感が出ず平坦な進行になる | `jazzy maj7 chords, sophisticated harmony` を足す。コード直接指定は不安定なので記述子とムードで近似 (一般則は 02_style-assembly.md) |
| 現代的な EDM 風に寄る (年代感が消える) | 年代と衝突する `modern, edm` 系を Exclude。`80s, retro, analog` を重ねて過去へ引き戻す |
| シティポップがチルすぎて眠い (groove が死ぬ) | `funky slap bass, groovy, danceable disco beat` でリズムを立て、`lo-fi` を Exclude |
| synthwave でボーカルが前に出すぎる | `instrumental` か `airy distant vocals` を指定し、声を情景の一部に沈める |

## 6. ことば側への申し送り

- シティポップの歌詞は「都会・夜・ネオン・海辺・ドライブ」の情景語彙が signature。心情を説明するより情景を描き、80 年代的な洗練とほろ苦さをまとわせる
- 英語まじりの語感が当時の様式だが、多用は禁物。キーフレーズやサビ頭に散らす程度にとどめる
- 昭和歌謡はより直接的でドラマティックな情感。歌謡的な語彙と、七五調的に据わる字数が乗りやすい
- synthwave / future funk は歌詞が薄い・断片的でも成立する (情景と質感が主役)。反復するワンフレーズで足りることが多い
- ノスタルジアは「原曲世代の記憶」と「知らない世代の新鮮さ」の二重性で成立する — 懐古に閉じず、今聴いても効く普遍的な情景語を選ぶ
- タイトル/キーフレーズは母音の開いた滑らかな語がシティポップの歌唱に乗りやすい。作詞の一般則は songwriting 側が正

## 7. 研究出典

技法は 2026-07-11 取得の下記調査に基づく。実在アーティスト・作品への言及はこの欄のみ (本書は個別名を参照していない)。歌詞原文は引用していない。確度: High = 複数ソース一致 / Med = 単一ソースまたはコミュニティ知 / Low = 推定・本調査の対象外。

- シティポップの系譜・録音の質感・リバイバルの構造: https://en.wikipedia.org/wiki/City_pop / https://en.wikipedia.org/wiki/Plastic_Love / https://web-japan.org / https://musicindustryweekly.com / https://note.com/rhythm_mind — High (BPM 帯のみ Low・推定)
- 昭和歌謡 (Kayōkyoku) のローマ字表記と Suno の出力挙動 (マクロンの有無): skills/suno-spec/references/style-vocab.md §6 が正 (一次出典はそちらに記載。二重管理を避けここでは再掲しない) — Med (未検証枠)
- Suno の Style 実務・年代/質感語彙の効き方: https://blakecrosley.com/guides/suno / https://sunoaiwiki.com — High (コミュニティ検証)
- synthwave / future funk の BPM・記述子: 本調査の対象外。一般に流通する目安に基づく — Low
