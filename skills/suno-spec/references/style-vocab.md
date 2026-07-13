# Suno Style 語彙辞典 — 非音楽語リファレンス (同梱スナップショット)

調査日: 2026-07-11
<!-- 上の「調査日: YYYY-MM-DD」行は hook が上書き版との新旧比較に機械抽出する。位置と形式を変えないこと -->

**要旨**: Style 欄はジャンル・楽器などの音楽用語だけでなく、**ムード・情景・質感・動作・メディア連想の非音楽語でも条件付けできる** (公式が V4.5 以降「Mood, vibe, instruments, and detail are captured with precision」と明言 — High)。本辞典は P の日本語の要望を英語記述子へ変換するための「日本語の意図 → 英語」逆引き表である。字数上限・タグ数・並び順・Exclude の一般則は spec.md (§2・§3・§5) が正で、ここでは繰り返さない。

- 読み方: songsmith (制作) が作曲工程で Style のムード枠・情景枠・質感枠を決めるときに、**通読せず該当カテゴリ (§2〜§6) だけを拾い読み**する。
- **表スキーマは契約** (update-spec の更新でも変えない): 列 = `日本語の意図 / 英語記述子 (推奨) / 日本語表記の挙動 / 確度 / 相性ジャンル / 備考`。

---

## 1. 使い方と確度の読み方

- **Style 欄は英語が基本。日本語の意図語は英語に訳して使うのが原則。** 日本語直書きは「入力は可能だが認識が弱い」が日本語圏の一致した所感で (Med)、内部翻訳が禁止ワードに偶然衝突してブロックされた事故例もある (Low)。「日本語で発想を整理 → この辞典で英語に変換」が最良ワークフロー。例外はローマ字の日本文化語 (§6) で、これはタグとして強く効く。歌詞欄は逆に日本語文字が推奨 (spec §7) なので混同しない。
- 「日本語表記の挙動」列 = その日本語を Style 欄にそのまま書いた場合に確認されている挙動。**現時点では語単位の検証報告が無く全行「未検証」**。これは調査結果の正直な反映であり、§8 の実測と update-spec の再調査で埋めていく枠である。
- 確度: **High** = 公式言及 / **Med** = 複数コミュニティ検証の一致 / **Low** = 単一報告・推測含む / **未検証** = 報告なし (実験枠)。
- 量の目安: **ムード語 1〜2 + 情景フレーズ 1 まで**。High/Med を骨格にし、Low/未検証は実験枠 1 語まで (積み過ぎの害は §7)。
- よくある要望の早見: **疾走感 → driving (§5) / 孤独感 → melancholic, intimate, sparse (§2) / カフェっぽく → cozy morning cafe vibe (§3) / ドライブ向け → night drive (§3)**。

---

## 2. ムード・感情語

非音楽語の中で最も強く効く系統 (公式がムード・バイブの精密反映を明言 — High)。generic な語 (happy / sad) は平均化されるので、特異的な語へ置き換える (Med)。

| 日本語の意図 | 英語記述子 (推奨) | 日本語表記の挙動 | 確度 | 相性ジャンル | 備考 |
|---|---|---|---|---|---|
| 切ない | melancholic, bittersweet | 未検証 | Med | バラード, シティポップ, lo-fi | sad より個性が出る。bittersweet は甘さが残りコード感が複雑になる |
| 孤独感 | melancholic, intimate, sparse | 未検証 | Med | バラード, アンビエント, lo-fi | lonely 単独より「感情 + 距離感 + 音数」への分解が再現しやすい (分解推奨は一部推測)。輪郭を強めるなら desolate |
| 多幸感・高揚 | euphoric | 未検証 | Med | EDM, ポップ, K-POP | 開けたコーラスとビルドを誘発する |
| 懐かしさ | nostalgic, wistful | 未検証 | Med | シティポップ, lo-fi, レトロ系 | レトロな音色選択を誘発。wistful はより静的で物憂げ |
| 前向き・希望 | hopeful, uplifting | 未検証 | Med | ポップ, アンセム系 | 明るい進行と上昇感 |
| 不穏・ゾクッと | haunting, eerie, unsettling | 未検証 | Med | ダークポップ, シネマティック | 残響深め・浮遊和声 |
| ダーク・威圧 | dark, menacing | 未検証 | Med | trap, phonk, メタル | dark は短調・低域寄りの万能語。menacing はベース強調 |
| 優しさ・親密 | tender, intimate | 未検証 | Med | アコースティック, バラード | 小編成・クローズ録音・囁き系 |
| 穏やか・癒し | serene, peaceful, calm | 未検証 | Med | アンビエント, lo-fi | 遅テンポ・アンビエント寄りになる |
| 壮大・勝利感 | triumphant | 未検証 | Med | オーケストラル, アンセム | ブラス・オーケストラ寄り |
| 切迫・焦燥 | urgent | 未検証 | Med | ロック, ドラムンベース | 前のめりの推進力 |
| ミステリアス | mysterious | 未検証 | Med | エレクトロニカ, シネマティック | eerie より恐怖成分が薄い |
| ロマンチック | romantic | 未検証 | Med | R&B, バラード | 甘いメロディ・ストリングス |
| 荒々しさ・衝動 | feral, aggressive | 未検証 | Low〜Med | ロック, メタル, パンク | 爆発力。穏やか系との単純併記は §7 |
| 遊び心 | playful | 未検証 | Med | ポップ, 電子ポップ | — |
| 相反の同居 (複雑な質感) | "warm but lonely", "dark yet beautiful" | 未検証 | Low〜Med | — | 意図的な緊張ペアは "X but Y" 形の 1 フレーズで書く。単純併記 (calm, aggressive) は混濁する (§7) |

