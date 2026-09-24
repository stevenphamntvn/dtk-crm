# TÀI LIỆU TỔNG QUAN: ĐẠI THẾ KỶ ADVISOR CRM (V1.0 - Cập Nhật Mới Nhất)

## 1. Giới thiệu dự án
**Đại Thế Kỷ Advisor CRM** là một hệ thống phần mềm nội bộ được xây dựng bằng Python (framework Streamlit). Mục đích cốt lõi của phần mềm là **tự động hóa và tối ưu hóa quy trình môi giới bất động sản**, cụ thể:
* **Quản lý Nguồn hàng (Kho nhà) & Nhu cầu Khách hàng:** Nhanh chóng tìm ra những căn nhà phù hợp nhất với tiêu chí khắt khe của từng khách hàng.
* **Định giá & Tích hợp Tài nguyên thông minh:** Tự động tính toán định giá dựa trên diện tích thực tế và tích hợp sẵn link Bản đồ Quy hoạch, link Google Drive hình ảnh nhà ngay trong lúc lướt dữ liệu.
* **Quản lý luồng gửi nhà qua Zalo:** Theo dõi căn nhà nào đã gửi, căn nào chờ gửi, khách hàng phản hồi ra sao, nhằm tránh gửi trùng lặp hoặc bỏ sót khách.
* **Lưu trữ thông minh:** Ghi nhớ thói quen tìm kiếm và khách hàng mở cuối cùng để những lần chăm sóc sau chỉ mất vài giây thao tác.

---

## 2. Từ điển Thuật ngữ Cốt lõi (Phải biết trước khi đọc code)
Để hiểu được các biến và hàm trong code, người đọc cần nắm vững các từ viết tắt nghiệp vụ Bất động sản sau:

### A. Nhóm Định danh (ID)
* **KID (Khách ID):** Mã định danh duy nhất của một khách hàng (Ví dụ: K001, K002).
* **UID (Unique ID):** Mã định danh duy nhất của một căn nhà trong kho hàng.

### B. Nhóm Nguồn dữ liệu & Trạng thái
* **GSK (Giỏ Sách Kho):** Ám chỉ kho lưu trữ toàn bộ dữ liệu nhà bán (thường lưu trên Google Sheets).
* **PL (Pháp lý / Phân loại):** Cấp bậc đánh giá độ "ngon" của căn nhà.
    * `TAR` (Target): Hàng mục tiêu, nhà ngon nhất, ưu tiên hiển thị số 1.
    * `A`: Hàng tốt, ưu tiên số 2.
    * `HID` (Hidden): Hàng ẩn, bán chậm hoặc có vấn đề, xếp cuối.

### C. Nhóm Đặc điểm (Tags & Checkboxes)
Hệ thống sử dụng các mã Code 3 chữ cái để quét mô tả nhà:
* **Vị trí (Lọc theo toán tử HOẶC - Có 1 trong các điều kiện là lấy):**
    * `MAT`: Mặt tiền (Nhận diện: Số nhà không có dấu chấm `.`).
    * `HXT`: Hẻm xe tải (Mã hẻm = 1).
    * `HXH`: Hẻm xe hơi (Mã hẻm = 2 hoặc bỏ trống).
    * `HBG`: Hẻm ba gác (Mã hẻm = 3).
* **Đặc điểm cộng thêm & Thuộc tính giá trị (Lọc theo toán tử VÀ - Phải thỏa mãn tất cả):**
    * `TMA`: Có thang máy.
    * `NTC`: Nội thất cao cấp.
    * `2MT`: 2 Mặt tiền.
    * `CGO`: Căn góc.
* **Phong Thủy (Hướng trạch):**
    * `TTT`: Tây Tứ Trạch.
    * `DTT`: Đông Tứ Trạch.
* **Lỗi Phong Thủy (Danh sách đen):**
    * `TOH` (Tóp hậu), `DAD` (Đâm đường), `QHH` (Dính quy hoạch), `GCH` (Gần chùa/nhà thờ), `GAC` (Gần gác/miếu mạo).
    * *Bộ lọc **KLP (Không lỗi phong thủy)** sẽ tự động quét và loại bỏ toàn bộ nhà dính các mã lỗi này.*

