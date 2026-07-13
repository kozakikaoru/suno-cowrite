#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""作品版歌詞 → Suno 入稿版歌詞 変換スクリプト (suno-cowrite)

日本語の「作品版歌詞」(漢字かな交じり + 構成タグ) を、Suno 入稿版歌詞
(かな主体 + 構成タグ) へ決定論的に機械変換する。作詞家が 2 版を手で書く
負担を無くすためのヘルパー。Python 3 標準ライブラリのみで動く。

変換の正典は skills/songwriting/references/06_language-ja.md 第 2 部 R1〜R9。
辞書が必要な R2 (全漢字→かな) は「ルビ注釈」方式で吸収する — 作者が作品版で
難読・当て字・多読み漢字に読みを与え、本スクリプトはそのルビを畳んで
「よみ」だけを残す。ルビの無い漢字は残存漢字チェック (手順 7) で拾い、作者へ
「ルビを足して再実行」を促す。

# 行構造の保存 (三原則 3)
1 行 → 1 行の写像。行の分割・結合・並べ替えは一切しない (行構造 = 譜割り)。
入力の行数・行順・末尾改行をそのまま保つ。

# 変換の適用順 (1 行ごと)
  0. タグ行 (^\\s*\\[.*\\]\\s*$) は一切変換せず素通し (R9)。行内の [ ... ] も
     内部を変換しない (番兵にマスクし、全変換後に原文どおり復元する)
  1. 全角→半角の正規化 (全角数字 ０-９ / 全角空白)
  2. ルビ注釈の畳み込み (R1/R2 の作者判断ぶんを吸収)
  3. 記号・括弧の排除 (R4/R7)、！→! ？→? (長音「ー」は残す)
  4. 助詞のローマ字化 (R3、は→wa へ→e を→wo)
  5. 数字の読み下し (R5、算用数字 + 漢数字、万・億対応)
  6. スペース整理 (R8、連続半角空白を 1 つに・行頭行末を除去)
  7. 残存漢字チェック (R2 完全性の担保、WARN のみ・終了コードは 0)

  ※ R 表の番号では R5(数字) → R3(助詞) の順だが、本実装は R3 を先に適用する。
    数詞リーダの出力に「は」を含む語 (8→はち, 800→はっぴゃく) があり、数字を先に
    開くと生成された「は」を助詞と誤認して壊すため (例: よる8じ→よるはちじ を
    「よる wa ちじ」にしない)。この 1 点だけ順序を入れ替える意図的な判断。

# ルビ注釈記法 (作者が作品版でこう読みを付ける)
  括弧記法  漢字(よみ) / 漢字（よみ） / 漢字《よみ》
            base = 「(」直前の連続漢字列 (不規則な数量語は漢数字で書く: 二人(ふたり))
            しない (通常の括弧として手順 3 で除去)。数字・英字に読みを付けたい
            ときは縦棒記法を使う
  縦棒記法  非空白｜よみ / 非空白|よみ
            base = 直前の連続非空白列 (数字・英字にも掛けられる。例 2049｜にせん…)
  「よみ」がかな (ひらがな/カタカナ/長音) のみのとき畳む。よみに漢字を含む/空の
  ときは畳まず、括弧として手順 3 で除去する。畳み込みでは base を捨て「よみ」だけ残す。
    例) 街(まち) → まち  /  明日(あした) → あした  /  2049｜にせんよんじゅうきゅう → にせんよんじゅうきゅう

