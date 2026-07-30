import csv
import random
from datetime import datetime, timedelta

# Số lượng bản ghi cần tạo
NUM_RECORDS = 10000

# 1. Dữ liệu tĩnh (để sinh dữ liệu ngẫu nhiên thực tế hơn)
ho_list = ['Nguyen', 'Tran', 'Le', 'Pham', 'Hoang', 'Huynh', 'Phan', 'Vu', 'Vo', 'Dang', 'Bui', 'Do', 'Ho', 'Ngo', 'Duong']
dem_list = ['Van', 'Thi', 'Minh', 'Ngoc', 'Thanh', 'Gia', 'Hai', 'Duc', 'Thu', 'Khanh', 'Xuan', 'Quoc', 'Huu', 'Hoang', 'Tuan']
ten_list = ['An', 'Binh', 'Hoang', 'Anh', 'Bao', 'Tung', 'Huy', 'Khang', 'Nam', 'Lan', 'Phuc', 'Trang', 'Linh', 'Long', 'Son', 'Khoa', 'Vy', 'Nhung', 'Dat', 'Kiet']

cities = ['Ha Noi', 'Ho Chi Minh', 'Da Nang', 'Can Tho', 'Hai Phong', 'Nha Trang', 'Hue', 'Quang Ninh', 'Vung Tau', 'Dong Nai']
card_brands = ['VISA', 'MasterCard', 'JCB', 'Amex']
card_types = ['Classic', 'Gold', 'Platinum', 'Infinite']
credit_limits = [10000000, 20000000, 30000000, 50000000, 100000000, 200000000, 500000000]

# Danh sách Terminal & Merchant hợp lệ (dựa trên dữ liệu gốc của bạn để map chuẩn xác)
terminals = [
    {'TERMINAL_ID': 'T001', 'MERCHANT_ID': 'M001', 'CITY': 'Ha Noi'},
    {'TERMINAL_ID': 'T002', 'MERCHANT_ID': 'M002', 'CITY': 'HCM'},
    {'TERMINAL_ID': 'T003', 'MERCHANT_ID': 'M003', 'CITY': 'Singapore'},
    {'TERMINAL_ID': 'T004', 'MERCHANT_ID': 'M004', 'CITY': 'Hong Kong'},
    {'TERMINAL_ID': 'T005', 'MERCHANT_ID': 'M005', 'CITY': 'Lagos'},
    {'TERMINAL_ID': 'T006', 'MERCHANT_ID': 'M006', 'CITY': 'Ho Chi Minh'},
    {'TERMINAL_ID': 'T007', 'MERCHANT_ID': 'M007', 'CITY': 'Ha Noi'},
    {'TERMINAL_ID': 'T008', 'MERCHANT_ID': 'M008', 'CITY': 'Da Nang'},
    {'TERMINAL_ID': 'T009', 'MERCHANT_ID': 'M009', 'CITY': 'Can Tho'},
    {'TERMINAL_ID': 'T010', 'MERCHANT_ID': 'M010', 'CITY': 'Ho Chi Minh'},
    {'TERMINAL_ID': 'T011', 'MERCHANT_ID': 'M011', 'CITY': 'Ha Noi'},
    {'TERMINAL_ID': 'T012', 'MERCHANT_ID': 'M012', 'CITY': 'Da Nang'},
    {'TERMINAL_ID': 'T013', 'MERCHANT_ID': 'M013', 'CITY': 'Ho Chi Minh'},
    {'TERMINAL_ID': 'T014', 'MERCHANT_ID': 'M014', 'CITY': 'Ha Noi'}
]

def random_date(start_year, end_year):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

