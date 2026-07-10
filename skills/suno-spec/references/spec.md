# Suno 仕様書 — 実務リファレンス (同梱スナップショット)

調査日: 2026-07-10
<!-- 上の「調査日: YYYY-MM-DD」行は hook が上書き版との新旧比較に機械抽出する。位置と形式を変えないこと -->

**要旨**: 現行フラッグシップは **v5.5** (2026-03-26、Pro/Premier 限定)。Free は v4.5-all のみ。Custom Mode 上限は **Style 1,000 字 / Lyrics 5,000 字 (実用 3,000 字) / Title 100 字**。旧 Persona は 2026-03 に **Voices メニューへ統合** (Style Persona / Voice の 2 系統)。継続プロデュースの主軸は **Style Persona + Custom Models (6 曲〜)**。公式 API は**未公開**。

- 出典はすべて 2026-07-10 取得。確度 (High / Med-High / Med / Med-Low) は原調査レポートの評価を踏襲。
- 読み方: composer は全節必読 (特に §1〜§3・§5・§6)。lyricist は §4・§7。マネージャーは §2・§3・§8。

---

## 1. モデル一覧と使い分け

| バージョン | リリース | 要点 | 使い分けの目安 |
|---|---|---|---|
| V3.5 | 2024 夏 | 初回生成 最大 4 分 | レガシー |
| V4 | 2024-11 | ボーカル品質向上。Extend / Cover / Persona が柱 | 旧 Persona 資産互換、v4 声質の好み |
| V4.5 | 2025-05-01 | **初回生成 最大 8 分**、追従性向上、Enhance、Cover × Persona 併用可 | 8 分曲、旧曲との質感統一 |
| V4.5+ | 2025-07 | Add Vocals / Add Instrumental (既存音源への追加) | 既存音源起点のワークフロー |
| V5 | 2025-09-23 | 音質の大幅向上、旧曲の Remaster | 個人化機能が不要な純粋生成の安定株 |
| v4.5-all | 2025-10-21 | v4.5 ベースの無料枠向け | **Free 唯一のモデル**。無料検証用 |
| **V5.5** | 2026-03-26 | 最も表現力の高いモデル。Voices / Custom Models / My Taste を同時投入 | **現行フラッグシップ。デフォルト推奨** |

- V4〜V5.5 は有料プラン (Pro/Premier) で選択可 (§8)。「使い分けの目安」列は非公式検証の総合 (Med)。

確度: モデル一覧・時期 = **High** (公式 3 ソース一致) / 使い分け = **Med** (非公式)。
出典 (取得 2026-07-10): https://help.suno.com/en/articles/5782721 (公式) / https://suno.com/release-notes (公式) / https://suno.com/blog/v5-5 (公式) / https://help.suno.com/en/articles/5782593 (公式) / https://suno.hk/blog/suno-v55-comprehensive-comparison/ / https://moelueker.com/blog/suno-v5-vs-v4-5-what-actually-changed-and-when-to-use-each / https://techjacksolutions.com/ai-tools/suno/suno-v5/

---

## 2. Custom Mode フィールドと文字数上限

| フィールド | v4.5 以降 | v4 以前 | 実務メモ |
|---|---|---|---|
| Style of Music | **1,000 字** | 200 字 | カンマ区切りタグ。実用 15〜30 語 = 10 タグ前後 (§5) |
| Lyrics | **5,000 字** | 3,000 字 | **実用は約 3,000 字まで** (超過で歌唱が駆け足になる報告) |
| Title | **100 字** | 80 字 | — |
| Exclude Styles | 上限の公式明記なし | 同左 | **5 項目程度までが安定** |

- 上限値は複数サードパーティで一致するが**公式明文の確認なし**。文字の数え方も未確認のため、上限ぎりぎりの入稿は避ける。
- Free (v4.5-all) の上限が 1,000 字系か 200 字系かは公式明記なし (要実機確認)。

確度: **Med-High**。
出典 (取得 2026-07-10): https://hookgenius.app/learn/suno-character-limits/ / https://hookgenius.app/learn/suno-custom-mode-guide/ (非公式)

