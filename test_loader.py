from modules.loader import DatabaseLoader

db = DatabaseLoader()

print("===== CUSTOMER =====")
print(db.load_customer())

print("\n===== CARD =====")
print(db.load_card())

print("\n===== ACCOUNT =====")
print(db.load_account())

print("\n===== TRANSACTION =====")
print(db.load_transaction())

print("\n===== MERCHANT =====")

merchant = db.load_merchant()

print(merchant)
print()
print(merchant.columns.tolist())

db.close()