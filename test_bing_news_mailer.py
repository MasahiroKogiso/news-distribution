import os
import json
import requests
import msal
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()  # .env をロード

# ===========================
# 1. 環境変数の取得
# ===========================
BING_NEWS_API_KEY = os.getenv("BING_NEWS_API_KEY")
BING_NEWS_ENDPOINT = os.getenv('BING_NEWS_ENDPOINT')
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

SHARED_MAILBOX = "news_updates@db.nkc.co.jp"
MY_EMAIL = "mk11765@ad.nkc.co.jp"
KEYWORD = os.getenv("KEYWORD", "生成AI")   # 検索キーワード

if not BING_NEWS_API_KEY or not BING_NEWS_ENDPOINT:
    raise ValueError("Bing News APIの環境変数が設定されていません。")
if not (TENANT_ID and CLIENT_ID and CLIENT_SECRET):
    raise ValueError("Graph API用の環境変数(TENANT_ID, CLIENT_ID, CLIENT_SECRET)が不足しています。")
if not (SHARED_MAILBOX and MY_EMAIL):
    raise ValueError("SHARED_MAILBOX, YOUR_EMAIL が設定されていません。")


# ===========================
# 2. Bing Newsから1件取得する関数
# ===========================
def fetch_one_news(keyword: str):
    """
    指定キーワードのニュースを1件だけ取得して返す。
    取得できなかった場合は None を返す。
    """
    url = f"{BING_NEWS_ENDPOINT}v7.0/news/search"
    headers = {"Ocp-Apim-Subscription-Key": BING_NEWS_API_KEY}
    
    # 検索パラメータ - 1件だけ取得
    params = {
        "q": keyword,
        "count": 1,
        "mkt": "ja-JP",
        "sortBy": "Date"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        articles = data.get("value", [])
        if not articles:
            return None

        article = articles[0]  # 先頭1件を返す
        return {
            "title": article.get("name", "タイトルなし"),
            "author": article.get("provider", [{}])[0].get("name", "不明"),
            "published_at": article.get("datePublished", "日時不明"),
            "description": article.get("description", ""),
            "url": article.get("url", ""),
            "image": article.get("image", {}).get("thumbnail", {}).get("contentUrl", "")
        }
    except Exception as e:
        print("Bing News API呼び出し中にエラー:", e)
        return None


# ===========================
# 3. HTMLテーブルに整形
# ===========================
def format_news_table(article: dict) -> str:
    """
    1件のニュース記事をHTMLテーブル形式に整形する。
    """
    if not article:
        return "<p>ニュース情報がありません。</p>"

    # 日付フォーマット
    published_at = article.get("published_at", "")
    try:
        published_datetime = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ')
        published_at = published_datetime.strftime('%Y/%m/%d')
    except ValueError:
        published_at = published_at.split('T')[0].replace('-', '/')

    # 画像
    if article["image"]:
        image_html = f'<img src="{article["image"]}" width="100">'
    else:
        image_html = '画像なし'

    # タイトルはリンク化
    title_link = f'<a href="{article["url"]}" target="_blank">{article["title"]}</a>'

    html_content = f"""
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr style="background-color: #f2f2f2;">
            <th style="width:15%;">画像</th>
            <th style="width:25%;">タイトル</th>
            <th style="width:10%;">著者</th>
            <th style="width:15%;">公開日時</th>
            <th style="width:35%;">説明</th>
        </tr>
        <tr>
            <td style="text-align:center;">{image_html}</td>
            <td>{title_link}</td>
            <td>{article["author"]}</td>
            <td>{published_at}</td>
            <td>{article["description"]}</td>
        </tr>
    </table>
    """
    return html_content


# ===========================
# 4. Graph APIでメール送信
# ===========================
def send_email_via_graph(html_body: str, subject: str, from_mailbox: str, to_mail: str):
    """
    共有メールボックス (from_mailbox) から、
    指定アドレス (to_mail) へ HTMLメールを送信する。
    """
    # --- 4-1. トークンを取得 (Client Credential Flow) ---
    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    app = msal.ConfidentialClientApplication(
        client_id=CLIENT_ID,
        authority=authority,
        client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if not "access_token" in result:
        raise Exception("アクセストークン取得に失敗しました: " + str(result))

    access_token = result["access_token"]

    # --- 4-2. /sendMail エンドポイントを呼ぶ ---
    endpoint = f"https://graph.microsoft.com/v1.0/users/{from_mailbox}/sendMail"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # HTML本文を送る場合は contentType="HTML" にする
    message = {
        "subject": subject,
        "body": {
            "contentType": "HTML",
            "content": html_body
        },
        "toRecipients": [
            {"emailAddress": {"address": to_mail}}
        ]
    }

    payload = {
        "message": message,
        "saveToSentItems": "true"
    }

    response = requests.post(endpoint, headers=headers, json=payload)
    if response.status_code == 202:
        print("メール送信に成功しました。")
    else:
        print("メール送信に失敗しました。")
        print("status code:", response.status_code)
        print("response:", response.text)


# ===========================
# メイン処理
# ===========================
def main():
    print(f"キーワード '{KEYWORD}' に関するニュースをBing News APIで取得します...")

    article = fetch_one_news(KEYWORD)
    if not article:
        print("ニュースが取得できませんでした。終了します。")
        return

    # テーブル化
    html_table = format_news_table(article)
    print("取得したニュース:")
    print(f"- タイトル: {article['title']}")
    print(f"- URL: {article['url']}")

    # メール件名・本文を設定して送信
    subject = f"[Bing News] {article['title']}"
    body_html = f"""
    <p>以下は Bing News API で取得した 1 件のニュースです (キーワード: {KEYWORD}).</p>
    <hr>
    {html_table}
    """

    print(f"共有メールボックス '{SHARED_MAILBOX}' から '{MY_EMAIL}' 宛にメール送信します...")
    send_email_via_graph(
        html_body=body_html,
        subject=subject,
        from_mailbox=SHARED_MAILBOX,
        to_mail=MY_EMAIL
    )


if __name__ == "__main__":
    main()
