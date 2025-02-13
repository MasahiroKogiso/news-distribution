import os
import msal
from dotenv import load_dotenv

# 環境変数をロード
load_dotenv()

def get_access_token():
    """Client Credential Flow でアクセストークンを取得し、返す。失敗時は例外を投げる。"""
    TENANT_ID = os.getenv("TENANT_ID")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")

    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    scopes = ["https://graph.microsoft.com/.default"]  # Application Permissions

    # MSALでConfidentialClientApplicationを生成
    app = msal.ConfidentialClientApplication(
        client_id=CLIENT_ID,
        authority=authority,
        client_credential=CLIENT_SECRET
    )

    # Client Credential Flowでトークンを取得
    result = app.acquire_token_for_client(scopes=scopes)

    if "access_token" in result:
        return result["access_token"]
    else:
        # トークン取得失敗時はエラー内容を表示して例外を投げる
        error = result.get("error")
        desc = result.get("error_description")
        raise Exception(f"Failed to acquire token. Error: {error}, Description: {desc}")
