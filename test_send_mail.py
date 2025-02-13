import json
import requests
from auth_helper import get_access_token  # トークン取得を別ファイルに切り出している想定

def main():
    try:
        # アプリケーション (Client Credential Flow) でアクセストークン取得
        access_token = get_access_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # 送信元となる共有メールボックス
        shared_mailbox_address = "news_updates@db.nkc.co.jp"

        # 送信先（テスト用に自分のアドレスなど別アドレスを指定してOK）
        to_address = "mk11765@ad.nkc.co.jp"

        send_mail_endpoint = f"https://graph.microsoft.com/v1.0/users/{shared_mailbox_address}/sendMail"

        # 送信するメールの内容
        email_msg = {
            "message": {
                "subject": "Test Mail from Shared Mailbox via Graph API",
                "body": {
                    "contentType": "Text",
                    "content": "This mail is sent from a shared mailbox using Graph API with Application Permissions."
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": to_address
                        }
                    }
                ],
            },
            "saveToSentItems": "true"  # 送信済みフォルダに残したい場合
        }

        response = requests.post(
            send_mail_endpoint,
            headers=headers,
            data=json.dumps(email_msg)
        )

        if response.status_code == 202:
            print("共有メールボックスからのメール送信に成功しました。")
        else:
            print("メールの送信に失敗しました。")
            print("status code:", response.status_code)
            print("response:", response.text)

    except Exception as e:
        print("エラーが発生しました:", e)


if __name__ == "__main__":
    main()
