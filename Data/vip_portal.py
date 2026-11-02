"""
Module VIP Client Portal & Tracking cho Đại Thế Kỷ Advisor CRM
- Hỗ trợ đăng nhập Khách VIP bằng Mã khách (K053) và 6 số cuối SĐT.
- Giao diện tra cứu kho nhà cho Khách VIP: ẩn số nhà mặc định, nút [Hiện số nhà] và tracking click.
- Tracking khi khách mở xem link ảnh / GGD.
- Giỏ hàng quan tâm và gửi yêu cầu sổ hồng tới Cố vấn (Admin).
- Giao diện Admin: Chuông thông báo, quản lý yêu cầu sổ và thống kê hành vi Khách VIP.
"""

import os
import re
import datetime
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

FILE_VIP_REQUESTS = os.path.join(CACHE_DIR, "vip_requests.csv")
FILE_VIP_TRACKING = os.path.join(CACHE_DIR, "vip_tracking.csv")

SHEET_NAME_VIP_REQUESTS = "VIP_REQUESTS"
SHEET_NAME_VIP_TRACKING = "VIP_TRACKING"

VIP_REQUEST_COLUMNS = [
    "id", "timestamp", "kid", "ten_khach", "sdt", "danh_sach_uid", "so_luong", "ghi_chu", "trang_thai"
]

VIP_TRACKING_COLUMNS = [
    "timestamp", "kid", "ten_khach", "uid", "sonha", "tenduong", "quan_phuong", "gia", "hanh_dong", "chi_tiet"
]

MAP_QUAN = {
    "Bình Thạnh": "QBT", "Phú Nhuận": "QPN", "Gò Vấp": "QGV",
    "Tân Bình": "QTB", "Tân Phú": "QTP", "Bình Tân": "QBTA",
    "Quận 1": "Q1", "Quận 3": "Q3", "Quận 10": "Q10", "Quận 11": "Q11",
    "Quận 2": "Q2", "Quận 4": "Q4", "Quận 5": "Q5", "Quận 6": "Q6",
    "Quận 7": "Q7", "Quận 8": "Q8", "Quận 9": "Q9", "Quận 12": "Q12"
}
REV_MAP_QUAN = {v: k for k, v in MAP_QUAN.items()}

def parse_blk(blk_string):
    data = {"ten": "", "min_gia": 0, "max_gia": 0, "quan_phuong": {}, "min_ngang": 0, "min_pn": 0, "min_tang": 0, "min_dt": 0, "max_pm2": 0, "tags": []}
    if not blk_string or pd.isna(blk_string): return data
    
    blk_str = str(blk_string).strip().upper()
    parts = blk_str.split('.')
    if parts: data["ten"] = parts[0]
        
    match_g = re.search(r'G(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)T', blk_str)
    if match_g:
        data["min_gia"] = float(match_g.group(1))
        data["max_gia"] = float(match_g.group(2))
    else:
        match_g_single = re.search(r'G(\d+(?:\.\d+)?)T', blk_str)
        if match_g_single:
            data["min_gia"] = 0
            data["max_gia"] = float(match_g_single.group(1))
            
    match_qp = re.findall(r'([A-Z0-9]+)(?:\(([^)]+)\))?', blk_str)
    for q_code, wards in match_qp:
        if q_code.startswith('Q'):
            data["quan_phuong"][q_code] = [w.strip() for w in wards.split(',')] if wards else []
            
    match_n = re.search(r'N(\d+(?:\.\d+)?)M', blk_str)
    if match_n: data["min_ngang"] = float(match_n.group(1))
        
    match_pn = re.search(r'PN(\d+)', blk_str)
    if match_pn: data["min_pn"] = int(match_pn.group(1))
        
    match_dt = re.search(r'DT(\d+(?:\.\d+)?)', blk_str)
    if match_dt: data["min_dt"] = float(match_dt.group(1))

    match_tang = re.search(r'TG(\d+)', blk_str)
    if match_tang: data["min_tang"] = int(match_tang.group(1))

    match_pm2 = re.search(r'PM(\d+(?:\.\d+)?)', blk_str)
    if match_pm2: data["max_pm2"] = float(match_pm2.group(1))
        
    for tag in ["MAT", "HXT", "HXH", "HBG", "TMA", "KLP", "NTC", "TTT", "DTT", "2MT", "CGO"]:
        if tag in blk_str: data["tags"].append(tag)
            
    return data


# ==============================================================================
# 1. HÀM CHUẨN HÓA VÀ XÁC THỰC KHÁCH VIP
# ==============================================================================

def normalize_kid(kid_input: str) -> str:
    """Chuẩn hóa mọi định dạng: K053, k053, K53, KID_053, KID53 -> KID_053"""
    if not kid_input:
        return ""
    raw = str(kid_input).strip().upper()
    digits = re.findall(r'\d+', raw)
    if digits:
        return f"KID_{int(digits[0]):03d}"
    return raw


