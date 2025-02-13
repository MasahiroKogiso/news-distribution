import requests
import json
from auth_helper import get_access_token

def main():
    try:
        # アクセストークンを取得
        access_token = get_access_token()
        
        # Graph API呼び出し
        endpoint = "https://graph.microsoft.com/v1.0/users"
        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(endpoint, headers=headers)
        
        # if response.status_code == 200:
        #     users = response.json()
        #     print("ユーザー一覧の取得に成功しました。")
        #     print(users)
        # else:
        #     print(f"ユーザー取得に失敗しました。status_code={response.status_code}, response={response.text}")
        if response.status_code == 200:
            users = response.json()
            print("ユーザー一覧の取得に成功しました。")
            
            # ユーザー情報をファイルにエクスポート
            with open("users.json", "w", encoding="utf-8") as f:
                json.dump(users, f, ensure_ascii=False, indent=4)
            print("ユーザー情報がusers.jsonにエクスポートされました。")
        else:
            print(f"ユーザー取得に失敗しました。status_code={response.status_code}, response={response.text}")

    except Exception as e:
        print("エラーが発生しました:", e)


if __name__ == "__main__":
    main()
