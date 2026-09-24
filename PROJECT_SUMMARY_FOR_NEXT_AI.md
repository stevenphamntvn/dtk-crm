# 📘 DTK CRM - MASTER HANDOVER & TECHNICAL DOCUMENTATION
> **Tài liệu bàn giao dự án toàn diện dành cho AI Agent & Developer tiếp quản.**  
> *Cập nhật mới nhất: 2025 - Đã tối ưu hóa 100% cho cả môi trường Local Windows và Streamlit Cloud.*

---

## 1. 📌 TỔNG QUAN DỰ ÁN (PROJECT OVERVIEW)

* **Tên dự án**: **DTK CRM (Đại Thế Kỷ Advisor CRM V1.0)**
* **Mục đích**: Hệ thống CRM chuyên dụng cho Cố vấn Bất động sản (Real Estate Advisor) của Đại Thế Kỷ:
  1. Quản lý kho hàng bất động sản khổng lồ (Khối Nhà - GSK).
  2. Quản lý danh sách khách hàng và radar chăm sóc (Khối Khách - MyKID).
  3. Khớp nối thông minh (AI/Rule Matching) 2 chiều: **Gợi ý nhà cho khách** hoặc **Tìm khách cho nhà**.
  4. Quản lý lịch sử tương tác và nhật ký gửi hàng Zalo (KID_log).
  5. Khả năng hoạt động **Hybrid**: Chạy Offline-first trên máy tính cá nhân (Local) và chạy Online bảo mật trên Cloud (Streamlit Cloud / Tablet PWA).
* **GitHub Repo**: `https://github.com/stevenphamntvn/dtk-crm`
* **Cloud App**: `https://dtk-crm.streamlit.app`
* **Tech Stack**:
  * **Framework UI**: Streamlit (`streamlit >= 1.40`)
  * **Bảng tương tác chuyên sâu**: `streamlit-aggrid` (`AgGrid`, `JsCode`, `GridOptionsBuilder`)
  * **Xử lý dữ liệu & Vectorized**: `pandas`, `numpy`
  * **Google Sheets API**: `gspread`, `oauth2client`
  * **Styling**: Custom Dark Theme CSS (`#0f0f0f`)

---

## 2. 📁 CẤU TRÚC THƯ MỤC & FILE TRỌNG YẾU

```text
DTK_CRM/
├── Data/
│   ├── crm_app.py              # ⭐ FILE SOURCE DUY NHẤT CHỨA TOÀN BỘ LOGIC APP (~2,700 dòng)
│   ├── credentials.json        # Google Service Account Key (DÙNG CHO LOCAL PC)
│   └── cache/                  # Thư mục lưu dữ liệu đệm Offline (Local CSV)
│       ├── gsk_cache.csv       # Cache Khối Nhà & Link
│       ├── mykid_cache.csv     # Cache Khối Khách (MyKID)
│       ├── kid_log_cache.csv   # Cache Nhật ký Zalo (KID_log)
│       ├── filter_prefs.json   # Bộ nhớ lưu thói quen lọc từng khách
│       └── last_kid_cache.txt  # Ghi nhớ mã khách đang chọn gần nhất
├── .streamlit/
│   ├── config.toml             # Cấu hình server Streamlit (headless, CORS, stats)
│   ├── secrets.toml.example    # Mẫu secrets cho Cloud (GOOGLE_CREDENTIALS, users)
│   └── static/                 # Tài nguyên tĩnh phục vụ PWA Android Tablet
│       ├── manifest.json
│       ├── service-worker.js
│       ├── indexeddb-manager.js
│       ├── pwa-integration.js
│       └── icon-*.png
├── Support/                    # Script hỗ trợ cài đặt, backup & context handover
│   ├── Context_Handover.md
│   ├── install.bat
│   └── export_to_ai.py
├── run.bat                     # File 1-click khởi chạy app trên Windows
├── requirements.txt            # Danh sách thư viện Python cần thiết
├── secrets.toml.template       # Mẫu cấu hình Secrets
└── PROJECT_SUMMARY_FOR_NEXT_AI.md # ⭐ MASTER DOCUMENT NÀY
```

---

## 3. 🧠 THUẬT NGỮ & GIAO THỨC CỐT LÕI (DOMAIN KNOWLEDGE)