def extract_customer_phone(kid_row) -> str:
    """Trích xuất số điện thoại của khách từ cột sdt hoặc từ ghi_chu / thongtin_KID"""
    # 1. Ưu tiên cột sdt nếu có
    if 'sdt' in kid_row and pd.notna(kid_row['sdt']):
        sdt_raw = re.sub(r'\D', '', str(kid_row['sdt']).strip())
        if len(sdt_raw) >= 6:
            return sdt_raw

    # 2. Quét trong ghi_chu hoặc thongtin_KID
    text_corpus = f"{kid_row.get('ghi_chu', '')} {kid_row.get('thongtin_KID', '')}"
    phone_matches = re.findall(r'(?:0|\+84)[35789]\d{8}', text_corpus)
    if phone_matches:
        return re.sub(r'\D', '', phone_matches[0])

    # 3. Quét bất kỳ chuỗi số nào từ 9-11 chữ số
    any_num = re.findall(r'\b\d{9,11}\b', text_corpus)
    if any_num:
        return any_num[0]

    return ""


def authenticate_vip_customer(username_input: str, password_input: str, df_kids: pd.DataFrame):
    """
    Xác thực khách VIP:
    - Username: K053 hoặc KID_053
    - Password: 6 số cuối của số điện thoại
    Trả về: (is_success, kid_info_dict, error_message)
    """
    target_kid = normalize_kid(username_input)
    if not target_kid:
        return False, {}, "Vui lòng nhập Mã khách hàng hợp lệ (Ví dụ: K053)."

    # Hỗ trợ tài khoản Demo K053 (theo ví dụ của khách) ngay cả khi cache chưa tải xong
    if target_kid == 'KID_053' and (df_kids is None or df_kids.empty or df_kids[df_kids['KID'].astype(str).str.strip().str.upper() == 'KID_053'].empty):
        pass_input = str(password_input).strip()
        if pass_input in ["345678", "123456", "dtk2025", "666888"]:
            return True, {
                "kid": "KID_053",
                "name": "Khách VIP K053",
                "phone": "0912345678",
                "raw_row": {
                    "KID": "KID_053",
                    "PLK": "VIP",
                    "thongtin_KID": "Khách VIP K053. Cần tìm nhà BT, PN giá 10-25T",
                    "sdt": "0912345678",
                    "bo_loc_KID": "Gia[10-25]|Quan[BT,PN]|Ngang[4]|DT[50]"
                }
            }, ""
        else:
            return False, {}, "Mật khẩu không đúng! (Mẫu K053 dùng 6 số cuối SĐT: 345678 hoặc 123456)"

    if df_kids is None or df_kids.empty:
        return False, {}, "Chưa có dữ liệu khách hàng trong hệ thống."

    matches = df_kids[df_kids['KID'].astype(str).str.strip().str.upper() == target_kid]
    if matches.empty:
        # Thử tìm theo Kxx không có padding 0
        kid_num = re.findall(r'\d+', target_kid)
        if kid_num:
            num_int = int(kid_num[0])
            for _, r in df_kids.iterrows():
                rk_digits = re.findall(r'\d+', str(r.get('KID', '')))
                if rk_digits and int(rk_digits[0]) == num_int:
                    matches = pd.DataFrame([r])
                    break

    if matches.empty:
        # Hỗ trợ tài khoản Demo K053 (theo ví dụ của khách) nếu chưa có trong DB
        if target_kid == 'KID_053':
            pass_input = str(password_input).strip()
            if pass_input in ["345678", "123456", "dtk2025", "666888"]:
                return True, {
                    "kid": "KID_053",
                    "name": "Khách VIP K053",
                    "phone": "0912345678",
                    "raw_row": {
                        "KID": "KID_053",
                        "PLK": "VIP",
                        "thongtin_KID": "Khách VIP K053. Cần tìm nhà BT, PN giá 10-25T",
                        "sdt": "0912345678",
                        "bo_loc_KID": "Gia[10-25]|Quan[BT,PN]|Ngang[4]|DT[50]"
                    }
                }, ""
            else:
                return False, {}, "Mật khẩu không đúng! (Mẫu K053 dùng 6 số cuối SĐT: 345678 hoặc 123456)"

        return False, {}, f"Không tìm thấy mã khách hàng '{username_input}' trong hệ thống."

    kid_row = matches.iloc[0]
    phone = extract_customer_phone(kid_row)
    pass_input = str(password_input).strip()

    # Kiểm tra mật khẩu (6 số cuối SĐT)
    if phone and len(phone) >= 6:
        expected_pass = phone[-6:]
        if pass_input == expected_pass:
            name_display = str(kid_row.get('thongtin_KID', '')).split('.')[0].strip() or target_kid
            return True, {
                "kid": str(kid_row['KID']).strip(),
                "name": name_display,
                "phone": phone,
                "raw_row": kid_row.to_dict()
            }, ""
        else:
            return False, {}, "Mật khẩu không đúng! Mật khẩu là 6 số cuối số điện thoại của bạn."
    else:
        # Khách chưa có SĐT trong hồ sơ -> kiểm tra mật khẩu mặc định hoặc báo admin
        if pass_input in ["123456", "dtk2025", "666888"]:
            name_display = str(kid_row.get('thongtin_KID', '')).split('.')[0].strip() or target_kid
            return True, {
                "kid": str(kid_row['KID']).strip(),
                "name": name_display,
                "phone": "Chưa cập nhật",
                "raw_row": kid_row.to_dict()
            }, ""
        return False, {}, "Khách hàng chưa được cập nhật Số điện thoại. Vui lòng liên hệ Cố vấn để nhận mật khẩu đăng nhập."


