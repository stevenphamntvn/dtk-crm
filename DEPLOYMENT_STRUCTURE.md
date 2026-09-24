# Cấu trúc Deployment cho CRM

## 🎯 Mục tiêu: Tách biệt Local và Online deployment

## 📁 Cấu trúc hiện tại (Đơn giản hóa)

```
D:\DSH_WP\DTK_CRM/
├── data/
│   ├── crm_app.py              # Code chính (tương thích cả local & online)
│   └── credentials.json         # Local credentials (KHÔNG push lên GitHub)
├── .streamlit/
│   ├── config.toml             # Cấu hình (giống CRM gốc)
│   └── secrets.toml.example    # Template cho local secrets
├── requirements.txt            # Dependencies cho cả 2 môi trường
└── [Các file khác]
```

## 🔧 Cách hoạt động:

### Local Development:
- Sử dụng `Data/credentials.json`
- Không cần file `.streamlit/secrets.toml`
- Chạy: `streamlit run data/crm_app.py`

### Online Deployment (Streamlit Cloud):
- Sử dụng Streamlit Cloud Secrets
- Không cần file credentials.json trên server
- Tự động detect environment

## 🚀 Quy trình Deploy:

### 1. Local Development:
```bash
cd D:\DSH_WP\DTK_CRM
streamlit run data/crm_app.py
```

### 2. Deploy lên Streamlit Cloud:
```bash
# Commit code (loại bỏ credentials.json)
git add .
git commit -m "Update CRM app"
git push origin main

# Streamlit Cloud sẽ tự deploy
```

### 3. Setup Secrets trên Streamlit Cloud:
- Vào app settings → Secrets
- Add: `GOOGLE_CREDENTIALS` với value từ credentials.json

## 🎯 Giải pháp đề xuất (Tách bản):

### Option 1: Keep Single Codebase (Khuyên dùng)
- **Ưu điểm:** Dễ maintain, code đồng bộ
- **Cách làm:** Code tự detect environment (đã implement)
- **File nhạy cảm:** credentials.json chỉ local, secrets chỉ cloud

### Option 2: Separate Branches
- **Local branch:** `local-dev` 
- **Online branch:** `main` (cho Streamlit Cloud)
- **Ưu điểm:** Tách biệt hoàn toàn
- **Nhược điểm:** Cần merge code giữa branches

### Option 3: Separate Folders
```
D:\DSH_WP\
├── DTK_CRM_LOCAL/          # Bản local đầy đủ
│   ├── data/credentials.json
│   └── .streamlit/secrets.toml
└── DTK_CRM_ONLINE/         # Bản cho deploy
    ├── data/crm_app.py     # Code tương thích cloud
    └── requirements.txt
```

## 💡 Khuyên dùng:

**Chọn Option 1 (Single Codebase):**
- Code hiện tại đã được viết để tương thích cả 2 môi trường
- Local dùng credentials.json
- Cloud dùng secrets
- Không cần tách branch hay folder

**Nếu thực sự cần tách:**
- Tạo branch `local-dev` cho local development
- Branch `main` cho Streamlit Cloud deployment
- Merge changes từ local → main khi cần deploy

## 🔧 Fix lỗi hiện tại:

Đã fix:
- ✅ Xóa file secrets.toml bị lỗi
- ✅ Thêm try-catch để tránh lỗi secrets parsing
- ✅ Local ưu tiên credentials.json
- ✅ Cloud tự động dùng secrets

## 📋 Steps để test:

### Test Local:
```bash
cd D:\DSH_WP\DTK_CRM
streamlit run data/crm_app.py
```

### Test Online:
1. Code đã push lên GitHub
2. Streamlit Cloud tự deploy
3. Setup secrets trong Cloud settings
4. Test functionality

## 🎯 Kết luận:

**Không cần tách làm 2 bản phức tạp.** Code hiện tại đã được thiết kế để:
- Local development: credentials.json
- Online deployment: Streamlit Cloud Secrets
- Tự động detect và sử dụng đúng method

Nếu bạn vẫn muốn tách, tôi có thể implement Option 2 hoặc 3.