# 🏢 Đại Thế Kỷ Advisor CRM - Documentation v2.0

## 📋 Tổng quan dự án

**Đại Thế Kỷ Advisor CRM** là hệ thống CRM Bất Động Sản nội bộ được xây dựng bằng Python/Streamlit, tối ưu hóa quy trình môi giới với các tính năng chính:

- 🏠 **Quản lý Kho Nhà (GSK)**: Đồng bộ & lọc hàng nghìn căn nhà từ Google Sheets
- 👥 **Quản lý Khách Hàng (MyKID)**: Theo dõi danh sách khách với bộ lọc thông minh (BLK)  
- 🎯 **Khớp Nhu Cầu**: Tự động tìm nhà phù hợp theo tiêu chí khách hàng
- 📝 **Nhật Ký Zalo**: Theo dõi lịch sử gửi nhà và phản hồi khách hàng
- 🗺️ **Tích hợp Bản Đồ**: Link quy hoạch & Google Drive cho từng căn nhà
- 💾 **Offline-First**: Cache local để làm việc nhanh mà không cần mạng

---

## 🗂️ Cấu trúc dự án

```
DTK_CRM/
├── run.bat                      # Script khởi động ứng dụng
├── data/
│   ├── crm_app.py              # Main application file
│   ├── credentials.json        # Google Service Account credentials
│   └── cache/                  # Thư mục cache offline
│       ├── gsk_cache.csv       # Cache Khối Nhà
│       ├── mykid_cache.csv     # Cache Khách Hàng
│       ├── kid_log_cache.csv   # Cache Nhật Ký Zalo
│       ├── pending_logs.csv    # Logs chờ đồng bộ
│       ├── filter_prefs.json   # Bộ lọc khách hàng (BLK)
│       └── last_kid_cache.txt  # Khách hàng cuối cùng chọn
└── Support/
    ├── requirements.txt        # Python dependencies
    └── README.md              # File này
```

---

## 🚀 Cài đặt & Chạy

### Yêu cầu
- Python 3.8+
- Google Service Account với quyền Google Sheets API

### Cài đặt
```bash
# Cài đặt dependencies
pip install -r Support/requirements.txt

# Hoặc cài đặt từng package
pip install streamlit==1.46.1 pandas gspread oauth2client streamlit-aggrid==1.1.8.post1
```

### Chạy ứng dụng
```bash
# Sử dụng batch file (Windows)
run.bat

# Hoặc chạy trực tiếp
streamlit run data/crm_app.py
```

---

## 📖 Từ điển thuật ngữ (Domain Knowledge)

### 🆔 Nhóm định danh
- **KID (Khách ID)**: Mã định danh duy nhất của khách hàng (Ví dụ: K001, K002)
- **UID (Unique ID)**: Mã định danh duy nhất của căn nhà trong kho hàng

### 📊 Nhóm dữ liệu & trạng thái
- **GSK (Giỏ Sách Kho)**: Kho dữ liệu nhà gốc từ Google Sheets (Sheet: `BT-PN.PK-6.0-10000`)
- **PL (Pháp lý/Phân loại)**: Đánh giá độ "ngon" của căn nhà
  - `TAR` (Target): Hàng mục tiêu, ưu tiên #1
  - `A`: Hàng tốt, ưu tiên #2  
  - `HID` (Hidden): Hàng ẩn, xếp cuối

### 🏷️ Tags đặc điểm (Mã 3 chữ cái)
**Vị trí (Lọc HOẶC - có 1 điều kiện là lấy):**
- `MAT`: Mặt tiền (nhận diện: số nhà không có dấu `.`)
- `HXT`: Hẻm xe tải (mã hẻm = 1)
- `HXH`: Hẻm xe hơi (mã hẻm = 2 hoặc trống)
- `HBG`: Hẻm ba gác (mã hẻm = 3)

**Đặc điểm cộng thêm (Lọc VÀ - phải thỏa mãn tất cả):**
- `TMA`: Có thang máy
- `NTC`: Nội thất cao cấp
- `2MT`: 2 Mặt tiền
- `CGO`: Căn góc

**Phong thủy:**
- `TTT`: Tây Tứ Trạch
- `DTT`: Đông Tứ Trạch

**Lỗi phong thủy (Danh sách đen):**
- `TOH` (Tóp hậu), `DAD` (Đâm đường), `QHH` (Dính quy hoạch)
- `GCH` (Gần chùa/nhà thờ), `GAC` (Gần gác/miếu mạo)
- **KLP (Không lỗi phong thủy)**: Tự động loại bỏ các nhà dính lỗi trên

### 🔗 Nhóm tài nguyên ẩn
- **URL_Quy_Hoach**: Link bản đồ quy hoạch (merge từ sheet `linkcolfuid`)
- **URL_GGD**: Link Google Drive hình ảnh nhà (merge từ sheet `linkcolfuid`)
- **CUS (Copy TT)**: Nội dung đã tối ưu để gửi khách qua Zalo

