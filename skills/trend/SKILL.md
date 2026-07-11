---
name: trend
description: トレンド調査。「トレンド調べて」「今どんな曲が流行ってる?」「最近の J-POP の傾向は?」「ショート動画で伸びてる音楽って何?」などの発言、または /suno-artist-production:trend で起動。リサーチャーが Web 調査し、出典 (URL + 取得日) 付きで strategy/trends/ に保存。次の曲への活かし方まで提案する。
---

# トレンド調査 — /suno-artist-production:trend

音楽トレンドをリサーチャーに調査させ、出典付きでアーティストの戦略資料に残すフロー。マネージャー (メイン会話のペルソナ) として進行する。スラッシュ起動でも、会話からの自発起動 (Skill ツール) でも同じフローに従う。

## このスキル実行中の共通ルール

- ユーザーは「〇〇P」と呼ぶ (producer_name 未設定時は「P」)
- 質問はテキストで行う。AskUserQuestion は使わない
- ツールを使うターンでは前置きの実況テキストを書かず、報告はツール結果が返ってからまとめる
- サブエージェント起動プロンプトには、参照させるファイルの**絶対パス**を必ず書く。プラグインルートは hook が注入する絶対パスを使う (未注入なら、この SKILL.md の読み込み元 `<プラグインルート>/skills/trend/SKILL.md` から 2 階層上をプラグインルートとする)
- リサーチャーの調査結果は**必ず出典 (URL + 取得日) 付きでファイルに記録する**
- 作業の区切りで `.production/log.md` に 1 行追記し、`.production/state.md` を最新化する

## Step 0 — 前提チェック (scaffold)

```bash
DIR="$PWD"; ARTIST_ROOT=""
while :; do
  if [ -f "$DIR/artist.yaml" ]; then ARTIST_ROOT="$DIR"; break; fi
  if [ "$DIR" = "$HOME" ] || [ "$DIR" = "/" ]; then break; fi
  DIR=$(dirname "$DIR")
done
[ -n "$ARTIST_ROOT" ] || ARTIST_ROOT="$PWD"
if [ "$ARTIST_ROOT" = "$HOME" ] || [ "$ARTIST_ROOT" = "/" ]; then
  echo "UNSAFE_DIR"
else
  mkdir -p "$ARTIST_ROOT/.production"
  touch "$ARTIST_ROOT/.production/ACTIVE"
  [ -f "$ARTIST_ROOT/.production/state.md" ] || printf '# state\n\n- 現在フォーカス: (未設定)\n- 進行中の曲: (なし)\n- 未解決事項: (なし)\n- 次のアクション: (なし)\n' > "$ARTIST_ROOT/.production/state.md"
  [ -f "$ARTIST_ROOT/.production/log.md" ] || : > "$ARTIST_ROOT/.production/log.md"
  echo "ARTIST_ROOT=$ARTIST_ROOT"
  if [ -f "$ARTIST_ROOT/artist.yaml" ]; then echo "artist=yes"; else echo "artist=no"; fi
fi
```

- 以降の `$ARTIST_ROOT` は、ここで判明した絶対パスに置き換えて使う
- artist.yaml はあれば文脈に使うが、**無くても調査自体は動く** (`UNSAFE_DIR` の場合も調査してチャット報告まではできる。保存はしない)

## Step 1 — 調査観点の確定

- P の要望からトピックを決める (例: 「J-POP 全般の今」「ショート動画で伸びてる音」「シティポップ再燃の現在地」)。曖昧なら 1 問だけ確認する
- `artist=yes` なら、artist.yaml のジャンル帯・言語・テーマを「このアーティストにどう関係するか」の観点としてプロンプトに含める

## Step 2 — リサーチャー起動

subagent_type `suno-artist-production:researcher` を起動する。プロンプトに含めるもの:

- 調査トピックと観点
- **調査規約**: すべての事実に出典 (URL + 取得日) を付す / 一次情報と複数ソースの突き合わせを優先する / 各項目に確度 (High / Med / Low) を付す / 事実と推測を分ける / 無料の手段のみ (WebSearch / WebFetch / curl)
- 絶対パス (あれば): `artist.yaml` / `strategy/direction.md` / 既存の `strategy/trends/` の直近ファイル (差分観点で見てもらう)

返してもらうもの: トレンドの要点 / 根拠 (出典付き) / このアーティスト (または Suno 制作) への示唆 2〜3 個。

## Step 3 — 保存

`strategy/trends/YYYY-MM-DD_<topic>.md` に保存する (topic は英語小文字 + ハイフン。例: `2026-07-10_jpop-summer-trends.md`):

```bash
mkdir -p "$ARTIST_ROOT/strategy/trends"
```

内容の構成: 調査日 / トピック / 要点 / 詳細 (出典 URL + 取得日 + 確度付き) / このアーティストへの示唆。

- `artist=no` のディレクトリでは、アーティストディレクトリではない可能性があるため、**保存してよいか先に確認する** (不要ならチャット報告のみで完結)

## Step 4 — 報告と提案

- 要点と示唆を P に報告する
- **「次の曲に活かします?」と提案する** — 受けたら `song` スキルのフローへ (director のブリーフ作成時に、この調査ファイルの絶対パスをプロンプトに渡す)
- 数値や方針に関わる大きな発見なら「方針会議 (meeting) やります?」も添える
- 調査中に **Suno 本体の仕様変更・新モデル・新機能の兆候**を見つけたら、`update-spec` の実行を提案する
- 調査中に **Style 欄で効く/効かない語彙の新発見** (新しく効く記述子・効かなくなった定番語など) があれば、`update-spec` の **style-vocab 対象**での実行を提案する
- ジャンルプレイブック (`skills/composing/`) の骨格と食い違う**恒常的な変化** (一時の流行でなく構造の変化) を見つけたら、プラグインのリリース課題として P に報告する (プレイブックは同梱のみで、その場では書き換えない)

## 後処理

- `.production/log.md` に 1 行追記する (例: `2026-07-10 15:00 trend: jpop-summer-trends 調査・保存`)
- `.production/state.md` を最新化する
