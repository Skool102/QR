from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import qrcode
import io
import base64

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Thông tin tài khoản (username: password)
users = {
    "doctor": {"password": "12345", "role": "doctor"},
    "patient": {"password": "67890", "role": "patient"}
}

# Lưu thông tin hồ sơ bệnh án
medical_records = {}

# Trang đăng nhập
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users and users[username]["password"] == password:
            session['username'] = username
            session['role'] = users[username]["role"]
            return redirect(url_for('index'))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không đúng!", "error")
    return render_template("login.html")

# Trang chính
@app.route("/", methods=["GET", "POST"])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    role = session.get('role')
    if role == "doctor":
        if request.method == "POST":
            patient_name = request.form.get("patient_name")
            phone_number = request.form.get("phone_number")
            cccd = request.form.get("cccd")
            blood_type = request.form.get("blood_type")
            diagnosis = request.form.get("diagnosis")
            treatment = request.form.get("treatment")

            if patient_name:
                # Tạo tài khoản cho bệnh nhân nếu chưa tồn tại
                if phone_number not in users:  # Kiểm tra nếu tài khoản chưa tồn tại
                    users[phone_number] = {"password": "123456", "role": "patient"}  # Tạo tài khoản với số điện thoại và mật khẩu mặc định

                # Lưu hồ sơ bệnh án vào medical_records
                medical_records[phone_number] = {  # Lưu theo số điện thoại làm key
                    "name": patient_name,
                    "phone_number": phone_number,
                    "cccd": cccd,
                    "blood_type": blood_type,
                    "diagnosis": diagnosis,
                    "treatment": treatment
                }

                flash("Hồ sơ bệnh án đã được lưu và tài khoản bệnh nhân đã được tạo!", "success")
        return render_template("doctor.html", medical_records=medical_records)
    
    elif role == "patient":
        patient_name = session.get('username')
        patient_record = medical_records.get(patient_name, None)  # Lấy hồ sơ bệnh án theo username (số điện thoại)
        return render_template("patient.html", patient_record=patient_record)
    
    return redirect(url_for('logout'))



# Tạo mã QR cho hồ sơ bệnh án
@app.route("/generate_qr/<string:phone_number>")
def generate_qr(phone_number):
    if 'username' not in session or session.get('role') != "doctor":
        flash("Bạn không có quyền truy cập chức năng này.", "error")
        return redirect(url_for('login'))

    record = medical_records.get(phone_number)
    if record:
        qr_data = (
        f"Họ và tên: {record['name']}\n"
        f"Nhóm máu: {record['blood_type']}\n"
        f"Kết quả khám bệnh: {record['diagnosis']}\n"
        f"Quá trình chẩn đoán: {record['treatment']}"
    )

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # Lưu mã QR vào hồ sơ bệnh nhân
        medical_records[phone_number]['qr_code'] = qr_base64
        
        flash("Mã QR đã được tạo thành công!", "success")
        return redirect(url_for('index'))
    else:
        flash("Không tìm thấy hồ sơ bệnh án!", "error")
        return redirect(url_for('index'))



# Đăng xuất
@app.route("/logout")
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