---

## 3. Advanced Options とスライダー定石値

| 項目 | 仕様 | 定石・注意 |
|---|---|---|
| Exclude Styles | 除外したい楽器・スタイル・ボーカル種をカンマ区切り指定 | **Pro/Premier 限定**。Style 欄の否定形より確実 (§5) |
| Vocal Gender | Male / Female で主ボーカルの性別を直接指定 | — |
| Weirdness (0–100%) | ジャンル慣習からの逸脱許容度 | 0–20 = 定石的・商業的 / **40–60 = 推奨デフォルト帯 (初期値 50)** / 60–80 = 実験的 / **81 以上 = 破綻 (グリッチ) 領域** |
| Style Influence (0–100%) | Style タグへの追従度 (低 = ヒント扱い / 高 = ほぼ厳守) | **高追従 × 5〜8 タグに絞った Style 欄**が定石。初期値 50〜70 |
| Audio Influence (0–100%) | アップロード音源 (Cover / Sample / Add Vocals / Voices) の影響度。音源入力時のみ表示 | Sample 用途は約 55% がスイートスポット。**Style Influence と両方 100% は競合して破綻** |

- **Instrumental トグル** — 確実なインスト化は「トグル ON + Lyrics `[Instrumental]` + Exclude `vocals`」の**三重指定**が定番。
- **Enhance ボタン** (v4.5〜) は雑なタグから Style を自動拡張する。プラグイン出力を貼る運用では競合に注意。
- Personas / Voices セレクタは Lyrics 欄直上 (挙動は §6)。**My Taste は明示した Style・メタタグを上書きしない** (v5.5、全ユーザー)。
- Studio の拍子設定 (3/4 等) は編集グリッド用で、**生成モデルは条件付けしない**。

確度: 機能の存在・提供条件 = **High** (公式) / スライダーの % 閾値 = **Med** (コミュニティ検証値、モデル更新で変わりうる)。
出典 (取得 2026-07-10): https://suno.com/release-notes/exclude-styles (公式) / https://help.suno.com/en/articles/3161921 (公式) / https://acetaggen.com/blog/weirdness-exclude-styles-reference-suno-advanced-parameters / https://blakecrosley.com/guides/suno / https://jackrighteous.com/en-us/blogs/guides-using-suno-ai-music-creation/how-to-change-voices-in-suno-and-use-your-own

---

## 4. メタタグ語彙一覧 (歌詞欄)

v5.5 まで語彙・処理系に変更なし。

| 分類 | タグ |
|---|---|
| 構造 | `[Intro]` `[Verse]` / `[Verse 1]` `[Verse 2]` `[Pre-Chorus]` `[Chorus]` `[Post-Chorus]` `[Bridge]` `[Breakdown]` `[Build]` / `[Build-Up]` `[Drop]` `[Hook]` `[Interlude]` `[Outro]` `[End]` |
| インスト指示 | `[Instrumental]` `[Instrumental Intro]` `[Instrumental Break]` `[Guitar Solo]` `[Piano Solo]` `[Drum Solo]` `[Bass Solo]` `[Saxophone Solo]` `[Synth Solo]` `[Strings Rise]` `[Percussion Break]` |
| ボーカル指示 | `[Male Vocal]` `[Female Vocal]` `[Duet]` `[Choir]` `[Harmony]` `[Rap]` `[Spoken Word]` `[Whisper]` `[Scream]` `[Ad-lib]` `[Humming]` `[Backing Vocals]` |
| ダイナミクス/制御 | `[Fade In]` `[Fade Out]` `[Silence]` `[Crescendo]` `[Decrescendo]` `[Tempo: slow]` `[Key Change]` |

- タグは**編曲指示として処理され歌われない** (稀に読み上げ事故あり)。大文字小文字は不問。番号付き `[Verse 1]` `[Verse 2]` は別展開を、同一歌詞の `[Chorus]` 反復はメロディの反復を誘導する。
- **パラメータ付きタグ構文** `[Bridge: stripped down, piano only, vulnerable vocals]` — Style 設定を変えずに**セクション単位で音作りを指示**できる、実用上最も強力な制御手段。
- タグを使わないと歌詞が一塊で処理され構成が崩れやすい。装飾目的の括弧 `()` はリフレイン扱いされうる (日本語の括弧対策は §7)。

