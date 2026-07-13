---
description: 制作コア束ねの参照資料（songsmith が制作前に読む・非コマンド）
---

# production — 制作ノウハウ参照資料集 (制作コア)

このスキルはコマンドではなく、**制作エージェント (songsmith) が設計前に読む参照資料のコンテナ**です。songsmith は作曲・作詞・韻・タイトルを 1 起動で一括制作するため、必読資料を**役割ごとに 1 ファイルへ束ねて 1 回の Read で読めるようにしてあります** (読む回数を減らすための束ね。中身は原本と同一テキストで品質は不変)。

## 束ねファイル (references/)

| ファイル | 内容 (原本) | いつ読む |
|---|---|---|
| `references/write_core.md` | composing `02_style-assembly` + songwriting `01_song-structure` / `05_emotional-arc` / `06_language-ja` / `07_language-en` / `08_originality-checklist` / `11_title-craft` を連結 | **毎回必読** (1 Read)。作曲・作詞の骨格すべてここ |
| `references/rhyme_core.md` | songwriting `03_rhyme-and-rhythm` + `09_rhyme-advanced-ja` を連結 | **韻プロファイル heavy の日本語曲のみ**必読 (1 Read) |

- `write_core.md` は言語別 (06 日本語 / 07 英語) を両方含む。曲の言語に該当する節だけを使う。
- 束ねは `scripts/build_production_refs.py` が原本から生成する**自動生成物**。原本 (composing/songwriting の各 references) が単一の真実源。**束ねを直接編集せず**、原本を直して再生成する。

## 条件付き参照 (従来どおり、必要時に原本を個別に読む)

束ねに入れていない資料は、曲の性格に応じて**必要時だけ**原本ディレクトリから読みます (毎回は読まない)。パスは呼び出しプロンプトで渡されます。

| 資料 | 読む条件 |
|---|---|
| `composing/references/01_arrangement-craft.md` | セクション演出を作り込む曲、「アレンジが平板/もっと激しく」系の修正。迷ったら読む |
| `composing/references/03〜09` (ジャンルプレイブック) | 該当ジャンルの曲。**主 1 本 + 副 1 本まで** (composing/SKILL.md の運用規則に従う) |
| `songwriting/references/02_hook-design.md` | フック勝負の曲 (キャッチー狙い・ショート動画展開) |
| `songwriting/references/04_motif-and-lyric-devices.md` | モチーフの練りが要る曲 (世界観重視・物語性・バラード) |
| `songwriting/references/10_hiphop-genre-ja.md` | ジャンルが HIPHOP/ラップ系の曲 (作曲・作詞・韻の全工程で参照) |
| `composing/references/06_poetry-spoken.md` の「ことば側への申し送り」節 | 語り主導 (ポエトリー) の曲 |
| `composing/references/04_kpop.md` の「ことば側への申し送り」節 | K-POP 系の曲 |

## 使い方 (songsmith の読み順)

1. **write_core.md を 1 Read** で読む (作曲必読 02 + 作詞必読 01/05/06 または 07/08/11)。
2. 韻プロファイルが **heavy かつ日本語**なら **rhyme_core.md を 1 Read** で追加。
3. 曲の性格に該当する**条件付き参照**があれば、原本を必要な分だけ個別に読む (主 1 + 副 1 まで)。
4. suno-spec (実効パスは呼び出しプロンプト参照) は、使う節 (モデル / 上限 / スライダー定石 / Style 記法 / Persona 運用) に**限定して**読む。判断に迷う値が出たら該当節を追い読みする。

## この資料群の前提

- 文字数上限・メタタグ語彙・スライダー数値・モデル仕様は、すべて **suno-spec (実効パスは呼び出しプロンプト参照) が正**。束ね内の数値は設計の目安として扱う。
- 例文・Style 例・サンプル歌詞はすべて原本のための自作。実在アーティスト名・実在曲名は本文に書かない (原本の規範をそのまま継承)。
- 束ねの原本行き先・生成手順は `scripts/build_production_refs.py` を参照。
