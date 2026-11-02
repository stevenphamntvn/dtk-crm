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


if __name__ == '__main__':
    unittest.main()