# 助詞ヒューリスティック (R3)
  は/へ/を の直前の文字が日本語文字 (かな・漢字・長音符) のとき助詞とみなし
  wa/e/wo に変換し、前後に半角スペースを 1 つ入れる (連続空白は手順 6 で畳み、
  行末なら後ろの空字は除去される)。語頭 (直前が空白・記号・タグ・行頭・数字) の
  は/へ/を は変換しない。「を」もこの一様な規則で扱う (日本語で「を」はほぼ常に
  格助詞のため、直前が日本語文字ならほぼ確実に助詞になる)。
  既知の誤変換パターン (作者はカタカナ化や字空けで回避でき、--report で列挙される):
    - 語中の は/へ/を: 「はやく」「へや」「このへや」の は/へ は、直前が日本語文字だと
      助詞と誤認しうる (「この e や」等)。回避: 該当語をカタカナ化 (ヘヤ) する
    - 字空けを挟んだ助詞: 「きみ を」のように助詞の直前に空白があると直前が
      日本語文字でないため変換されない。作者が助詞を語に密着させれば変換される
    - 算用数字直後の は: 「2は」は数字を開く前の判定で直前が日本語文字でないため
      変換されない (「には」のまま)。回避: 読みを「にわ」等で直接書く

# 数詞リーダ (R5)
  0〜999,999,999 を万・億対応で開く。よくある連濁は内蔵表で対応する:
    百: 300→さんびゃく 600→ろっぴゃく 800→はっぴゃく
    千: 3000→さんぜん 8000→はっせん
  算用数字は連続する [0-9] だけを開き、直後の助数詞漢字 (人・回・歳・番・度・年・
  月・日・円・万 等) は残す (「2人」→「に人」。人は残存漢字チェックで拾い、作者が
  ルビで上書きできる)。漢数字は numeral 列 [〇零一二三四五六七八九十百千万億] を
  整数化して開く。
  簡略化した判断 (報告済み):
    - 一千 は整数正規化のため「せん」と読む (漢字表記の「いっせん」とは区別しない)。
      2049→にせんよんじゅうきゅう と一貫させるための割り切り
    - 先行する数字の無い単独の 万・億 は開かず残す (助数詞的用法とみなし、残存
      漢字チェックで拾う)。例: 100万 → ひゃく万 (万は残存として報告)

使い方:
    python3 build_submission_lyrics.py [--in PATH|-] [--out PATH|-] [--report]
    python3 build_submission_lyrics.py --json song.json [--report]
    python3 build_submission_lyrics.py --selftest

終了コード:
    0 = 変換成功 (残存漢字があっても 0)
    1 = --selftest 失敗
    2 = 引数エラー / JSON 不正 / lyrics_display 欠落
