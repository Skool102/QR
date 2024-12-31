import qrcode
import base64
from cryptography.fernet import Fernet

# Tạo khóa bí mật AES để mã hóa
def generate_key():
    key = Fernet.generate_key()
    print(f"Khóa giải mã (giữ bí mật): {key.decode()}")
    return key

# Mã hóa dữ liệu cá nhân
def encrypt_data(data, key):
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data

# Giải mã dữ liệu để kiểm tra
def decrypt_data(encrypted_data, key):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data).decode()

# Tạo mã QR chứa thông tin bệnh lý và cá nhân
def generate_qr(public_data, encrypted_data, filename="qrcode.png"):
    combined_data = f"Bệnh lý: {public_data}\nThông tin mã hóa: {base64.urlsafe_b64encode(encrypted_data).decode()}"
    
    qr = qrcode.QRCode(
        version=1, 
        error_correction=qrcode.constants.ERROR_CORRECT_M, 
        box_size=10, 
        border=4,
    )
    qr.add_data(combined_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    print(f"Mã QR đã được lưu tại: {filename}")

# Chương trình chính
if __name__ == "__main__":
    public_info = "Nhóm máu: Lon\nDị ứng: Không\nTiền sử bệnh: Tiểu đường"
    personal_info = "Họ tên: Nguyễn Văn A\nSố CMND: 012345678\nĐịa chỉ: Quận 1, TP.HCM"

    # Tạo khóa và mã hóa thông tin cá nhân
    key = generate_key()
    encrypted_personal_info = encrypt_data(personal_info, key)

    # Tạo mã QR với thông tin bệnh lý và cá nhân mã hóa
    generate_qr(public_info, encrypted_personal_info, filename="medical_qr.png")

    # (Tùy chọn) Kiểm tra giải mã
    print("Thông tin giải mã:", decrypt_data(encrypted_personal_info, key))
