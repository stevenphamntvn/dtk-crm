# Các bước tiếp theo để Push lên GitHub

## ✅ Đã hoàn thành:
- ✅ Khởi tạo git repository
- ✅ Tạo .gitignore (đã loại bỏ file nhạy cảm)
- ✅ Add và commit code
- ✅ Đổi branch thành main

## 🔜 Các bước bạn cần làm:

### Bước 1: Tạo Repository trên GitHub

1. Truy cập [github.com](https://github.com) và đăng nhập
2. Click vào "+" → "New repository"
3. Điền thông tin:
   - **Repository name**: `dtk-crm` (hoặc tên bạn muốn)
   - **Description**: "CRM Bất động sản với PWA Offline support"
   - **Public/Private**: Chọn Public (miễn phí)
   - **KHÔNG** check: "Add a README file", "Add .gitignore", "Choose a license"
4. Click "Create repository"

### Bước 2: Connect và Push Code

Sau khi tạo repository xong, GitHub sẽ hiện các lệnh. Copy và chạy lệnh sau trong terminal:

```bash
cd D:\DSH_WP\DTK_CRM

# Thay URL bằng repository của bạn
git remote add origin https://github.com/USERNAME/dtk-crm.git

# Push code lên GitHub
git push -u origin main
```

### Bước 3: Xử lý Authentication

Khi được hỏi username/password:
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

### Bước 4: Kiểm tra trên GitHub

1. Truy cập repository trên GitHub
2. Kiểm tra các file đã được push
3. **QUAN TRỌNG**: Đảm bảo `Data/credentials.json` KHÔNG có trên GitHub

### Bước 5: Deploy lên Streamlit Cloud

1. Truy cập [share.streamlit.io](https://share.streamlit.io)
2. "New app" → Connect GitHub repository
3. Cấu hình:
   - Main file path: `data/crm_app.py`
   - Python version: 3.9+
   - Requirements: Copy từ `Support/requirements.txt`

### Bước 6: Setup Credentials cho Production

Vì `credentials.json` không được push, bạn cần:

**Option 1: Streamlit Cloud Secrets (Khuyên dùng)**
1. Trong Streamlit Cloud app settings
2. Thêm secrets:
   - Key: `GOOGLE_CREDENTIALS`
   - Value: Nội dung file `credentials.json` (copy từ file local)

**Option 2: Sửa code để đọc từ secrets**
Bạn cần sửa `data/crm_app.py` để đọc credentials từ secrets thay vì file:

```python
import streamlit as st
import json
import tempfile
import os

# Thay thế phần đọc credentials.json
if "GOOGLE_CREDENTIALS" in st.secrets:
    # Tạo temporary file từ secrets
    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(creds_dict, f)
        CREDS_JSON = f.name
else:
    # Fallback cho local development
    CREDS_JSON = os.path.join(BASE_DIR, "credentials.json")
```

### Bước 7: Test PWA trên Android

1. Truy cập URL từ Streamlit Cloud
2. Mở trong Chrome trên Android tablet
3. "Add to Home Screen"
4. Test offline mode theo hướng dẫn trong `PWA_ANDROID_GUIDE.md`

---

## 📝 Lệnh git nhanh tham khảo:

```bash
# Xem status
git status

# Xem remote
git remote -v

# Thay đổi remote URL
git remote set-url origin https://github.com/NEW_USERNAME/NEW_REPO.git

# Force push (cẩn thận!)
git push -f origin main
```

## ⚠️ Lưu ý quan trọng:

- 🔒 File `Data/credentials.json` đã được .gitignore bảo vệ - KHÔNG ĐƯỢC PUSH
- 🔐 Luôn dùng secrets/environment variables cho production credentials
- 🔄 Personal Access Token cần scope `repo` để push code
- 📱 Test kỹ PWA trên Android trước khi production

---

**Khi nào cần giúp đỡ**:
- Nếu gặp lỗi khi push, copy error message và hỏi
- Nếu cần trợ giúp setup Streamlit Cloud secrets, tôi có thể hướng dẫn chi tiết
- Nếu muốn test PWA local trước khi deploy, tôi có thể hướng dẫn setup HTTPS local