確度: **Med** (複数ガイド一致のコミュニティ検証ベース。細部はモデル更新で変わりうる)。
出典 (取得 2026-07-10): https://blakecrosley.com/guides/suno / https://sunometatagcreator.com/metatags-guide / https://jackrighteous.com/en-us/pages/suno-ai-meta-tags-guide / https://qiita.com/inukai-masanori/items/5369db77c63d7c8f615e

---

## 5. Style 記述ベストプラクティス

- **並び順**: `ジャンル → ムード → 楽器 → ボーカル → プロダクション` (テンポ感・ミックス意図を適宜挟む)。
- **形式**: 文章ではなく**カンマ区切りの記述子**。「**1 行に収まる密度、10 タグ前後**」が共通見解 (少なすぎると自由すぎ、多すぎると競合して濁る)。
- 良い例: `dreamy bass house, dreamstep influence, 126 bpm feel, deep sub bass, crisp drums, wide synth pads, airy topline, modern clean mix, festival-ready drop, emotional but restrained`

| 効く要素 | 例 | 備考 |
|---|---|---|
| ジャンル + サブジャンル | `city pop, shoegaze, trap` | 最重要。先頭に置く |
| テンポ感 | `slow, upbeat, 126 bpm feel` | **BPM は目安扱いで固定されない**。`126 bpm feel` 表記が安全 |
| 楽器 | `acoustic guitar, synth pad, brass` | 示唆であり保証ではない |
| ボーカル質感 | `raspy male vocals, ethereal female vocals` | Vocal Gender 設定と併用 (§3) |
| プロダクション | `lo-fi, polished, raw, clean mix` | 質感全般に効く |
| ムード / 年代 | `melancholic, euphoric, 80s, 90s grunge` | 年代指定はその時代の慣習を引き出す |

| 効かない / 非推奨 | 理由 |
|---|---|
| 実在アーティスト名 (`sounds like Adele`) | 不安定でモデレーション対象。**特徴を形容詞に分解**して書く |
| 技術的ミキシング用語 (`sidechain compression`) | 無視される |
| Style 欄での否定形 (`no drums`) | 不安定。**Exclude Styles を使う** (§3) |
| ストーリー・歌詞内容の混入 | Style 欄は音響指示専用。歌詞的内容は Lyrics 欄へ |

- 日本語曲でも **Style 欄は英語表記が推奨** (`Japanese city pop` / `J-pop, female vocal` など)。精密な Style には **Style Influence を高く**、探索目的なら低く。

確度: **Med** (複数の独立ガイドで一致するコミュニティ知見)。
出典 (取得 2026-07-10): https://blakecrosley.com/guides/suno / https://howtopromptsuno.com/making-music / https://hookgenius.app/learn/suno-custom-mode-guide/ / https://hookgenius.app/learn/best-suno-settings-explained/ / https://genai-ai.co.jp/ai-kanri/blog/cc-suno-ai-japanese-music/

---

## 6. Persona / Voices / Custom Models のライフサイクル

2026-03-26 に Create メニューの Personas ボタンは **Voices メニューへ統合**。位置づけは「**Persona = アーティストの同一性の錨 / Style 欄 = 曲ごとのプロデューサー指示**」。

| 系統 | ラベル | 内容 |
|---|---|---|
| **Style Persona** (旧 Persona、2024-10 導入) | `(style)` | 既存の **Suno 生成曲**から「声質 + スタイル + 雰囲気」を保存して新曲で再利用 |
| **Voice** (v5.5 新機能) | `(voice)` | **自分の歌声**を録音/アップロードしてクローンし、ボーカルに使う |

### Style Persona (アーティスト運用の主軸)

