#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""制作コア (production references) の束ねビルダー (suno-cowrite / D38)

制作エージェント (songsmith) が「毎回必読」する参照資料を、役割ごとに 1 ファイルへ
連結して 1 回の Read で読めるようにする。**原本 (skills/composing・skills/songwriting の
各 references) が単一の真実源**であり、この束ねファイルは原本からの自動生成物。中身は
原本と同一テキスト (品質不変・副作用ゼロ) で、読む回数だけを減らす。

使い方:
    python3 build_production_refs.py            # 束ねファイルを生成 (上書き)
    python3 build_production_refs.py --check    # 生成物が最新か検査 (CI/監査用。差分あれば exit 1)

原本を編集したら本スクリプトを再実行して束ねを更新する (束ねを直接編集しない)。
Python 3 標準ライブラリのみで動く。
"""

import argparse
import sys
from pathlib import Path

# プラグインルート = このスクリプト (scripts/) の 1 階層上
PLUGIN_ROOT = Path(__file__).resolve().parent.parent

# 束ね定義: 出力相対パス -> (見出し, [原本の相対パス, ...])。
# 原本の順序 = 制作エージェントが読む順序 (作曲必読 → 作詞必読)。
BUNDLES = {
    "skills/production/references/write_core.md": (
        "制作コア — 作編曲 + 作詞の必読 (毎回)",
        [
            "skills/composing/references/02_style-assembly.md",
            "skills/songwriting/references/01_song-structure.md",
            "skills/songwriting/references/05_emotional-arc.md",
            "skills/songwriting/references/06_language-ja.md",
            "skills/songwriting/references/07_language-en.md",
            "skills/songwriting/references/08_originality-checklist.md",
            "skills/songwriting/references/11_title-craft.md",
        ],
    ),
    "skills/production/references/rhyme_core.md": (
        "韻コア — 韻プロファイル heavy の曲でのみ必読 (日本語)",
        [
            "skills/songwriting/references/03_rhyme-and-rhythm.md",
            "skills/songwriting/references/09_rhyme-advanced-ja.md",
        ],
    ),
}

# 束ねファイル先頭に付ける警告ヘッダ (原本が真実源であることを明示)。
GENERATED_BANNER = (
    "<!-- 自動生成ファイル — 直接編集しないこと。\n"
    "     原本 (下記の各節の見出しに記載) を編集し、"
    "scripts/build_production_refs.py を再実行して更新する。\n"
    "     これは読む回数を減らすための束ね (D38)。中身は原本と同一テキスト (品質不変)。 -->"
)


def build_one(title, rel_sources):
    """1 つの束ねファイルの本文を生成して返す"""
    parts = [GENERATED_BANNER, "", f"# {title}", ""]
    parts.append(
        "この束ねは、制作エージェント (songsmith) が 1 回の Read で必読資料を読むための連結版です。"
        "各節は原本のフルテキストです。深追いが要る条件付き資料 (ジャンルプレイブック等) は"
        "従来どおり原本ディレクトリから必要時に個別に読みます。"
    )
    parts.append("")
    for rel in rel_sources:
        src = PLUGIN_ROOT / rel
        text = src.read_text(encoding="utf-8").rstrip("\n")
        parts.append("---")
        parts.append("")
        parts.append(f"<!-- 原本: {rel} -->")
        parts.append("")
        parts.append(text)
        parts.append("")
    return "\n".join(parts).rstrip("\n") + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="build_production_refs.py",
        description="制作コア (production references) を原本から束ねて生成する (D38)。",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="生成物が原本と一致しているか検査する (書き込まない。差分があれば exit 1)",
    )
    args = parser.parse_args(argv)

    stale = []
    for out_rel, (title, rel_sources) in BUNDLES.items():
        content = build_one(title, rel_sources)
        out_path = PLUGIN_ROOT / out_rel
        if args.check:
            current = out_path.read_text(encoding="utf-8") if out_path.exists() else None
            if current != content:
                stale.append(out_rel)
        else:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(content, encoding="utf-8")
            print(f"生成: {out_rel} ({len(content):,} 字 / 原本 {len(rel_sources)} 本)")

    if args.check:
        if stale:
            print("束ねが最新ではありません (原本編集後に再生成してください):", file=sys.stderr)
            for rel in stale:
                print(f"  - {rel}", file=sys.stderr)
            return 1
        print("束ねは最新です (原本と一致)")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