| Thuật ngữ | Ý nghĩa | Chi tiết kỹ thuật |
| :--- | :--- | :--- |
| **KID** | Mã khách hàng | Định danh duy nhất của khách hàng (VD: `K001`, `K002`). |
| **UID** | Mã căn nhà | Định danh duy nhất của căn nhà (VD: `SH1234`, `BT005`). |
| **PLK** | Phân loại khách | Mức độ ưu tiên: `A` (Đỏ - Rất nét), `B` (Xanh dương - Nét), `C` (Vàng - Tiềm năng), `D` (Xám - Đã bỏ). |
| **GSK** | Kho Nhà | Sheet `BT-PN.PK-6.0-10000` trên Google Spreadsheet chính. |
| **MyKID** | Khối Khách | Sheet `MyKID` lưu danh sách khách hàng và chuỗi bộ lọc BLK. |
| **KID_log**| Nhật ký gửi nhà | Sheet `KID_log` lưu lịch sử gửi nhà, phản hồi và trạng thái. |
| **BLK** | Chuỗi bộ lọc | Chuỗi quy chuẩn lưu cấu hình lọc của từng khách (xem chi tiết dưới). |
| **TTK** | Thông tin KID | Ghi chú văn bản thô tóm tắt nhu cầu khách. |

### Giao thức chuỗi BLK (`bo_loc_KID` Protocol):
* **Cú pháp mẫu**: `TenKhach.G10-15T.QBT(1,2)+QPN.N4M.MAT.TMA`
* **Quy tắc giải mã**:
  * `G10-15T` $\rightarrow$ Giá từ 10 Tỷ đến 15 Tỷ.
  * `QBT(1,2)+QPN` $\rightarrow$ Quận Bình Thạnh (Phường 1, Phường 2) VÀ Quận Phú Nhuận (tất cả phường).
  * `N4M` $\rightarrow$ Chiều ngang tối thiểu 4 mét.
  * `MAT` $\rightarrow$ Yêu cầu nhà Mặt tiền (không lấy hẻm).
  * `TMA` $\rightarrow$ Yêu cầu có Thang máy.
  * `NTC` $\rightarrow$ Yêu cầu Nội thất cao cấp.
  * `KLP` $\rightarrow$ Yêu cầu Không lỗi phong thủy (đường đâm, tóp hậu, cột điện...).
* **Hàm xử lý trong code**:
  * `parse_blk(blk_string)`: Tách chuỗi BLK thành dictionary các tiêu chí lọc.
  * `build_blk(...)`: Gom các input trên UI thành chuỗi BLK chuẩn để lưu trữ.

---

## 4. 🖥️ CHI TIẾT 3 TAB CHỨC NĂNG CHÍNH

### Tab 1: 🎯 Khớp Nhu Cầu (Matching & Recommendation)
* **2 Chế độ hoạt động**:
  1. `GUI_KHACH` (Mặc định): Chọn 1 khách hàng $\rightarrow$ Hệ thống tự động load chuỗi BLK của khách vào các thanh trượt/bộ lọc $\rightarrow$ Bảng AgGrid lọc ra các căn nhà phù hợp nhất.
  2. `TIM_KHACH` (Tìm khách cho Siêu Phẩm): Advisor tick chọn 1 hoặc nhiều căn nhà tâm đắc $\rightarrow$ Bấm [🎯 TÌM KHÁCH] $\rightarrow$ Hệ thống quét toàn bộ database khách hàng xem khách nào đang có nhu cầu khớp với căn nhà đó.
* **Cột tác vụ AgGrid Tab 1**:
  * `🔘 Tick chọn`: Đưa căn nhà vào khay gửi khách.
  * `🗺️ Quy hoạch`: Double click số nhà để mở link bản đồ quy hoạch (`URL_Quy_Hoach`).
  * `📂 GGD (Mới)`: Cột riêng nằm giữa `sonha` và `tenduong`, độ rộng 25px, click mở thẳng thư mục ảnh Google Drive của căn nhà.
  * `🏷️ Đặc điểm (dacdiem)`: Độ rộng 250px, tự động trích xuất các tag cố định và tag động từ `motachitiet`: `PNxx` (PN5), `SCNxx` (SCN97), `SLGxx` (SLG26), `QHxx` (QH10), `DTNxx` (DTN4), `SA4`, `2MT`, `TTT`, `DTT`, `NTC`, `KLP`, v.v.
  * `📝 Ghi chú (note_rieng)`: Cột mới nằm ở vị trí cuối cùng của bảng, độ rộng 650px, tự động bóc tách nội dung ghi chú riêng `N(...)` từ cột `motachitiet`.
  * `🎯 Chốt lịch gửi`: Nhập ngày hẹn và đẩy vào danh sách gửi (`save_pending_logs`).