| 項目 | 要点 |
|---|---|
| 作成 | 対象曲の More Actions (⋯) → Create → **Make Persona** → 名前 / アバター / 説明文。**Pro/Premier 限定**。**Suno 生成曲が必要** (音源アップロードからは作れない) |
| 公開設定 | **デフォルトは Public** (他ユーザーが利用可能 + プロフィールへリンクバック)。**作成時にトグルで Private 化する** — 本プラグインは Private 推奨 |
| 利用 | Custom Mode の Lyrics 欄直上のセレクタで選択 → スタイル記述が **Style 欄に自動挿入** (消して曲ごとの演出タグへ書き換え可)。クレジットは通常生成と同じ。Cover × Persona 併用可 (v4.5〜)。保管はライブラリの Personas タブ |
| 安定性 | **元曲とジャンルが近いほど安定** (lo-fi 由来はメタルで崩れやすい)。Style 欄に矛盾する指示を詰めると一貫性が落ちる |

### Voice (v5.5 専用)

| 項目 | 要点 |
|---|---|
| 作成 | ライブラリの曲から Create > Voice、または録音/アップロード。**モデルは v5.5 選択が必須**。読み上げフレーズによる本人確認あり |
| 権限・品質 | **完全プライベート** (本人のみ使用可、共有機能は開発中)。クリーンな**アカペラ音源** + Audio Influence 調整 (§3) で品質向上 |
| 制限 | **Pro/Premier・18 歳以上・一部地域は利用不可** |

### Custom Models / My Taste

- **Custom Models**: 自作カタログ**最低 6 トラック**で v5.5 を自分のスタイルにチューニング。**Pro/Premier で最大 3 個**。
- **My Taste**: 全ユーザー。好みを学習して薄いプロンプト時の既定を寄せる。明示プロンプトを上書きしない。

### 成長パス (継続プロデュースの型)

1. 1 曲目の採用テイクから **Style Persona を Private で作成**し、Persona 名・元曲 URL/ID・公開設定をアーティスト定義に永続化する。
2. 通常曲は Persona 適用 + Style 欄は曲ごとの演出差分。**基準ジャンル帯を大きく外れる曲は Persona 非適用か新 Persona 作成**を検討する (ジャンル漂流対策)。
3. カタログが **6 曲**を超えたら **Custom Models 化**を検討する。
4. 本人の実声を使う運用なら **Voices** を使う。

確度: 公式記述部分 (作成手順・公開設定・提供条件) = **High** / 安定性など実用上の性質 = **Med**。作成可能数の上限など一部は公式未記載。
出典 (取得 2026-07-10): https://suno.com/blog/personas (公式) / https://help.suno.com/en/articles/3484161 (公式) / https://help.suno.com/en/articles/11362433 (公式 Voices FAQ) / https://suno.com/blog/v5-5 (公式) / https://jackrighteous.com/en-us/blogs/guides-using-suno-ai-music-creation/suno-ai-personas-update-dec-2025-what-changed-how-to-use-it / https://songsmith.studio/blog/suno-personas-guide

---

## 7. 日本語入稿対策

| 問題 | 対策 |
|---|---|
| 多読み漢字の誤読 (「明日」→ あす/あした) | 意図した読みの**ひらがな表記に統一** (「明日は」→「あすは」)。最初からひらがな/ローマ字が安全 |
| 助詞「は」「へ」「を」の発音事故 | **助詞だけローマ字化**: 「私は」→「わたし wa」/「君を」→「きみ wo」/「〜へ」→「e」 |
| ルビ・括弧書き | 括弧はリフレイン (コーラス反復) として解釈されうる。**入稿版に括弧を残さない** |
| 歌詞量とテンポの不整合 | バラードに詰めると早口化、速い曲で少ないと早終了。**短めから始めて調整**が定石 |

- **Style 欄は英語、構成タグも英語、歌詞本文だけ日本語** — この分業が最も安定 (§5)。
- 生成ごとの揺らぎが大きく、**修正対象を 1 箇所ずつ決めて再生成を回す**運用が前提。日本語曲はクレジット消費が嵩みやすい (仕上げまで 20〜100 生成の一般報告)。
- v3 → v4 で日本語は大幅改善。v5 は改善報告があるが定量比較の一次情報なし。**v5.5 の日本語発音の体系評価は未発見** (未取得事項) → 対策表記は引き続き適用し、モデル更新ごとに再検証する。