---

## 3. 情景・シチュエーション語

**なぜ非音楽語が効くのか**: モデルはプロンプトを命令文としてではなく、高次属性へ圧縮する条件付けシグナルとして扱う。情景語は**訓練データ中でその場面と共起する音楽属性 (テンポ・楽器・空間処理) を引き寄せる** (Med)。つまり情景フレーズは「ジャンル + 楽器 + ムード」をまとめて引く複合ショートカットとして働く。

- 使い方: ジャンル等の主柱を先頭に立てた後に、**情景フレーズを 1 つだけ**添える (単語でなくフレーズで書く)。
- 情景だけの長文は圧縮時に切り捨てられる (先頭の語が支配的 — Med)。先頭に情景・末尾にジャンルという並びは効かない。

| 日本語の意図 | 英語記述子 (推奨) | 日本語表記の挙動 | 確度 | 相性ジャンル | 備考 |
|---|---|---|---|---|---|
| 夜のドライブ | night drive, midnight highway | 未検証 | Med | synthwave, phonk, city pop | 定番。drive 単独は方向が曖昧。ミドルテンポ・ネオン感を誘発 |
| ネオン・夜の街 | neon-lit city, city lights at night | 未検証 | Med | シンセポップ, 80s, シティポップ | シンセパッド寄りになる |
| カフェで流れてそう | cozy morning cafe vibe, coffee shop ambience | 未検証 | Med | lo-fi, jazz | 実例は「ジャンル + 情景フレーズ併記」型が主流。アコースティック + ローファイ化 |
| 雨の日の室内 | rainy day cafe, "rain outside window, warm inside" | 未検証 | Med | lo-fi, jazz, バラード | 遅テンポ・暖色系へ |
| 深夜のクラブ | late night club | 未検証 | Med | ハウス, R&B | こもった低域 |
| 夏・ビーチ・夕暮れ | beach sunset, tropical | 未検証 | Med | トロピカルハウス, レゲエ系 | breezy でレイドバックする |
| 焚き火・縁側 | campfire feel, front-porch feel | 未検証 | Med | フォーク, カントリー | 素朴な録音感 |
| 作業用・勉強用 | study session | 未検証 | Low〜Med | lo-fi | 反復ミニマル・控えめなドラム |
| 旅・ロードトリップ | road trip | 未検証 | Low | ロック, カントリー | 開放感 |
| 深夜の東京 | late night Tokyo apartment, Tokyo highway | 未検証 | Low〜Med | シティポップ, vaporwave | ノスタルジー寄り |

---

## 4. 質感・時間帯・季節語

質感語は実質的に**エフェクト・録音環境の選択**に翻訳される (Med): warm → アナログ系処理 / gritty → 歪み / spacious → リバーブ深め / intimate → クローズマイク、など。

