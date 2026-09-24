# Hướng dẫn Push Code lên GitHub

## Bước 1: Tạo Repository trên GitHub

1. Truy cập [github.com](https://github.com) và đăng nhập
2. Click vào "+" → "New repository"
3. Điền thông tin:
   - **Repository name**: `dtk-crm` (hoặc tên bạn muốn)
   - **Description**: "CRM Bất động sản với PWA Offline support"
   - **Public/Private**: Chọn Public (miễn phí) hoặc Private (có phí)
   - **KHÔNG** check: "Add a README file", "Add .gitignore", "Choose a license"
4. Click "Create repository"

## Bước 2: Chuẩn bị Local Repository

Đã thực hiện:
- ✅ Khởi tạo git: `git init`
- ✅ Tạo file .gitignore (để tránh push file nhạy cảm)

## Bước 3: Thay đổi file nhạy cảm

⚠️ **QUAN TRỌNG**: File `Data/credentials.json` chứa thông tin Google API - KHÔNG ĐƯỢC PUSH LÊN GITHUB!

1. **Backup credentials.json**:
```bash
copy Data\credentials.json Data\credentials.json.backup
```

2. **Xóa credentials.json khỏi git tracking** (nếu đã add):
```bash
git rm --cached Data/credentials.json
```

3. **Đảm bảo credentials.json trong .gitignore** (đã có sẵn)

## Bước 4: Add và Commit Code

Chạy các lệnh sau trong terminal:

```bash
cd D:\DSH_WP\DTK_CRM

# Add tất cả file
git add .

# Kiểm tra những gì sẽ được commit
git status

# Commit code
git commit -m "Add PWA support for CRM - Offline capability for Android tablets"
```

## Bước 5: Connect với GitHub Repository

Copy lệnh từ GitHub (sau khi tạo repository xong):

```bash
# Đổi URL thành repository của bạn
git remote add origin https://github.com/USERNAME/dtk-crm.git

# Hoặc nếu dùng SSH:
git remote add origin git@github.com:USERNAME/dtk-crm.git
```

## Bước 6: Push lên GitHub

```bash
# Đổi tên branch thành main
git branch -M main

# Push code lên GitHub
git push -u origin main
```

Nếu được hỏi username/password:
- **Username**: GitHub username của bạn
- **Password**: GitHub Personal Access Token (không phải password thông thường)

### Tạo GitHub Personal Access Token:

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Đặt tên: "DTK CRM Deploy"
4. Select scopes: `repo` (để push code)
5. Click "Generate token"
6. **COPY TOKEN** (chỉ hiện 1 lần)
7. Dùng token này làm password khi git push

## Bước 7: Xác nhận trên GitHub

1. Truy cập repository trên GitHub
2. Kiểm tra các file đã được push:
   - ✅ `data/crm_app.py`
   - ✅ `.streamlit/static/manifest.json`
   - ✅ `.streamlit/static/service-worker.js`
   - ✅ `.streamlit/static/indexeddb-manager.js`
   - ✅ `.streamlit/static/pwa-integration.js`
   - ✅ `.streamlit/static/icon-192.png`
   - ✅ `.streamlit/static/icon-512.png`
   - ✅ `.streamlit/config.toml`
   - ✅ `PWA_ANDROID_GUIDE.md`
   - ✅ `PWA_README.md`

3. **KIỂM TRA QUAN TRỌNG**: Đảm bảo `Data/credentials.json` KHÔNG có trên GitHub

## Bước 8: Setup Credentials cho Deploy

Vì `credentials.json` không được push, bạn cần setup lại khi deploy:

### Cách 1: Streamlit Cloud Secrets (Khuyên dùng)

1. Trên Streamlit Cloud, trong app settings
2. Thêm secrets:
   - Key: `GOOGLE_CREDENTIALS`
   - Value: Nội dung file `credentials.json` (dạng JSON string)

3. Sửa code để đọc từ secrets:
```python
import streamlit as st
import json

# Thay thế đọc file credentials.json
if "GOOGLE_CREDENTIALS" in st.secrets:
    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    # Sử dụng creds_dict thay vì file
else:
    # Fallback cho local development
    CREDS_JSON = os.path.join(BASE_DIR, "credentials.json")
```

### Cách 2: Upload credentials.json thủ công

1. Sau khi deploy, upload `credentials.json` lên server
2. Hoặc dùng environment variables

## Troubleshooting

### Lỗi "fatal: not a git repository"
```bash
cd D:\DSH_WP\DTK_CRM
git init
```

### Lỗi "Permission denied"
- Kiểm tra Personal Access Token có đúng scope `repo`
- Xác nhận token chưa hết hạn

### Lỗi "refusing to merge unrelated histories"
```bash
git pull origin main --allow-unrelated-histories
git push origin main
```

### File credentials.json vẫn bị push
```bash
# Xóa khỏi git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch Data/credentials.json" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (CẢNH BÁO: sẽ xóa history)
git push origin main --force
```

## Sau khi Push thành công

1. **Deploy lên Streamlit Cloud**:
   - Truy cập [share.streamlit.io](https://share.streamlit.io)
   - "New app" → Connect GitHub repository
   - Main file: `data/crm_app.py`
   - Python version: 3.9+

2. **Test PWA**:
   - Truy cập URL từ Streamlit Cloud
   - Test trên Android tablet theo hướng dẫn trong `PWA_ANDROID_GUIDE.md`

---

**Lưu ý quan trọng**:
- 🔒 KHÔNG BAO GIỜ push file chứa credentials/API keys lên GitHub
- 🔄 Luôn dùng .gitignore để bảo vệ file nhạy cảm
- 🔐 Sử dụng environment variables hoặc secrets cho production