"""

import argparse
import json
import re
import sys

# =============================================================================
# 文字クラス・正規表現
# =============================================================================

# 漢字の範囲 (ルビ base と残存漢字チェックで共通に使う。CJK 統合漢字 + 々〆〤)
_KANJI = r"一-鿿々〆〤"
_KANJI_RE = re.compile("[" + _KANJI + "]")

# ルビの「よみ」に許すかな (ひらがな/カタカナ/長音符/かな繰り返し記号)
_KANA = r"ぁ-ゖァ-ヶーゝゞヽヾｰ"

# 行全体が構成タグの行 (素通し)。行内タグ (マスク対象、1 行内で閉じるもの)
_FULL_TAG_RE = re.compile(r"^\s*\[.*\]\s*$")
_INLINE_TAG_RE = re.compile(r"\[[^\[\]\n]*\]")
_TAG_SENTINEL = chr(0xE000)   # マスク用の番兵 (漢字・かな・数字・記号・空白のいずれでもない私用領域文字)

# ルビ注釈: 括弧記法 (base = 「(」直前の連続漢字列、よみ = かなのみ)。
# base は漢字のみにする — 数字+漢字で不規則に読む語 (2人=ふたり) は、数字が読みに
# 含まれるか (ふたり) 単独で読むか (2時→に+じ) が曖昧なため、数字を base に含めない。
# 不規則な数量語はアーティストが漢数字で書いてルビを付ける規約 (二人(ふたり))。
_RUBY_BRACKET_RE = re.compile(
    r"[" + _KANJI + r"]+"
    r"(?:\((?P<y1>[" + _KANA + r"]+)\)"
    r"|（(?P<y2>[" + _KANA + r"]+)）"
    r"|《(?P<y3>[" + _KANA + r"]+)》)"
)
# ルビ注釈: 縦棒記法 (base = 直前の連続非空白列、よみ = かなのみ)
_RUBY_PIPE_RE = re.compile(
    r"[^\s｜|" + _TAG_SENTINEL + r"]+(?:｜|\|)(?P<y>[" + _KANA + r"]+)"
)

# 除去する記号・括弧 (長音「ー」は残す)
_REMOVE_CHARS = set("「」『』（）()《》【】〈〉…―〜、。・；：,")

# 全角→半角の変換表 (全角数字 ０-９ と全角空白)
_WIDTH_TABLE = {0x3000: ord(" ")}
for _i in range(10):
    _WIDTH_TABLE[0xFF10 + _i] = ord("0") + _i

# 助詞ローマ字化の対応
_PARTICLE_ROMAN = {"は": "wa", "へ": "e", "を": "wo"}

# 漢数字 → 整数
_KANJI_DIGIT = {"〇": 0, "零": 0, "一": 1, "二": 2, "三": 3, "四": 4,
                "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_KANJI_SMALL_UNIT = {"十": 10, "百": 100, "千": 1000}
_KANJI_BIG_UNIT = {"万": 10000, "億": 100000000}
_KANJI_NUM_RE = re.compile(r"[〇零一二三四五六七八九十百千万億]+")
_ASCII_NUM_RE = re.compile(r"[0-9]+")

# 数詞の読み表 (連濁を織り込む)
_ONES = {1: "いち", 2: "に", 3: "さん", 4: "よん", 5: "ご",
         6: "ろく", 7: "なな", 8: "はち", 9: "きゅう"}
_TENS = {1: "じゅう", 2: "にじゅう", 3: "さんじゅう", 4: "よんじゅう", 5: "ごじゅう",
         6: "ろくじゅう", 7: "ななじゅう", 8: "はちじゅう", 9: "きゅうじゅう"}
_HUNDREDS = {1: "ひゃく", 2: "にひゃく", 3: "さんびゃく", 4: "よんひゃく", 5: "ごひゃく",
             6: "ろっぴゃく", 7: "ななひゃく", 8: "はっぴゃく", 9: "きゅうひゃく"}
_THOUSANDS = {1: "せん", 2: "にせん", 3: "さんぜん", 4: "よんせん", 5: "ごせん",
              6: "ろくせん", 7: "ななせん", 8: "はっせん", 9: "きゅうせん"}

_READ_MAX = 999_999_999   # 数詞リーダの対応上限 (これを超える数字列は開かず残す)


# =============================================================================
# 数詞リーダ (R5)
# =============================================================================

def _read_below_10000(n):
    """0 < n < 10000 の整数をかなに開く (連濁対応)"""
    out = []
    if n >= 1000:
        out.append(_THOUSANDS[n // 1000])
        n %= 1000
    if n >= 100:
        out.append(_HUNDREDS[n // 100])
        n %= 100
    if n >= 10:
        out.append(_TENS[n // 10])
        n %= 10
    if n:
        out.append(_ONES[n])
    return "".join(out)


def read_number_kana(n):
    """0〜999,999,999 の整数をかなに開く (万・億対応)"""
    if n == 0:
        return "ぜろ"
    out = []
    oku = n // 100_000_000
    man = (n % 100_000_000) // 10_000
    rest = n % 10_000
    if oku:
        out.append(_read_below_10000(oku) + "おく")
    if man:
        out.append(_read_below_10000(man) + "まん")
    if rest:
        out.append(_read_below_10000(rest))
    return "".join(out)


def _kanji_to_int(s):
    """漢数字列を整数へ。解釈できなければ (単独の万/億など) None を返す"""
    if not s:
        return None
    # 単位語 (十百千万億) を含まない場合は位取りの数字列 (二〇四九 = 2049) とみなす
    has_unit = any(c in _KANJI_SMALL_UNIT or c in _KANJI_BIG_UNIT for c in s)
    if not has_unit:
        val = 0
        for c in s:
            if c not in _KANJI_DIGIT:
                return None
            val = val * 10 + _KANJI_DIGIT[c]
        return val
    total = 0     # 万・億で締めた確定分
    section = 0   # 万未満の現セクション
    current = 0   # 単位待ちの数字
    for c in s:
        if c in _KANJI_DIGIT:
            current = current * 10 + _KANJI_DIGIT[c]
        elif c in _KANJI_SMALL_UNIT:
            section += (current if current else 1) * _KANJI_SMALL_UNIT[c]
            current = 0
        elif c in _KANJI_BIG_UNIT:
            base = section + current
            if base == 0:
                return None   # 先行数字の無い単独の 万・億 は開かない
            total += base * _KANJI_BIG_UNIT[c]
            section = 0
            current = 0
        else:
            return None
    return total + section + current


def _open_numbers(text):
    """算用数字と漢数字をかなに開く (R5)。解釈不能・上限超過はそのまま残す"""
    def ascii_repl(m):
        val = int(m.group(0))
        if val > _READ_MAX:
            return m.group(0)
        return read_number_kana(val)

    def kanji_repl(m):
        val = _kanji_to_int(m.group(0))
        if val is None or val > _READ_MAX:
            return m.group(0)
        return read_number_kana(val)

    text = _ASCII_NUM_RE.sub(ascii_repl, text)
    return _KANJI_NUM_RE.sub(kanji_repl, text)


# =============================================================================
# 各変換ステップ
# =============================================================================

def _is_japanese_char(ch):
    """かな・漢字・長音符など日本語の文字か (助詞判定の直前文字チェック用)"""
    if not ch:
        return False
    o = ord(ch)
    if 0x3041 <= o <= 0x309F:      # ひらがな
        return True
    if 0x30A1 <= o <= 0x30FF:      # カタカナ + 長音符
        return True
    if 0x4E00 <= o <= 0x9FFF:      # CJK 統合漢字
        return True
    return ch in "々〆〤ｰ"


def _mask_tags(line):
    """行内の [ ... ] を番兵に置き換え、原文リストを返す (順序保持)"""
    tags = []

    def repl(m):
        tags.append(m.group(0))
        return _TAG_SENTINEL

    return _INLINE_TAG_RE.sub(repl, line), tags


def _restore_tags(text, tags):
    """番兵を原文タグへ順番に戻す"""
    it = iter(tags)
    return re.sub(re.escape(_TAG_SENTINEL), lambda m: next(it), text)


def _fold_ruby(text, stats):
    """ルビ注釈を畳み込み、base を捨てて「よみ」だけ残す (R1/R2)"""
    def repl_bracket(m):
        stats["ruby"] += 1
        return m.group("y1") or m.group("y2") or m.group("y3")

    def repl_pipe(m):
        stats["ruby"] += 1
        return m.group("y")

    text = _RUBY_BRACKET_RE.sub(repl_bracket, text)
    return _RUBY_PIPE_RE.sub(repl_pipe, text)


def _strip_symbols(text):
    """記号・括弧を除去し、！？ を半角化する (R4/R7)。長音「ー」は残す"""
    out = []
    for ch in text:
        if ch in _REMOVE_CHARS:
            continue
        if ch == "！":
            out.append("!")
        elif ch == "？":
            out.append("?")
        else:
            out.append(ch)
    return "".join(out)


def _romanize_particles(text, lineno, stats):
    """助詞 は/へ/を をローマ字化する (R3)。前後に半角スペースを付け、後段で畳む"""
    out = []
    for i, ch in enumerate(text):
        if ch in _PARTICLE_ROMAN:
            prev = text[i - 1] if i > 0 else ""
            if _is_japanese_char(prev):
                roman = _PARTICLE_ROMAN[ch]
                out.append(" " + roman + " ")
                stats["particles"].append((lineno, ch, roman))
                continue
        out.append(ch)
    return "".join(out)


def _tidy_spaces(text):
    """連続する半角スペースを 1 つに畳み、行頭・行末のスペースを除去する (R8)"""
    return re.sub(r" +", " ", text).strip(" ")


def _convert_line(line, lineno, stats):
    """1 行を変換する。タグ行は素通し、行内タグはマスクして復元する"""
    if _FULL_TAG_RE.match(line):      # 手順 0: タグ行の素通し (R9)
        return line
    masked, tags = _mask_tags(line)
    masked = masked.translate(_WIDTH_TABLE)                 # 1. 全角→半角
    masked = _fold_ruby(masked, stats)                      # 2. ルビ畳み込み
    masked = _strip_symbols(masked)                         # 3. 記号・括弧排除
    masked = _romanize_particles(masked, lineno, stats)     # 4. 助詞ローマ字化
    masked = _open_numbers(masked)                          # 5. 数字読み下し
    masked = _tidy_spaces(masked)                           # 6. スペース整理
    # 7. 残存漢字チェック (タグ内部は除外 = マスク済み文字列で検査する)
    residual = _KANJI_RE.findall(masked)
    if residual:
        uniq = []
        for c in residual:
            if c not in uniq:
                uniq.append(c)
        stats["residual"].append((lineno, "".join(uniq)))
    return _restore_tags(masked, tags)


def convert_text(text):
    """作品版歌詞テキストを入稿版へ変換する。(変換後テキスト, 統計) を返す。
    行数・行順・末尾改行は保持する"""
    stats = {"ruby": 0, "particles": [], "residual": []}
    lines = text.split("\n")
    out_lines = [_convert_line(line, i, stats) for i, line in enumerate(lines, 1)]
    return "\n".join(out_lines), stats


# =============================================================================
# レポート出力
# =============================================================================

def format_report(stats):
    """--report 用の変換ログ (stderr 向け) を組み立てる"""
    lines = ["== 変換レポート =="]
    lines.append(f"ルビ畳み込み: {stats['ruby']} 件")
    if stats["particles"]:
        joined = " / ".join(f"{ln}行目 {ch}→{ro}" for ln, ch, ro in stats["particles"])
        lines.append(f"助詞ローマ字化: {len(stats['particles'])} 件 ({joined})")
    else:
        lines.append("助詞ローマ字化: 0 件")
    if stats["residual"]:
        joined = " / ".join(f"{ln}行目 {chars}" for ln, chars in stats["residual"])
        lines.append(f"残存漢字: {len(stats['residual'])} 行 ({joined})")
        lines.append("→ 作品版で該当漢字にルビ注釈 (例: 漢字(かんじ)) を足して再実行すれば全ひらがな化に到達できます。")
    else:
        lines.append("残存漢字: なし")
    return "\n".join(lines)


def format_residual_warning(stats):
    """--report を付けない通常時に stderr へ出す残存漢字 WARN。無ければ空文字"""
    if not stats["residual"]:
        return ""
    joined = " / ".join(f"{ln}行目 {chars}" for ln, chars in stats["residual"])
    return (
        f"[WARN] 残存漢字があります ({len(stats['residual'])} 行: {joined})。\n"
        "作品版で該当漢字にルビ注釈 (例: 漢字(かんじ)) を足して再実行すれば全ひらがな化に到達できます。"
    )


def _emit_stderr_log(stats, report):
    """変換ログ (--report) または残存漢字 WARN を stderr へ出す"""
    if report:
        sys.stderr.write(format_report(stats) + "\n")
    else:
        warn = format_residual_warning(stats)
        if warn:
            sys.stderr.write(warn + "\n")


# =============================================================================
# 実行モード
# =============================================================================

def run_text(infile, outfile, report):
    """テキストモード: 標準入力/ファイル → 変換 → 標準出力/ファイル"""
    if infile in (None, "-"):
        text = sys.stdin.read()
    else:
        with open(infile, encoding="utf-8") as f:
            text = f.read()
    out_text, stats = convert_text(text)
    if outfile in (None, "-"):
        sys.stdout.write(out_text)
    else:
        with open(outfile, "w", encoding="utf-8") as f:
            f.write(out_text)
    _emit_stderr_log(stats, report)
    return 0


def run_json(path, report):
    """JSON モード: song.json の lyrics_display を変換し lyrics_suno に書き戻す"""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        sys.stderr.write(f"エラー: ファイルを読み込めません: {e}\n")
        return 2
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        sys.stderr.write(f"エラー: JSON として解釈できません ({e})。\n")
        return 2
    if not isinstance(data, dict):
        sys.stderr.write("エラー: song.json のトップレベルがオブジェクトではありません。\n")
        return 2
    display = data.get("lyrics_display")
    if not isinstance(display, str) or not display.strip():
        sys.stderr.write(
            "エラー: lyrics_display がありません (または空です)。"
            "作品版歌詞を lyrics_display に入れてから再実行してください。\n"
        )
        return 2
    out_text, stats = convert_text(display)
    data["lyrics_suno"] = out_text
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
    except OSError as e:
        sys.stderr.write(f"エラー: 書き戻しに失敗しました: {e}\n")
        return 2
    _emit_stderr_log(stats, report)
    sys.stderr.write(f"lyrics_display を変換して lyrics_suno に書き戻しました: {path}\n")
    return 0


# =============================================================================
# 自己検査 (--selftest)
# =============================================================================

# 変換フィクスチャ (06 の例をルビ注釈化したもの)。畳み込み・助詞・数字・タグ保全・
# 英単語素通しを検証する。期待値は本実装の確定仕様に厳密一致させてある。
_SELFTEST_CASES = (
    (
        "入力1: タグ保全・ルビ畳み込み・を/へ・字空け保持",
        "[Verse 1]\n"
        "街(まち)の灯(あか)り ほどけて\n"
        "君(きみ)を探(さが)す 夜(よる)の底(そこ)\n"
        "二人(ふたり)の 明日(あした)へ",
        "[Verse 1]\n"
        "まちのあかり ほどけて\n"
        "きみ wo さがす よるのそこ\n"
        "ふたりの あした e",
    ),
    (
        "入力2: は→wa・数字 2→に・英単語素通し・へ→e",
        "[Chorus]\n"
        "今夜(こんや)は 眠(ねむ)らないまま\n"
        "午前(ごぜん)2時(じ)の melody\n"
        "君(きみ)へ 鳴(な)らす",
        "[Chorus]\n"
        "こんや wa ねむらないまま\n"
        "ごぜんにじの melody\n"
        "きみ e ならす",
    ),
    (
        "入力3: 行内タグの保全 + ルビ",
        "夜(よる)[Ad-lib]の うた",
        "よる[Ad-lib]の うた",
    ),
)


def run_selftest():
    """内蔵フィクスチャで自己検査する。全通過で SELFTEST: OK / 失敗で差分を出し 1"""
    failures = []   # (名称, 期待, 実際)

    for name, src, expected in _SELFTEST_CASES:
        got, _ = convert_text(src)
        if got != expected:
            failures.append((name, expected, got))

    # 数詞リーダ (整数 → かな)
    for n, exp in ((0, "ぜろ"), (2, "に"), (17, "じゅうなな"), (100, "ひゃく"),
                   (2049, "にせんよんじゅうきゅう"), (300, "さんびゃく"),
                   (600, "ろっぴゃく"), (800, "はっぴゃく"), (3000, "さんぜん"),
                   (8000, "はっせん"), (10000, "いちまん"), (123456789, None)):
        got = read_number_kana(n)
        if exp is not None and got != exp:
            failures.append((f"数詞 {n}", exp, got))

    # 漢数字 → 整数
    for s, exp in (("三百", 300), ("一千", 1000), ("二千四十九", 2049),
                   ("十七", 17), ("二〇四九", 2049), ("万", None)):
        got = _kanji_to_int(s)
        if got != exp:
            failures.append((f"漢数字 {s}", str(exp), str(got)))

    # 残存漢字チェック (終了コードは 0、residual に記録されること)
    _, res_stats = convert_text("[Verse 2]\n海(うみ)の記憶")
    res_chars = "".join(chars for _, chars in res_stats["residual"])
    if "記" not in res_chars or "憶" not in res_chars:
        failures.append(("残存漢字検出", "記・憶 を検出", res_chars or "(検出なし)"))

    # 単独の万は開かず残す (100万 → ひゃく万)
    got_man, _ = convert_text("100万")
    if got_man != "ひゃく万":
        failures.append(("助数詞・単独万の残存", "ひゃく万", got_man))

    if failures:
        sys.stderr.write(f"SELFTEST: FAIL ({len(failures)} 件)\n")
        for name, exp, got in failures:
            sys.stderr.write(f"--- {name} ---\n期待:\n{exp}\n実際:\n{got}\n")
        return 1
    sys.stdout.write("SELFTEST: OK\n")
    return 0


# =============================================================================
# 引数解析 / エントリポイント
# =============================================================================

class JapaneseArgumentParser(argparse.ArgumentParser):
    """引数エラーを日本語プレフィックス付きで出す ArgumentParser (終了コード 2)"""

    def error(self, message):
        self.print_usage(sys.stderr)
        sys.stderr.write(f"引数エラー: {message}\n")
        sys.exit(2)


def build_parser():
    parser = JapaneseArgumentParser(
        prog="build_submission_lyrics.py",
        description="作品版歌詞 (漢字かな交じり + 構成タグ) を Suno 入稿版歌詞 (かな主体 + 構成タグ) へ機械変換します。",
        epilog=(
            "変換規則 (06_language-ja.md 第2部 R1〜R9 の機械化ぶん):\n"
            "  R9 タグ保全 / ルビ畳み込み / R4・R7 記号排除 / R3 助詞ローマ字化 /\n"
            "  R5 数字読み下し / R8 スペース整理 / 残存漢字チェック(WARN)\n"
            "行構造 (行数・行順) は保存します。既定は標準入力→標準出力。\n"
            "--json は song.json の lyrics_display を変換して lyrics_suno に書き戻します\n"
            "(--in/--out とは排他)。\n"
            "終了コード: 0=成功(残存漢字があっても0) / 1=selftest失敗 / 2=引数・JSON不正"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--in", dest="infile", metavar="PATH", default=None,
                        help="入力パス (省略時または - で標準入力)")
    parser.add_argument("--out", dest="outfile", metavar="PATH", default=None,
                        help="出力パス (省略時または - で標準出力)")
    parser.add_argument("--report", action="store_true",
                        help="変換ログ (ルビ畳み込み数・助詞変換箇所・残存漢字) を stderr に出力")
    parser.add_argument("--json", dest="json_path", metavar="PATH", default=None,
                        help="song.json の lyrics_display を変換し lyrics_suno に書き戻す (テキスト入出力と排他)")
    parser.add_argument("--selftest", action="store_true",
                        help="内蔵フィクスチャで自己検査する (全通過で SELFTEST: OK)")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.selftest:
        return run_selftest()
    if args.json_path is not None:
        if args.infile is not None or args.outfile is not None:
            sys.stderr.write("引数エラー: --json はテキスト入出力 (--in/--out) と併用できません。\n")
            return 2
        return run_json(args.json_path, args.report)
    try:
        return run_text(args.infile, args.outfile, args.report)
    except OSError as e:
        sys.stderr.write(f"エラー: 入出力に失敗しました: {e}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