* **Tối ưu hóa Bố cục Full-Width (Cloud vs Local)**:
  * **Trên Cloud / Tablet**: Khung kết quả hiển thị nhà kéo dài 100% Full-Width từ trái qua phải; phần chọn khách đặt ở thanh gọn phía trên, còn phần *2. Tinh chỉnh bộ lọc* được đưa xuống dưới bảng nhà giúp Advisor quan sát rổ hàng rộng rãi tối đa trên màn hình tablet.
  * **Trên Local**: Giữ bố cục chia 2 cột (`col_left 1 : col_right 3`) phù hợp với màn hình máy tính rộng.

### Tab 2: 👥 Danh Sách MyKID (Radar Chăm Sóc Khách Hàng)
* Hiển thị toàn bộ khách hàng dạng AgGrid.
* **Chỉnh sửa Inline tốc độ cao**: Cho phép click đúp sửa trực tiếp Phân loại `PLK`, `ghi_chu`, `ngay_tuong_tac`.
* **Cơ chế Silent Vectorized Auto-Save**: Tự động so sánh chênh lệch (`mask` Pandas) và lưu xuống file mà không làm mất trạng thái Sort/Filter của người dùng.
* **Tự động đồng bộ Max Date**: Tự động lấy ngày tương tác mới nhất giữa việc sửa tay và ngày gửi nhà gần nhất bên Tab 3.

### Tab 3: 📝 Nhật Ký Zalo (Zalo Dashboard & Tương Tác)
* Bảng thống kê toàn bộ lịch sử gửi nhà cho khách (`df_log` join với `df_houses`).
* **1-Click Đổi Trạng Thái**: Bấm vào ô trạng thái để xoay vòng màu: `Chờ gửi` $\rightarrow$ `Đã gửi` $\rightarrow$ `Khách thích` $\rightarrow$ `Dẫn xem` $\rightarrow$ `Chê/Lệch` $\rightarrow$ `Blacklist`.
* **Blacklist Protection**: Khi đánh dấu `black_list`, căn nhà đó sẽ vĩnh viễn bị loại khỏi gợi ý của khách hàng đó ở Tab 1.
* **Batch Action**: Cho phép tick chọn nhiều dòng log để xóa hàng loạt.

---

## 5. 🌐 CƠ CHẾ HYBRID DUAL-MODE (LOCAL vs CLOUD)

Ứng dụng được thiết kế chạy song song 2 môi trường hoàn hảo:

| Tiêu chí | 💻 Local PC (Windows) | ☁️ Streamlit Cloud (Linux) |
| :--- | :--- | :--- |
| **Nhận diện** | `IS_CLOUD = False` | `IS_CLOUD = True` (qua `detect_is_cloud()`) |
| **Xác thực** | Bỏ qua đăng nhập (Vào thẳng app) | **Bắt buộc Đăng nhập** (`check_authentication()`) |
| **Cấu hình Auth** | Không cần | Cấu hình qua `st.secrets["users"]` hoặc `APP_PASSWORD` |
| **Google Credentials** | Đọc từ `Data/credentials.json` | Đọc từ `st.secrets["GOOGLE_CREDENTIALS"]` |
| **Đọc dữ liệu** | Đọc nhanh từ Cache CSV cục bộ | Tự động Pull từ Google Sheets khi khởi động |
| **Mở File Explorer**| Chạy `explorer "path"` | Thông báo Toast / Link web |
| **Đồng bộ dữ liệu** | Trạm Kiểm Duyệt KK (So sánh diff trước khi Push/Pull) | Có nút Reset All và Sync 2 chiều |

### 🔒 Luồng Đăng Nhập & Duy Trì Phiên (Persistent Cloud Auth):
1. `check_authentication()` kiểm tra `IS_CLOUD`. Nếu `False` $\rightarrow$ Cho qua.
2. Kiểm tra `st.session_state['authenticated']`. Nếu đã đăng nhập $\rightarrow$ Cho qua.
3. Kiểm tra URL Query Params `?u=...&auth=...`: Sử dụng hàm `generate_auth_token()` để so khớp chữ ký SHA-256 an toàn với `valid_users`. Nếu khớp $\rightarrow$ Tự động đăng nhập lại ngay lập tức khi người dùng F5/tải lại trang trên tablet.
4. Kiểm tra `localStorage` của trình duyệt: Nếu mở lại web/PWA từ màn hình chính mà không có query param, JS tự động inject token vào URL để khôi phục phiên làm việc mà không bắt nhập lại mật khẩu.
5. Nếu chưa có thông tin xác thực: Dừng vẽ toàn bộ UI (`st.stop()`) và hiển thị Form Đăng nhập giữa màn hình.
6. Khi bấm nút **🚪 Đăng Xuất**: Hệ thống xóa toàn bộ `session_state`, xóa sạch `query_params`, và xóa toàn bộ key trong `localStorage` của trình duyệt để đăng xuất hoàn toàn.

---

