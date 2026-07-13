---
description: Suno 仕様の参照資料コンテナ (実行フローを持つコマンドではない)。仕様本体は references/spec.md、Style 欄に効く非音楽語の辞典 (日本語の意図 → 英語記述子) は references/style-vocab.md。モデル選択・文字数上限・Advanced Options・メタタグ語彙・Style 記法・Persona/Voices/Custom Models・日本語入稿対策・プラン/商用権・API 状況を確認するときに読む。制作 (songsmith) は曲作りごとに必読 (作曲工程は全体、作詞工程はメタタグと日本語対策の節)、マネージャーは検証時に参照する。実効 spec / 実効 style-vocab の決め方 (ユーザー上書き版と同梱版の 2 層) と更新フロー (update-spec) への導線もここで定義する。
---

# Suno 仕様参照 — suno-spec

Suno のバージョン固有情報 (モデル名・文字数上限・メタタグ語彙・スライダー定石値など) を集約する参照資料コンテナである。これらの値をエージェント定義・コード・会話の記憶で判断してはならず、**必ず実効 spec を読んで従う** (ハードコード回避の原則)。

## ファイル構成

| ファイル | 内容 |
|---|---|
| `references/spec.md` | 仕様本体 (プラグインリリース時のスナップショット、9 セクション構成) |
| `references/style-vocab.md` | Style 語彙辞典 — Style 欄に効く非音楽語 (ムード・情景・質感・動作・メディア連想) の「日本語の意図 → 英語記述子」変換表。spec.md と同じ 2 層上書き対象 |
| `references/update-log.md` | 更新履歴 (追記専用、1 件 1 行。spec と style-vocab で共用) |

## 実効 spec の決め方 (2 層構造)

| 層 | パス | 性質 |
|---|---|---|
| 上書き版 | `${XDG_CONFIG_HOME:-~/.config}/suno-cowrite/suno-spec.md` | update-spec フローが保存する更新版。プラグイン更新で消えず、全アーティストで共有 |
| 同梱版 | `<プラグインルート>/skills/suno-spec/references/spec.md` | リリース時のスナップショット。**読み取り専用扱い (書き換えない)** |

**判定規則: 上書き版が存在し、その調査日が同梱版より新しければ上書き版が実効。なければ同梱版が実効。**

- 実効パスと鮮度 (例: 「spec 調査日: 2026-07-10 / 30 日経過」) は hook (`scripts/inject-manager-context.sh`) が**毎ターン注入する**。通常は注入済みの実効パスをそのまま読めばよい。
- 注入がない文脈で自前判定する場合は、両ファイルの先頭付近にある `調査日: YYYY-MM-DD` 行を比較する (ISO 形式のため文字列比較がそのまま新旧比較になる)。
- **契約**: spec ファイルは先頭付近に、行頭から装飾なしで `調査日: YYYY-MM-DD` の行を必ず持つ。hook と更新フローが機械抽出するため、この形式を変えない。
- 調査日から **60 日超過**の場合、studio 起動時にマネージャーが再調査 (update-spec) を提案する。
- **style-vocab.md も同じ 2 層構造・同じ判定規則・同じ調査日契約**で実効版を決める (上書き版: `${XDG_CONFIG_HOME:-~/.config}/suno-cowrite/style-vocab.md`。実効パスと鮮度は hook が spec と並べて毎ターン注入する)。ただし鮮度の声かけ閾値は spec と別で、調査日から **90 日超過**のときに再調査 (update-spec、対象: style-vocab) を提案する。

## 誰がいつ読むか

| 読む人 | タイミング | 読む範囲 |
|---|---|---|
| songsmith (作曲工程) | **曲作りごとに毎回** (モデル・Style・Exclude・スライダー・Persona 適用を決める前) | 全体。特に §1〜§3 (モデル/上限/設定値)・§5 (Style 記法)・§6 (Persona 運用) |
| songsmith (style-vocab) | Style のムード・情景・質感の枠を決めるとき | 通読しない。該当カテゴリ (§2〜§6) だけ拾い読み |
| songsmith (作詞工程) | 歌詞執筆と入稿版変換の前 | §4 (メタタグ語彙)・§7 (日本語入稿対策。日本語アーティストのみ) |
| マネージャー | song.json の検証時、プラン・商用権に関わる提案時 | §2 (上限)・§3 (設定値)・§8 (プラン/商用権) |

- spec.md のセクション構成: §1 モデル一覧と使い分け / §2 Custom Mode フィールドと文字数上限 / §3 Advanced Options / §4 メタタグ語彙一覧 / §5 Style 記述ベストプラクティス / §6 Persona・Voices・Custom Models / §7 日本語入稿対策 / §8 プラン別制限と商用権 / §9 API 状況。
- サブエージェントはプラグインのファイルパスを知らない。マネージャーは songsmith の起動プロンプトに**実効 spec の絶対パス**を必ず含める。

## 更新フロー (概要)

詳細手順は update-spec スキル (`/suno-cowrite:update-spec`) を参照。style-vocab の更新も同スキルの「対象の決定」に従う (researcher は対象別に実行)。以下は spec の例。

1. マネージャーが researcher を起動する (現行 spec の全文と「公式一次情報を優先、各項目に確度と取得日を付す」という調査規約をプロンプトに含める)。
2. researcher が差分調査を行い、差分サマリ (何が変わったか) と更新版 spec 全文を返す。
3. マネージャーが**上書き版パスへ保存**し (同梱版は書き換えない)、ユーザー設定ディレクトリ側の `update-log.md` (無ければ `references/update-log.md` を複製して作成) に 1 行追記して、P に差分を報告する。
4. 差分が文字数上限・既定モデルに触れる場合は、`scripts/validate_song.py` の定数と artist.yaml の `preferred_model` の見直しを P に提案する (自動書き換えはしない)。