確度: 対策テクニック = **Med** (多数の独立した日本語ソースで一致、公式情報なし) / バージョン間比較 = **Med-Low** (体系的一次情報なし)。
出典 (取得 2026-07-10): https://qiita.com/inukai-masanori/items/5369db77c63d7c8f615e / https://genai-ai.co.jp/ai-kanri/blog/cc-suno-ai-japanese-music/ / https://shift-ai.co.jp/blog/15829/ / https://note.com/hiro_seki/n/n352c480453f5 / https://gen-ai-note.hatenablog.com/entry/suno-japanese-guide

---

## 8. プラン別制限と商用権の罠

| 項目 | Free | Pro | Premier |
|---|---|---|---|
| 料金 | $0 | **$10/月** (年払い実質 $8/月) | **$30/月** (年払い実質 $24/月) |
| クレジット | **50/日** (毎日リセット ≒ 10 曲/日) | **2,500/月** (繰越なし) | **10,000/月** (繰越なし) |
| 生成コスト | 1 生成 = 10 クレジットで 2 バリエーション (実質 5/曲) | 同左 | 同左 |
| 使えるモデル | **v4.5-all のみ** | v4 / v4.5 / v4.5+ / v5 / **v5.5** | Pro と同じ |
| **商用利用** | **不可** (個人・非商用のみ) | **可** (加入中に作った曲) | **可** (同左) |
| オーディオアップロード | 最大 8 分 | 最大 30 分 | 最大 30 分 |
| ステム分離 | なし | 2 方式 | **3 方式** (Advanced Split ≒ 約 100 楽器) |
| Voices / Custom Models (v5.5) | 不可 | **可** (Custom Models 最大 3) | **可** (同左) |
| Suno Studio (マルチトラック DAW) | 不可 | 不可 | **可** (Premier 限定) |

> **商用権の罠**: 商用権は「**その曲を作った時点のプラン**」に紐づく。**Free 時代に作った曲は、後で Pro に上げても商用化できない**。商用リリース前提の運用ではこの警告の提示が必須。

- Exclude Styles・v5.5・Persona 作成・商用利用はすべて **Pro 以上**が前提 (本プラグインは Pro/Premier 前提)。

確度: **High** (公式料金ページ + 複数独立ソース一致。月払い/年払い表示の混在にのみ注意)。
出典 (取得 2026-07-10): https://suno.com/pricing (公式) / https://margabagus.com/suno-pricing/ / https://dynamoi.com/learn/ai-music-distribution/suno-commercial-rights-explained / https://gptprompts.ai/suno-pricing

---

## 9. API 状況

- **公式 API は未公開**。2026-07-01 に開発者 API のパートナープログラム募集開始が発表されたのみで (「少数の厳選パートナーから慎重に始める」方針)、**公開時期は未発表**。
- 当面の正攻法は **suno.com の Web UI に貼り付けるプロンプト/設定値の生成**。将来の接続に備えて出力は JSON 等で構造化しておく (本プラグインの song.json)。
- サードパーティ API (sunoapi.org / gcui-art/suno-api / 各種アグリゲータ) は**規約違反・アカウント BAN・法的グレーのリスク**が指摘されており、商用プロダクトの基盤には不適。

確度: パートナープログラム発表 = **High** (複数の独立報道で一致) / 非公式 API のリスク評価 = **Med**。
出典 (取得 2026-07-10): https://www.musicbusinessworldwide.com/suno-explores-developer-api-seeking-apps-that-unlock-experiences-generative-music-makes-possible-for-the-first-time/ / https://www.digitalmusicnews.com/2026/07/03/suno-is-opening-an-api-partner-program/ (本文 403 のため見出し + 検索スニペットで確認) / https://docs.sunoapi.org/ / https://musicgpt.com/blog/suno-api / https://aimlapi.com/blog/the-suno-api-reality