## 6. 🔄 LUỒNG DỮ LIỆU & ĐỒNG BỘ GOOGLE SHEETS

### Google Spreadsheet ID:
* `SHEET_ID = "1a0roK3rSRQYlFMYIyC_5iMLNr0t7wUz5IRi0OdckPKA"`
* Sheets con:
  * `BT-PN.PK-6.0-10000`: Khối Nhà
  * `linkcolfuid`: Link quy hoạch & Link Google Drive
  * `MyKID`: Khối Khách
  * `KID_log`: Lịch sử tương tác Zalo

### Các hàm tải/ghi dữ liệu quan trọng:
* `get_gspread_client()`: Khởi tạo kết nối gspread (bọc an toàn try-except cho cả secrets và json file).
* `pull_khoi_nha()`: Tải Khối Nhà + Link quy hoạch, kiểm tra an toàn Header (Fail-fast).
* `pull_khoi_khach_va_log()`: Tải bảng MyKID và KID_log về Cache.
* `pull_all_data()`: Tải toàn bộ 3 bảng trong 1 lần gọi.
* `load_local_data()`: Hàm khởi động cốt lõi — nếu thiếu bất kỳ dữ liệu nào sẽ tự động kích hoạt pull từ Google Sheets.
* `trigger_sync_khoi_khach(direction="push"|"pull")`: Kích hoạt `dialog_kiem_duyet_khoi_khach` để so sánh khóa chính (`compare_dataframes`) và hiển thị báo cáo thay đổi (Thêm mới, Xóa, Cập nhật, Blacklist) trước khi ghi đè.

---

## 7. ⚠️ QUY TẮC PHÁT TRIỂN & BẢO TRÌ BẮT BUỘC (CRITICAL RULES FOR AI)

Nếu bạn là AI hoặc Developer tiếp tục chỉnh sửa code này, **BẮT BUỘC TUÂN THỦ CÁC QUY TẮC SAU**:

1. 🛑 **`st.set_page_config()` PHẢI Ở ĐẦU FILE**:
   * Luôn nằm ngay sau các dòng `import`, trước bất kỳ lệnh `st.*` nào khác.
   * Không bao giờ gọi lại `st.set_page_config()` lần thứ 2 trong code.
2. 🛑 **TRUY XUẤT `st.secrets` PHẢI LUÔN BỌC `try...except`**:
   * Streamlit sẽ văng lỗi `StreamlitSecretNotFoundError` nếu truy xuất `st.secrets` trên máy Local không có file `secrets.toml`.
   * Luôn dùng hàm bọc hoặc kiểm tra trong `try...except`.
3. 🛑 **ÉP KIỂU STRING TUYỆT ĐỐI KHI ĐỌC CSV**:
   * Luôn dùng `pd.read_csv(..., dtype=str)`.
   * **Lý do**: Tránh lỗi Pandas tự convert số nhà/tầng như `3,7` thành `37` hoặc làm mất số `0` ở đầu số điện thoại/mã căn.
4. 🛑 **BẢO VỆ VÒNG LẶP RERUN CỦA AGGRID**:
   * Khi bắt sự kiện chỉnh sửa bảng AgGrid (Tab 2, Tab 3), chỉ gọi `st.rerun()` khi và chỉ khi dữ liệu mới **thực sự khác** dữ liệu cũ (`if not df_old.equals(df_new)`).
5. 🛑 **GIỮ NGUYÊN BỘ HEADER CHỐT CHẶN (FAIL-FAST)**:
   * Các cột `UID`, `sonha`, `quan` là cột sống còn. Nếu tải từ Google Sheets về mà thiếu cột này, phải ngắt lệnh ngay để không làm hỏng cache Local.

---

## 8. 🛠️ HƯỚNG DẪN TEST & VẬN HÀNH

### Chạy Local (Windows):
```bash
# Cách 1: Click đúp vào file run.bat
# Cách 2: Chạy lệnh terminal
python -m streamlit run Data/crm_app.py
```

### Deploy lên Streamlit Cloud:
1. Push code lên GitHub repo: `git push origin main`.
2. Truy cập [share.streamlit.io](https://share.streamlit.io).
3. Cấu hình App:
   * **Main file path**: `Data/crm_app.py`
4. Vào **App Settings > Secrets**, dán cấu hình:
```toml
GOOGLE_CREDENTIALS = '{"type": "service_account", "project_id": "...", ...}'

[users]
admin = "MatKhauCuaBan2025"
```
5. Bấm **Save** $\rightarrow$ App sẽ tự build và sẵn sàng sử dụng.

---
*Tài liệu này phản ánh chính xác 100% cấu trúc và logic mã nguồn hiện tại của dự án DTK CRM.*