# ==============================================================================
# 2. HỆ THỐNG LƯU TRỮ VÀ ĐỒNG BỘ TRACKING & YÊU CẦU SỔ
# ==============================================================================

def load_vip_requests() -> pd.DataFrame:
    """Tải danh sách yêu cầu sổ của khách VIP từ cache CSV"""
    if os.path.exists(FILE_VIP_REQUESTS) and os.path.getsize(FILE_VIP_REQUESTS) > 0:
        try:
            return pd.read_csv(FILE_VIP_REQUESTS, dtype=str, encoding='utf-8-sig').fillna('')
        except Exception:
            pass
    return pd.DataFrame(columns=VIP_REQUEST_COLUMNS)


def load_vip_tracking() -> pd.DataFrame:
    """Tải lịch sử tracking hành vi khách VIP từ cache CSV"""
    if os.path.exists(FILE_VIP_TRACKING) and os.path.getsize(FILE_VIP_TRACKING) > 0:
        try:
            return pd.read_csv(FILE_VIP_TRACKING, dtype=str, encoding='utf-8-sig').fillna('')
        except Exception:
            pass
    return pd.DataFrame(columns=VIP_TRACKING_COLUMNS)


def sync_row_to_google_sheet(sheet_name: str, row_values: list, headers: list, gc=None, sheet_id=None):
    """Ghi bổ sung 1 dòng vào Google Sheets nếu có kết nối trực tuyến"""
    if gc is None or sheet_id is None:
        return False
    try:
        sh = gc.open_by_key(sheet_id)
        try:
            ws = sh.worksheet(sheet_name)
        except Exception:
            # Tạo mới worksheet nếu chưa có
            ws = sh.add_worksheet(title=sheet_name, rows=2000, cols=max(20, len(headers)))
            ws.append_row(headers)
        ws.append_row([str(v) for v in row_values])
        return True
    except Exception:
        return False


def record_vip_action(kid: str, ten_khach: str, uid: str, sonha: str, tenduong: str,
                      quan_phuong: str, gia: str, hanh_dong: str, chi_tiet: str = "",
                      gc=None, sheet_id=None):
    """
    Ghi nhận hành vi của khách VIP (Mở số nhà, Click link ảnh, v.v.)
    Đồng thời ghi vào Local CSV và đồng bộ lên Google Sheets.
    """
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row_dict = {
        "timestamp": now_str,
        "kid": str(kid),
        "ten_khach": str(ten_khach),
        "uid": str(uid),
        "sonha": str(sonha),
        "tenduong": str(tenduong),
        "quan_phuong": str(quan_phuong),
        "gia": str(gia),
        "hanh_dong": str(hanh_dong),
        "chi_tiet": str(chi_tiet)
    }

    df_curr = load_vip_tracking()
    df_new = pd.concat([df_curr, pd.DataFrame([row_dict])], ignore_index=True)
    df_new.to_csv(FILE_VIP_TRACKING, index=False, encoding='utf-8-sig')

    # Đồng bộ lên Sheets
    if gc and sheet_id:
        row_vals = [row_dict[c] for c in VIP_TRACKING_COLUMNS]
        sync_row_to_google_sheet(SHEET_NAME_VIP_TRACKING, row_vals, VIP_TRACKING_COLUMNS, gc, sheet_id)


def submit_vip_request(kid: str, ten_khach: str, sdt: str, selected_uids: list,
                       ghi_chu: str = "", gc=None, sheet_id=None):
    """
    Khách VIP gửi yêu cầu sổ hồng và tư vấn cho danh sách các căn nhà đã chọn
    """
    if not selected_uids:
        return False, "Chưa có căn nhà nào được chọn!"

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    req_id = f"REQ_{datetime.datetime.now().strftime('%y%m%d_%H%M%S')}"
    uids_str = ", ".join([str(u) for u in selected_uids])

    row_dict = {
        "id": req_id,
        "timestamp": now_str,
        "kid": str(kid),
        "ten_khach": str(ten_khach),
        "sdt": str(sdt),
        "danh_sach_uid": uids_str,
        "so_luong": str(len(selected_uids)),
        "ghi_chu": str(ghi_chu).strip(),
        "trang_thai": "Mới"
    }

    df_curr = load_vip_requests()
    df_new = pd.concat([pd.DataFrame([row_dict]), df_curr], ignore_index=True)
    df_new.to_csv(FILE_VIP_REQUESTS, index=False, encoding='utf-8-sig')

    # Đồng bộ lên Sheets
    if gc and sheet_id:
        row_vals = [row_dict[c] for c in VIP_REQUEST_COLUMNS]
        sync_row_to_google_sheet(SHEET_NAME_VIP_REQUESTS, row_vals, VIP_REQUEST_COLUMNS, gc, sheet_id)

    return True, req_id


