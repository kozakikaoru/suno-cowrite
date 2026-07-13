#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""song.json 検証スクリプト (suno-artist-production-x)

song.json (Suno Custom Mode 入稿設定の canonical データ) を決定論的に検証し、
人間可読の日本語レポートを stdout に出力する。Python 3 標準ライブラリのみで動く。

判定レベル:
  FAIL … ハード上限超過・必須フィールド欠落・メタタグ括弧不整合など (差し戻しが必要)
  WARN … 推奨範囲からの逸脱 (続行できるが確認を推奨)

文字数はすべて Unicode コードポイント数 (Python の len) で数える。Suno 側の数え方は
公式に確認できていないため、各ハード上限の 90% 到達時点で早期警告を出して安全側に倒す。

使い方:
    python3 validate_song.py <song.json のパス>

終了コード:
    0 = PASS または WARN のみ / 1 = FAIL あり / 2 = 引数の誤り
"""

import argparse
import json
import re
import sys

# =============================================================================
# 定数 — Suno 仕様のスナップショット (v1 はスクリプト内定数で割り切る)
# update-spec で spec.md と不一致が出たら更新
# 出典: 調査レポート 2026-07-10 (§2-1 文字数上限 / §2-2 スライダー / §5-1 メタタグ語彙)
#       および設計書 §5-3 バリデーション方針
# =============================================================================

SPEC_SNAPSHOT_DATE = "2026-07-10"   # この定数群の元にした Suno 仕様の調査日

TITLE_MAX_CHARS = 100               # Title 上限 (v4.5 以降)
STYLE_MAX_CHARS = 1_000             # Style of Music 上限 (フル / Persona 適用時の両変種とも)
LYRICS_MAX_CHARS = 5_000            # Lyrics 上限 (入稿版)
LYRICS_SOFT_MAX_CHARS = 3_000       # 超えると歌唱が駆け足になる報告がある実用閾値
EXCLUDE_ITEMS_SOFT_MAX = 5          # Exclude Styles の安定動作の目安 (項目数)
SLIDER_MIN = 0                      # Weirdness / Style Influence の下限
SLIDER_MAX = 100                    # 同上限
SLIDER_GLITCH_FROM = 81             # 81 以上は破綻 (グリッチ) 領域という検証報告
STYLE_TAG_COUNT_MIN = 4             # Style タグ数の推奨下限
STYLE_TAG_COUNT_MAX = 15            # Style タグ数の推奨上限
EARLY_WARN_RATIO = 0.9              # ハード上限の 90% 到達で早期警告

# 派生リリース用スキーマ予約 (提案8 / 契約 C5)。v1 は許容と WARN のみ、派生フローは v1.1。
VALID_SONG_TYPES = ("original", "cover", "remaster", "extend")   # song_type の既定 4 値 (既定 original)

# 行密度 (かなモーラ) 検査の定数 (提案4)。日本語入稿版の早口事故を生成前に WARN で知らせる。
# 小書きの拗音・小母音 (ゃゅょ・ぁぃぅぇぉ 等) は直前のかなと合わせて 1 モーラなので数えない。
# 小書きの促音「っ/ッ」と長音「ー」は 1 モーラとして数える (日本語の詩学の慣習)。
SMALL_KANA_NO_MORA = frozenset("ぁぃぅぇぉゃゅょゎゕゖァィゥェォャュョヮ")
LONG_VOWEL_MARKS = frozenset("ーｰ")
# セクション種別ごとの 1 行あたりモーラ数の目安上限 (かな概算)。キーは _normalize_tag 済みの形。
SECTION_MORA_CAP = {
    "verse": 20, "pre chorus": 20, "chorus": 22, "post chorus": 18,
    "hook": 18, "bridge": 20, "breakdown": 20, "drop": 16,
    "rap": 34, "spoken word": 30,
}
DEFAULT_MORA_CAP = 24               # 表にないセクションの目安上限
MORA_REFERENCE_BPM = 100            # この BPM を基準にテンポ連動で目安を伸縮する
MORA_TEMPO_FACTOR_MIN = 0.7         # テンポ連動係数の下限 (速い曲でも目安を下げすぎない)
MORA_TEMPO_FACTOR_MAX = 1.4         # テンポ連動係数の上限 (遅い曲でも目安を上げすぎない)
MORA_IMBALANCE_DIFF = 12           # 同一セクション内の (最長 - 最短) がこれ以上で行長ばらつき WARN
MORA_IMBALANCE_MIN_LINES = 3       # 行長ばらつき検査の対象にする最小本文行数

# 必須フィールド (欠落 = FAIL。設計書 §5-2 の song.json スキーマより)
REQUIRED_FIELDS = ("title", "style", "lyrics_suno", "model", "language")

# 推奨フィールド (欠落 = WARN。paste.md 生成に使う)
RECOMMENDED_FIELDS = (
    "lyrics_display", "vocal_gender", "weirdness", "style_influence", "instrumental",
)

# メタタグ語彙一覧 (調査 §5-1。v5.5 までタグ語彙は不変)
# パラメータ付きタグ [Tag: modifiers] は「Tag」部分で照合する。
# 番号付きタグ ([Verse 2] 等) は末尾の数字を除いて照合する。
META_TAG_VOCAB = (
    # 構造
    "Intro", "Verse", "Pre-Chorus", "Chorus", "Post-Chorus", "Bridge",
    "Breakdown", "Build", "Build-Up", "Drop", "Hook", "Interlude",
    "Outro", "End",
    # インスト指示
    "Instrumental", "Instrumental Intro", "Instrumental Break",
    "Guitar Solo", "Piano Solo", "Drum Solo", "Bass Solo",
    "Saxophone Solo", "Synth Solo", "Strings Rise", "Percussion Break",
    # ボーカル指示
    "Male Vocal", "Female Vocal", "Duet", "Choir", "Harmony", "Rap",
    "Spoken Word", "Whisper", "Scream", "Ad-lib", "Humming",
    "Backing Vocals",
    # ダイナミクス / 制御
    "Fade In", "Fade Out", "Silence", "Crescendo", "Decrescendo",
    "Tempo", "Key Change",
)

# =============================================================================
# 内部ユーティリティ
# =============================================================================

# 歌詞中のメタタグ抽出 ([ ] が同一行で閉じているもののみ。跨ぎは括弧検査で拾う)
TAG_RE = re.compile(r"\[([^\[\]\n]*)\]")

# 実在固有名詞らしき大文字連語 (例: Taylor Swift)。ヒューリスティックであり最終判断はモデル側
PROPER_NOUN_RE = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b")

# 日本語入稿版に残ってはいけない括弧 (リフレイン誤解釈リスク)
PAREN_CHARS = "()（）"

# Style から BPM を拾う (「92 bpm feel」表記。テンポ連動のモーラ目安に使う)
BPM_RE = re.compile(r"(\d{2,3})\s*bpm", re.IGNORECASE)

# 単独行のセクションタグ ([Verse 1] / [Bridge: piano only] など) を判定する
SECTION_HEADER_RE = re.compile(r"^\[([^\[\]]+)\]$")


def _normalize_tag(name):
    """タグ名を照合用に正規化する (小文字化・ハイフンを空白扱い・連続空白の圧縮)"""
    s = name.strip().lower().replace("-", " ")
    return re.sub(r"\s+", " ", s)


_VOCAB_NORMALIZED = frozenset(_normalize_tag(t) for t in META_TAG_VOCAB)


def _is_known_tag(name):
    """語彙一覧にあるタグか判定する (大文字小文字不問、末尾の番号は無視)"""
    base = _normalize_tag(name)
    if base in _VOCAB_NORMALIZED:
        return True
    return re.sub(r"\s+\d+$", "", base) in _VOCAB_NORMALIZED


class Report:
    """検査結果 (FAIL / WARN / PASS) を検査順に蓄積する"""

    def __init__(self):
        self.entries = []  # (level, message) のリスト

    def fail(self, message):
        self.entries.append(("FAIL", message))

    def warn(self, message):
        self.entries.append(("WARN", message))

    def ok(self, message):
        self.entries.append(("PASS", message))

    @property
    def errors(self):
        return sum(1 for level, _ in self.entries if level == "FAIL")

    @property
    def warnings(self):
        return sum(1 for level, _ in self.entries if level == "WARN")


# =============================================================================
# 各検査
# =============================================================================

def check_required(data, rep):
    """必須フィールドの存在検査 (欠落・空文字 = FAIL)"""
    missing = []
    for field in REQUIRED_FIELDS:
        raw = data.get(field)
        if raw is None or (isinstance(raw, str) and not raw.strip()):
            missing.append(field)
    if missing:
        rep.fail(f"必須フィールドが欠落しています ({', '.join(missing)})。song.json の組み立てを確認してください。")
    else:
        rep.ok(f"必須フィールド ({', '.join(REQUIRED_FIELDS)}): すべてあり")


def collect_typed_values(data, rep):
    """型を検査しつつ値を取り出す。型不正は FAIL とし、その値は以降の検査から除外する"""
    values = {}
    str_fields = (
        "title", "style", "style_with_persona", "lyrics_suno", "lyrics_display",
        "model", "language", "exclude_styles", "vocal_gender",
    )
    for field in str_fields:
        raw = data.get(field)
        if raw is None or isinstance(raw, str):
            values[field] = raw
        else:
            rep.fail(f"{field}: 型が不正です (文字列のはずが {type(raw).__name__})。")
            values[field] = None
    for field in ("weirdness", "style_influence"):
        raw = data.get(field)
        if raw is None:
            values[field] = None
        elif isinstance(raw, bool) or not isinstance(raw, (int, float)):
            rep.fail(f"{field}: 型が不正です (0〜100 の数値のはずが {raw!r})。")
            values[field] = None
        else:
            values[field] = raw
    inst = data.get("instrumental")
    if inst is not None and not isinstance(inst, bool):
        rep.fail(f"instrumental: 型が不正です (true/false のはずが {inst!r})。")
        inst = None
    values["instrumental"] = inst
    persona = data.get("persona")
    if persona is not None and not isinstance(persona, dict):
        rep.fail(f"persona: 型が不正です (オブジェクトのはずが {type(persona).__name__})。")
        persona = None
    values["persona"] = persona
    return values


def check_recommended(data, values, rep):
    """推奨フィールドの存在検査 (欠落 = WARN)"""
    fields = list(RECOMMENDED_FIELDS)
    if values.get("instrumental") is True:
        fields.remove("vocal_gender")  # インスト曲では vocal_gender 未設定を許容する
    missing = [f for f in fields if data.get(f) is None]
    if missing:
        rep.warn(f"推奨フィールドが未設定です ({', '.join(missing)})。paste.md の生成に使うため、揃えておくことを推奨します。")
    else:
        rep.ok("推奨フィールド: すべてあり")


def check_text_limit(label, text, limit, rep):
    """文字数のハード上限 (FAIL) と 90% 早期警告 (WARN)"""
    n = len(text)  # Unicode コードポイント数
    early = int(limit * EARLY_WARN_RATIO)
    if n > limit:
        rep.fail(f"{label}: {n:,} 字 — 上限 {limit:,} 字を {n - limit:,} 字超過しています。")
    elif n >= early:
        rep.warn(
            f"{label}: {n:,} 字 — 上限 {limit:,} 字の 90% ({early:,} 字) に到達しています。"
            f"Suno 側の数え方が公式未確認のため、余裕を持って収めてください。"
        )
    else:
        rep.ok(f"{label}: {n:,} 字 (上限 {limit:,} 字)")


def check_style_variant(label, text, rep):
    """Style 1 変種分の検査 (文字数 / タグ数 / 固有名詞ヒューリスティック)"""
    check_text_limit(label, text, STYLE_MAX_CHARS, rep)

    tags = [t.strip() for t in text.split(",") if t.strip()]
    n = len(tags)
    if n < STYLE_TAG_COUNT_MIN:
        rep.warn(
            f"{label} のタグ数: {n} 個 — 推奨は {STYLE_TAG_COUNT_MIN}〜{STYLE_TAG_COUNT_MAX} 個です。"
            f"少なすぎると生成の自由度が高くなり、狙いから外れやすくなります。"
        )
    elif n > STYLE_TAG_COUNT_MAX:
        rep.warn(
            f"{label} のタグ数: {n} 個 — 推奨は {STYLE_TAG_COUNT_MIN}〜{STYLE_TAG_COUNT_MAX} 個です。"
            f"多すぎると指示が競合して音が濁ります。"
        )
    else:
        rep.ok(f"{label} のタグ数: {n} 個 (推奨 {STYLE_TAG_COUNT_MIN}〜{STYLE_TAG_COUNT_MAX} 個)")

    hits = sorted(set(PROPER_NOUN_RE.findall(text)))
    if hits:
        rep.warn(
            f"{label} に実在の固有名詞かもしれない大文字連語があります: {', '.join(hits)}。"
            f"実在アーティスト名などは Style に書けないため、特徴を形容詞・楽器・年代に分解してください "
            f"(ヒューリスティック検出のため、誤検知ならこの警告は無視してかまいません)。"
        )


def check_persona_consistency(values, rep):
    """persona.use = true のとき style_with_persona の併記を要求する (設計 D9)"""
    persona = values.get("persona")
    if not persona or not persona.get("use"):
        return
    if not (values.get("style_with_persona") or "").strip():
        rep.fail(
            "persona.use が true なのに style_with_persona がありません。"
            "Persona 適用時は Style 2 変種 (適用時 / フル) の併記が必須です。"
        )
    else:
        rep.ok("Persona 適用 (persona.use = true): style_with_persona 併記あり")


def check_lyrics_length(text, rep):
    """入稿版歌詞の文字数 (>5,000 = FAIL / 90% 到達 = WARN / >3,000 = WARN)"""
    n = len(text)
    early = int(LYRICS_MAX_CHARS * EARLY_WARN_RATIO)
    if n > LYRICS_MAX_CHARS:
        rep.fail(f"入稿版歌詞 (lyrics_suno): {n:,} 字 — 上限 {LYRICS_MAX_CHARS:,} 字を {n - LYRICS_MAX_CHARS:,} 字超過しています。")
    elif n >= early:
        rep.warn(
            f"入稿版歌詞 (lyrics_suno): {n:,} 字 — 上限 {LYRICS_MAX_CHARS:,} 字の 90% ({early:,} 字) に到達しています。"
            f"Suno 側の数え方が公式未確認のため、余裕を持って収めてください。"
        )
    elif n > LYRICS_SOFT_MAX_CHARS:
        rep.warn(
            f"入稿版歌詞 (lyrics_suno): {n:,} 字 — {LYRICS_SOFT_MAX_CHARS:,} 字を超えると歌唱が駆け足になる報告があります。"
            f"テンポに対して歌詞が多すぎないか確認してください。"
        )
    else:
        rep.ok(f"入稿版歌詞 (lyrics_suno): {n:,} 字 (上限 {LYRICS_MAX_CHARS:,} 字 / 実用目安 {LYRICS_SOFT_MAX_CHARS:,} 字)")


def check_brackets(lyrics, rep):
    """メタタグの [ ] 対応検査 (不整合 = FAIL)。行単位で走査し、行番号付きで報告する"""
    problems = []
    for lineno, line in enumerate(lyrics.split("\n"), 1):
        depth = 0
        problem = None
        for ch in line:
            if ch == "[":
                depth += 1
                if depth > 1:
                    problem = "'[' が閉じられる前に次の '[' があります"
                    break
            elif ch == "]":
                depth -= 1
                if depth < 0:
                    problem = "対応する '[' のない ']' があります"
                    break
        if problem is None and depth > 0:
            problem = "閉じられていない '[' があります"
        if problem:
            problems.append(f"{lineno} 行目: {problem}")
    if problems:
        shown = " / ".join(problems[:5])
        more = f" ほか {len(problems) - 5} 件" if len(problems) > 5 else ""
        rep.fail(f"メタタグの [ ] が対応していません ({shown}{more})。")
    else:
        rep.ok("メタタグの [ ] 対応: 問題なし")


def check_meta_tag_vocab(lyrics, rep):
    """メタタグの語彙照合 (語彙一覧にないタグ = WARN)。[Tag: modifiers] は Tag 部分で照合"""
    tags = TAG_RE.findall(lyrics)
    if not tags:
        return
    unknown = []
    for tag in tags:
        base = tag.split(":", 1)[0]
        if not _is_known_tag(base):
            display = f"[{tag}]"
            if display not in unknown:
                unknown.append(display)
    if unknown:
        shown = " ".join(unknown[:8])
        more = f" ほか {len(unknown) - 8} 件" if len(unknown) > 8 else ""
        rep.warn(
            f"語彙一覧にないメタタグがあります: {shown}{more}。"
            f"誤記の可能性を確認してください (意図的な独自タグなら無視してかまいません)。"
        )
    else:
        rep.ok(f"メタタグ語彙: {len(tags)} 個すべて語彙一覧に一致")


def check_ja_parens(language, lyrics, rep):
    """日本語 (language: ja) の入稿版に括弧が残っていないか (残存 = WARN)"""
    if (language or "").strip().lower() != "ja":
        return
    hit_lines = [
        str(lineno)
        for lineno, line in enumerate(lyrics.split("\n"), 1)
        if any(c in line for c in PAREN_CHARS)
    ]
    if hit_lines:
        shown = ", ".join(hit_lines[:5])
        more = " ほか" if len(hit_lines) > 5 else ""
        rep.warn(
            f"日本語の入稿版歌詞に括弧 ( ) （ ） が残っています (計 {len(hit_lines)} 行: {shown} 行目{more})。"
            f"括弧はコーラス/リフレインとして誤解釈されることがあるため、ルビ・補足は入稿版から外してください。"
        )
    else:
        rep.ok("日本語入稿版の括弧: 残存なし")


def _count_kana_mora(text):
    """1 行のかなモーラ数を概算する (決定論的)。
    ひらがな/カタカナは 1 字 1 モーラ、小書き拗音・小母音は 0、促音「っ」・長音「ー」は 1 として数える。
    ローマ字 (助詞 wa/e/wo や混在英単語) は母音の数で 1 モーラ相当に近似する。"""
    mora = 0
    for ch in text:
        if ch in SMALL_KANA_NO_MORA:
            continue
        code = ord(ch)
        if 0x3041 <= code <= 0x3096 or 0x30A1 <= code <= 0x30FA:  # ひらがな / カタカナ
            mora += 1
        elif ch in LONG_VOWEL_MARKS:
            mora += 1
        elif ch in "aiueoAIUEO":  # ローマ字助詞・混在英単語の母音を 1 モーラ相当で近似
            mora += 1
    return mora


def _extract_bpm(values):
    """Style / Style(Persona 適用時) から BPM 値を拾う (最初の一致)。無ければ None。"""
    for key in ("style", "style_with_persona"):
        text = values.get(key) or ""
        m = BPM_RE.search(text)
        if m:
            return int(m.group(1))
    return None


def _tempo_scaled_cap(base_cap, bpm):
    """テンポが速いほど 1 行に詰め込める目安を厳しく (低く) する。係数はクランプする。"""
    if not bpm:
        return base_cap
    factor = MORA_REFERENCE_BPM / bpm
    factor = max(MORA_TEMPO_FACTOR_MIN, min(MORA_TEMPO_FACTOR_MAX, factor))
    return max(1, int(round(base_cap * factor)))


def check_mora_density(language, lyrics, values, rep):
    """入稿版歌詞の行ごとのかなモーラ数を概算し、早口の恐れと行長ばらつきを WARN で知らせる (提案4)。
    日本語 (language: ja) の歌ものだけが対象。モーラは概算のため FAIL にはしない (表現の自由を奪わない)。"""
    if (language or "").strip().lower() != "ja":
        return
    if values.get("instrumental") is True:
        return

    bpm = _extract_bpm(values)
    sections = []            # [(section_key, [(lineno, mora), ...]), ...] を出現順に
    current_lines = None
    for lineno, raw in enumerate(lyrics.split("\n"), 1):
        stripped = raw.strip()
        if not stripped:
            continue
        header = SECTION_HEADER_RE.match(stripped)
        if header:
            key = _normalize_tag(header.group(1).split(":", 1)[0])
            key = re.sub(r"\s+\d+$", "", key)     # 末尾の番号 (Verse 2 → verse) を落とす
            current_lines = []
            sections.append((key, current_lines))
            continue
        mora = _count_kana_mora(TAG_RE.sub(" ", stripped))  # 行内タグを除いて数える
        if mora <= 0:
            continue
        if current_lines is None:                  # セクションタグより前の本文
            current_lines = []
            sections.append(("", current_lines))
        current_lines.append((lineno, mora))

    if not any(lines for _, lines in sections):
        return  # 数えられる本文行がない (インスト等)

    over, uneven = [], []
    for key, lines in sections:
        if not lines:
            continue
        cap = _tempo_scaled_cap(SECTION_MORA_CAP.get(key, DEFAULT_MORA_CAP), bpm)
        label = f"[{key.title()}]" if key else "(冒頭)"
        for lineno, mora in lines:
            if mora > cap:
                over.append(f"{lineno}行目 {label} {mora}モーラ (目安 {cap})")
        moras = [m for _, m in lines]
        if len(moras) >= MORA_IMBALANCE_MIN_LINES and (max(moras) - min(moras)) >= MORA_IMBALANCE_DIFF:
            uneven.append(f"{label} {min(moras)}〜{max(moras)}モーラ")

    tempo_note = f"テンポ {bpm}bpm 連動" if bpm else "固定目安"
    if over:
        shown = " / ".join(over[:6])
        more = f" ほか {len(over) - 6} 件" if len(over) > 6 else ""
        rep.warn(
            f"早口の恐れ ({tempo_note}): 次の行がセクションのモーラ目安を超えています — {shown}{more}。"
            f"かなモーラは概算です。テンポに対して詰め込みすぎなら行の分割・語数削減を検討してください。"
        )
    if uneven:
        shown = " / ".join(uneven[:5])
        rep.warn(
            f"行長のばらつき ({tempo_note}): {shown} — 同一セクション内で行の長さの開きが大きいと譜割りが不安定になりやすいです"
            f" (意図的な字余り/字足らずなら無視してかまいません)。"
        )
    if not over and not uneven:
        rep.ok(f"行密度 (かなモーラ概算・{tempo_note}): 各セクションの目安内")


def check_song_type(data, rep):
    """派生リリース用フィールド (song_type / derived_from) の予約検査 (契約 C5 / 提案8)。
    未使用なら無言。既定 4 値以外や整合しない指定は WARN のみ (FAIL にしない。v1 は予約だけ)。"""
    raw_type = data.get("song_type")
    derived = data.get("derived_from")
    if raw_type is None and derived is None:
        return  # 既定 (original / 派生なし)。予約フィールド未使用時は報告しない
    song_type = raw_type.strip().lower() if isinstance(raw_type, str) and raw_type.strip() else "original"
    if raw_type is not None and not (isinstance(raw_type, str) and song_type in VALID_SONG_TYPES):
        rep.warn(
            f"song_type: {raw_type!r} は既定の 4 値 ({' / '.join(VALID_SONG_TYPES)}) にありません。"
            f"派生リリースは v1.1 で扱うため、誤記でなければ original として進めてください。"
        )
        return
    if song_type == "original":
        if derived not in (None, "", 0):
            rep.warn(
                f"song_type が original なのに derived_from ({derived!r}) が設定されています。"
                f"派生曲なら song_type を cover / remaster / extend にしてください。"
            )
        else:
            rep.ok("曲種別 (song_type): original")
    elif derived in (None, "", 0):
        rep.warn(
            f"song_type が {song_type} (派生曲) なのに derived_from が未指定です。"
            f"元曲の番号 (song_no) を derived_from に入れてください。"
        )
    else:
        rep.ok(f"曲種別 (song_type): {song_type} / 元曲 (derived_from): {derived}")


def check_exclude_styles(exclude, rep):
    """Exclude Styles の項目数 (6 項目以上 = WARN)"""
    if exclude is None or not exclude.strip():
        return
    items = [s for s in re.split(r"[,、]", exclude) if s.strip()]
    if len(items) > EXCLUDE_ITEMS_SOFT_MAX:
        rep.warn(
            f"Exclude Styles が {len(items)} 項目あります。"
            f"安定して効くのは {EXCLUDE_ITEMS_SOFT_MAX} 項目程度までという検証報告があるため、優先度の低い項目を削ってください。"
        )
    else:
        rep.ok(f"Exclude Styles: {len(items)} 項目 (目安 {EXCLUDE_ITEMS_SOFT_MAX} 項目以内)")


def check_slider(label, value, rep):
    """スライダー値の検査 (0〜100 外 = FAIL / 81 以上 = WARN)"""
    if value is None:
        return
    if value < SLIDER_MIN or value > SLIDER_MAX:
        rep.fail(f"{label}: {value} — {SLIDER_MIN}〜{SLIDER_MAX} の範囲外です。")
    elif value >= SLIDER_GLITCH_FROM:
        rep.warn(
            f"{label}: {value} — {SLIDER_GLITCH_FROM} 以上は破綻 (グリッチ) しやすい領域という検証報告があります。"
            f"意図的でなければ 80 以下に下げてください。"
        )
    else:
        rep.ok(f"{label}: {value} (範囲 {SLIDER_MIN}〜{SLIDER_MAX})")


def run_checks(data, rep):
    """検査一式を設計 §5-3 の表に沿って実行する"""
    check_required(data, rep)
    values = collect_typed_values(data, rep)
    check_recommended(data, values, rep)
    if values["title"]:
        check_text_limit("Title", values["title"], TITLE_MAX_CHARS, rep)
    if values["style"]:
        check_style_variant("Style (フル)", values["style"], rep)
    if values["style_with_persona"]:
        check_style_variant("Style (Persona 適用時)", values["style_with_persona"], rep)
    check_persona_consistency(values, rep)
    lyrics = values["lyrics_suno"]
    if lyrics:
        check_lyrics_length(lyrics, rep)
        check_brackets(lyrics, rep)
        check_meta_tag_vocab(lyrics, rep)
        check_ja_parens(values["language"], lyrics, rep)
        check_mora_density(values["language"], lyrics, values, rep)
    check_exclude_styles(values["exclude_styles"], rep)
    check_slider("Weirdness", values["weirdness"], rep)
    check_slider("Style Influence", values["style_influence"], rep)
    check_song_type(data, rep)


# =============================================================================
# レポート出力 / エントリポイント
# =============================================================================

def build_meta_line(data):
    """レポートヘッダに出す曲情報の 1 行を組み立てる"""
    parts = []
    for label, key in (("曲", "title"), ("アーティスト", "artist"), ("モデル", "model"), ("言語", "language")):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(f"{label}: {value}")
    return " / ".join(parts)


def print_report(path, meta_line, rep):
    """日本語レポートを stdout に出力し、終了コードを返す"""
    print("=" * 60)
    print("song.json 検証レポート")
    print("=" * 60)
    print(f"対象: {path}")
    if meta_line:
        print(meta_line)
    print(f"基準: スクリプト内定数 (Suno 仕様調査日 {SPEC_SNAPSHOT_DATE} 時点)")
    print("-" * 60)
    for level, message in rep.entries:
        print(f"[{level}] {message}")
    print("-" * 60)
    errors, warnings = rep.errors, rep.warnings
    verdict = "FAIL" if errors else ("WARN" if warnings else "PASS")
    note = {
        "FAIL": "差し戻しが必要です",
        "WARN": "警告を確認のうえ続行できます",
        "PASS": "問題なし",
    }[verdict]
    print(f"判定: {verdict} (FAIL {errors} 件 / WARN {warnings} 件) — {note}")
    print(f"RESULT: {verdict} errors={errors} warnings={warnings}")
    return 1 if errors else 0


class JapaneseArgumentParser(argparse.ArgumentParser):
    """引数エラーを日本語プレフィックス付きで出す ArgumentParser"""

    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"引数エラー: {message}", file=sys.stderr)
        sys.exit(2)


def build_parser():
    parser = JapaneseArgumentParser(
        prog="validate_song.py",
        description="song.json (Suno Custom Mode 入稿設定) を検証し、日本語レポートを stdout に出力します。",
        epilog=(
            "検査内容 (設計 §5-3):\n"
            "  FAIL: Title > 100 字 / Style > 1,000 字 (両変種) / 入稿歌詞 > 5,000 字 /\n"
            "        スライダー 0〜100 外 / メタタグ [ ] の不整合 / 必須フィールド欠落\n"
            "  WARN: Style タグ数 4 未満・15 超 / 入稿歌詞 > 3,000 字 / Exclude 6 項目以上 /\n"
            "        スライダー 81 以上 / 語彙一覧にないメタタグ / 日本語入稿版の括弧残存 /\n"
            "        Style 内の固有名詞らしき大文字連語 / 各上限の 90% 到達 /\n"
            "        日本語の行密度 (かなモーラ) 目安超過・行長ばらつき / song_type が既定外\n"
            "文字数は Unicode コードポイント数で数えます。かなモーラ数は概算です。\n"
            "終了コード: 0 = PASS/WARN のみ, 1 = FAIL あり, 2 = 引数の誤り\n"
            "最終行に機械可読サマリを出します (例: RESULT: FAIL errors=2 warnings=1)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )
    parser.add_argument("song_json", metavar="<song.json>", help="検証する song.json のパス")
    parser.add_argument("-h", "--help", action="help", help="このヘルプを表示して終了します")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    path = args.song_json
    rep = Report()
    data = None
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        rep.fail(f"ファイルを読み込めません: {e}")
    except json.JSONDecodeError as e:
        rep.fail(f"JSON として解釈できません ({e.lineno} 行 {e.colno} 文字目: {e.msg})。")
    except UnicodeDecodeError as e:
        rep.fail(f"UTF-8 として読み込めません: {e}")
    if data is not None and not isinstance(data, dict):
        rep.fail(f"トップレベルがオブジェクトではありません ({type(data).__name__})。")
        data = None
    meta_line = ""
    if data is not None:
        meta_line = build_meta_line(data)
        run_checks(data, rep)
    return print_report(path, meta_line, rep)


if __name__ == "__main__":
    sys.exit(main())