### D. Chuỗi Protocol (BLK - Bộ Lọc Khách)
* Là một chuỗi ký tự được phần mềm tự động mã hóa để "nhớ" thói quen của khách. 
* *Ví dụ:* `AnhA.G10-15T.QBT(P1,P2)+QPN.N4M.MAT.KLP.TTT` nghĩa là: Khách tên Anh A, tìm nhà từ 10-15 Tỷ, ở Quận Bình Thạnh (Phường 1, 2) hoặc Phú Nhuận, bề ngang tối thiểu 4 mét, yêu cầu Mặt tiền, Không lỗi phong thủy và hợp Tây Tứ Trạch.

### E. Nhóm Tài nguyên Ẩn & Định Giá
* **`URL_Quy_Hoach` / `URL_GGD`:** Các liên kết ẩn (Tọa độ Bản đồ / Hình ảnh Google Drive) được trích xuất từ Google Sheets và gộp (merge) ngầm vào bảng dữ liệu.
* **Định giá (D: xxx tỷ):** Thuật toán tự động đọc Diện tích thật (`SLG`, `SCN`) nhân với Đơn giá trần để ra con số định giá thực tế, giúp so sánh ngay lập tức với Giá bán.
* **`CUS` (Copy TT):** Cột chứa nội dung đã được tối ưu hóa để gửi khách hàng qua Zalo.

---

## 3. Kiến trúc Hệ thống & Luồng Dữ liệu (Data Flow)
Dự án được thiết kế theo mô hình **Offline-First (Ưu tiên chạy trên máy cá nhân)** kết hợp đồng bộ đám mây (Google Sheets) để giải quyết bài toán: Chạy mượt mà, không bị độ trễ và không bị Google chặn do gọi API quá nhiều lần.

**Cấu trúc 3 tầng:**
1.  **Tầng Đám mây (Cloud - Google Sheets):** Nơi chứa dữ liệu gốc do đội ngũ nhập vào. **Đặc biệt:** Hệ thống có 1 sheet phụ (`linkcolfuid`) làm nhiệm vụ kho lưu trữ các URL bị ẩn, được cập nhật thông qua Google Apps Script.
2.  **Tầng Trạm Đệm (Local Cache - Thư mục `cache`):** Phần mềm tải dữ liệu từ Cloud về lưu thành các file `.csv` và `.json` trên ổ cứng máy tính. Các file này đóng vai trò như bộ nhớ tạm (Offline Database - OD).
    *   *Cơ chế Merge thông minh:* Ngay khi tải về, dữ liệu nhà (GSK) và dữ liệu link ẩn (`linkcolfuid`) sẽ được Python "khâu" lại với nhau thông qua mã `UID`.
3.  **Tầng Giao diện (Streamlit UI):** Tương tác với người dùng. Mọi thao tác tìm kiếm, lọc nhà, click chép dữ liệu diễn ra ở đây với tốc độ mili-giây.

**💡 Điểm đặc biệt trong Code xử lý Dữ liệu:**
*   Đặc thù thị trường BĐS Việt Nam dùng dấu phẩy cho số thập phân (Ví dụ: Ngang 3,7 mét). Hệ thống sử dụng hàm `clean_numeric()` và lấy dữ liệu thô (List of Lists) để bảo vệ tuyệt đối các con số này.
*   "Trí nhớ F5": Hệ thống sử dụng biến đếm Session State để ép giao diện bảng vẽ lại lập tức khi có dữ liệu mới tải về từ kho đệm.

***





## 4. Giải phẫu Giao diện Người dùng (3 Tab chính)
Toàn bộ phần mềm được chia thành 3 không gian làm việc chính (Tabs), thiết kế mô phỏng chính xác quy trình chốt sale thực tế:

### Tab 1: 🎯 Khớp Nhu Cầu (Trái tim của hệ thống)
Nơi diễn ra các thao tác phức tạp nhất, được chia làm 2 cột bất đối xứng (25% - 75%):
*   **Cột Trái (Bộ lọc & Hồ sơ khách - 25%):**
    *   **Trí nhớ thông minh:** Ô chọn Khách hàng tự động định vị lại khách hàng cuối cùng mà môi giới đang chăm sóc (đọc từ file `last_kid_cache.txt`).
    *   **Cụm Vị trí (Tích chọn HOẶC):** Có thể chọn kết hợp nhiều vị trí (MAT, HXT, HXH, HBG).
    *   **Cụm Đặc điểm (Tích chọn VÀ):** (Thang máy, Nội thất, Không lỗi, TTT, DTT...). Nhà phải có đủ các đặc điểm này mới được hiển thị.