### 🧠 Nhóm Protocol
- **BLK (Bộ Lọc Khách)**: Chuỗi mã hóa thói quen lọc của khách
  - Ví dụ: `AnhA.G10-15T.QBT(P1,P2)+QPN.N4M.MAT.KLP.TTT`
  - Nghĩa: Khách Anh A, tìm 10-15 Tỷ, Q.BT (P1,P2) hoặc Q.PN, bề ngang ≥4m, Mặt tiền, Không lỗi, Tây Tứ Trạch

---

## 🏗️ Kiến trúc hệ thống

### Mô hình 3-tầng Offline-First

```
┌─────────────────────────────────────────────────────────┐
│  Tầng Cloud (Google Sheets)                              │
│  - BT-PN.PK-6.0-10000 (Khối Nhà)                         │
│  - MyKID (Khách Hàng)                                    │
│  - KID_log (Nhật Ký Zalo)                                │
│  - linkcolfuid (Link ẩn: Quy hoạch + Drive)              │
└─────────────────────────────────────────────────────────┘
                          ↕ Sync
┌─────────────────────────────────────────────────────────┐
│  Tầng Cache Local (data/cache/)                          │
│  - gsk_cache.csv (Khối Nhà + Link merged)               │
│  - mykid_cache.csv (Khách Hàng + BLK)                   │
│  - kid_log_cache.csv (Nhật Ký Zalo)                     │
│  - filter_prefs.json (Bộ lọc khách)                     │
│  - last_kid_cache.txt (Khách cuối cùng)                 │
└─────────────────────────────────────────────────────────┘
                          ↕ Read/Write
┌─────────────────────────────────────────────────────────┐
│  Tầng UI (Streamlit + AgGrid)                            │
│  - Tab 1: Khớp Nhu Cầu (Lọc & Gửi nhà)                  │
│  - Tab 2: Danh Sách MyKID                                │
│  - Tab 3: Nhật Ký Zalo                                   │
└─────────────────────────────────────────────────────────┘
```

### Cơ chế đồng bộ

**1. Đồng bộ Khối Nhà (1 chiều: Cloud → Local)**
- Hàm: `pull_khoi_nha()`
- Merge dữ liệu nhà + link ẩn qua `UID`
- Có chốt chặn bảo vệ header quan trọng (UID, SONHA, QUAN)

**2. Đồng bộ Khối Khách (2 chiều với Dialog kiểm duyệt)**
- Hàm: `trigger_sync_khoi_khach(direction)`
- **Pull (Cloud → Local)**: Tải khách & nhật ký từ Cloud về
- **Push (Local → Cloud)**: Đẩy khách & nhật ký từ Local lên Cloud
- Có Dialog so sánh diff trước khi thực hiện (hàm `compare_dataframes()`)

---

## 🎨 Giao diện (3 Tabs chính)

### Tab 1: 🎯 Khớp Nhu Cầu
**Cột Trái (25%) - Bộ lọc & Hồ sơ khách:**
- Chọn khách hàng (tự động nhớ khách cuối cùng từ `last_kid_cache.txt`)
- Bộ lọc vị trí (HOẶC): MAT, HXT, HXH, HBG
- Bộ lọc đặc điểm (VÀ): TMA, NTC, KLP, TTT, DTT...
- Lọc theo Giá, Quận, Phường, Bề ngang

**Cột Phải (75%) - Kết quả & Khay tác vụ:**
- Bảng AgGrid với độ rộng cột cố định (`UI_WIDTH` config)
- Cột "Định giá" màu vàng cam (`#D97706`)
- Cột "Số nhà"/"Tên đường": Click copy, Double-click mở link
- Cột "Copy TT": Click 1 lần copy nội dung chào khách
- 3 nút cố định: F5, Lưu Bộ Lọc, Gửi Khách

### Tab 2: 👥 Danh Sách MyKID
- Bảng đơn giản hiển thị toàn bộ khách hàng
- Cột `ngay_tuong_tac`: Tự động tính từ Nhật Ký Zalo (Max Date)
- Cột `bo_loc_KID`: Lưu BLK của từng khách

### Tab 3: 📝 Nhật Ký Zalo
- Danh sách nhà đã chọn gửi cho khách
- Click 1 lần đổi trạng thái: Chưa gửi → Đã gửi
- Tự động lưu xuống ổ cứng (không cần nút Save)
- Tích hợp timestamp và phản hồi khách

---

## ⚙️ Cấu hình hệ thống

### Cấu hình Google Sheets
```python
SHEET_ID = "1a0roK3rSRQYlFMYIyC_5iMLNr0t7wUz5IRi0OdckPKA"
GSK_SHEET_NAME = "BT-PN.PK-6.0-10000"
LINK_SHEET_NAME = "linkcolfuid"
COL_LINK_URL = "URL_Quy_Hoach"
COL_LINK_GGD = "URL_GGD"
```

### Cấu hình Column Map (GSK ↔ Local)
```python
CONFIG_GSK_CM = {
    "STT": "stt", "STATUS": "status", "NGAY": "ngay", "PL": "PL", 
    "QUAN": "quan", "SONHA": "sonha", "TENDUANG": "tenduong",
    "PHUONG": "phuong", "NGANG": "ngang", "DAI": "dai",
    "GIA": "gia", "PM2": "p/m2", "DIENTICH": "dientich",
    "KETCAU": "ketcau", "UID": "uid", "MOTACHITIET": "motachitiet",
    "UPDATE": "update", "HEM": "hem", "CUS": "cus", "DINHGIA_Q": "dinhgia"
}
```