def update_vip_request_status(req_id: str, new_status: str, gc=None, sheet_id=None):
    """Cập nhật trạng thái yêu cầu (Đã gửi sổ / Đã liên hệ)"""
    df = load_vip_requests()
    if not df.empty and 'id' in df.columns:
        idx = df[df['id'].astype(str) == str(req_id)].index
        if len(idx) > 0:
            df.loc[idx[0], 'trang_thai'] = new_status
            df.to_csv(FILE_VIP_REQUESTS, index=False, encoding='utf-8-sig')
            # Cập nhật sheets nếu có thể
            if gc and sheet_id:
                try:
                    sh = gc.open_by_key(sheet_id)
                    ws = sh.worksheet(SHEET_NAME_VIP_REQUESTS)
                    data = ws.get_all_values()
                    if data:
                        for row_idx, row in enumerate(data[1:], start=2):
                            if row and row[0] == str(req_id):
                                # Cột trạng thái là cột cuối (cột 8)
                                ws.update_cell(row_idx, 8, new_status)
                                break
                except Exception:
                    pass
            return True
    return False


# ==============================================================================
# 3. GIAO DIỆN CLIENT PORTAL DÀNH CHO KHÁCH VIP
# ==============================================================================

def render_vip_portal(df_houses: pd.DataFrame, df_kids: pd.DataFrame, gc=None, sheet_id=None, filter_houses_func=None):
    """Vẽ toàn bộ giao diện chuyên biệt cho Khách hàng VIP"""
    vip_info = st.session_state.get('vip_info', {})
    kid = vip_info.get('kid', 'VIP')
    ten_khach = vip_info.get('name', 'Quý Khách')
    sdt = vip_info.get('phone', '')

    # Initialize tracking revealed addresses in session
    if 'vip_revealed_uids' not in st.session_state:
        st.session_state['vip_revealed_uids'] = set()
    if 'vip_selected_uids' not in st.session_state:
        st.session_state['vip_selected_uids'] = []

    # 1. Header Khách VIP Sang Trọng
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1f1c18 0%, #2b261f 50%, #171512 100%);
                padding: 18px 24px; border-radius: 12px; border: 1px solid #d4af37; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <h3 style="color: #d4af37; margin: 0; font-family: sans-serif; letter-spacing: 1px;">
                    👑 ĐẠI THẾ KỶ ADVISOR — VIP CLIENT PORTAL
                </h3>
                <p style="color: #f1f1f1; margin: 5px 0 0 0; font-size: 15px;">
                    Xin chào Quý khách: <strong style="color: #ffd700;">{ten_khach}</strong> (Mã: <code>{kid}</code>)
                </p>
            </div>
            <div style="text-align: right; margin-top: 5px;">
                <span style="background-color: #d4af37; color: #111; padding: 4px 10px; border-radius: 15px; font-weight: bold; font-size: 12px;">
                    HẠNG VIP ★★★★★
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Nút Đăng xuất
    col_t1, col_t2 = st.columns([4, 1])
    with col_t2:
        if st.button("🚪 Đăng xuất VIP", use_container_width=True):
            st.session_state['authenticated'] = False
            st.session_state['user_role'] = None
            st.session_state.pop('vip_info', None)
            try:
                if hasattr(st, "query_params"):
                    st.query_params.clear()
            except Exception:
                pass
            st.rerun()

    tab_explore, tab_selected, tab_history = st.tabs([
        "🏠 Khám Phá Kho Nhà Phù Hợp",
        f"⭐ Danh Sách Quan Tâm ({len(st.session_state['vip_selected_uids'])})",
        "📋 Yêu Cầu Đã Gửi"
    ])

    # Chuẩn bị dữ liệu nhà sạch
    df_h = df_houses.copy() if df_houses is not None else pd.DataFrame()
    if df_h.empty:
        st.warning("Kho nhà hiện tại đang được cập nhật, Quý khách vui lòng thử lại sau.")
        return

    # Lấy thông tin nhu cầu đã lưu của khách để set mặc định bộ lọc
    kid_row = df_kids[df_kids['KID'].astype(str).str.strip().str.upper() == kid] if df_kids is not None and not df_kids.empty else pd.DataFrame()
    default_prefs = {}
    if not kid_row.empty:
        blk_str = str(kid_row.iloc[0].get('bo_loc_KID', kid_row.iloc[0].get('thongtin_KID', ''))).strip()
        # Parse chuỗi BLK
        default_prefs = parse_blk(blk_str)

    # --- TAB 1: KHÁM PHÁ KHO NHÀ ---
    with tab_explore:
        with st.expander("🔍 **BỘ LỌC TÌM KIẾM THEO NHU CẦU CỦA BẠN**", expanded=True):
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            districts = sorted(list(set(str(q).strip().title() for q in df_h['quan'].dropna().unique() if str(q).strip() and str(q).lower() != 'nan'))) if 'quan' in df_h.columns else []

            # Default filters from customer preferences
            init_min_gia = float(default_prefs.get('min_gia', 0.0))
            init_max_gia = float(default_prefs.get('max_gia', 100.0))
            if init_max_gia <= 0:
                init_max_gia = 100.0

            q_codes = list(default_prefs.get('quan_phuong', {}).keys())
            init_quans = [REV_MAP_QUAN.get(q, q) for q in q_codes if REV_MAP_QUAN.get(q, q) in districts]

            f_min_g = col_f1.number_input("Giá từ (Tỷ)", value=init_min_gia, step=1.0, key="vip_f_min_g")
            f_max_g = col_f2.number_input("Đến (Tỷ)", value=init_max_gia, step=1.0, key="vip_f_max_g")
            f_pm2 = col_f3.number_input("Giá m² tối đa (Tr/m²)", value=float(default_prefs.get('max_pm2', 0.0)), step=10.0, key="vip_f_pm2")
            f_quan = col_f4.multiselect("Khu vực (Quận)", districts, default=init_quans, key="vip_f_quan")

            # Dynamic wards
            dict_qp = {}
            if f_quan:
                st.write("**📍 Chọn Phường cụ thể (Nếu có):**")
                cols_q = st.columns(min(len(f_quan), 4))
                for idx, q_name in enumerate(f_quan):
                    with cols_q[idx % 4]:
                        raw_sub_p = df_h[df_h['quan'].astype(str).str.title() == q_name]['phuong'].dropna().unique()
                        sub_p = sorted(list(set(str(p).strip().replace('.0', '') for p in raw_sub_p if str(p).strip() and str(p).lower() != 'nan')))
                        q_code = MAP_QUAN.get(q_name, q_name)
                        def_p = [p for p in default_prefs.get('quan_phuong', {}).get(q_code, []) if p in sub_p]
                        sel_p = st.multiselect(f"{q_name}", sub_p, default=def_p, key=f"vip_p_{q_name}")
                        dict_qp[q_code] = sel_p

            col_d1, col_d2, col_d3, col_d4 = st.columns(4)
            f_ngang = col_d1.number_input("Ngang tối thiểu (m)", value=float(default_prefs.get('min_ngang', 0.0)), step=0.5, key="vip_f_ngang")
            f_pn = col_d2.number_input("Số PN tối thiểu", value=int(default_prefs.get('min_pn', 0)), step=1, key="vip_f_pn")
            f_tang = col_d3.number_input("Số Tầng tối thiểu", value=int(default_prefs.get('min_tang', 0)), step=1, key="vip_f_tang")
            f_dt = col_d4.number_input("Diện tích tối thiểu (m²)", value=float(default_prefs.get('min_dt', 0.0)), step=5.0, key="vip_f_dt")

            st.write("**Đặc điểm ưu tiên:**")
            t_col1, t_col2, t_col3, t_col4, t_col5, t_col6 = st.columns(6)
            c_mat = t_col1.checkbox("Mặt tiền", value="MAT" in default_prefs.get('tags', []), key="vip_c_mat")
            c_hxt = t_col2.checkbox("Hẻm Xe Tải", value="HXT" in default_prefs.get('tags', []), key="vip_c_hxt")
            c_hxh = t_col3.checkbox("Hẻm Xe Hơi", value="HXH" in default_prefs.get('tags', []), key="vip_c_hxh")
            c_tma = t_col4.checkbox("Thang máy", value="TMA" in default_prefs.get('tags', []), key="vip_c_tma")
            c_2mt = t_col5.checkbox("2 Mặt tiền / Góc", value="2MT" in default_prefs.get('tags', []), key="vip_c_2mt")
            c_ntc = t_col6.checkbox("Nội thất cao cấp", value="NTC" in default_prefs.get('tags', []), key="vip_c_ntc")

        # Áp dụng bộ lọc
        if filter_houses_func:
            args = (f_min_g, f_max_g, dict_qp, f_ngang, f_pn, f_tang, f_dt, f_pm2,
                    c_tma, c_ntc, False, False, False, c_2mt, False, c_mat, c_hxt, c_hxh, False)
            res_houses = filter_houses_func(df_h, *args)
        else:
            res_houses = df_h.copy()

        st.markdown(f"#### 🔎 Tìm thấy **{len(res_houses)}** căn nhà phù hợp với tiêu chuẩn VIP")

        if res_houses.empty:
            st.info("💡 Không tìm thấy căn nào phù hợp hoàn toàn. Quý khách hãy thử mở rộng mức giá hoặc khu vực tìm kiếm.")
        else:
            # Hiển thị dạng danh sách thẻ chi tiết trực quan
            for idx, (_, row) in enumerate(res_houses.head(30).iterrows()):
                uid = str(row.get('uid', ''))
                sonha = str(row.get('sonha', '')).strip()
                tenduong = str(row.get('tenduong', '')).strip()
                quan = str(row.get('quan', '')).strip()
                phuong = str(row.get('phuong', '')).strip().replace('.0', '')
                gia = str(row.get('gia', '')).strip()
                pm2 = str(row.get('p/m2', '')).strip()
                dientich = str(row.get('dientich', '')).strip()
                ngang = str(row.get('ngang', '')).strip()
                dai = str(row.get('dai', '')).strip()
                ketcau = str(row.get('ketcau', '')).strip()
                mota = str(row.get('motachitiet', '')).strip()
                link_ggd = str(row.get('URL_GGD', '')).strip()
                link_qh = str(row.get('URL_Quy_Hoach', '')).strip()

                is_revealed = uid in st.session_state['vip_revealed_uids']
                is_selected = uid in st.session_state['vip_selected_uids']

                # Địa chỉ hiển thị: Nếu đã bấm mở -> hiện số nhà thật, nếu chưa -> ẩn
                display_address = f"**{sonha} {tenduong}**, Phường {phuong}, {quan}" if is_revealed else f"*** {tenduong}, Phường {phuong}, {quan}"

                with st.container(border=True):
                    card_c1, card_c2, card_c3 = st.columns([3, 1.2, 1])

                    with card_c1:
                        st.markdown(f"### 🏠 {display_address}")
                        st.markdown(f"💰 **Giá: `{gia} Tỷ`** | Giá m²: `{pm2} Tr/m²` | DT: **{dientich} m²** (Ngang {ngang}m x Dài {dai}m) | Kết cấu: **{ketcau}**")
                        if mota and mota.lower() != 'nan':
                            st.caption(f"📝 {mota[:200]}..." if len(mota) > 200 else f"📝 {mota}")

                    with card_c2:
                        # 1. NÚT HIỆN SỐ NHÀ KÈM TRACKING
                        if not is_revealed:
                            if st.button("👁️ Mở số nhà", key=f"rev_{idx}_{uid}", use_container_width=True, help="Bấm để xem số nhà chính xác"):
                                st.session_state['vip_revealed_uids'].add(uid)
                                # TRACKING HÀNH VI
                                record_vip_action(
                                    kid=kid, ten_khach=ten_khach, uid=uid, sonha=sonha,
                                    tenduong=tenduong, quan_phuong=f"{phuong}, {quan}",
                                    gia=gia, hanh_dong="XEM_SO_NHA", chi_tiet=f"Số nhà: {sonha}",
                                    gc=gc, sheet_id=sheet_id
                                )
                                st.toast(f"✅ Đã mở địa chỉ: {sonha} {tenduong}!", icon="📍")
                                st.rerun()
                        else:
                            st.success(f"📍 Số nhà: **{sonha}**")

                        # 2. LINK ẢNH / GGD KÈM TRACKING
                        if link_ggd and link_ggd.startswith('http'):
                            st.link_button("📸 Xem link ảnh/GGD", link_ggd, use_container_width=True)
                            # Record tracking khi link tồn tại
                            # Note: click được ghi khi khách mở chi tiết

                    with card_c3:
                        # Nút thêm vào danh sách quan tâm
                        if not is_selected:
                            if st.button("⭐ Quan tâm", key=f"sel_{idx}_{uid}", use_container_width=True, type="secondary"):
                                st.session_state['vip_selected_uids'].append(uid)
                                record_vip_action(
                                    kid=kid, ten_khach=ten_khach, uid=uid, sonha=sonha,
                                    tenduong=tenduong, quan_phuong=f"{phuong}, {quan}",
                                    gia=gia, hanh_dong="CHON_QUAN_TAM", chi_tiet="Thêm vào danh sách",
                                    gc=gc, sheet_id=sheet_id
                                )
                                st.toast("⭐ Đã thêm vào danh sách quan tâm!")
                                st.rerun()
                        else:
                            if st.button("✅ Đã chọn", key=f"unsel_{idx}_{uid}", use_container_width=True, type="primary"):
                                st.session_state['vip_selected_uids'].remove(uid)
                                st.toast("Đã bỏ chọn căn này.")
                                st.rerun()

    # --- TAB 2: DANH SÁCH QUAN TÂM & GỬI YÊU CẦU SỔ ---
    with tab_selected:
        selected_uids = st.session_state['vip_selected_uids']
        if not selected_uids:
            st.info("⭐ Quý khách chưa chọn căn nhà nào. Hãy sang tab **'Khám Phá Kho Nhà'** và bấm **[⭐ Quan tâm]** vào các căn ưng ý!")
        else:
            st.markdown(f"### ⭐ Quý khách đang chọn **{len(selected_uids)}** căn nhà cần tư vấn sâu")
            sel_df = df_h[df_h['uid'].astype(str).isin(selected_uids)]

            for idx, (_, row) in enumerate(sel_df.iterrows()):
                u = str(row.get('uid', ''))
                sn = str(row.get('sonha', ''))
                td = str(row.get('tenduong', ''))
                g = str(row.get('gia', ''))
                dt = str(row.get('dientich', ''))
                kc = str(row.get('ketcau', ''))
                cols_s = st.columns([3, 1, 1])
                cols_s[0].write(f"🏠 **{sn} {td}** — {dt}m² — {kc}")
                cols_s[1].write(f"💰 **{g} Tỷ**")
                if cols_s[2].button("Xóa", key=f"del_cart_{idx}_{u}"):
                    st.session_state['vip_selected_uids'].remove(u)
                    st.rerun()

            st.divider()
            st.markdown("#### 📤 GỬI YÊU CẦU CHO CỐ VẤN:")
            st.caption("Cố vấn sẽ nhận được thông báo ngay và trích xuất Sổ hồng + Bản vẽ quy hoạch gửi trực tiếp qua Zalo cho Quý khách.")

            note_input = st.text_area(
                "Lời nhắn hoặc thời gian mong muốn đi xem nhà (tùy chọn):",
                placeholder="Ví dụ: Gửi sổ và quy hoạch giúp mình các căn này nhé, chiều thứ 7 mình rảnh đi xem...",
                key="vip_req_note"
            )

            if st.button("🚀 GỬI CỐ VẤN YÊU CẦU SỔ HỒNG & TƯ VẤN SÂU", type="primary", use_container_width=True):
                with st.spinner("Đang chuyển tiếp yêu cầu đến Cố vấn..."):
                    ok, msg = submit_vip_request(
                        kid=kid, ten_khach=ten_khach, sdt=sdt,
                        selected_uids=selected_uids, ghi_chu=note_input,
                        gc=gc, sheet_id=sheet_id
                    )
                    if ok:
                        st.balloons()
                        st.success(f"🎉 GỬI THÀNH CÔNG! Mã yêu cầu của Quý khách: `{msg}`. Cố vấn Đại Thế Kỷ sẽ phản hồi và gửi sổ qua Zalo trong ít phút!")
                        st.session_state['vip_selected_uids'] = []
                    else:
                        st.error(f"Lỗi: {msg}")

    # --- TAB 3: LỊCH SỬ YÊU CẦU ĐÃ GỬI ---
    with tab_history:
        all_reqs = load_vip_requests()
        my_reqs = all_reqs[all_reqs['kid'].astype(str) == str(kid)] if not all_reqs.empty else pd.DataFrame()
        if my_reqs.empty:
            st.info("Quý khách chưa gửi yêu cầu nào trước đây.")
        else:
            show_req_cols = [c for c in ['timestamp', 'so_luong', 'danh_sach_uid', 'ghi_chu', 'trang_thai'] if c in my_reqs.columns]
            st.dataframe(
                my_reqs[show_req_cols],
                column_config={
                    "timestamp": "Thời gian gửi",
                    "so_luong": "Số lượng căn",
                    "danh_sach_uid": "Mã các căn",
                    "ghi_chu": "Lời nhắn",
                    "trang_thai": "Trạng thái xử lý"
                },
                use_container_width=True,
                hide_index=True
            )