| 日本語の意図 | 英語記述子 (推奨) | 日本語表記の挙動 | 確度 | 相性ジャンル | 備考 |
|---|---|---|---|---|---|
| 夢見心地 | dreamy | 未検証 | Med | dream pop, シューゲイズ, lo-fi | 空間系リバーブ。hazy の代用にもなる |
| 透明感 | ethereal | 未検証 | Med | アンビエント, 聖歌系 | 高域の透明感 |
| 温かみ | warm | 未検証 | Med | ソウル, アコースティック, lo-fi | アナログ系飽和・丸い低域 |
| 冷たさ・無機質 | cold, icy | 未検証 | Low | エレクトロニカ, ミニマル | dark, minimal で補強すると安定しやすい |
| ザラつき・生々しさ | gritty, raw | 未検証 | Med | ガレージロック, パンク, hiphop | 歪み・ガレージ感 |
| なめらか・艶 | smooth, velvet | 未検証 | Med (velvet は Low) | R&B, ソウル, jazz | — |
| 豪華・厚み | lush | 未検証 | Med | オーケストラル, R&B | 厚いレイヤー・ストリングス |
| きらめき | shimmering | 未検証 | Med | ドリームポップ, シンセ系 | 高域のきらめき |
| 広がり・空気感 | spacious, atmospheric | 未検証 | Med | アンビエント, ポストロック | リバーブ深く広い定位。lo-fi production と喧嘩する (§7) |
| 映画みたい | cinematic | 未検証 | Med | スコア系, トレーラー風 | オーケストラルな広がり |
| ビンテージ・古い録音 | vintage, retro, dusty | 未検証 | Med (dusty は Low〜Med) | シティポップ, ソウル, jazz | 古レコード質感 |
| 年代の空気 (80年代っぽく 等) | 80s, 90s, 2010s, modern | 未検証 | Med | 全般 | 「最も過小評価された強タグ」。その年代の音響慣習を丸ごと引き寄せる (年代指定は spec §5 でも「効く要素」) |
| 近未来・サイバー | cyberpunk | 未検証 | Med | synthwave, エレクトロ | 未来的デジタル質感。retro-futuristic の近似にも使える |
| 時間帯 (朝・深夜) | morning / late night / midnight を情景フレーズに織り込む | 未検証 | Med (フレーズ形のみ) | 全般 | 時間帯単独の効果報告は薄い。§3 のフレーズ型が確実 |
| 季節 (夏以外) | (推奨候補なし — 分解して書く) | 未検証 | 未検証 | — | 夏は §3 の beach sunset, tropical。春・秋・冬の単独季節語は使用報告が無く、質感語 (warm, icy 等) + 情景フレーズへの分解を推奨 |
| 水中・ガラス質 | underwater, glassy | 未検証 | 未検証 | — | muffled / dreamy 化との推測のみ (Low)。実験枠向き |

---

## 5. 動作・身体感覚語

動き・体感の語はテンポとリズムの推進力に翻訳される。BPM 数値の単独指定は効きが弱く、**エネルギー語 + テンポ表記の併用**が安定する (Low〜Med。テンポの書式は spec §5 の `bpm feel` 表記が正)。

| 日本語の意図 | 英語記述子 (推奨) | 日本語表記の挙動 | 確度 | 相性ジャンル | 備考 |
|---|---|---|---|---|---|
| 疾走感 | driving | 未検証 | Med | ロック, EDM, ドラムンベース | **第一候補**。fast-paced, high-energy で補強。`driving rock, 170 bpm feel` のようにテンポ併記が安定 |
| 突き抜け・上昇 | soaring | 未検証 | Med | アンセム, ポストロック | "soaring melody" が定番形 |
| 弾む・跳ねる | bouncy | 未検証 | Med | ポップ, ファンク | — |
| ゆったり・後ノリ | laid-back | 未検証 | Med | lo-fi, R&B, レゲエ | — |
| 慌ただしさ・性急 | frantic, frenetic | 未検証 | Med | パンク, ハイパーポップ | 高速で忙しい展開 |
| 浮遊感 | floating | 未検証 | Low〜Med | ドリームポップ, アンビエント | dreamy / ethereal 側での代用が確実 (§4) |
| 反復への没入 | hypnotic, hypnotic loop | 未検証 | Med | テクノ, ミニマル | 公式例文にも "hypnotic rhythms" がある (High) |
| 爆発 | explosive | 未検証 | Med | EDM, ロック | サビ・ドロップ向き |
| じわじわ高まる | building, slow-burn build | 未検証 | Med | ポストロック, EDM | 展開を作る位置に置く。終盤配置は逆効果の報告 (Low〜Med) |
| 大合唱感 | anthemic | 未検証 | Med | スタジアムロック, アンセム系 | — |
| 全開・高出力 | high-octane | 未検証 | Low | EDM, メタル | 実験枠 |