*   **Cột Phải (Kết quả & Khay tác vụ - 75%):**
    *   Hiển thị danh sách nhà dưới dạng Bảng tương tác (AgGrid). Bảng này được tối ưu bề rộng cột cứng (`suppressSizeToFit=True`) để không bị vỡ layout.
    *   **Cột "Định giá":** Hiển thị nổi bật bằng chữ màu vàng cam đậm (`#D97706`), giúp môi giới "soi" giá trị thật của căn nhà ngay lập tức.
    *   **Cột "Số nhà" & "Tên đường":** Nếu có link ẩn (Bản đồ / Drive), chữ sẽ tự động chuyển màu xanh gạch chân. Click 1 lần để chép văn bản, Double-Click (DCL) để mở bản đồ/ảnh trên tab mới.
    *   **Cột "Copy TT" (`cus`):** Click 1 lần để tự động copy toàn bộ nội dung chào khách đã được biên soạn sẵn vào Clipboard (kèm thông báo Pop-up).
    *   **Cụm Nút cố định:** 3 nút (Làm mới F5, Lưu Bộ Lọc, Gửi Khách) được neo cố định ngay dưới bảng, không bị đẩy xuống khi môi giới chọn ngày hẹn cho nhà. (Nút "Gửi khách" sẽ bị khóa mờ nếu chưa chọn nhà nào).

### Tab 2: 👥 Danh Sách MyKID
Bảng hiển thị đơn giản toàn bộ dữ liệu thô của khách hàng (Lấy từ sheet MyKID), giúp môi giới xem nhanh thông tin tổng quan của toàn bộ tệp khách đang chăm sóc.

### Tab 3: 📝 Nhật Ký Zalo (Dashboard)
Đóng vai trò như một cuốn sổ tay theo dõi tiến độ chăm sóc:
*   Hiển thị danh sách tất cả các nhà đã được chọn gửi cho khách từ Tab 1.
*   **Tính năng 1-click:** Bấm 1 lần vào cột Trạng thái để đổi từ "Chưa gửi" (màu trắng) sang "Đã gửi" (màu xanh lá).
*   **Lưu ngầm tự động:** Khi người dùng đổi trạng thái hoặc gõ "Phản hồi" của khách, hệ thống sẽ tự động lưu xuống ổ cứng mà không cần bấm nút "Save", giúp thao tác trơn tru, không bị giật lag (chớp màn hình).

---

## 5. Giải mã Các Hàm Lập Trình Cốt Lõi (Core Functions)
Khi đọc mã nguồn (code), bạn hãy tập trung vào các nhóm hàm (functions) mang tính chất "xương sống" sau đây:

### 5.1. Nhóm Đồng bộ & Hợp nhất Dữ liệu (`sync_data_with_gsheet` & `pull_latest_houses_only`)
*   **Nhiệm vụ:** Kéo (Pull) dữ liệu từ Google Sheets về máy, đặc biệt là phục vụ nút "F5 Làm Mới".
*   **Điểm nhấn kỹ thuật - Kỹ thuật Merge:** Hàm không chỉ tải sheet nhà (GSK) mà còn ngầm tải sheet link (`linkcolfuid`). Bằng lệnh `pd.merge()` của Pandas (Left Join qua `UID`), nó "dán" 2 cột `URL_Quy_Hoach` và `URL_GGD` vào bảng nhà gốc trước khi lưu xuống ổ cứng. Nhờ vậy, App luôn chạy mượt mà không cần truy vấn web mỗi khi người dùng click xem bản đồ.

