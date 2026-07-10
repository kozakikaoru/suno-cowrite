#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""YouTube Analytics API クライアント (suno-artist-production)

外部ライブラリを使わず (Python 3 標準ライブラリのみ)、OAuth 2.0 (インストール
アプリ型 + PKCE) で YouTube Analytics API v2 / YouTube Data API v3 に接続する。

サブコマンド:
  auth    初回のブラウザ認証 (localhost ループバックで認可コードを受領)
  report  分析数値を取得し、JSON を stdout に出力
  status  設定ファイルと認証状態の確認

認証情報の置き場所 (${XDG_CONFIG_HOME:-~/.config}/suno-artist-production/):
  client_secret.json  Google Cloud Console で作成した OAuth クライアント (ユーザーが配置)
  token.json          アクセストークン (本スクリプトが保存、パーミッション 600)

終了コード: 0 = 成功 / 1 = 実行時エラー / 2 = 要セットアップ (未配置・未認証・要再認証)
"""

import argparse
import base64
import datetime
import hashlib
import http.server
import json
import os
import secrets
import stat
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

# =============================================================================
# 定数
# =============================================================================

SCOPES = (
    "https://www.googleapis.com/auth/yt-analytics.readonly "
    "https://www.googleapis.com/auth/youtube.readonly"
)
DEFAULT_AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
DEFAULT_TOKEN_URI = "https://oauth2.googleapis.com/token"
ANALYTICS_REPORTS_URL = "https://youtubeanalytics.googleapis.com/v2/reports"
DATA_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

AUTH_TIMEOUT_SEC = 300          # ブラウザ認証の待ち時間上限
HTTP_TIMEOUT_SEC = 30           # API 呼び出しのタイムアウト
TOKEN_REFRESH_MARGIN_SEC = 60   # 期限のこの秒数前から refresh する

EXIT_OK = 0
EXIT_ERROR = 1                  # API エラーなどの実行時エラー
EXIT_SETUP = 2                  # ユーザー操作が必要 (未配置・未認証・要再認証)

# refresh_token 失効 (invalid_grant) 時の案内文
REAUTH_GUIDANCE = (
    "再認証が必要: yt_analytics.py auth を実行してください。"
    "OAuth 同意画面がテストモードだと 7 日で失効します — 本番公開を推奨"
)


class CliError(Exception):
    """ユーザー向けメッセージと終了コードを持つエラー"""

    def __init__(self, message, exit_code=EXIT_ERROR):
        super().__init__(message)
        self.exit_code = exit_code


# =============================================================================
# 設定ファイルの置き場所
# =============================================================================

def config_dir():
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "suno-artist-production")


def client_secret_path():
    return os.path.join(config_dir(), "client_secret.json")


def token_path():
    return os.path.join(config_dir(), "token.json")


def ensure_config_dir():
    path = config_dir()
    os.makedirs(path, mode=0o700, exist_ok=True)
    try:
        os.chmod(path, 0o700)
    except OSError:
        pass  # 権限を変えられない環境では作成できていれば良しとする


def client_secret_guidance(path):
    """client_secret.json 未配置時のセットアップ手順 (日本語)"""
    return "\n".join([
        f"client_secret.json が見つかりません: {path}",
        "",
        "セットアップ手順 (無料 / 初回のみ 10〜15 分):",
        "  1. https://console.cloud.google.com/ にログインし、プロジェクトを作成する",
        "  2. 「API とサービス」→「ライブラリ」で次の 2 つの API を有効化する",
        "       - YouTube Analytics API",
        "       - YouTube Data API v3",
        "  3. 「OAuth 同意画面」を設定する (User Type は「外部」、テストユーザーに自分の Google アカウントを追加)",
        "     ※ テストモードのままだとリフレッシュトークンが 7 日で失効します。長期運用では本番公開を推奨します",
        "  4. 「認証情報」→「認証情報を作成」→「OAuth クライアント ID」で、種類「デスクトップ アプリ」を作成する",
        "  5. 作成したクライアントの JSON をダウンロードし、次のパスに置く:",
        f"       {path}",
        "  6. 置いたら `python3 yt_analytics.py auth` を実行してブラウザ認証を完了する",
    ])


def load_client_secret():
    """client_secret.json を読み込む。未配置・形式不正は CliError (終了コード 2)"""
    path = client_secret_path()
    if not os.path.isfile(path):
        raise CliError(client_secret_guidance(path), EXIT_SETUP)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise CliError(
            f"client_secret.json を読み込めません ({e})。"
            f"Google Cloud Console からダウンロードし直して配置してください: {path}",
            EXIT_SETUP,
        )
    entry = data.get("installed") or data.get("web")
    if not isinstance(entry, dict) or not entry.get("client_id"):
        raise CliError(
            "client_secret.json の形式が想定と異なります ('installed' か 'web' キーの下に client_id が必要)。"
            "OAuth クライアントの種類は「デスクトップ アプリ」を選んでください。",
            EXIT_SETUP,
        )
    return {
        "client_id": entry["client_id"],
        "client_secret": entry.get("client_secret", ""),
        "auth_uri": entry.get("auth_uri", DEFAULT_AUTH_URI),
        "token_uri": entry.get("token_uri", DEFAULT_TOKEN_URI),
    }


# =============================================================================
# token.json の読み書き
# =============================================================================

def load_token_quiet():
    """token.json を読む。無い・壊れている場合は None (status / auth 用)"""
    try:
        with open(token_path(), encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def load_token_strict():
    """token.json を読む。無い・壊れている場合は CliError (report 用)"""
    path = token_path()
    if not os.path.isfile(path):
        raise CliError(
            "未認証です。まず `python3 yt_analytics.py auth` を実行してブラウザ認証を完了してください。\n"
            "(client_secret.json が未配置の場合は、auth 実行時に配置手順を案内します)",
            EXIT_SETUP,
        )
    token = load_token_quiet()
    if not token or not token.get("access_token"):
        raise CliError(
            "token.json が壊れているか内容が不正です。`python3 yt_analytics.py auth` で再認証してください。",
            EXIT_SETUP,
        )
    return token


def save_token(token):
    """token.json をパーミッション 600 で保存する"""
    ensure_config_dir()
    path = token_path()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(token, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.chmod(path, 0o600)  # 既存ファイルを上書きした場合も 600 に揃える


# =============================================================================
# HTTP ヘルパー
# =============================================================================

def _post_form(url, fields):
    """フォームエンコードで POST し、JSON を返す (HTTPError は呼び出し側で処理)"""
    data = urllib.parse.urlencode(fields).encode("ascii")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SEC) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _read_error_body(err):
    """HTTPError のボディを JSON として読む (読めなければ raw で返す)"""
    try:
        body = err.read().decode("utf-8", errors="replace")
    except Exception:
        body = ""
    try:
        parsed = json.loads(body)
        return parsed if isinstance(parsed, dict) else {"raw": body}
    except (json.JSONDecodeError, ValueError):
        return {"raw": body}


def _api_http_error(err):
    """Google API の HTTPError を日本語の CliError に整形する"""
    info = _read_error_body(err)
    error = info.get("error")
    message = ""
    reason = ""
    if isinstance(error, dict):
        message = error.get("message", "")
        errors = error.get("errors") or []
        if errors and isinstance(errors[0], dict):
            reason = errors[0].get("reason", "")
        reason = reason or error.get("status", "")
    elif isinstance(error, str):
        reason = error
        message = info.get("error_description", "")
    detail = f" (原文: {message})" if message else ""
    if err.code == 401:
        return CliError(f"アクセストークンが拒否されました。`python3 yt_analytics.py auth` で再認証してください{detail}", EXIT_SETUP)
    if err.code == 403 and reason in ("quotaExceeded", "rateLimitExceeded", "userRateLimitExceeded", "dailyLimitExceeded"):
        return CliError(f"API の割り当て (quota) を超過しました。時間を置いて再実行してください{detail}", EXIT_ERROR)
    if err.code == 403:
        return CliError(
            "アクセスが拒否されました。Google Cloud Console で YouTube Analytics API / YouTube Data API v3 が"
            f"有効になっているか、認証したアカウントが対象チャンネルの所有者かを確認してください{detail}",
            EXIT_ERROR,
        )
    if err.code == 400:
        return CliError(f"リクエストが不正と判定されました (HTTP 400){detail}", EXIT_ERROR)
    summary = message or info.get("raw", "") or str(err)
    label = f"HTTP {err.code}" + (f" / {reason}" if reason else "")
    return CliError(f"API エラー ({label}): {summary}", EXIT_ERROR)


def api_get(url, params, access_token):
    """Bearer トークン付き GET。エラーは日本語整形済みの CliError にして投げる"""
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(full_url, headers={"Authorization": f"Bearer {access_token}"})
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SEC) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise _api_http_error(e)
    except urllib.error.URLError as e:
        raise CliError(f"API に接続できません: {e.reason}", EXIT_ERROR)


# =============================================================================
# トークンの取得と更新
# =============================================================================

def refresh_access_token(token, client):
    """refresh_token でアクセストークンを更新し、token.json を上書きする"""
    fields = {
        "client_id": client["client_id"],
        "refresh_token": token["refresh_token"],
        "grant_type": "refresh_token",
    }
    if client["client_secret"]:
        fields["client_secret"] = client["client_secret"]
    try:
        resp = _post_form(client["token_uri"], fields)
    except urllib.error.HTTPError as e:
        info = _read_error_body(e)
        if info.get("error") == "invalid_grant":
            # refresh_token 失効 (テストモード 7 日失効・取り消しなど)
            raise CliError(REAUTH_GUIDANCE, EXIT_SETUP)
        detail = info.get("error_description") or info.get("error") or info.get("raw") or str(e)
        raise CliError(f"トークン更新に失敗しました (HTTP {e.code}): {detail}", EXIT_ERROR)
    except urllib.error.URLError as e:
        raise CliError(f"Google のトークンエンドポイントに接続できません: {e.reason}", EXIT_ERROR)
    if "access_token" not in resp:
        raise CliError(f"トークン更新の応答に access_token がありません: {resp}", EXIT_ERROR)
    token["access_token"] = resp["access_token"]
    token["expires_at"] = int(time.time()) + int(resp.get("expires_in", 3600))
    if resp.get("refresh_token"):
        token["refresh_token"] = resp["refresh_token"]
    if resp.get("scope"):
        token["scope"] = resp["scope"]
    save_token(token)
    return token


def get_valid_token():
    """有効なアクセストークンを持つ token dict を返す (必要なら自動 refresh)"""
    token = load_token_strict()
    try:
        expires_at = float(token.get("expires_at") or 0)
    except (TypeError, ValueError):
        expires_at = 0
    if time.time() < expires_at - TOKEN_REFRESH_MARGIN_SEC:
        return token
    if not token.get("refresh_token"):
        raise CliError(REAUTH_GUIDANCE, EXIT_SETUP)
    client = load_client_secret()
    return refresh_access_token(token, client)


# =============================================================================
# auth サブコマンド (インストールアプリ型 OAuth + PKCE)
# =============================================================================

class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    """OAuth リダイレクトを 1 回だけ受けるハンドラ"""

    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if "code" not in params and "error" not in params:
            # favicon などの無関係なリクエストは無視して待ち続ける
            self.send_response(404)
            self.end_headers()
            return
        self.server.oauth_params = params
        body = (
            "<!doctype html><html lang='ja'><head><meta charset='utf-8'>"
            "<title>認証完了</title></head>"
            "<body style='font-family: sans-serif; margin: 3em;'>"
            "<p>認証が完了しました。このタブを閉じて、ターミナルに戻ってください。</p>"
            "</body></html>"
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass  # アクセスログは出さない


def cmd_auth(args):
    ensure_config_dir()
    client = load_client_secret()

    # PKCE (S256): verifier は 43〜128 文字の URL セーフ文字列
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(64)).rstrip(b"=").decode("ascii")
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
    state = secrets.token_urlsafe(16)

    # localhost の空きポートで一時 HTTP サーバを立てる (ループバックフロー)
    server = http.server.HTTPServer(("127.0.0.1", 0), _CallbackHandler)
    server.oauth_params = None
    server.timeout = 1.0
    port = server.server_address[1]
    redirect_uri = f"http://127.0.0.1:{port}"

    auth_url = client["auth_uri"] + "?" + urllib.parse.urlencode({
        "client_id": client["client_id"],
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": SCOPES,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",  # refresh_token を確実に発行させる
    })

    print("ブラウザで Google 認証を開きます。自動で開かない場合は、次の URL を手動で開いてください:")
    print()
    print(auth_url)
    print()
    print(f"({redirect_uri} で認証完了を待っています。最大 {AUTH_TIMEOUT_SEC // 60} 分でタイムアウト)")
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass  # 開けない環境では手動で URL を開いてもらう

    deadline = time.time() + AUTH_TIMEOUT_SEC
    try:
        while server.oauth_params is None and time.time() < deadline:
            server.handle_request()
    finally:
        server.server_close()

    params = server.oauth_params
    if params is None:
        raise CliError("認証がタイムアウトしました。もう一度 `auth` を実行してください。", EXIT_ERROR)
    if "error" in params:
        error = params["error"][0]
        if error == "access_denied":
            raise CliError("認証がキャンセルされました (同意画面で拒否)。やり直す場合は再度 `auth` を実行してください。", EXIT_ERROR)
        raise CliError(f"認証エラーが返されました: {error}", EXIT_ERROR)
    if params.get("state", [None])[0] != state:
        raise CliError("state が一致しません (CSRF の可能性)。もう一度 `auth` をやり直してください。", EXIT_ERROR)
    code = params.get("code", [None])[0]
    if not code:
        raise CliError("認可コードを受け取れませんでした。もう一度 `auth` を実行してください。", EXIT_ERROR)

    # 認可コード → トークン交換
    fields = {
        "code": code,
        "client_id": client["client_id"],
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
        "code_verifier": verifier,
    }
    if client["client_secret"]:
        fields["client_secret"] = client["client_secret"]
    try:
        resp = _post_form(client["token_uri"], fields)
    except urllib.error.HTTPError as e:
        info = _read_error_body(e)
        detail = info.get("error_description") or info.get("error") or info.get("raw") or str(e)
        raise CliError(f"トークン交換に失敗しました (HTTP {e.code}): {detail}", EXIT_ERROR)
    except urllib.error.URLError as e:
        raise CliError(f"Google のトークンエンドポイントに接続できません: {e.reason}", EXIT_ERROR)
    if "access_token" not in resp:
        raise CliError(f"トークン交換の応答に access_token がありません: {resp}", EXIT_ERROR)

    old_token = load_token_quiet() or {}
    token = {
        "access_token": resp["access_token"],
        "refresh_token": resp.get("refresh_token") or old_token.get("refresh_token"),
        "token_type": resp.get("token_type", "Bearer"),
        "scope": resp.get("scope", SCOPES),
        "expires_at": int(time.time()) + int(resp.get("expires_in", 3600)),
        "obtained_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    save_token(token)

    print()
    print("認証に成功しました。")
    print(f"トークンを保存しました: {token_path()} (パーミッション 600)")
    if not token["refresh_token"]:
        print("注意: refresh_token が発行されませんでした。期限切れ時に再認証が必要になります。", file=sys.stderr)
    print("次の一歩: `python3 yt_analytics.py report --days 28` で数値を取得できます")
    return EXIT_OK


# =============================================================================
# report サブコマンド
# =============================================================================

def _resolve_video_titles(video_ids, access_token):
    """YouTube Data API で動画 ID → タイトル/公開日を解決する (1 回 50 件まで)"""
    resolved = {}
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i + 50]
        data = api_get(
            DATA_VIDEOS_URL,
            {"part": "snippet", "id": ",".join(chunk), "maxResults": "50"},
            access_token,
        )
        for item in data.get("items", []):
            snippet = item.get("snippet") or {}
            resolved[item.get("id")] = {
                "title": snippet.get("title"),
                "published_at": snippet.get("publishedAt"),
            }
    return resolved


def cmd_report(args):
    if args.days < 1:
        raise CliError("--days は 1 以上を指定してください。", EXIT_ERROR)
    if not (1 <= args.max_results <= 200):
        raise CliError("--max-results は 1〜200 の範囲で指定してください。", EXIT_ERROR)

    token = get_valid_token()
    access_token = token["access_token"]

    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=args.days)
    base_params = {
        "ids": "channel==MINE",
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
    }

    if args.mode == "channel":
        metrics = "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained"
        params = dict(base_params, metrics=metrics)
        if args.daily:
            params.update(dimensions="day", sort="day")
    elif args.mode == "videos":
        metrics = "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage"
        params = dict(
            base_params, metrics=metrics,
            dimensions="video", sort="-views", maxResults=str(args.max_results),
        )
    else:  # traffic
        metrics = "views"
        params = dict(base_params, metrics=metrics, dimensions="insightTrafficSourceType", sort="-views")

    data = api_get(ANALYTICS_REPORTS_URL, params, access_token)
    headers = [h.get("name") for h in data.get("columnHeaders", [])]
    rows = [dict(zip(headers, row)) for row in (data.get("rows") or [])]

    result = {
        "mode": args.mode,
        "channel": "MINE",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "days": args.days,
        "metrics": metrics.split(","),
        "row_count": len(rows),
        "rows": rows,
        "fetched_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    if args.mode == "channel":
        result["granularity"] = "daily" if args.daily else "total"
    if not rows:
        result["note"] = "期間内のデータがありません (Analytics の集計は 24〜48 時間ほど遅れることがあります)"

    # videos モードは Data API で動画タイトルを解決して行に付与する
    if args.mode == "videos" and rows:
        video_ids = [r.get("video") for r in rows if r.get("video")]
        try:
            titles = _resolve_video_titles(video_ids, access_token)
            for row in rows:
                meta = titles.get(row.get("video"), {})
                row["title"] = meta.get("title")
                row["published_at"] = meta.get("published_at")
        except CliError as e:
            # タイトル解決の失敗は致命ではないので、数値だけでも返す
            result["note"] = f"動画タイトルの解決に失敗しました: {e}"
            print(f"警告: 動画タイトルの解決に失敗しました ({e})", file=sys.stderr)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return EXIT_OK


# =============================================================================
# status サブコマンド
# =============================================================================

def cmd_status(args):
    print("=== YouTube Analytics 接続状況 ===")
    print(f"設定ディレクトリ: {config_dir()}")

    # client_secret.json
    client_ok = False
    if os.path.isfile(client_secret_path()):
        try:
            client = load_client_secret()
            client_ok = True
            client_id = client["client_id"]
            display_id = client_id if len(client_id) <= 64 else f"{client_id[:24]}...{client_id[-28:]}"
            print(f"client_secret.json : あり (client_id: {display_id})")
        except CliError as e:
            print("client_secret.json : あり (ただし形式エラー)")
            print(f"  → {e}")
    else:
        print("client_secret.json : なし — Google Cloud Console の OAuth クライアント JSON を配置してください")
        print("  (詳しい手順は `python3 yt_analytics.py auth` を実行すると表示されます)")

    # token.json
    token = load_token_quiet()
    token_usable = False
    if token is None:
        print("token.json         : なし (未認証)")
    else:
        print("token.json         : あり")
        try:
            mode = stat.S_IMODE(os.stat(token_path()).st_mode)
            if mode & 0o077:
                print(f"  パーミッション  : {mode:03o} — chmod 600 を推奨します (次回のトークン保存時に自動で 600 に戻ります)")
            else:
                print("  パーミッション  : 600 (OK)")
        except OSError:
            pass
        try:
            expires_at = float(token.get("expires_at") or 0)
        except (TypeError, ValueError):
            expires_at = 0
        now = time.time()
        if token.get("access_token") and expires_at > now + TOKEN_REFRESH_MARGIN_SEC:
            print(f"  アクセストークン: 有効 (残り約 {int((expires_at - now) // 60)} 分)")
            token_usable = True
        else:
            print("  アクセストークン: 期限切れ")
        if token.get("refresh_token"):
            print("  refresh_token   : あり (期限切れ時は自動更新されます)")
            token_usable = True
        else:
            print("  refresh_token   : なし — 期限切れ後は `auth` のやり直しが必要です")
        scope = token.get("scope", "")
        if "yt-analytics.readonly" in scope:
            print(f"  スコープ        : {scope}")
        else:
            print(f"  スコープ        : {scope or '(不明)'} — yt-analytics.readonly が含まれていません。`auth` をやり直してください")
            token_usable = False

    print("-" * 40)
    if client_ok and token is not None and token_usable:
        print("総合: 利用可能です — `python3 yt_analytics.py report` で数値を取得できます")
        return EXIT_OK
    steps = []
    if not client_ok:
        steps.append("client_secret.json を配置する")
    if token is None or not token_usable:
        steps.append("`python3 yt_analytics.py auth` でブラウザ認証する")
    print("総合: 未接続 — 次の手順が必要です: " + " → ".join(steps))
    return EXIT_SETUP


# =============================================================================
# エントリポイント
# =============================================================================

class JapaneseArgumentParser(argparse.ArgumentParser):
    """引数エラーを日本語プレフィックス付きで出す ArgumentParser"""

    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"引数エラー: {message}", file=sys.stderr)
        sys.exit(2)


def build_parser():
    parser = JapaneseArgumentParser(
        prog="yt_analytics.py",
        description=(
            "YouTube Analytics API から自分のチャンネルの数値を取得する CLI です。\n"
            "外部ライブラリ不要 (Python 3 標準ライブラリのみ)、認証は OAuth 2.0 (PKCE) を使います。"
        ),
        epilog=(
            "認証情報の置き場所: " + config_dir() + "\n"
            "  client_secret.json … Google Cloud Console で作成した OAuth クライアント (ユーザーが配置)\n"
            "  token.json         … 本スクリプトが保存するトークン (パーミッション 600)\n"
            "終了コード: 0 = 成功 / 1 = 実行時エラー / 2 = 要セットアップ (未配置・未認証・要再認証)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )
    parser.add_argument("-h", "--help", action="help", help="このヘルプを表示して終了します")
    sub = parser.add_subparsers(dest="command", metavar="<コマンド>")

    p_auth = sub.add_parser(
        "auth",
        help="初回のブラウザ認証を行い、token.json を保存します",
        description=(
            "インストールアプリ型 OAuth (ループバックフロー + PKCE) でブラウザ認証します。\n"
            "localhost の空きポートで一時サーバを立て、認可 URL をブラウザで開き、\n"
            "リダイレクトで認可コードを受け取ってトークンに交換します。"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )
    p_auth.add_argument("-h", "--help", action="help", help="このヘルプを表示して終了します")

    p_report = sub.add_parser(
        "report",
        help="分析数値を取得し、JSON を stdout に出力します (認証済み前提)",
        description=(
            "YouTube Analytics API v2 (ids=channel==MINE) から数値を取得し、JSON を stdout に出力します。\n"
            "モード:\n"
            "  channel … 期間の views / estimatedMinutesWatched / averageViewDuration /\n"
            "            averageViewPercentage / subscribersGained (既定は期間合計、--daily で日次)\n"
            "  videos  … 動画別の同指標を再生数順に上位 N 本 (動画タイトルは Data API で解決)\n"
            "  traffic … insightTrafficSourceType (流入経路) 別の views"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )
    p_report.add_argument("--days", type=int, default=28, metavar="N",
                          help="集計期間の日数 (今日から遡る)。既定: 28")
    p_report.add_argument("--mode", choices=["channel", "videos", "traffic"], default="channel",
                          help="取得モード (channel / videos / traffic)。既定: channel")
    p_report.add_argument("--daily", action="store_true",
                          help="channel モードで日次の内訳を出力します (他モードでは無視)")
    p_report.add_argument("--max-results", type=int, default=10, metavar="N",
                          help="videos モードで取得する動画数 (1〜200)。既定: 10")
    p_report.add_argument("-h", "--help", action="help", help="このヘルプを表示して終了します")

    p_status = sub.add_parser(
        "status",
        help="client_secret / token の有無と有効性を確認して表示します",
        description=(
            "設定ファイルの有無・トークンの有効期限・スコープなどを人間可読で表示します。\n"
            "終了コード: 0 = 利用可能 / 2 = 要セットアップ"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )
    p_status.add_argument("-h", "--help", action="help", help="このヘルプを表示して終了します")

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return EXIT_SETUP
    handlers = {"auth": cmd_auth, "report": cmd_report, "status": cmd_status}
    try:
        return handlers[args.command](args)
    except CliError as e:
        print(str(e), file=sys.stderr)
        return e.exit_code
    except KeyboardInterrupt:
        print("\n中断しました", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
