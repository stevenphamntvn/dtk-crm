import os
import shutil
import tempfile
import unittest
import pandas as pd
from pathlib import Path

from Data.vip_portal import (
    normalize_kid,
    extract_customer_phone,
    authenticate_vip_customer,
    record_vip_action,
    load_vip_tracking,
    submit_vip_request,
    load_vip_requests,
    update_vip_request_status,
    extract_highlight,
    explain_tags,
    build_vip_display_df,
)


class TestVipPortal(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.orig_cache = None

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_normalize_kid(self):
        self.assertEqual(normalize_kid("K053"), "KID_053")
        self.assertEqual(normalize_kid("k53"), "KID_053")
        self.assertEqual(normalize_kid("KID_053"), "KID_053")
        self.assertEqual(normalize_kid("KID53"), "KID_053")
        self.assertEqual(normalize_kid("53"), "KID_053")
        self.assertEqual(normalize_kid(""), "")

    def test_extract_customer_phone(self):
        row_with_sdt = {'KID': 'KID_001', 'sdt': '0901234567', 'thongtin_KID': 'Anh Tuan'}
        self.assertEqual(extract_customer_phone(row_with_sdt), "0901234567")

        row_with_note = {'KID': 'KID_002', 'sdt': '', 'ghi_chu': 'Khach VIP goi 0988776655 gap chu'}
        self.assertEqual(extract_customer_phone(row_with_note), "0988776655")

    def test_authenticate_vip_customer(self):
        df_kids = pd.DataFrame([
            {
                'KID': 'KID_053',
                'PLK': 'A',
                'thongtin_KID': 'Anh Minh.G10-15T',
                'sdt': '0912345678',
                'ghi_chu': 'Khach VIP'
            },
            {
                'KID': 'KID_010',
                'PLK': 'B',
                'thongtin_KID': 'Chi Lan',
                'sdt': '',
                'ghi_chu': 'Lien he 0909888999 gap chi'
            }
        ])

        # Test K053 đúng pass (6 số cuối: 345678)
        ok, info, err = authenticate_vip_customer("K053", "345678", df_kids)
        self.assertTrue(ok)
        self.assertEqual(info['kid'], 'KID_053')
        self.assertEqual(info['name'], 'Anh Minh')
        self.assertEqual(info['phone'], '0912345678')

        # Test K053 sai pass
        ok, info, err = authenticate_vip_customer("K053", "111111", df_kids)
        self.assertFalse(ok)
        self.assertIn("Mật khẩu không đúng", err)

        # Test K010 trích xuất pass từ ghi chú (6 số cuối: 888999)
        ok, info, err = authenticate_vip_customer("K010", "888999", df_kids)
        self.assertTrue(ok)
        self.assertEqual(info['kid'], 'KID_010')

        # Test mã khách không tồn tại
        ok, info, err = authenticate_vip_customer("K999", "123456", df_kids)
        self.assertFalse(ok)
        self.assertIn("Không tìm thấy", err)

    def test_submit_and_update_vip_request(self):
        # Test submit
        ok, req_id = submit_vip_request(
            kid="KID_053",
            ten_khach="Anh Minh",
            sdt="0912345678",
            selected_uids=["3835", "4197"],
            ghi_chu="Xin gui so som nhe",
            gc=None,
            sheet_id=None
        )
        self.assertTrue(ok)
        self.assertTrue(req_id.startswith("REQ_"))

        # Test load
        df_reqs = load_vip_requests()
        self.assertFalse(df_reqs.empty)
        match = df_reqs[df_reqs['id'] == req_id]
        self.assertEqual(len(match), 1)
        self.assertEqual(match.iloc[0]['trang_thai'], 'Mới')
        self.assertEqual(match.iloc[0]['so_luong'], '2')

        # Test update status
        up_ok = update_vip_request_status(req_id, "Đã gửi sổ", gc=None, sheet_id=None)
        self.assertTrue(up_ok)
        df_reqs_updated = load_vip_requests()
        match_updated = df_reqs_updated[df_reqs_updated['id'] == req_id]
        self.assertEqual(match_updated.iloc[0]['trang_thai'], 'Đã gửi sổ')

    def test_record_vip_action(self):
        record_vip_action(
            kid="KID_053",
            ten_khach="Anh Minh",
            uid="3835",
            sonha="280.4",
            tenduong="Bạch Đằng",
            quan_phuong="P.14, Bình Thạnh",
            gia="9.9",
            hanh_dong="XEM_SO_NHA",
            chi_tiet="Số nhà: 280.4",
            gc=None,
            sheet_id=None
        )

        df_track = load_vip_tracking()
        self.assertFalse(df_track.empty)
        match = df_track[(df_track['kid'] == 'KID_053') & (df_track['uid'] == '3835')]
        self.assertGreaterEqual(len(match), 1)
        self.assertEqual(match.iloc[-1]['hanh_dong'], 'XEM_SO_NHA')

    def test_demo_k053_fallback_authentication(self):
        # Khi df_kids trống hoặc không có K053, Demo K053 vẫn hoạt động với pass 345678 / 123456
        df_kids_empty = pd.DataFrame(columns=['KID', 'thongtin_KID', 'sdt'])
        ok, info, err = authenticate_vip_customer("K053", "345678", df_kids_empty)
        self.assertTrue(ok)
        self.assertEqual(info['kid'], 'KID_053')
        self.assertEqual(info['phone'], '0912345678')

        # Test pass sai cho K053
        ok, info, err = authenticate_vip_customer("K053", "000000", df_kids_empty)
        self.assertFalse(ok)
        self.assertIn("Mật khẩu không đúng", err)

    def test_extract_and_explain_tags(self):
        desc = "CVI DAD 2MT TMA CHV6 PN4 N(Gặp trực tiếp chủ nhà)"
        tags = extract_highlight(desc)
        self.assertIn("CVI", tags)
        self.assertIn("DAD", tags)
        self.assertIn("2MT", tags)
        self.assertIn("TMA", tags)
        self.assertIn("CHV6", tags)
        self.assertIn("PN4", tags)

        explained = explain_tags(tags)
        self.assertIn("Mặt tiền công viên", explained)
        self.assertIn("đâm đường", explained)
        self.assertIn("thang máy", explained)
        self.assertIn("Căn hộ dịch vụ 6P", explained)
        self.assertIn("4 Phòng ngủ", explained)

    def test_build_vip_display_df(self):
        df_dummy = pd.DataFrame([{
            'uid': '1001',
            'sonha': '123/45',
            'tenduong': 'Lê Quang Định',
            'quan': 'Bình Thạnh',
            'phuong': '14',
            'ngang': '4.2',
            'dai': '15',
            'dientich': '63',
            'gia': '8.5',
            'p/m2': '135',
            'ketcau': '4T',
            'PL': 'TAR',
            'motachitiet': 'CVI TMA N(Bán gấp) SCN63',
            'dinhgia': '9.0',
            'URL_GGD': 'https://drive.google.com/drive/folders/test1234',
            'cus': 'NỘI BỘ BROKER',
        }])

        df_disp = build_vip_display_df(df_dummy, selected_uids=['1001'], revealed_uids=set())

        expected_cols = [
            '⭐', 'PL', 'Số nhà', 'Ảnh', 'Đường', 'P.', 'Q.',
            'Ngang', 'Dài', 'DT', 'Giá', 'Đ.Giá', 'Tr/m²', 'K.Cấu',
            'Đ.Điểm', 'G.Chú',
            '_uid', '_real_sonha', '_link_ggd', '_reveal_trigger', '_link_trigger', '_dacdiem_tooltip'
        ]
        self.assertEqual(list(df_disp.columns), expected_cols)

        # Bảo mật: không chứa motachitiet hoặc cus
        self.assertNotIn('motachitiet', df_disp.columns)
        self.assertNotIn('cus', df_disp.columns)

        # Kiểm tra dữ liệu
        row = df_disp.iloc[0]
        self.assertEqual(row['⭐'], '✅ Đã chọn')
        self.assertEqual(row['Số nhà'], '👁️ ***')
        self.assertEqual(row['PL'], 'TAR')
        self.assertEqual(row['Ảnh'], '📂')
        self.assertEqual(row['Đường'], 'Lê Quang Định')
        self.assertIn('CVI', row['Đ.Điểm'])
        self.assertEqual(row['G.Chú'], 'Bán gấp')
        self.assertIn('công viên', row['_dacdiem_tooltip'])


if __name__ == '__main__':
    unittest.main()