### Cấu hình Độ rộng cột UI
```python
UI_WIDTH = {
    "t1_trangthai": 35, "t1_pl": 42, "t1_quan": 60,
    "t1_phuong": 42, "t1_sonha": 90, "t1_tenduong": 120,
    # ... (tham khảo file crm_app.py dòng 99-143)
}
```

---

## 🔧 Các hàm cốt lõi (Core Functions)

### Xử lý dữ liệu
- **`clean_numeric(series)`**: Xử lý số thập phân Việt Nam (3,7 → 3.7)
- **`remove_vietnamese_accent(s)`**: Gọt dấu tiếng Việt để match folder Windows
- **`get_gspread_client()`**: Kết nối Google API (cached)

### Đồng bộ dữ liệu
- **`pull_khoi_nha()`**: Tải Khối Nhà + Link từ Cloud về Local (có chốt chặn header)
- **`trigger_sync_khoi_khach(direction)`**: Đồng bộ Khối Khách 2 chiều với Dialog kiểm duyệt
- **`compare_dataframes(df_local, df_cloud, primary_keys)`**: So sánh diff giữa Local và Cloud

### Lọc & Matching
- **`filter_houses()`**: Bộ não lọc dữ liệu (giá, vị trí, đặc điểm, sorting)
- **`apply_dinh_gia()`**: Thuật toán định giá tự động (regex tìm SLG/SCN × đơn giá)

### Giao diện AgGrid
- **`get_aggrid_js_codes()`**: Tạo JavaScript code cho bảng tương tác
- **`render_aggrid()`**: Render bảng với styling và event handlers

### Bộ nhớ hệ thống
- **`build_blk()` / `parse_blk()`**: Mã hóa/giải mã chuỗi BLK
- **`get_kid_prefs()` / `save_kid_prefs()`**: Lưu/đọc bộ lọc khách
- **`FILE_LAST_KID`**: Tự động nhớ khách hàng cuối cùng

---

## 🛡️ Các điểm đặc biệt trong code

### Xử lý số thập phân Việt Nam
```python
# 3,7 mét → 3.7 mét
s = series.astype(str).str.replace(',', '.', regex=False)
```

### Merge dữ liệu ẩn
```python
# Merge Khối Nhà + Link ẩn qua UID
df_h = pd.merge(df_h, df_l[cols_to_merge], 
                left_on=CONFIG_GSK_CM["UID"], right_on="UID", 
                how="left")
```

### Chốt chặn bảo vệ dữ liệu
```python
# Ngắt đồng bộ nếu mất header quan trọng
critical_cols = [CONFIG_GSK_CM["UID"], CONFIG_GSK_CM["SONHA"], CONFIG_GSK_CM["QUAN"]]
missing_cols = [col for col in critical_cols if col not in df_h.columns]
if missing_cols:
    st.error(f"🚨 LỖI: Mất cột Header: {', '.join(missing_cols)}")
    return
```

### Thuật toán Max Date (Ngày tương tác)
```python
# Lấy ngày lớn nhất giữa Manual (ngay_tuong_tac) và Auto (từ KID_log)
def get_max_date(kid, current_date_str):
    log_dt = last_interaction.get(str(kid).strip(), pd.NaT)
    curr_dt = pd.to_datetime(current_date_str, errors='coerce')
    return max(log_dt, curr_dt).strftime("%Y-%m-%d")
```

---

## 🚨 Lưu ý quan trọng cho lập trình viên

1. **Cấu hình tên cột**: Thay đổi `CONFIG_GSK_CM` sẽ ảnh hưởng toàn bộ hệ thống
2. **Xử lý số thập phân**: Luôn dùng `clean_numeric()` khi làm việc với số liệu Việt Nam
3. **Session State**: Các biến đếm dùng để ép UI reload khi có dữ liệu mới
4. **Bảo vệ dữ liệu**: Không bao giờ chỉnh sửa hàm `pull_khoi_nha()` để bỏ qua chốt chặn header
5. **So sánh DataFrames**: Dùng `compare_dataframes()` để tránh lỗi cấu trúc khác nhau
6. **Bản đồ địa phương**: Hàm `remove_vietnamese_accent()` dùng để match với folder Windows

---

## 📝 Dependencies

```
streamlit==1.46.1
pandas
gspread
oauth2client
streamlit-aggrid==1.1.8.post1
```

---

## 🤝 Hỗ trợ

Nếu gặp lỗi hoặc cần hỗ trợ, kiểm tra:
1. File `credentials.json` có đúng không
2. Google Service Account có quyền Google Sheets API không
3. Cấu hình `CONFIG_GSK_CM` có khớp với Google Sheets không
4. Đường dẫn `path_pc` / `path_laptop` có đúng không

---

**Phiên bản tài liệu**: v2.0 (Cập nhật theo code hiện tại)  
**Cập nhật lần cuối**: 2026-09-16