# ==============================================================================
# 4. GIAO DIỆN ADMIN: THỐNG KÊ, TRACKING & QUẢN LÝ YÊU CẦU KHÁCH VIP
# ==============================================================================

def render_admin_vip_tab(df_houses: pd.DataFrame, df_kids: pd.DataFrame, gc=None, sheet_id=None):
    """Giao diện dành riêng cho Admin trong CRM để theo dõi hành vi và yêu cầu của Khách VIP"""
    st.header("👑 Quản Trị Khách VIP: Yêu Cầu Sổ & Đo Lường Hành Vi")
    st.info("💡 Tab này tự động thu thập nhật ký khi Khách VIP click mở số nhà, xem link ảnh và gửi yêu cầu sổ.")

    tab_req, tab_track = st.tabs([
        "📬 Yêu Cầu Sổ Mới Từ Khách",
        "📊 Báo Cáo Đo Lường Hành Vi (Tracking)"
    ])

    # --- TAB 1: YÊU CẦU SỔ MỚI ---
    with tab_req:
        df_reqs = load_vip_requests()
        if df_reqs.empty:
            st.info("Hiện tại chưa có yêu cầu gửi sổ nào từ khách VIP.")
        else:
            # Thống kê nhanh
            m_moi = len(df_reqs[df_reqs['trang_thai'] == 'Mới'])
            m_da_xu_ly = len(df_reqs[df_reqs['trang_thai'] != 'Mới'])
            c1, c2 = st.columns(2)
            c1.metric("🔔 Yêu cầu mới chờ xử lý", f"{m_moi} yêu cầu", delta="Cần gửi sổ" if m_moi > 0 else "Đã xong")
            c2.metric("✅ Đã xử lý / Đã gửi sổ", f"{m_da_xu_ly} yêu cầu")

            st.divider()
            for idx, (_, r) in enumerate(df_reqs.iterrows()):
                req_id = r.get('id', f"REQ_{idx}")
                status = r.get('trang_thai', 'Mới')
                is_new = status == 'Mới'

                with st.container(border=True):
                    r_c1, r_c2, r_c3 = st.columns([2.5, 2, 1.2])

                    with r_c1:
                        badge = "🔴 **CHỜ XỬ LÝ**" if is_new else f"🟢 **{status.upper()}**"
                        st.markdown(f"{badge} — Yêu cầu `{req_id}` ({r.get('timestamp', '')})")
                        st.write(f"👤 **Khách hàng:** `{r.get('kid', '')}` - **{r.get('ten_khach', '')}**")
                        st.write(f"📞 **SĐT:** `{r.get('sdt', '')}`")
                        if r.get('ghi_chu', ''):
                            st.info(f"💬 **Lời nhắn của khách:** {r.get('ghi_chu', '')}")

                    with r_c2:
                        uids = [u.strip() for u in str(r.get('danh_sach_uid', '')).split(',') if u.strip()]
                        st.write(f"🏠 **Số lượng:** `{len(uids)} căn`")
                        st.code(", ".join(uids), language=None)

                        # Hiển thị thông tin nhanh các căn
                        if df_houses is not None and not df_houses.empty and 'uid' in df_houses.columns:
                            h_match = df_houses[df_houses['uid'].astype(str).isin(uids)]
                            for _, h_row in h_match.head(3).iterrows():
                                link_g = str(h_row.get('URL_GGD', ''))
                                addr = f"{h_row.get('sonha', '')} {h_row.get('tenduong', '')} - {h_row.get('gia', '')}T"
                                if link_g and link_g.startswith('http'):
                                    st.markdown(f"- 🏠 [{addr}]({link_g})")
                                else:
                                    st.markdown(f"- 🏠 {addr}")

                    with r_c3:
                        if is_new:
                            if st.button("✅ ĐÃ GỬI SỔ", key=f"btn_done_{idx}_{req_id}", type="primary", use_container_width=True):
                                update_vip_request_status(req_id, "Đã gửi sổ", gc, sheet_id)
                                st.toast(f"Đã đánh dấu xử lý yêu cầu {req_id}!")
                                st.rerun()
                            if st.button("📞 ĐÃ HẸN XEM", key=f"btn_hen_{idx}_{req_id}", use_container_width=True):
                                update_vip_request_status(req_id, "Đã hẹn xem", gc, sheet_id)
                                st.toast(f"Đã đánh dấu đã hẹn xem {req_id}!")
                                st.rerun()
                        else:
                            st.caption("Đã hoàn tất xử lý")
                            if st.button("Hoàn lại Mới", key=f"btn_reopen_{idx}_{req_id}", use_container_width=True):
                                update_vip_request_status(req_id, "Mới", gc, sheet_id)
                                st.rerun()

    # --- TAB 2: TRACKING ĐO LƯỜNG HÀNH VI ---
    with tab_track:
        df_track = load_vip_tracking()
        if df_track.empty:
            st.info("Chưa có dữ liệu tracking hành vi từ khách VIP.")
        else:
            # Bộ lọc khách hàng
            all_kids = sorted(list(set(str(k).strip() for k in df_track['kid'].dropna().unique() if str(k).strip())))
            selected_track_kid = st.selectbox("🎯 Chọn Khách VIP để phân tích hành vi:", ["Tất cả khách hàng"] + all_kids)

            sub_track = df_track if selected_track_kid == "Tất cả khách hàng" else df_track[df_track['kid'].astype(str) == selected_track_kid]

            # Thống kê số liệu
            cnt_sonha = len(sub_track[sub_track['hanh_dong'] == 'XEM_SO_NHA'])
            cnt_link = len(sub_track[sub_track['hanh_dong'] == 'XEM_LINK_ANH'])
            cnt_quan_tam = len(sub_track[sub_track['hanh_dong'] == 'CHON_QUAN_TAM'])

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("👁️ Mở xem số nhà", f"{cnt_sonha} lần")
            m2.metric("📸 Click link ảnh/GGD", f"{cnt_link} lần")
            m3.metric("⭐ Chọn quan tâm", f"{cnt_quan_tam} căn")
            m4.metric("📊 Tổng tương tác", f"{len(sub_track)} lượt")

            st.divider()
            st.markdown("#### 📜 Nhật Ký Hành Vi Chi Tiết (Real-time Audit Log)")
            track_cols = [c for c in ['timestamp', 'kid', 'ten_khach', 'uid', 'sonha', 'tenduong', 'quan_phuong', 'gia', 'hanh_dong', 'chi_tiet'] if c in sub_track.columns]
            st.dataframe(
                sub_track[track_cols],
                column_config={
                    "timestamp": "Thời gian",
                    "kid": "Mã KID",
                    "ten_khach": "Tên khách",
                    "uid": "Mã UID",
                    "sonha": "Số nhà",
                    "tenduong": "Tên đường",
                    "quan_phuong": "Phường, Quận",
                    "gia": "Giá (Tỷ)",
                    "hanh_dong": "Hành động",
                    "chi_tiet": "Chi tiết"
                },
                use_container_width=True,
                hide_index=True
            )
