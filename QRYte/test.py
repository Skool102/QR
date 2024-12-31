import qrcode
import base64
from cryptography.fernet import Fernet

# Hàm tạo khóa bí mật AES
def generate_key():
    key = Fernet.generate_key()
    print(f"Khóa giải mã (giữ bí mật): {key.decode()}")
    return key

# Hàm mã hóa thông tin
def encrypt_data(data, key):
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data

# Hàm giải mã thông tin (để kiểm tra)
def decrypt_data(encrypted_data, key):
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data).decode()
    return decrypted_data

# Hàm tạo mã QR chứa 2 thông tin
def generate_qr(public_data, encrypted_data, filename="qrcode.png"):
    # Ghép 2 dữ liệu thành 1 chuỗi
    combined_data = f"Public: {public_data}\nEncrypted: {base64.urlsafe_b64encode(encrypted_data).decode()}"

    # Tạo mã QR
    qr = qrcode.QRCode(
        version=1, 
        error_correction=qrcode.constants.ERROR_CORRECT_M, 
        box_size=10, 
        border=4,
    )
    qr.add_data(combined_data)
    qr.make(fit=True)

    # Lưu hình ảnh QR code
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    print(f"Mã QR đã được lưu tại: {filename}")

# Ví dụ sử dụng
if __name__ == "__main__":
    public_data = "Thông tin công khai: https://www.example.com"
    secret_data = "Thông tin bí mật: Mật khẩu là 123456"
    
    # Tạo khóa và mã hóa dữ liệu
    key = generate_key()
    encrypted_data = encrypt_data(secret_data, key)

    # Tạo mã QR với 2 thông tin
    generate_qr(public_data, encrypted_data, filename="secure_qr.png")

    # (Tùy chọn) Kiểm tra giải mã
    print("Thông tin sau khi giải mã:", decrypt_data(encrypted_data, key))
