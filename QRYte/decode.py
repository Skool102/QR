import base64
from cryptography.fernet import Fernet

def decrypt_data(encrypted_data_b64, key):
    encrypted_data = base64.urlsafe_b64decode(encrypted_data_b64)
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data).decode()

# Nhập chuỗi mã hóa và khóa bí mật
encrypted_b64 = input("Nhập dữ liệu mã hóa (Base64): ")
key = input("Nhập khóa giải mã: ").encode()

# Giải mã và hiển thị thông tin
try:
    decrypted_data = decrypt_data(encrypted_b64, key)
    print("Thông tin cá nhân:", decrypted_data)
except Exception as e:
    print(f"Lỗi giải mã: {e}")
