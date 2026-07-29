import sqlite3
conn = sqlite3.connect("database/banking.db")
cursor = conn.cursor()

# CUSTOMER

customers = [
("C001","Nguyen Van A","1990-01-01","Ha Noi","LOW",20,"FULL"),
("C002","Tran Thi B","1995-05-11","HCM","MEDIUM",65,"FULL"),
("C003","Le Van C","1980-08-20","Da Nang","HIGH",95,"PARTIAL")
]

cursor.executemany("""

INSERT INTO CUSTOMER
VALUES(?,?,?,?,?,?,?)

""",customers)

# CARD


cards=[
("CARD001","C001","VISA","Gold",50000000,"ACTIVE"),
("CARD002","C002","Master","Classic",20000000,"ACTIVE"),
("CARD003","C003","VISA","Infinite",100000000,"ACTIVE")
]

cursor.executemany("""

INSERT INTO CARD
VALUES(?,?,?,?,?,?)

""",cards)

# ACCOUNT

accounts=[
("ACC001","C001",120000000,"ACTIVE"),
("ACC002","C002",30000000,"ACTIVE"),
("ACC003","C003",550000000,"ACTIVE")
]

cursor.executemany("""

INSERT INTO ACCOUNT
VALUES(?,?,?,?)

""",accounts)

# MERCHANT

merchant=[
("M001","Vinmart","VN","Retail","LOW"),
("M002","Shopee","VN","Ecommerce","LOW"),
("M003","Apple Store","SG","Electronic","LOW"),
("M004","Crypto Exchange","HK","Crypto","HIGH")

]

cursor.executemany("""

INSERT INTO MERCHANT
VALUES(?,?,?,?,?)

""",merchant)


# TERMINAL


terminal=[
("T001","M001","POS","Ha Noi"),
("T002","M002","ECOM","HCM"),
("T003","M003","ECOM","Singapore"),
("T004","M004","ECOM","Hong Kong")

]

cursor.executemany("""

INSERT INTO TERMINAL
VALUES(?,?,?,?)

""",terminal)


# TRANSACTION


txn=[

("TXN001","CARD001","C001","M001","T001",
"2026-07-20 08:00",
150000,
"VN",
"DEV001",
0),

("TXN002","CARD003","C003","M004","T004",
"2026-07-20 23:45",
35000000,
"HK",
"NEW_DEVICE",
1)

]

cursor.executemany("""
INSERT INTO TRANSACTION_HISTORY
VALUES(?,?,?,?,?,?,?,?,?,?)
""",txn)
conn.commit()

conn.close()
print("Seed data inserted.")