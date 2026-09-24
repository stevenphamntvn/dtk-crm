# 📑 PROJECT HANDOVER: ĐẠI THẾ KỶ ADVISOR CRM (V1.0)

## 1. 🎯 Bối cảnh & Mục tiêu dự án
Hệ thống là một công cụ **Sales Advisor CRM** chuyên dụng cho lĩnh vực bất động sản (Đại Thế Kỷ). Nhiệm vụ cốt lõi là: 
- Quản lý kho nhà khổng lồ (GSK).
- Quản lý danh sách khách hàng tiềm năng (MyKID).
- Khớp nối (Matching) nhu cầu khách hàng với nhà hiện có thông qua bộ lọc thông minh.
- **Tech-stack:** Streamlit (UI), Pandas (Data Processing), Gspread (Google Sheets API), AgGrid (Interactive Grid), Oauth2client (Auth).

## 2. 📖 Từ điển Thuật ngữ & Ký hiệu (Domain Knowledge)
- **KID :** Mã định danh duy nhất của khách hàng.
- **UID :** Mã định danh duy nhất của mỗi căn nhà.
- **GSK :** Kho dữ liệu nhà gốc từ Google Sheets.
- **BLK (bo_loc_KID):** Chuỗi Protocol "não bộ" lưu trữ thói quen lọc của khách (VD: `Ten.G10-15T.QBT(1,2)+QPN.N4M.MAT.NOH`).
- **TTK / Thông tin KID:** Snapshot nhu cầu khách hàng dạng văn bản thô.
- **Thẻ Tag Đặc điểm:**
    - `MAT`: Mặt tiền | `NOH`: Nở hậu | `TMA`: Thang máy | `NTC`: Nội thất | `KLP`: Không lỗi phong thủy.
    - `CTB / SBT`: Trạng thái nhà đã bán (SOLD), cần hiển thị Italic/Xám trong Dashboard.
- **Trạng thái gửi nhà:**
    - `❌ Chưa gửi`: Nhà phù hợp nhưng chưa tương tác.
    - `🔘 Đã chọn`: Trạng thái tạm thời trên UI khi đang chọn nhà để gửi.
    - `✅ Đã gửi`: Đã lưu vào lịch sử gửi nhà (KID_log).


