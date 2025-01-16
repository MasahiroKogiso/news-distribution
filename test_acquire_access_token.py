import msal
from dotenv import load_dotenv
import os

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
tenant_id = os.getenv("TENANT_ID")

# Azure AD Authority
authority = f"https://login.microsoftonline.com/{tenant_id}"

# 要求するスコープ一覧 (.default を指定)
scope = ["https://graph.microsoft.com/.default"]

# MSALのConfidentialClientApplicationを初期化
app = msal.ConfidentialClientApplication(
    client_id=client_id,
    client_credential=client_secret,
    authority=authority
)

# アクセストークンの取得
result = app.acquire_token_for_client(scopes=scope)

if "access_token" in result:
    access_token = result["access_token"]
    print("Access Token:", access_token)
else:
    print("Error:", result.get("error"))
    print("Description:", result.get("error_description"))
