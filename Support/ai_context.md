# TÓM TẮT DỰ ÁN
> [DÁN NỘI DUNG TỪ CONTEXT HANDOVER]

---
# CẤU TRÚC THƯ MỤC
```text
|-- DTK_CRM/
    |-- run.bat
    |-- Support/
        |-- ai_context.md
        |-- Context_Handover.md
        |-- export_to_ai.py
        |-- install.bat
    |-- Data/
        |-- crm_app.py
        |-- temp/
```

---
# CHI TIẾT MÃ NGUỒN

## File: `run.bat`
```python
@echo off
title HE THONG DAI THE KY ADVISOR (CRM V1.0)
color 0A

:: 1. Tự động chuyển đến thư mục gốc chứa file run.bat này
cd /d "%~dp0"

:: 2. Chạy Streamlit thông qua module Python để tránh lỗi 'not recognized'
echo [+] Dang khoi dong CRM Dashboard...
python -m streamlit run data\crm_app.py

pause
```

## File: `Support\Context_Handover.md`
```python
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



```

## File: `Support\export_to_ai.py`
```python
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

# Thêm 'cache' vào danh sách loại trừ để AI không đọc dữ liệu khách hàng
IGNORE_DIRS = {'.git', '__pycache__', 'venv', 'cache', '.streamlit'}
ALLOWED_EXTENSIONS = {'.py', '.bat', '.md'}
OUTPUT_FILE = os.path.join(CURRENT_DIR, 'ai_context.md')

def generate_context():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# TÓM TẮT DỰ ÁN\n> [DÁN NỘI DUNG TỪ CONTEXT HANDOVER]\n\n---\n")
        
        # Phần cấu trúc thư mục
        f.write("# CẤU TRÚC THƯ MỤC\n```text\n")
        for root, dirs, files in os.walk(PROJECT_ROOT):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            level = root.replace(PROJECT_ROOT, '').count(os.sep)
            indent = ' ' * 4 * level
            f.write(f"{indent}|-- {os.path.basename(root)}/\n")
            for file in files:
                if os.path.splitext(file)[1] in ALLOWED_EXTENSIONS:
                    f.write(f"{indent}    |-- {file}\n")
        f.write("```\n\n---\n")

        # Phần nội dung code
        f.write("# CHI TIẾT MÃ NGUỒN\n\n")
        for root, dirs, files in os.walk(PROJECT_ROOT):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for file in files:
                if os.path.splitext(file)[1] in ALLOWED_EXTENSIONS and file != 'ai_context.md':
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, PROJECT_ROOT)
                    f.write(f"## File: `{rel_path}`\n```python\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as cf:
                            f.write(cf.read())
                    except: pass
                    f.write("\n```\n\n")
    print(f"✅ Đã gộp code xong tại: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_context()
```

## File: `Support\install.bat`
```python
@echo off
title CAI DAT MOI TRUONG CRM (PYTHON 3.13)
color 0B

:: 1. Kiểm tra xem Python đã được cài chưa
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [LOI] Khong tim thay Python. Vui long cai Python 3.13 va tich vao 'Add Python to PATH'.
    pause
    exit
)

echo [+] Dang khoi tao moi truong ao (env_crm)...
python -m venv env_crm

echo [+] Dang kich hoat moi truong va cai dat thu vien...
:: Gọi pip của môi trường ảo để cài đặt
env_crm\Scripts\python.exe -m pip install --upgrade pip
env_crm\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo [OK] Moi truong da san sang!
echo [!] Luu y: Hay dung file run.bat moi de chay App.
pause
```

## File: `Data\crm_app.py`
```python
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import csv

from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from st_aggrid.shared import GridUpdateMode, DataReturnMode

# ==========================================
# 1. CẤU HÌNH HỆ THỐNG & COLUMN MAP
# ==========================================

# Tự động nhận diện thư mục đang chứa file crm_app.py (chính là thư mục 'data')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Nối vào tên file json
CREDS_JSON = os.path.join(BASE_DIR, "credentials.json")
SHEET_ID = "1a0roK3rSRQYlFMYIyC_5iMLNr0t7wUz5IRi0OdckPKA"
GSK_SHEET_NAME = "BT-PN.PK-6.0-10000"

CONFIG_GSK_CM = {
    "STT": "stt", "STATUS": "status", "NGAY": "ngay", "PL": "PL", 
    "QUAN": "quan", "SONHA": "sonha", "TENDUONG": "tenduong",
    "PHUONG": "phuong", "NGANG": "ngang", "DAI": "dai",
    "GIA": "gia", "PM2": "p/m2", "DIENTICH": "dientich",
    "KETCAU": "ketcau", "UID": "uid", "MOTACHITIET": "motachitiet"
}


import json # Thư viện bắt buộc cho tính năng Nhớ bộ lọc

# --- CẤU HÌNH TRẠM OFFLINE CACHE ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

FILE_GSK = os.path.join(CACHE_DIR, "gsk_cache.csv")
FILE_KID = os.path.join(CACHE_DIR, "mykid_cache.csv")
FILE_LOG = os.path.join(CACHE_DIR, "kid_log_cache.csv")
FILE_PENDING = os.path.join(CACHE_DIR, "pending_logs.csv")
FILE_PREFS = os.path.join(CACHE_DIR, "filter_prefs.json") # File não bộ CRM

# ==========================================
# 2. CÁC HÀM XỬ LÝ LÕI (CORE FUNCTIONS)
# ==========================================
def clean_numeric(series):
    """Xử lý số thập phân Việt Nam (3,5 -> 3.5)"""
    return pd.to_numeric(series.astype(str).str.replace(',', '.', regex=False), errors='coerce')

@st.cache_resource
def get_gspread_client():
    """Hàm sống còn: Kết nối Google API"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_JSON, scope)
    return gspread.authorize(creds)

def sync_data_with_gsheet():
    """Hàm Đồng bộ: Đẩy Log lên và Tải Data về"""
    gc = get_gspread_client()
    with st.spinner("🔄 Đang đồng bộ dữ liệu... Vui lòng không đóng trang!"):
        try:
            # 1. PUSH PENDING LOGS
            if os.path.exists(FILE_PENDING):
                df_pending = pd.read_csv(FILE_PENDING)
                if not df_pending.empty:
                    ws_log = gc.open_by_key(SHEET_ID).worksheet("KID_log")
                    ws_log.append_rows(df_pending.values.tolist())
                    os.remove(FILE_PENDING) 

            # 2. PULL NEW DATA
            ws_houses = gc.open_by_key(SHEET_ID).worksheet(GSK_SHEET_NAME)
            ws_kids = gc.open_by_key(SHEET_ID).worksheet("MyKID")
            ws_logs = gc.open_by_key(SHEET_ID).worksheet("KID_log")

            df_houses = pd.DataFrame(ws_houses.get_all_records())
            df_kids = pd.DataFrame(ws_kids.get_all_records())
            df_logs = pd.DataFrame(ws_logs.get_all_records())

            if 'sonha' in df_houses.columns:
                df_houses['isMAT'] = ~df_houses['sonha'].astype(str).str.contains(r'\.', na=False)

            df_houses.to_csv(FILE_GSK, index=False)
            df_kids.to_csv(FILE_KID, index=False)
            df_logs.to_csv(FILE_LOG, index=False)
            
            st.toast("✅ Đã đồng bộ hoàn tất với Google Sheets!")
        except Exception as e:
            st.error(f"Lỗi đồng bộ: {e}")

def load_local_data():
    """Hàm Đọc Cache: Tốc độ O(1)"""
    try:
        if not os.path.exists(FILE_GSK):
            st.warning("Lần đầu khởi chạy, hệ thống đang tải kho dữ liệu gốc...")
            sync_data_with_gsheet()
            
        df_h = pd.read_csv(FILE_GSK) if os.path.exists(FILE_GSK) else pd.DataFrame()
        df_k = pd.read_csv(FILE_KID) if os.path.exists(FILE_KID) else pd.DataFrame()
        df_l = pd.read_csv(FILE_LOG) if os.path.exists(FILE_LOG) else pd.DataFrame()
        
        # Trộn Log Pending để hiện dấu ✅ Realtime
        if os.path.exists(FILE_PENDING):
            df_p = pd.read_csv(FILE_PENDING)
            if not df_p.empty:
                df_p.columns = df_l.columns 
                df_l = pd.concat([df_l, df_p], ignore_index=True)
                
        return df_h, df_k, df_l
    except Exception as e:
        st.error(f"Lỗi đọc Cache: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# ==========================================
# 3. CÁC HÀM XỬ LÝ GIAO DIỆN & LOGIC (MODULES)
# ==========================================
# ==========================================
# 3. CÁC HÀM XỬ LÝ GIAO DIỆN & LOGIC (MODULES)
# ==========================================
def get_kid_prefs(kid_id, default_tc, kid_tags_str):
    """Trích xuất thói quen lọc của khách hàng từ ổ cứng"""
    default_prefs = {
        "min_gia": max(0.0, default_tc - 2.0), "max_gia": default_tc + 1.0,
        "quan": [], "phuong": [], "min_ngang": 3.7,
        "mat": "MAT" in str(kid_tags_str), "noh": "NOH" in str(kid_tags_str), 
        "tma": "TMA" in str(kid_tags_str), "ntc": False, "no_bad": True
    }
    if os.path.exists(FILE_PREFS):
        try:
            with open(FILE_PREFS, "r", encoding="utf-8") as f:
                all_prefs = json.load(f)
                if kid_id in all_prefs:
                    saved = all_prefs[kid_id]
                    for k, v in saved.items():
                        default_prefs[k] = v
        except:
            pass
    return default_prefs

def save_kid_prefs(kid_id, prefs_dict):
    """Ghi nhớ thói quen lọc của khách hàng vào ổ cứng"""
    all_prefs = {}
    if os.path.exists(FILE_PREFS):
        try:
            with open(FILE_PREFS, "r", encoding="utf-8") as f:
                all_prefs = json.load(f)
        except:
            pass
    all_prefs[kid_id] = prefs_dict
    with open(FILE_PREFS, "w", encoding="utf-8") as f:
        json.dump(all_prefs, f, ensure_ascii=False, indent=4)



from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from st_aggrid.shared import GridUpdateMode, DataReturnMode

# ==========================================
# 1. CẤU HÌNH HỆ THỐNG & COLUMN MAP
# ==========================================
CREDS_JSON = os.path.join(BASE_DIR, "credentials.json")
SHEET_ID = "1a0roK3rSRQYlFMYIyC_5iMLNr0t7wUz5IRi0OdckPKA"
GSK_SHEET_NAME = "BT-PN.PK-6.0-10000"

CONFIG_GSK_CM = {
    "STT": "stt", "STATUS": "status", "NGAY": "ngay", "PL": "PL", 
    "QUAN": "quan", "SONHA": "sonha", "TENDUONG": "tenduong",
    "PHUONG": "phuong", "NGANG": "ngang", "DAI": "dai",
    "GIA": "gia", "PM2": "p/m2", "DIENTICH": "dientich",
    "KETCAU": "ketcau", "UID": "uid", "MOTACHITIET": "motachitiet"
}


import json # Thư viện bắt buộc cho tính năng Nhớ bộ lọc

# --- CẤU HÌNH TRẠM OFFLINE CACHE ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

FILE_GSK = os.path.join(CACHE_DIR, "gsk_cache.csv")
FILE_KID = os.path.join(CACHE_DIR, "mykid_cache.csv")
FILE_LOG = os.path.join(CACHE_DIR, "kid_log_cache.csv")
FILE_PENDING = os.path.join(CACHE_DIR, "pending_logs.csv")
FILE_PREFS = os.path.join(CACHE_DIR, "filter_prefs.json") # File não bộ CRM

# ==========================================
# 2. CÁC HÀM XỬ LÝ LÕI (CORE FUNCTIONS)
# ==========================================


def clean_numeric(series):
    """Xử lý số thập phân: Chuyển 3,5 hoặc 3.5 về đúng 3.5 (float)"""
    if series is None: return 0.0
    # Chuyển về string, thay dấu phẩy thành dấu chấm, sau đó ép kiểu float
    s = series.astype(str).str.replace(',', '.', regex=False).str.strip()
    return pd.to_numeric(s, errors='coerce').fillna(0.0)
@st.cache_resource
def get_gspread_client():
    """Hàm sống còn: Kết nối Google API"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_JSON, scope)
    return gspread.authorize(creds)

def sync_data_with_gsheet(direction="push"):
    """Hàm Đồng bộ: Đẩy (Push) hoặc Tải về (Pull) rõ ràng"""
    gc = get_gspread_client()
    with st.spinner(f"🔄 Đang đồng bộ ({'Đẩy lên Cloud' if direction=='push' else 'Tải về Máy'})..."):
        try:
            ws_houses = gc.open_by_key(SHEET_ID).worksheet(GSK_SHEET_NAME)
            ws_kids = gc.open_by_key(SHEET_ID).worksheet("MyKID")
            ws_logs = gc.open_by_key(SHEET_ID).worksheet("KID_log")

            # 1. NẾU LÀ PUSH: Lấy Local đè lên Cloud
            if direction == "push":
                if os.path.exists(FILE_LOG):
                    df_log_local = pd.read_csv(FILE_LOG).fillna("")
                    ws_logs.clear()
                    if not df_log_local.empty:
                        ws_logs.update([df_log_local.columns.tolist()] + df_log_local.astype(str).values.tolist())
                
                if os.path.exists(FILE_KID):
                    df_kid_local = pd.read_csv(FILE_KID).fillna("")
                    ws_kids.clear()
                    if not df_kid_local.empty:
                        ws_kids.update([df_kid_local.columns.tolist()] + df_kid_local.astype(str).values.tolist())

            # 2. LUÔN LUÔN PULL VỀ LẠI LOCAL CHUẨN HÓA (Dù push xong hay chỉ pull)
            df_houses = pd.DataFrame(ws_houses.get_all_records())
            df_kids = pd.DataFrame(ws_kids.get_all_records())
            df_logs = pd.DataFrame(ws_logs.get_all_records())

            if 'sonha' in df_houses.columns:
                df_houses['isMAT'] = ~df_houses['sonha'].astype(str).str.contains(r'\.', na=False)

            df_houses.to_csv(FILE_GSK, index=False)
            df_kids.to_csv(FILE_KID, index=False)
            df_logs.to_csv(FILE_LOG, index=False)

            if os.path.exists(FILE_PENDING):
                os.remove(FILE_PENDING)

            msg = "Đã lưu dữ liệu lên Google Sheets!" if direction == "push" else "Đã tải dữ liệu dọn dẹp từ Google Sheets về máy!"
            st.toast(f"✅ {msg}")
        except Exception as e:
            st.error(f"Lỗi đồng bộ: {e}")
import re

# ==========================================
# THÊM 2 HÀM BĂM CHUỖI VÀO PHẦN "CÁC HÀM XỬ LÝ LÕI"
# ==========================================
import re

# --- TỪ ĐIỂN ĐỒNG BỘ NGÔN NGỮ (GSK <-> BLK) NGUYÊN KHỐI ---
MAP_QUAN = {
    "Bình Thạnh": "QBT", "Phú Nhuận": "QPN", "Gò Vấp": "QGV",
    "Tân Bình": "QTB", "Tân Phú": "QTP", "Bình Tân": "QBTA",
    "Quận 1": "Q1", "Quận 3": "Q3", "Quận 10": "Q10", "Quận 11": "Q11",
    "Quận 2": "Q2", "Quận 4": "Q4", "Quận 5": "Q5", "Quận 6": "Q6",
    "Quận 7": "Q7", "Quận 8": "Q8", "Quận 9": "Q9", "Quận 12": "Q12"
}
# Từ điển dịch ngược để UI hiểu (VD: QBT -> Bình Thạnh)
REV_MAP_QUAN = {v: k for k, v in MAP_QUAN.items()}

# ==========================================
# CÁC HÀM XỬ LÝ LÕI CHUỖI PROTOCOL
# ==========================================
def parse_blk(blk_string):
    """Giải mã chuỗi Protocol chuẩn nguyên khối"""
    data = {"ten": "", "min_gia": 0, "max_gia": 0, "quan_phuong": {}, "min_ngang": 0, "tags": []}
    if not blk_string or pd.isna(blk_string): return data
    
    blk_str = str(blk_string).strip()
    parts = blk_str.split('.')
    if parts: data["ten"] = parts[0]
    
    match_gia = re.search(r'G(\d+)-(\d+)T', blk_str)
    if match_gia:
        data["min_gia"], data["max_gia"] = int(match_gia.group(1)), int(match_gia.group(2))
    
    # Bóc chính xác cụm bắt đầu bằng Q (VD: QBT, Q1, QPN)
    q_parts = re.findall(r'(Q[A-Z0-9]+)(?:\(([\d,]+)\))?', blk_str)
    for q_code, p_list in q_parts:
        data["quan_phuong"][q_code] = p_list.split(',') if p_list else []
        
    match_ngang = re.search(r'N(\d+)M', blk_str)
    if match_ngang: data["min_ngang"] = int(match_ngang.group(1))
        
    for tag in ["MAT", "NOH", "TMA", "KLP", "NTC"]:
        if tag in blk_str: data["tags"].append(tag)
            
    return data

def build_blk(ten_khach, min_gia, max_gia, dict_qp_codes, min_ngang, tags):
    """Đóng gói chuỗi Protocol chuẩn"""
    parts = [str(ten_khach)]
    parts.append(f"G{int(min_gia)}-{int(max_gia)}T")
    
    q_list = []
    for q_code, ps in dict_qp_codes.items():
        q_list.append(f"{q_code}({','.join(ps)})" if ps else f"{q_code}")
    if q_list: parts.append("+".join(q_list))
    
    if min_ngang > 0: parts.append(f"N{int(min_ngang)}M")
    if tags: parts.append(".".join(tags))
    return ".".join(parts)


def load_local_data():
    """Đọc dữ liệu, an toàn với file rỗng (chống lỗi No columns to parse)"""
    try:
        if not os.path.exists(FILE_GSK): 
            st.warning("Lần đầu khởi chạy, hệ thống đang tải kho dữ liệu gốc...")
            sync_data_with_gsheet(direction="pull")
            
        # HÀM ĐỌC AN TOÀN: Bỏ qua lỗi nếu file bị xóa trắng 0 byte
        def safe_read(filepath):
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                try:
                    return pd.read_csv(filepath)
                except:
                    return pd.DataFrame()
            return pd.DataFrame()

        df_h = safe_read(FILE_GSK)
        df_k = safe_read(FILE_KID)
        df_l = safe_read(FILE_LOG)
        
        for df in [df_h, df_k, df_l]:
            if not df.empty: df.columns = df.columns.str.strip()
            
        if not df_k.empty:
            if 'bo_loc_KID' not in df_k.columns: df_k['bo_loc_KID'] = ""
            ttk_col = next((c for c in df_k.columns if 'thongtin' in c.lower() or 'ttk' in c.lower()), None)
            if ttk_col:
                mask = (df_k['bo_loc_KID'].isna()) | (df_k['bo_loc_KID'].astype(str).str.strip() == "")
                df_k.loc[mask, 'bo_loc_KID'] = df_k.loc[mask, ttk_col]
                    
        return df_h, df_k, df_l
    except Exception as e:
        st.error(f"Lỗi đọc Cache: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
# ==========================================
# DÁN ĐÈ TOÀN BỘ KHỐI "with tab1:" CHO ĐẾN "with tab2:"
# --- HÀM CẬP NHẬT TRẠNG THÁI UI ---
def update_filters_from_kid():
    selected_str = st.session_state.selected_kid_ui
    kid_id = selected_str.split(" - ")[0]
    
    # Tìm chuỗi BLK (ưu tiên BLK, nếu không có lấy TTK)
    kid_row = df_kids[df_kids['KID'].astype(str) == kid_id].iloc[0]
    blk_str = kid_info.get('bo_loc_KID', kid_info.get('thongtin_KID', ""))
    
    # Giải mã
    prefs = parse_blk(blk_str)
    
    # Cập nhật vào session_state của các widget
    st.session_state.f_min_gia = float(prefs['min_gia'])
    st.session_state.f_max_gia = float(prefs['max_gia'])
    st.session_state.f_ngang = float(prefs['min_ngang'])
    st.session_state.f_quan = list(prefs['quan_phuong'].keys())
    
    # Cập nhật các checkbox tags
    for tag in ["MAT", "NOH", "TMA", "KLP", "NTC"]:
        st.session_state[f"f_tag_{tag}"] = tag in prefs['tags']

def pull_latest_houses_only():
    """Tải riêng danh sách nhà mới nhất từ Google Sheets (Không đụng tới Log/BLK)"""
    gc = get_gspread_client()
    with st.spinner("⬇️ Đang cập nhật kho nhà từ Google Sheets..."):
        try:
            ws_houses = gc.open_by_key(SHEET_ID).worksheet(GSK_SHEET_NAME)
            df_new_houses = pd.DataFrame(ws_houses.get_all_records())

            if 'sonha' in df_new_houses.columns:
                df_new_houses['isMAT'] = ~df_new_houses['sonha'].astype(str).str.contains(r'\.', na=False)

            df_new_houses.to_csv(FILE_GSK, index=False)
            st.toast("✅ Đã làm mới kho nhà thành công!")
        except Exception as e:
            st.error(f"Lỗi làm mới kho nhà: {e}")

# ==========================================
# 3. CÁC HÀM XỬ LÝ GIAO DIỆN & LOGIC (MODULES)
# ==========================================
def get_kid_prefs(kid_id, default_tc, kid_tags_str):
    """Trích xuất thói quen lọc của khách hàng từ ổ cứng"""
    default_prefs = {
        "min_gia": max(0.0, default_tc - 2.0), "max_gia": default_tc + 1.0,
        "quan": [], "phuong": [], "min_ngang": 3.7,
        "mat": "MAT" in str(kid_tags_str), "noh": "NOH" in str(kid_tags_str), 
        "tma": "TMA" in str(kid_tags_str), "ntc": False, "no_bad": True
    }
    if os.path.exists(FILE_PREFS):
        try:
            with open(FILE_PREFS, "r", encoding="utf-8") as f:
                all_prefs = json.load(f)
                if kid_id in all_prefs:
                    saved = all_prefs[kid_id]
                    for k, v in saved.items():
                        default_prefs[k] = v
        except: pass
    return default_prefs

def save_kid_prefs(kid_id, prefs_dict):
    """Ghi nhớ thói quen lọc của khách hàng vào ổ cứng"""
    all_prefs = {}
    if os.path.exists(FILE_PREFS):
        try:
            with open(FILE_PREFS, "r", encoding="utf-8") as f:
                all_prefs = json.load(f)
        except: pass
    all_prefs[kid_id] = prefs_dict
    with open(FILE_PREFS, "w", encoding="utf-8") as f:
        json.dump(all_prefs, f, ensure_ascii=False, indent=4)

def update_offline_logs(df_to_save):
    """Ghi đè 6 cột chuẩn xuống cache offline"""
    try:
        df_to_save.to_csv(FILE_LOG, index=False)
        return True
    except:
        return False

def filter_houses(df_houses, min_gia, max_gia, selected_quan, selected_phuong, min_ngang, require_noh, require_tma, require_ntc, no_bad_fengshui, only_mat):
    """Module Lọc Dữ Liệu - Khôi phục từ bản gốc"""
    results = df_houses.copy()
    results.columns = results.columns.str.strip()
    
    if CONFIG_GSK_CM["GIA"] in results.columns:
        results['gia_val'] = clean_numeric(results[CONFIG_GSK_CM["GIA"]])
        results = results[(results['gia_val'] >= min_gia) & (results['gia_val'] <= max_gia)]
        
    if selected_quan and CONFIG_GSK_CM["QUAN"] in results.columns:
        results = results[results[CONFIG_GSK_CM["QUAN"]].isin(selected_quan)]
    if selected_phuong and CONFIG_GSK_CM["PHUONG"] in results.columns:
        results = results[results[CONFIG_GSK_CM["PHUONG"]].isin(selected_phuong)]
        
    if min_ngang > 0 and CONFIG_GSK_CM["NGANG"] in results.columns:
        results['ngang_val'] = clean_numeric(results[CONFIG_GSK_CM["NGANG"]])
        results = results[results['ngang_val'] >= min_ngang]
    
    if CONFIG_GSK_CM["MOTACHITIET"] in results.columns:
        if require_noh:
            results = results[results[CONFIG_GSK_CM["MOTACHITIET"]].astype(str).str.contains("NOH", na=False)]
        if require_tma:
            results = results[results[CONFIG_GSK_CM["MOTACHITIET"]].astype(str).str.contains("TMA", na=False)]
        if require_ntc:
            results = results[results[CONFIG_GSK_CM["MOTACHITIET"]].astype(str).str.contains("NTC", na=False)]
        if no_bad_fengshui:
            for tag in ["TOH", "DAD", "QHH"]:
                results = results[~results[CONFIG_GSK_CM["MOTACHITIET"]].astype(str).str.contains(tag, na=False)]
    
    if only_mat and 'isMAT' in results.columns:
        results = results[results['isMAT'] == True]
        
    if CONFIG_GSK_CM["PL"] in results.columns:
        results['pl_upper'] = results[CONFIG_GSK_CM["PL"]].astype(str).str.strip().str.upper()
        results = results[results['pl_upper'].isin(['TAR', 'HID', 'A'])]
        results['pl_rank'] = results['pl_upper'].map({'TAR': 1, 'A': 2, 'HID': 3})
        results = results.sort_values(by='pl_rank')
    else:
        return pd.DataFrame()

    if not results.empty and CONFIG_GSK_CM["MOTACHITIET"] in results.columns:
        vip_tags = ["NOH", "TOH", "2MT", "CGO", "P1C", "T1C", "GAC", "DAD", "NTC", "SA4", "MTR", "SCN", "QHH"]
        results['dacdiem'] = results[CONFIG_GSK_CM["MOTACHITIET"]].apply(
            lambda x: ", ".join([tag for tag in vip_tags if tag in str(x)])
        )
    elif not results.empty:
        results['dacdiem'] = ""
        
    return results

def render_aggrid(results, df_log, kid_id):
    """Bảng chọn nhà Tab 1 - Bật bộ lọc cho toàn bộ các cột"""
    sent_uids = []
    target_kid = str(kid_id).strip()
    
    if not df_log.empty:
        kid_col = next((c for c in df_log.columns if 'KID' in c.upper()), df_log.columns[0])
        uid_col = next((c for c in df_log.columns if 'UID' in c.upper()), df_log.columns[1])
        try:
            df_log_kid = df_log[df_log[kid_col].astype(str).str.strip() == target_kid]
            sent_uids = df_log_kid[uid_col].astype(str).str.strip().tolist()
        except: pass
    
    results['Trạng thái'] = results[CONFIG_GSK_CM["UID"]].astype(str).str.strip().apply(
        lambda x: '✅ Đã gửi' if x in sent_uids else '❌ Chưa gửi'
    )
    
    display_cols = [
        'Trạng thái', CONFIG_GSK_CM["PL"], CONFIG_GSK_CM["QUAN"], CONFIG_GSK_CM["PHUONG"], 
        CONFIG_GSK_CM["SONHA"], CONFIG_GSK_CM["TENDUONG"], CONFIG_GSK_CM["NGANG"], 
        CONFIG_GSK_CM["DAI"], CONFIG_GSK_CM["GIA"], CONFIG_GSK_CM["KETCAU"], 
        'dacdiem', CONFIG_GSK_CM["UID"]
    ]
    
    # Đảm bảo các cột số là kiểu float để AgGrid lọc chính xác
    num_cols = [CONFIG_GSK_CM["NGANG"], CONFIG_GSK_CM["DAI"], CONFIG_GSK_CM["GIA"]]
    for col in num_cols:
        if col in results.columns:
            results[col] = clean_numeric(results[col])

    df_display = results[display_cols].copy()
    
    gb = GridOptionsBuilder.from_dataframe(df_display)
    
    # Cấu hình mặc định: Cho phép lọc và sắp xếp cho TẤT CẢ các cột
    gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True,
        menuTabs=['filterMenuTab', 'generalMenuTab']
    )

    # JS Code cho nút chọn nhà
    toggle_jscode = JsCode("""
    function(params) {
        setTimeout(function () {
            if (params.event && params.event.detail === 1) { 
                const value = params.value; const field = params.colDef.field;
                if (value === '✅ Đã gửi') return; 
                let newValue = (value === '🔘 Đã chọn') ? '❌ Chưa gửi' : '🔘 Đã chọn';
                params.node.setDataValue(field, newValue);
            }
        }, 80);
    }
    """)

    gb.configure_column('Trạng thái', onCellClicked=toggle_jscode, editable=False, pinned='left', width=130)
    
    # Định dạng hiển thị số thực trong bảng
    gb.configure_column(CONFIG_GSK_CM["NGANG"], type=["numericColumn", "numberColumnFilter"])
    gb.configure_column(CONFIG_GSK_CM["DAI"], type=["numericColumn", "numberColumnFilter"])
    gb.configure_column(CONFIG_GSK_CM["GIA"], type=["numericColumn", "numberColumnFilter"])

    ag_response = AgGrid(
        df_display, gridOptions=gb.build(), allow_unsafe_jscode=True, 
        update_mode=GridUpdateMode.VALUE_CHANGED, data_return_mode=DataReturnMode.AS_INPUT,
        fit_columns_on_grid_load=False, theme='streamlit', height=450,
        key=f"grid_tab1_{target_kid}"
    )
    return pd.DataFrame(ag_response['data'])

def render_tab3_aggrid(df_log, df_houses):
    """Bảng Tab 3: Hiển thị thông minh 6 cột GSK + Lookup Check SOLD"""
    if df_log.empty:
        st.info("Chưa có nhật ký gửi nhà.")
        return

    try:
        df_log = df_log.iloc[:, :6]
        df_log.columns = ["KID", "UID", "thongtin_KID", "ngay_gui", "trang_thai", "phan_hoi"]
    except Exception:
        pass

    houses_info = {}
    if not df_houses.empty:
        for _, h in df_houses.iterrows():
            uid = str(h.get('uid', '')).strip()
            sonha = str(h.get('sonha', '')).strip()
            tenduong = str(h.get('tenduong', '')).strip()
            gia = str(h.get('gia', '')).strip()
            pl = str(h.get('PL', '')).strip().upper()
            
            status_text = " [SOLD]" if pl in ['CTB', 'SBT'] else ""
            houses_info[uid] = {
                'display': f"{sonha} {tenduong} - {gia}T{status_text}",
                'is_sold': pl in ['CTB', 'SBT']
            }

    display_data = []
    for _, row in df_log.iloc[::-1].iterrows(): 
        uid = str(row['UID']).strip()
        h_data = houses_info.get(uid, {'display': uid, 'is_sold': False})
        
        display_data.append({
            'KID': row['KID'],
            'Thông tin KH': row.get('thongtin_KID', ''),
            'Nhà gửi': h_data['display'],
            'Ngày gửi': row.get('ngay_gui', ''),
            'Trạng thái': row.get('trang_thai', 'chưa gửi'),
            'Phản hồi': row.get('phan_hoi', ''),
            '_is_sold': h_data['is_sold'], 
            '_uid_key': uid 
        })

    df_display = pd.DataFrame(display_data)

    row_style_jscode = JsCode("""
    function(params) {
        if (params.data && params.data._is_sold) {
            return { 'color': '#9e9e9e', 'fontStyle': 'italic', 'backgroundColor': '#f5f5f5' };
        }
        if (params.data && params.data['Trạng thái'] === 'đã gửi') {
            return { 'backgroundColor': '#e8f5e9' };
        }
        return null;
    }
    """)

    gb = GridOptionsBuilder.from_dataframe(df_display)
    gb.configure_column('_is_sold', hide=True)
    gb.configure_column('_uid_key', hide=True)
    gb.configure_column('Trạng thái', editable=True, cellEditor='agSelectCellEditor', 
                        cellEditorParams={'values': ['chưa gửi', 'đã gửi']})
    gb.configure_column('Phản hồi', editable=True)
    gb.configure_grid_options(getRowStyle=row_style_jscode)
    
    ag_response = AgGrid(df_display, gridOptions=gb.build(), allow_unsafe_jscode=True, 
                         update_mode=GridUpdateMode.VALUE_CHANGED, theme='streamlit', height=500)

    if ag_response['data'] is not None:
        updated_df = pd.DataFrame(ag_response['data'])
        if not updated_df.empty:
            save_df = updated_df[['KID', '_uid_key', 'Thông tin KH', 'Ngày gửi', 'Trạng thái', 'Phản hồi']].copy()
            save_df.columns = ["KID", "UID", "thongtin_KID", "ngay_gui", "trang_thai", "phan_hoi"]
            
            # Logic lưu đè chuẩn xác, chống rác nhân bản
            if not updated_df.equals(df_display): 
                save_df.iloc[::-1].to_csv(FILE_LOG, index=False) 
                st.toast("💾 Đã lưu trạng thái vào hệ thống!")

def save_pending_logs(schedule_dict, kid_id, df_kids):
    """Lưu trực tiếp thẳng vào FILE_LOG, đoạn tuyệt với file pending trung gian"""
    try:
        file_exists = os.path.isfile(FILE_LOG)
        
        # 1. Chống trùng lặp từ Log gốc
        existing_pairs = set()
        if os.path.exists(FILE_LOG):
            try:
                tmp = pd.read_csv(FILE_LOG)
                if not tmp.empty:
                    for _, r in tmp.iterrows(): 
                        existing_pairs.add((str(r.iloc[0]).strip(), str(r.iloc[1]).strip()))
            except: pass

        # 2. Bóc thông tin Khách hàng
        kid_row = df_kids[df_kids['KID'].astype(str).str.strip() == str(kid_id).strip()]
        ttk_col = next((c for c in df_kids.columns if 'thongtin' in c.lower() or 'ttk' in c.lower()), df_kids.columns[1])
        ttk_snapshot = str(kid_row[ttk_col].values[0]) if not kid_row.empty else ""

        new_entries = []
        for uid, ngay_hen in schedule_dict.items():
            if (str(kid_id).strip(), str(uid).strip()) not in existing_pairs:
                new_entries.append([
                    str(kid_id).strip(),
                    str(uid).strip(),
                    ttk_snapshot,
                    ngay_hen.strftime("%Y-%m-%d"),
                    "chưa gửi",
                    ""
                ])
        
        if not new_entries:
            st.warning("⚠️ Những nhà này đã có trong lịch gửi của khách này rồi!")
            return

        # LƯU THẲNG VÀO FILE LOG GỐC
        with open(FILE_LOG, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["KID", "UID", "thongtin_KID", "ngay_gui", "trang_thai", "phan_hoi"])
            writer.writerows(new_entries)
                
        st.toast(f"✅ Đã thêm {len(new_entries)} lịch gửi mới!")
        st.rerun() 
    except Exception as e:
        st.error(f"Lỗi ghi log: {e}")
# ==========================================
# 4. GIAO DIỆN CHÍNH (MAIN UI)
# ==========================================
st.set_page_config(page_title="Đại Thế Kỷ Advisor CRM", layout="wide")
st.title("🚀 ĐẠI THẾ KỶ ADVISOR - CRM V1.0")
st.markdown("---")

df_houses, df_kids, df_log = load_local_data()

with st.sidebar:
    st.header("Trạm Đồng Bộ 🔄")
    st.info("💡 Hướng dẫn:\n- **Push**: Lưu thao tác (Gửi nhà/Đổi trạng thái) lên Cloud.\n- **Pull**: Tải dữ liệu về App (Dùng sau khi dọn rác trên Google Sheets).")
    
    if st.button("📤 ĐẨY LÊN CLOUD (Push)", type="primary", use_container_width=True):
        sync_data_with_gsheet(direction="push")
        st.rerun()
        
    if st.button("📥 TẢI VỀ MÁY (Pull)", use_container_width=True):
        sync_data_with_gsheet(direction="pull")
        st.rerun()

tab1, tab2, tab3 = st.tabs(["🎯 Khớp Nhu Cầu", "👥 Danh Sách MyKID", "📝 Nhật Ký Zalo (Dashboard)"])

# --- TAB 1 ---
# --- TAB 1 ---
with tab1:
    st.header("🎯 Gợi ý nhà phù hợp cho khách")
    if df_houses.empty or df_kids.empty:
        st.warning("Thiếu dữ liệu nguồn.")
    else:
        col_left, col_right = st.columns([1, 2])
        
        with col_left:
            st.subheader("1. Chọn khách hàng")
            ten_col = next((c for c in df_kids.columns if 'Tên' in c or 'Zalo' in c), df_kids.columns[1])
            
            kid_list = df_kids['KID'].astype(str) + " - " + df_kids[ten_col].astype(str)
            selected_kid_str = st.selectbox("Khách hàng đang chăm sóc:", kid_list, key="sb_kid")
            
            kid_id = selected_kid_str.split(" - ")[0]
            kid_row = df_kids[df_kids['KID'].astype(str) == str(kid_id)].iloc[0]
            
            # --- ĐỒNG BỘ BỘ LỌC TỪ BLK VÀO SESSION STATE ---
            if 'active_kid' not in st.session_state or st.session_state.active_kid != kid_id:
                st.session_state.active_kid = kid_id
                blk_str = kid_row.get('bo_loc_KID', '')
                prefs = parse_blk(blk_str)
                
                st.session_state.f_min_gia = float(prefs['min_gia'])
                st.session_state.f_max_gia = float(prefs['max_gia'])
                st.session_state.f_ngang = float(prefs['min_ngang'])
                
                # DỊCH MÃ TẮT (QBT) THÀNH TÊN FULL (Bình Thạnh) ĐỂ HIỆN LÊN UI
                q_codes = list(prefs['quan_phuong'].keys())
                st.session_state.f_quan = [REV_MAP_QUAN.get(q, q) for q in q_codes]
                st.session_state.f_phuong = [p for sub in prefs['quan_phuong'].values() for p in sub]
                st.session_state.f_tags = prefs['tags']

            txt_tc = f"{int(st.session_state.f_min_gia)}-{int(st.session_state.f_max_gia)} Tỷ"
            txt_kv = ", ".join(st.session_state.f_quan) if st.session_state.f_quan else "Chưa rõ"
            st.info(f"**Nhu cầu:** {txt_tc} | **Khu vực:** {txt_kv}")
            
            st.subheader("2. Tinh chỉnh bộ lọc")
            min_gia = st.number_input("Giá từ (Tỷ)", value=st.session_state.f_min_gia, step=1.0)
            max_gia = st.number_input("Đến (Tỷ)", value=st.session_state.f_max_gia, step=1.0)
            
            # ========================================================
            # TIỀN XỬ LÝ DỮ LIỆU: CHUẨN HÓA HOA THƯỜNG & LỌC TAR, A, HID
            # ========================================================
            df_h_clean = df_houses.copy()
            
            # 1. Chuẩn hóa Quận
            if CONFIG_GSK_CM["QUAN"] in df_h_clean.columns:
                df_h_clean[CONFIG_GSK_CM["QUAN"]] = df_h_clean[CONFIG_GSK_CM["QUAN"]].astype(str).str.strip().str.title()
            
            # 2. Chuẩn hóa Phường: Gọt bỏ đuôi .0 (VD: 15.0 -> 15)
            if CONFIG_GSK_CM["PHUONG"] in df_h_clean.columns:
                df_h_clean[CONFIG_GSK_CM["PHUONG"]] = (
                    df_h_clean[CONFIG_GSK_CM["PHUONG"]]
                    .astype(str)
                    .str.strip()
                    .str.replace(r'\.0$', '', regex=True) # Xóa .0 ở cuối
                    .str.title()
                )

            # 3. Chuẩn hóa Ngang/Dài/Giá để tránh lỗi hiển thị sai
            for col in [CONFIG_GSK_CM["NGANG"], CONFIG_GSK_CM["DAI"], CONFIG_GSK_CM["GIA"]]:
                if col in df_h_clean.columns:
                    df_h_clean[col] = clean_numeric(df_h_clean[col])
            
            # 4. Lọc danh sách nhà chỉ còn TAR, A, HID để cấp cho UI Dropdown
            valid_pl = ['TAR', 'A', 'HID']
            if CONFIG_GSK_CM["PL"] in df_h_clean.columns:
                mask_pl = df_h_clean[CONFIG_GSK_CM["PL"]].astype(str).str.strip().str.upper().isin(valid_pl)
                df_valid_pl = df_h_clean[mask_pl]
            else:
                df_valid_pl = df_h_clean
            # ========================================================

            # Lấy danh sách Quận SẠCH
            districts = df_valid_pl[CONFIG_GSK_CM["QUAN"]].dropna().unique().tolist()
            districts = [q for q in districts if q and q.lower() != 'nan']
            
            sel_q = st.multiselect("Chọn Quận", districts, default=[q for q in st.session_state.f_quan if q in districts])
            
            # Lấy danh sách Phường SẠCH theo Quận
            if sel_q:
                mask_q = df_valid_pl[CONFIG_GSK_CM["QUAN"]].isin(sel_q)
                list_p = df_valid_pl[mask_q][CONFIG_GSK_CM["PHUONG"]].dropna().unique().tolist()
                list_p = [p for p in list_p if p and p.lower() != 'nan']
            else:
                list_p = []
                
            sel_p = st.multiselect("Chọn Phường", list_p, default=[p for p in st.session_state.f_phuong if p in list_p])
            
            min_n = st.number_input("Ngang tối thiểu (m)", value=st.session_state.f_ngang, step=1.0)
            
            st.write("Yêu cầu:")
            t1, t2, t3 = st.columns(3)
            f_mat = t1.checkbox("Mặt tiền", value="MAT" in st.session_state.f_tags)
            f_noh = t1.checkbox("Nở hậu", value="NOH" in st.session_state.f_tags)
            f_tma = t2.checkbox("Thang máy", value="TMA" in st.session_state.f_tags)
            f_ntc = t2.checkbox("Nội thất", value="NTC" in st.session_state.f_tags)
            f_klp = t3.checkbox("Không lỗi", value="KLP" in st.session_state.f_tags)

        with col_right:
            st.subheader("3. Kết quả tìm kiếm")
            # TRUYỀN DỮ LIỆU ĐÃ CHUẨN HÓA (df_h_clean) ĐỂ LỌC CHÍNH XÁC 100%
            results = filter_houses(df_h_clean, min_gia, max_gia, sel_q, sel_p, min_n, f_noh, f_tma, f_ntc, f_klp, f_mat)
            
            if not results.empty:
                st.success(f"🔍 Tìm thấy **{len(results)}** căn phù hợp!")
                edited_df = render_aggrid(results, df_log, kid_id)
                
                if st.button("🔄 Làm mới kho nhà từ Google Sheets", use_container_width=True):
                    pull_latest_houses_only()
                    st.rerun()
                
                st.divider()
                st.subheader("4. Khay chuẩn bị gửi")
                selected_uids = edited_df[edited_df['Trạng thái'] == '🔘 Đã chọn'][CONFIG_GSK_CM["UID"]].tolist()
                
                if selected_uids:
                    original_selected = results[results[CONFIG_GSK_CM["UID"]].isin(selected_uids)]
                    schedule_dict = {}
                    for _, row in original_selected.iterrows():
                        uid = row[CONFIG_GSK_CM["UID"]]
                        cols = st.columns([3, 2])
                        cols[0].write(f"🏠 {row[CONFIG_GSK_CM['SONHA']]} {row[CONFIG_GSK_CM['TENDUONG']]} - {row[CONFIG_GSK_CM['GIA']]}T")
                        schedule_dict[uid] = cols[1].date_input("Hẹn:", key=f"d_{uid}", label_visibility="collapsed")
                    
                    if st.button("📤 GỬI KHÁCH & LƯU BỘ LỌC", type="primary", use_container_width=True):
                        # Dịch Tên Full thành Mã Tắt để lưu BLK (Dùng dữ liệu df_h_clean đã chuẩn hóa)
                        d_qp_codes = {}
                        for q in sel_q:
                            q_code = MAP_QUAN.get(q, f"Q{q.replace('Quận ', '').replace(' ', '').upper()}")
                            mask_q = df_h_clean[CONFIG_GSK_CM["QUAN"]] == q
                            valid_p = df_h_clean[mask_q][CONFIG_GSK_CM["PHUONG"]].values
                            d_qp_codes[q_code] = [str(p) for p in sel_p if str(p) in valid_p]
                        
                        tags = []
                        if f_mat: tags.append("MAT")
                        if f_noh: tags.append("NOH")
                        if f_tma: tags.append("TMA")
                        if f_ntc: tags.append("NTC")
                        if f_klp: tags.append("KLP")
                        
                        name_kh = selected_kid_str.split(" - ")[1].split('.')[0]
                        new_blk = build_blk(name_kh, min_gia, max_gia, d_qp_codes, min_n, tags)
                        
                        df_kids.loc[df_kids['KID'].astype(str) == str(kid_id), 'bo_loc_KID'] = new_blk
                        df_kids.to_csv(FILE_KID, index=False)
                        
                        save_pending_logs(schedule_dict, kid_id, df_kids)
                else: 
                    st.info("💡 Bấm ❌ trên bảng để chọn nhà.")
            else: 
                st.warning("⚠️ Không tìm thấy căn nào.")
# --- TAB 2 & 3 ---
with tab2:
    st.header("👥 Quản lý MyKID")
    st.dataframe(df_kids, use_container_width=True)

with tab3:
    st.header("📝 Bảng điều khiển Zalo (Zalo Dashboard)")
    st.info("💡 Click đúp vào ô 'Phản hồi' để gõ chữ (bấm Enter để lưu). Bấm đúp vào cột Trạng thái để đổi màu.")
    # Đã điều chỉnh chỉ truyền df_log và df_houses (Snapshot lấy từ log ra)
    render_tab3_aggrid(df_log, df_houses)
```

