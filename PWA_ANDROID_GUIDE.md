# Hướng dẫn Deploy và Test CRM PWA trên Android Tablet

## Tổng quan
Giải pháp PWA (Progressive Web App) cho phép ứng dụng Streamlit CRM của bạn hoạt động như một ứng dụng native trên Android tablet, với khả năng hoạt động offline.

## Cấu trúc Files đã tạo
```
.streamlit/
├── static/
│   ├── manifest.json          # PWA manifest
│   ├── service-worker.js      # Service worker cho cache
│   ├── indexeddb-manager.js  # IndexedDB manager cho offline storage
│   └── pwa-integration.js     # Main PWA integration script
└── config.toml               # Streamlit config với PWA settings
```

## Phương án Deploy

### Option 1: Streamlit Cloud (Khuyên dùng cho PWA)

#### Bước 1: Chuẩn bị Repository
1. Đẩy code lên GitHub:
```bash
git init
git add .
git commit -m "Add PWA support for CRM"
git branch -M main
git remote add origin https://github.com/username/dtk-crm.git
git push -u origin main
```

#### Bước 2: Deploy lên Streamlit Cloud
1. Truy cập [share.streamlit.io](https://share.streamlit.io)
2. Connect với GitHub repository của bạn
3. Cấu hình:
   - Main file path: `data/crm_app.py`
   - Python version: 3.9+
   - Requirements: Copy từ `Support/requirements.txt`

#### Bước 3: Cấu hình Domain cho PWA
PWA yêu cầu HTTPS và có thể cần custom domain:
1. Trong Streamlit Cloud settings, thêm custom domain
2. Cấu hình DNS để trỏ đến Streamlit Cloud
3. SSL certificate sẽ được tự động cấu hình

### Option 2: Self-hosted với HTTPS

#### Bước 1: Setup Server
1. Sử dụng VPS (Ubuntu 20.04+)
2. Cài đặt Python và dependencies:
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx certbot
```

#### Bước 2: Setup Streamlit App
```bash
cd /var/www
git clone <your-repo>
cd dtk-crm
python3 -m venv venv
source venv/bin/activate
pip install -r Support/requirements.txt
```

#### Bước 3: Cấu hình Systemd Service
Tạo file `/etc/systemd/system/crm.service`:
```ini
[Unit]
Description=Streamlit CRM
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/dtk-crm
Environment="PATH=/var/www/dtk-crm/venv/bin"
ExecStart=/var/www/dtk-crm/venv/bin/streamlit run data/crm_app.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Khởi động service:
```bash
sudo systemctl enable crm
sudo systemctl start crm
```

#### Bước 4: Cấu hình Nginx với HTTPS
Tạo file `/etc/nginx/sites-available/crm`:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # PWA specific headers
        add_header Service-Worker-Allowed /;
        add_header Cache-Control "public, max-age=31536000";
    }
    
    # Static files for PWA
    location /manifest.json {
        alias /var/www/dtk-crm/.streamlit/static/manifest.json;
        add_header Content-Type application/json;
    }
    
    location /service-worker.js {
        alias /var/www/dtk-crm/.streamlit/static/service-worker.js;
        add_header Content-Type application/javascript;
    }
    
    location /indexeddb-manager.js {
        alias /var/www/dtk-crm/.streamlit/static/indexeddb-manager.js;
        add_header Content-Type application/javascript;
    }
    
    location /pwa-integration.js {
        alias /var/www/dtk-crm/.streamlit/static/pwa-integration.js;
        add_header Content-Type application/javascript;
    }
}
```

Cài đặt SSL:
```bash
sudo certbot --nginx -d your-domain.com
```

## Test trên Android Tablet

### Bước 1: Truy cập ứng dụng
1. Mở Chrome trên Android tablet
2. Truy cập URL của ứng dụng (https://your-app.com)
3. Chờ ứng dụng load hoàn toàn

### Bước 2: Cài đặt PWA
1. Trong Chrome menu, chọn "Add to Home Screen" hoặc "Install App"
2. App sẽ xuất hiện trên home screen như native app
3. Mở app từ home screen

### Bước 3: Test Offline Mode
1. Mở ứng dụng khi có mạng
2. Đợi dữ liệu được cache (thông báo "✅ Đã đồng bộ dữ liệu")
3. Tắt WiFi/Internet
4. Mở lại ứng dụng từ home screen
5. Kiểm tra:
   - Ứng dụng vẫn mở được
   - Dữ liệu khách hàng/nhà vẫn hiển thị
   - Có thông báo "📱 Chế độ Offline"

### Bước 4: Test Sync
1. Tạo/sửa dữ liệu khi offline
2. Bật lại Internet
3. Kiểm tra dữ liệu được sync lên server
4. Xác nhận thông báo "✅ Đồng bộ dữ liệu thành công"

## Troubleshooting

### Service Worker không hoạt động
- Kiểm tra console của trình duyệt (F12)
- Đảm bảo URL là HTTPS (hoặc localhost cho testing)
- Xóa cache và reload: `chrome://serviceworker-internals/`

### Dữ liệu không sync
- Kiểm tra IndexedDB trong DevTools (Application tab)
- Xem console logs cho lỗi sync
- Đảm bảo file `crm_app.py` có PWA integration code

### App không cài được trên Android
- Kiểm tra manifest.json có đúng path
- Đảm bảo có icon files (icon-192.png, icon-512.png)
- Test PWA với [Lighthouse](https://developers.google.com/web/tools/lighthouse)

### Icon bị thiếu
Tạo icon files và đặt trong `.streamlit/static/`:
```bash
# Tạo icon từ image
convert your-logo.png -resize 192x192 .streamlit/static/icon-192.png
convert your-logo.png -resize 512x512 .streamlit/static/icon-512.png
```

## Performance Optimization

### Cache Strategy
- Static assets: Cache 1 năm
- API responses: Cache theo version
- Data: Cache offline với IndexedDB

### Data Size
- Giới hạn data cache ~50MB cho performance
- Implement pagination cho large datasets
- Clear old cache định kỳ

### Battery Optimization
- Giảm polling frequency
- Sử dụng background sync thay vì interval
- Optimize JavaScript execution

## Security Considerations

### Data Protection
- Dữ liệu offline được mã hóa trong IndexedDB
- Clear cache khi logout
- Validate data khi sync

### Authentication
- Implement auth tokens
- Refresh tokens khi có mạng
- Handle expired tokens gracefully

## Future Enhancements

### Push Notifications
- Thêm Firebase Cloud Messaging
- Notify khi có data mới
- Remind cho scheduled tasks

### Background Updates
- Sync data định kỳ
- Update house listings
- Refresh customer info

### Enhanced Offline Features
- Offline analytics
- Local search/indexing
- Offline reporting

## Support

Nếu gặp vấn đề:
1. Kiểm tra Console logs (Chrome DevTools)
2. Xem Service Worker status
3. Test trên multiple devices
4. Contact support với logs

## Files Checklist

Trước khi deploy, đảm bảo có:
- [x] `.streamlit/static/manifest.json`
- [x] `.streamlit/static/service-worker.js`
- [x] `.streamlit/static/indexeddb-manager.js`
- [x] `.streamlit/static/pwa-integration.js`
- [x] `.streamlit/static/icon-192.png`
- [x] `.streamlit/static/icon-512.png`
- [x] `.streamlit/config.toml` với PWA settings
- [x] `data/crm_app.py` với PWA integration code
- [x] HTTPS certificate
- [x] Custom domain (optional nhưng khuyến khích)