### 5.2. Hàm `filter_houses()` - Bộ Não Lọc Dữ Liệu
Hàm quyết định căn nhà nào được hiện ra, với các bước:
1.  **Làm sạch:** Chuyển dấu phẩy thành dấu chấm (`clean_numeric`).
2.  **Lọc Danh mục & Toán học:** Lọc Giá, Quận, Phường, Bề ngang.
3.  **Lọc Đặc điểm (VÀ) & KLP:** Quét cột mô tả tìm thang máy, hướng trạch... Nếu chọn `KLP`, tự động loại bỏ các nhà dính `TOH`, `DAD`, `QHH`, `GCH`, `GAC`.
4.  **Lọc Vị trí (HOẶC):** Tách bạch rõ "Mặt tiền" (số nhà không có dấu `.`) và "Hẻm" (Cột HEM = 1, 2, 3). Dùng "Mặt nạ" (Mask) gộp kết quả: *[Lấy Mặt Tiền] HOẶC [Lấy hẻm = 1]...*
5.  **Sắp xếp đa tầng (Multi-level Sorting):** Xếp hạng theo PL (TAR -> A -> HID), sau đó xếp theo Thời gian cập nhật (`Update_dt`) giảm dần (Mới nhất lên đầu).

### 5.3. Hàm `apply_dinh_gia()` - Thuật toán Định giá Tự động
Đây là hàm mô phỏng lại logic định giá phức tạp từ Google Sheets vào Python:
*   Dùng Regex (`re.search`) quét cột Mô tả tìm từ khóa `SLG` (Sau lộ giới) hoặc `SCN` (Sổ công nhận).
*   Lấy diện tích này nhân với "Đơn giá chuẩn" (Lấy từ Cột Q - `dinhgia`) để tính ra tổng giá trị thực (D: xxx Tỷ).

### 5.4. Nhóm hàm `get_aggrid_js_codes` & `render_aggrid` - Bảng Tương Tác & JavaScript
Để bảng dữ liệu có các tính năng tương tác giống một ứng dụng Web thực thụ, hệ thống tách riêng các đoạn mã JavaScript (JS) và "bơm" vào AgGrid:
*   `copy_text` / `copy_cus`: Lấy dữ liệu ô, gỡ bỏ các ký tự thừa (như http), tạo một thẻ text ảo, copy vào Clipboard và cảnh báo bằng hộp thoại Alert.
*   `sonha_dclick` / `tenduong_dclick`: Đọc dữ liệu từ "Cột tàng hình" (Hidden Columns chứa link quy hoạch / Drive) và dùng lệnh `window.open` để mở tab mới lập tức.
*   `sonha_style` / `tenduong_style`: Đổi màu CSS (Xanh dương, gạch chân) nếu phát hiện dòng đó có chứa "http" trong cột tàng hình.
*   **Khử trễ (Anti-Flicker):** Bảng Tab 1 có khả năng "đọc trộm" trực tiếp bộ nhớ của Tab 3 (thông qua `st.session_state`) để cập nhật trạng thái "Đã gửi" tức thì mà không cần chờ đọc file từ ổ cứng.

### 5.5. Hệ thống "Trí Nhớ Cơ Bắp" (Memory Mechanics)
*   **Nhớ Bộ Lọc Khách (BLK):** Hàm `build_blk` dịch các nút Checkbox trên UI thành 1 chuỗi ký tự (VD: `...MAT.HXT.KLP`) và lưu vào cột đặc biệt. Hàm `parse_blk` làm nhiệm vụ dịch ngược để tự động check lại các ô này.
*   **Nhớ Khách Hàng Cuối Cùng (`FILE_LAST_KID`):** Lưu ID khách hàng vào file text. Khi khởi động lại ứng dụng, hệ thống tự động quét vị trí Index của ID này để chọn sẵn khách hàng đang chăm sóc dở dang từ hôm trước.

---
**Lời kết cho lập trình viên kế nhiệm:** Mã nguồn của Đại Thế Kỷ Advisor CRM V1.0 kết hợp mạnh mẽ giữa Data Engineering (Xử lý chuỗi, Merge Data) và Frontend UX (AgGrid, JavaScript). Khi chỉnh sửa, hãy cực kỳ cẩn trọng với các cấu hình Tên Cột (trong `CONFIG_GSK_CM`), các hàm xử lý dấu thập phân và các biến đếm Session State (dùng để ép UI tải lại). Chúc bạn làm chủ dự án thành công!