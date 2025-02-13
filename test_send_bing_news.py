# send_bing_news.py

import os
# import json
import requests
from dotenv import load_dotenv
from auth_helper import get_access_token

def main():
    try:
        # -----------------------------
        # 1. Bing Newsで記事を1件取得
        # -----------------------------
        load_dotenv()  # .env から環境変数ロード

        BING_API_KEY = os.getenv("BING_NEWS_API_KEY")
        if not BING_API_KEY:
            raise ValueError("BING_NEWS_API_KEY が設定されていません。")

        # 指定キーワードを環境変数またはコードで指定
        keyword = "生成AI"

        # Bing News Search APIエンドポイント
        # v7 API: https://api.bing.microsoft.com/v7.0/news/search
        endpoint = "https://api.bing.microsoft.com/v7.0/news/search"

        # 検索パラメータ (トップニュース1件のみ)
        params = {
            "q": keyword,
            "count": 1,         # 取得件数
            "mkt": "ja-JP",     # ニュースの言語や国/地域
            "sortBy": "Date"    # 最新順に取得するなど
        }

        # ヘッダーにSubscription-Keyをセット
        headers = {
            "Ocp-Apim-Subscription-Key": BING_API_KEY
        }

        response = requests.get(endpoint, params=params, headers=headers)
        response.raise_for_status()

        data = response.json()
        value = data.get("value", [])

        if len(value) == 0:
            print("該当するニュースが見つかりませんでした。")
            return

        # 1件目のニュースを取得
        first_news = value[0]
        news_title = first_news.get("name", "No Title")
        news_url = first_news.get("url", "No URL")
        news_desc = first_news.get("description", "")
        
        # ------------------------------------------
        # 2. Graph API で共有メールボックスから送信
        # ------------------------------------------
        access_token = get_access_token()

        # 実行時に設定する想定、または下記に直書き
        # 送信元となる共有メールボックス
        shared_mailbox_address = "news_updates@db.nkc.co.jp"
        to_address = "mk11765@ad.nkc.co.jp"

        send_mail_endpoint = f"https://graph.microsoft.com/v1.0/users/{shared_mailbox_address}/sendMail"
        graph_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # メールの本文や件名にニュース情報を組み込み
        subject = f"[Bing News] {news_title}"
        body_text = (
            f"キーワード '{keyword}' で検索したBing Newsから1件取得しました。\n"
            f"タイトル: {news_title}\n\n"
            f"URL: {news_url}\n\n"
            f"概要: {news_desc}"
        )

        email_msg = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "Text",
                    "content": body_text
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": to_address
                        }
                    }
                ]
            },
            "saveToSentItems": "true"
        }

        resp = requests.post(send_mail_endpoint, headers=graph_headers, json=email_msg)

        if resp.status_code == 202:
            print("共有メールボックスからニュースURL送信に成功しました。")
        else:
            print(f"ニュースURL送信に失敗しました: {resp.status_code}")
            print(resp.text)

    except Exception as e:
        print("エラーが発生しました:", e)


if __name__ == "__main__":
    main()
