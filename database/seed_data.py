# import sqlite3
# conn = sqlite3.connect("database/banking.db")
# cursor = conn.cursor()

# # CUSTOMER

# customers = [
# ("C001","Nguyen Van A","1990-01-01","Ha Noi","LOW",20,"FULL"),
# ("C002","Tran Thi B","1995-05-11","HCM","MEDIUM",65,"FULL"),
# ("C003","Le Van C","1980-08-20","Da Nang","HIGH",95,"PARTIAL")
# ]

# cursor.executemany("""

# INSERT INTO CUSTOMER
# VALUES(?,?,?,?,?,?,?)

# """,customers)

# # CARD


# cards=[
# ("CARD001","C001","VISA","Gold",50000000,"ACTIVE"),
# ("CARD002","C002","Master","Classic",20000000,"ACTIVE"),
# ("CARD003","C003","VISA","Infinite",100000000,"ACTIVE")
# ]

# cursor.executemany("""

# INSERT INTO CARD
# VALUES(?,?,?,?,?,?)

# """,cards)

# # ACCOUNT

# accounts=[
# ("ACC001","C001",120000000,"ACTIVE"),
# ("ACC002","C002",30000000,"ACTIVE"),
# ("ACC003","C003",550000000,"ACTIVE")
# ]

# cursor.executemany("""

# INSERT INTO ACCOUNT
# VALUES(?,?,?,?)

# """,accounts)

# # MERCHANT

# merchant=[
# ("M001","Vinmart","VN","Retail","LOW"),
# ("M002","Shopee","VN","Ecommerce","LOW"),
# ("M003","Apple Store","SG","Electronic","LOW"),
# ("M004","Crypto Exchange","HK","Crypto","HIGH")

# ]

# cursor.executemany("""

# INSERT INTO MERCHANT
# VALUES(?,?,?,?,?)

# """,merchant)


# # TERMINAL


# terminal=[
# ("T001","M001","POS","Ha Noi"),
# ("T002","M002","ECOM","HCM"),
# ("T003","M003","ECOM","Singapore"),
# ("T004","M004","ECOM","Hong Kong")

# ]

# cursor.executemany("""

# INSERT INTO TERMINAL
# VALUES(?,?,?,?)

# """,terminal)


# # TRANSACTION


# txn=[

# ("TXN001","CARD001","C001","M001","T001",
# "2026-07-20 08:00",
# 150000,
# "VN",
# "DEV001",
# 0),

# ("TXN002","CARD003","C003","M004","T004",
# "2026-07-20 23:45",
# 35000000,
# "HK",
# "NEW_DEVICE",
# 1)

# ]

# cursor.executemany("""
# INSERT INTO TRANSACTION_HISTORY
# VALUES(?,?,?,?,?,?,?,?,?,?)
# """,txn)


# # # ==========================
# # # FRAUD CASE
# # # ==========================
# # cases = [
# #     ("FC001", "TXN002", 90, "OPEN", "2026-07-20 23:50"),
# #     ("FC002", "TXN001", 45, "IN_PROGRESS", "2026-07-21 08:15")
# # ]

# # cursor.executemany("""
# # INSERT INTO FRAUD_CASE (CASE_ID, TXN_ID, RISK_SCORE, STATUS, CREATED_TIME)
# # VALUES(?,?,?,?,?)
# # """, cases)

# conn.commit()

# conn.close()
# print("Seed data inserted.")

import sqlite3
import pandas as pd
from pathlib import Path

# =====================================
# Cấu hình đường dẫn (Paths)
# =====================================
# Lùi lại 1 thư mục để về thư mục gốc, sau đó trỏ tới folder data và database
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "banking.db"
DATA_DIR = BASE_DIR / "data"

def seed_data_from_csv():
    print("🚀 Bắt đầu nạp dữ liệu từ thư mục 'data' vào database...")

    # Mở kết nối tới database
    conn = sqlite3.connect(DB_PATH)

    # =====================================
    # Từ điển ánh xạ File CSV -> Tên bảng SQL
    # =====================================
    # Chú ý: Cột bên trái là tên file của bạn, cột bên phải là tên bảng trong DB
    csv_to_table_mapping = {
        "account.csv": "ACCOUNT",
        "card.csv": "CARD",
        "customer.csv": "CUSTOMER",
        "merchant.csv": "MERCHANT",
        "terminal.csv": "TERMINAL",
        "transaction.csv": "TRANSACTION" # Lưu ý: Nếu DB bạn đặt tên bảng này là TRANSACTION_HISTORY thì sửa lại ở đây nhé
    }

    # =====================================
    # Quét và nạp dữ liệu
    # =====================================
    for csv_file, table_name in csv_to_table_mapping.items():
        csv_path = DATA_DIR / csv_file
        
        if csv_path.exists():
            try:
                # Đọc dữ liệu từ file CSV
                df = pd.read_csv(csv_path)
                
                # Nạp vào Database
                # if_exists='append': Thêm dữ liệu vào bảng đã có sẵn cấu trúc (tạo bởi init_db.py)
                # index=False: Không đẩy cột index mặc định của pandas vào SQL
                df.to_sql(table_name, conn, if_exists='append', index=False)
                
                print(f"✅ Đã nạp thành công {len(df)} dòng từ '{csv_file}' vào bảng '{table_name}'.")
                
            except Exception as e:
                print(f"❌ Lỗi khi nạp file '{csv_file}': {e}")
        else:
            print(f"⚠️ Cảnh báo: Không tìm thấy file '{csv_path}'")

    # Đóng kết nối
    conn.close()
    print("🎉 Quá trình nạp dữ liệu hoàn tất!")

if __name__ == "__main__":
    seed_data_from_csv()