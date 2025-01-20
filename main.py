import msal
import requests
from dotenv import load_dotenv
import os

# .envファイルから環境変数を読み込む
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")

# スコープ
scopes = ['User.Read']

# トークンを取得する関数
def get_access_token():
    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    app = msal.PublicClientApplication(CLIENT_ID, authority=authority)
    
    # ユーザーの認証
    flow = app.initiate_device_flow(scopes=scopes)
    if "user_code" not in flow:
        raise Exception("Failed to create device flow")
    
    print(flow["message"])
    result = app.acquire_token_by_device_flow(flow)
    
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception("Failed to obtain access token")

# ユーザープロフィール情報を取得する関数
def get_user_profile(access_token):
    endpoint = "https://graph.microsoft.com/v1.0/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:  # 200は成功
        print("User profile obtained successfully!")
        print(response.json())
    else:
        print(f"Failed to obtain user profile: {response.status_code}")
        print(response.json())

# メイン処理
if __name__ == "__main__":
    try:
        print("Attempting to get access token...")
        token = get_access_token()
        print("Access token obtained:", token)
        
        print("Attempting to get user profile...")
        get_user_profile(token)
    except Exception as e:
        print(f"An error occurred: {e}")