---

## 6. メディア連想語

媒体・様式の名前は、ジャンル + 質感 + 構成慣習を束で引き寄せる。**書いてよいのは一般名詞の媒体・様式名だけ**。実在の作品名・番組名・アーティスト名はモデレーション対象で書かない (spec §5)。ローマ字の日本文化語もここに含める — **綴りゆれで結果が激変する**ので備考に注意。

| 日本語の意図 | 英語記述子 (推奨) | 日本語表記の挙動 | 確度 | 相性ジャンル | 備考 |
|---|---|---|---|---|---|
| アニメ OP っぽく | anime opening | 未検証 | Med | J-pop, ロック | 疾走感あるポップ / ロック化。実在作品名は書かない |
| 昭和歌謡っぽく | Kayōkyoku | 未検証 | Med | レトロ歌謡, シティポップ | 統制実験で 80 年代歌謡曲を再現。**マクロン必須 — Kayokyoku 表記はコミカル曲に化けた報告** |
| シティポップ | city pop | 未検証 | Med | — | ほぼ確立したジャンルタグ (spec §5 でも例示) |
| J-pop らしく | J-pop (ハイフン付き) | 未検証 | Med | — | Pop 単独とは明確に別物になる (統制実験) |
| 演歌っぽく | enka | 未検証 | Low〜Med | — | こぶし・ペンタトニック調 |
| かわいい電子音 | kawaii | 未検証 | Low〜Med | future bass, 電子ポップ | kawaii future bass 等の複合形で使う |
| 渋谷系 | shibuya-kei | 未検証 | Low | — | 60s ラウンジ折衷 |
| 民謡っぽく | Min'yō, J-folk (要注意) | 未検証 | Med (失敗報告) | — | 期待と違う出力の報告 (演歌寄りポップ・謎の和風ロック)。使うなら実験枠 |

---

## 7. 効かない・危険語

実在アーティスト名・曲名・ブランド / ミキシング専門指示 / Style 欄の否定形 / ストーリー・歌詞内容の混入 — これらは **spec.md §5 の「効かない / 非推奨」表が正** (ここでは繰り返さない。Exclude の使い分けは spec §3)。以下は本辞典スコープの追加注意:

| 危険パターン | 何が起きるか | 対処 | 確度 |
|---|---|---|---|
| generic ムード語 (happy, sad, beautiful, emotional) | 平均化されて個性が出ない | §2 の特異語へ置き換える | Med |
| 相反ペアの単純併記 (calm, aggressive) | 混濁 | 意図的な緊張は "X but Y" の 1 フレーズ形で (§2) | Med |
| 非音楽語の積み過ぎ | タグ 10 個超で「平均化された mush」 | ムード 1〜2 + 情景 1 に絞る (総タグ数の一般則は spec §5) | Med |
| 日本語直書き | 認識が弱いうえ、内部翻訳が禁止語に衝突した事例あり | §1 の英訳原則に従う | Med (事故例は Low) |
| ローマ字の綴りゆれ | 別ジャンルに化ける (Kayōkyoku / Kayokyoku) | §6 の表記どおりに書く | Med |
| BPM 数値の単独指定 | 効きが弱い | エネルギー語と併用する (§5。書式は spec §5) | Low〜Med |
| 飾りの長文 | 200 語でも 12 語とほぼ同じ出力になる (高頻度タグが支配) | 会話調で書くなら主柱 1 + 補強フレーズ 1〜2 で止める (会話調自体は公式サポート — High) | Med |

---

## 8. 検証プロトコル (P との A/B 実測)

Low・未検証の語は実測で確度を上げ下げできる。手順:

1. **変えるのは対象語 1 つだけ**。同一の Style 骨格・歌詞・モデル・Advanced Options で「対象語あり / なし」の 2 案を作る。
2. 生成の揺らぎと区別するため、**各案 2 生成以上**を聴き比べる。
3. 聴く観点: テンポ帯 / 音色・楽器選択 / 空間処理 (リバーブ) / ムードが意図した方向に動いたか。
4. 補助: 公式 **Enhance ボタン**に対象語を入れると、モデルがその語をどう展開するかを覗ける (公式機能 — High)。
5. 記録: 判定 (効いた / 効かない / 別物になった)・日付・モデルを、**上書き版** `${XDG_CONFIG_HOME:-~/.config}/suno-artist-production/style-vocab.md` の該当行の備考に追記する。例: `実測 2026-08-01 (v5.5): 効いた`。行が無ければ表に追加してよい (列構成の契約は変えない)。

- 同梱版 (このファイル) には書き込まない。上書き版がまだ無ければ、このファイルを丸ごと複製して作り、先頭の調査日を追記日に更新する (調査日が同梱版より新しくないと実効版にならないため)。
- 上書き版への実測追記は、次回の update-spec (対象: style-vocab) で researcher の再調査結果と**マージして保持される** (実測は捨てられない)。

---

## 9. 出典一覧

**公式 (High。いずれも取得 2026-07-11)**
- https://help.suno.com/en/articles/5782849 (Detailed Style Instructions — 会話調・質感語を公式例文で使用) / https://help.suno.com/en/articles/5782593 (What's new in V4.5 — ムード・バイブの精密反映を明言) / https://help.suno.com/en/articles/5804417 (Creative Prompt Boosting = Enhance) / https://help.suno.com/en/articles/9010177 (Music Glossary — 非音楽語の公式リストは存在しない) / https://suno.com/community-guidelines (著名人・商標・著作物への言及禁止)

**コミュニティ・検証系 (Med 以下。いずれも取得 2026-07-11)**
- https://sunoaiwiki.com/resources/2024-05-13-list-of-metatags/ / https://sunoaiwiki.com/tips/2024-05-04-how-to-structure-prompts-for-suno-ai/ / https://hookgenius.app/suno-cheat-sheet/ / https://hookgenius.app/learn/suno-custom-mode-guide/ / https://hookgenius.app/learn/suno-style-tags-guide/ / https://hookgenius.app/learn/suno-content-filter-blocked-words/ / https://hookgenius.app/learn/suno-japanese-prompts/
- https://blakecrosley.com/guides/suno (情景語の翻訳原理) / https://roo.beehiiv.com/p/suno-v5-and-v5-5-prompts-why-it-ignores-half-your-words-and-how-to-fix-it (条件付けシグナル・長文圧縮) / https://freesongwritingtools.com/blog/why-suno-ignores-your-prompt/ (ムード重み推定) / https://jackrighteous.com/en-us/blogs/guides-using-suno-ai-music-creation/suno-prompt-contained-inappropriate-material (モデレーション誤爆)
- https://travisnicholson.medium.com/complete-list-of-prompts-styles-for-suno-ai-music-2024-33ecee85f180 / https://openmusicprompt.com/blog/suno-ai-metatags-guide / https://medium.com/@aitooldiscovery/suno-reddit-tips-and-prompts-what-r-sunoai-users-actually-do-65b59d51bcad (r/SunoAI 使用例まとめ) / https://james-palm.medium.com/suno-ai-japanese-music-prompts-city-pop-anime-ad914ef46d72 / https://sunostyles.com/blog/suno-style-prompts-guide / https://musicsmith.ai/blog/ai-music-generation-prompts-best-practices

**日本語圏 (Med 以下。いずれも取得 2026-07-11)**
- https://note.com/sora_papa/n/n19e20a9a19b4 (ジャンルタグ効き方の統制実験 — Kayōkyoku / J-pop / Min'yō) / https://note.com/kao_kaoru/n/n8897e816ab26 (英語「合言葉」まとめ) / https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q10324317420 (Style 欄の日本語可否) / https://writing-corp.co.jp/media/suno-ai-nihongo/ / https://gen-ai-note.hatenablog.com/entry/suno-prompt-writing / https://ai.suno.jp/prompt/ / https://shift-ai.co.jp/blog/22691/ / https://qiita.com/inukai-masanori/items/5369db77c63d7c8f615e

**調査上の限界**: Reddit 本体は取得不可 (403) のため r/SunoAI の知見は二次まとめ経由 (Med 止まり)。Suno 公式に非音楽語の体系的リストは無く、本辞典の「効く / 効かない」は原則コミュニティ検証ベース。日本語直書きの語単位検証は存在しないため全行「未検証」とした (§1)。
