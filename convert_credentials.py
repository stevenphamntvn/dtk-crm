import json
import os

# Đọc file credentials.json
creds_path = 'Data/credentials.json'
if not os.path.exists(creds_path):
    print(f"Error: {creds_path} not found!")
    exit(1)

with open(creds_path, 'r', encoding='utf-8') as f:
    creds_json = json.load(f)

# Chuyển thành JSON string
creds_string = json.dumps(creds_json, ensure_ascii=False)

# Tạo TOML format cho Streamlit Cloud
toml_format_cloud = f'GOOGLE_CREDENTIALS = \'{creds_string}\''

# Tạo TOML format cho local development
toml_format_local = f'GOOGLE_CREDENTIALS = "{creds_string}"'

# Lưu ra file cho Streamlit Cloud
with open('streamlit_secrets.txt', 'w', encoding='utf-8') as f:
    f.write(toml_format_cloud)

print("Created streamlit_secrets.txt for Streamlit Cloud")
print("Copy content from this file to Streamlit Cloud Secrets")

# Tạo file secrets.toml cho local development
os.makedirs('.streamlit', exist_ok=True)
with open('.streamlit/secrets.toml', 'w', encoding='utf-8') as f:
    f.write(toml_format_local)

print("Created .streamlit/secrets.toml for local development")
print("Local development should now work without errors")