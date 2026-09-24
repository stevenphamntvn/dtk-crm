# Hướng dẫn Deploy lên Streamlit Cloud

## ✅ Đã hoàn thành:
- ✅ Push code lên GitHub: https://github.com/stevenphamntvn/dtk-crm
- ✅ Sửa code để hỗ trợ Streamlit Cloud Secrets
- ✅ Push code cập nhật lên GitHub

## 🚀 Bước tiếp theo: Deploy lên Streamlit Cloud

### Bước 1: Truy cập Streamlit Cloud
1. Truy cập: https://share.streamlit.io
2. Đăng nhập bằng GitHub

### Bước 2: Tạo App mới
1. Click "New app"
2. Chọn repository: `stevenphamntvn/dtk-crm`
3. Cấu hình:
   - **Repository**: stevenphamntvn/dtk-crm
   - **Branch**: main
   - **Main file path**: `data/crm_app.py`
   - **Python version**: 3.9+
4. Click "Deploy"

### Bước 3: Setup Requirements
1. Trong app settings, tìm "Requirements"
2. Copy nội dung từ file `Support/requirements.txt`:
```txt
streamlit
pandas
gspread
oauth2client
st-aggrid
```
3. Paste vào ô Requirements

### Bước 4: Setup Credentials (QUAN TRỌNG)
1. Trong app settings, tìm "Secrets"
2. Click "Add new secret"
3. Điền thông tin:
   - **Key**: `GOOGLE_CREDENTIALS`
   - **Value**: Copy toàn bộ nội dung file `Data/credentials.json` từ máy của bạn

**Cách lấy nội dung credentials.json:**
```bash
# Trên Windows
type Data\credentials.json

# Hoặc mở file trong Notepad và copy toàn bộ
```

### Bước 5: Deploy lại App
1. Sau khi thêm secrets, click "Deploy" lại
2. Chờ deploy hoàn thành (khoảng 2-3 phút)
3. App sẽ chạy tại URL: `https://your-app-name.streamlit.app`

### Bước 6: Test App
1. Truy cập URL của app
2. Kiểm tra các chức năng:
   - Hiển thị dữ liệu khách hàng
   - Tìm kiếm nhà
   - Đồng bộ với Google Sheets

## 📱 Test PWA trên Android Tablet

### Bước 1: Truy cập từ Android
1. Mở Chrome trên Android tablet
2. Truy cập URL của Streamlit app
3. Chờ app load hoàn toàn

### Bước 2: Cài đặt PWA
1. Trong Chrome menu (⋮)
2. Chọn "Add to Home Screen" hoặc "Install App"
3. App sẽ xuất hiện trên home screen như native app

### Bước 3: Test Offline Mode
1. Mở app khi có mạng (để cache dữ liệu)
2. Tắt WiFi/Internet
3. Mở lại app từ home screen
4. Kiểm tra:
   - App vẫn mở được
   - Dữ liệu vẫn hiển thị
   - Có thông báo "📱 Chế độ Offline"

### Bước 4: Test Sync
1. Sửa dữ liệu khi offline
2. Bật lại Internet
3. Kiểm tra dữ liệu được sync lên server
4. Xác nhận thông báo sync thành công

## 🔧 Troubleshooting

### App không deploy được
- Kiểm tra requirements có đúng không
- Xem log trong Streamlit Cloud dashboard
- Đảm bảo credentials.json đúng format

### Lỗi Google Sheets connection
- Kiểm tra secret `GOOGLE_CREDENTIALS` đúng format JSON
- Đảm bảo Google Service Account có quyền truy cập Sheets
- Test credentials local trước

### PWA không hoạt động
- Kiểm tra URL là HTTPS
- Xem Console logs (F12) trên browser
- Đảm bảo static files được load đúng

### Service Worker không hoạt động
- Kiểm tra browser console
- Xóa cache và reload
- Test trên Chrome for Android

## 📝 URL tham khảo

- **GitHub Repository**: https://github.com/stevenphamntvn/dtk-crm
- **Streamlit Cloud**: https://share.streamlit.io
- **PWA Guide**: Xem file `PWA_ANDROID_GUIDE.md`

## 🎯 Sau khi deploy thành công

1. **Share URL**: Share URL cho team members
2. **Custom Domain**: Có thể setup custom domain trong Streamlit Cloud
3. **Monitor**: Theo dõi usage và performance trong dashboard
4. **Update**: Khi update code, chỉ cần push lên GitHub và Streamlit sẽ auto-deploy

## 💡 Tips

- **Development**: Test local trước khi push
- **Backup**: Luôn backup credentials.json
- **Security**: Không bao giờ push credentials lên GitHub
- **Performance**: Monitor app performance và optimize nếu cần

---

**Cần hỗ trợ thêm?**
- Nếu gặp lỗi cụ thể khi deploy, copy error message
- Nếu cần hướng dẫn custom domain
- Nếu muốn thêm tính năng mới cho PWA