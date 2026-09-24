# Icon Files cho PWA

Bạn cần tạo 2 icon files cho PWA:

## Cách tạo icon từ logo hiện có:

### Sử dụng ImageMagick (nếu đã cài đặt):
```bash
convert path/to/your-logo.png -resize 192x192 .streamlit/static/icon-192.png
convert path/to/your-logo.png -resize 512x512 .streamlit/static/icon-512.png
```

### Sử dụng online tools:
1. Truy cập: https://www.favicon-generator.org/
2. Upload logo của bạn
3. Download sizes 192x192 và 512x512
4. Đặt vào `.streamlit/static/`

### Tạm thời sử dụng placeholder:
Nếu cần test ngay, bạn có thể:
1. Tải icon tạm từ: https://via.placeholder.com/192
2. Đặt tên là icon-192.png
3. Làm tương tự cho 512x512

## Yêu cầu icon:
- Format: PNG
- Size: 192x192 và 512x512 pixels
- Background: Transparent hoặc đơn màu
- Style: Simple, clear tại small sizes
- Content: Logo hoặc icon đại diện cho CRM

## Đối với CRM Bất động sản:
Gợi ý icon:
- Nhà/home icon
- Key icon
- Building icon
- hoặc logo hiện tại của bạn