def generate_customers():
    print("Đang tạo customer.csv...")
    with open('customer.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['CUSTOMER_ID', 'FULL_NAME', 'DOB', 'CITY', 'RISK_RATING', 'AML_SCORE', 'KYC_LEVEL'])
        for i in range(1, NUM_RECORDS + 1):
            cust_id = f"C{i:05d}"
            name = f"{random.choice(ho_list)} {random.choice(dem_list)} {random.choice(ten_list)}"
            dob = random_date(1960, 2005).strftime("%Y-%m-%d")
            city = random.choice(cities)
            risk = random.choices(['LOW', 'MEDIUM', 'HIGH'], weights=[70, 20, 10])[0]
            aml_score = random.randint(5, 95)
            kyc = random.choices(['FULL', 'PARTIAL'], weights=[85, 15])[0]
            writer.writerow([cust_id, name, dob, city, risk, aml_score, kyc])

def generate_accounts():
    print("Đang tạo account.csv...")
    with open('account.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ACCOUNT_ID', 'CUSTOMER_ID', 'BALANCE', 'ACCOUNT_STATUS'])
        for i in range(1, NUM_RECORDS + 1):
            acc_id = f"ACC{i:05d}"
            cust_id = f"C{i:05d}"
            balance = random.randint(10, 5000) * 100000  # Từ 1 triệu đến 500 triệu
            status = random.choices(['ACTIVE', 'BLOCKED', 'CLOSED'], weights=[90, 5, 5])[0]
            writer.writerow([acc_id, cust_id, balance, status])

def generate_cards():
    print("Đang tạo card.csv...")
    with open('card.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['CARD_ID', 'CUSTOMER_ID', 'CARD_BRAND', 'CARD_TYPE', 'CREDIT_LIMIT', 'CARD_STATUS'])
        for i in range(1, NUM_RECORDS + 1):
            card_id = f"CARD{i:05d}"
            cust_id = f"C{i:05d}"
            brand = random.choice(card_brands)
            c_type = random.choice(card_types)
            limit = random.choice(credit_limits)
            status = random.choices(['ACTIVE', 'BLOCKED'], weights=[95, 5])[0]
            writer.writerow([card_id, cust_id, brand, c_type, limit, status])

def generate_transactions():
    print("Đang tạo transaction.csv...")
    with open('transaction.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['TXN_ID', 'CARD_ID', 'CUSTOMER_ID', 'MERCHANT_ID', 'TERMINAL_ID', 'TXN_TIME', 'AMOUNT', 'COUNTRY', 'DEVICE_ID', 'FRAUD_LABEL'])
        
        start_time = datetime(2026, 7, 1) # Sinh giao dịch trong tháng 7 năm 2026
        
        for i in range(1, NUM_RECORDS + 1):
            txn_id = f"TXN{i:05d}"
            # Chọn ngẫu nhiên 1 khách hàng và thẻ tương ứng (giả định thẻ map 1:1 với khách hàng để dễ truy xuất)
            rand_idx = random.randint(1, NUM_RECORDS)
            card_id = f"CARD{rand_idx:05d}"
            cust_id = f"C{rand_idx:05d}"
            
            # Gắn với một Merchant & Terminal có sẵn
            term = random.choice(terminals)
            terminal_id = term['TERMINAL_ID']
            merchant_id = term['MERCHANT_ID']
            
            # Thời gian và số tiền
            txn_time = (start_time + timedelta(minutes=random.randint(1, 40000))).strftime("%Y-%m-%d %H:%M:%S")
            amount = random.randint(5, 5000) * 10000  # 50,000 VND đến 50,000,000 VND
            
            # Mô phỏng nhãn gian lận: ~3% giao dịch là gian lận
            is_fraud = random.choices([0, 1], weights=[97, 3])[0]
            
            # Thiết bị và quốc gia
            if is_fraud:
                device = "NEW_DEVICE"
                country = random.choices(['VN', 'SG', 'HK', 'US', 'NG'], weights=[30, 20, 20, 10, 20])[0]
            else:
                device = f"DEV{random.randint(1, 2000):04d}"
                country = 'VN' if term['CITY'] in cities else random.choice(['SG', 'HK', 'US'])

            writer.writerow([txn_id, card_id, cust_id, merchant_id, terminal_id, txn_time, amount, country, device, is_fraud])

if __name__ == "__main__":
    generate_customers()
    generate_accounts()
    generate_cards()
    generate_transactions()
    print("Hoàn tất! Đã tạo thành công 10,000 dòng cho mỗi file.")