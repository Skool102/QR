from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import qrcode
import io
import base64
import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter

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

@app.route("/download_pdf/<string:phone_number>")
def download_pdf(phone_number):
    record = medical_records.get(phone_number)
    if not record:
        flash("Không tìm thấy hồ sơ bệnh án!", "error")
        return redirect(url_for('index'))

    pdf_path = f"static/pdfs/{record['name']}_qr.pdf"
    if not os.path.exists(pdf_path):
        flash("Không tìm thấy file PDF!", "error")
        return redirect(url_for('index'))

    return send_file(pdf_path, as_attachment=True)

# Trang chính cho bác sĩ và bệnh nhân
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
                if phone_number not in users:
                    users[phone_number] = {"password": "123456", "role": "patient"}

                # Lưu hồ sơ bệnh án
                medical_records[phone_number] = {
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
        patient_record = medical_records.get(patient_name, None)
        return render_template("patient.html", patient_record=patient_record)

    return redirect(url_for('logout'))


# Tạo mã QR và PDF cho hồ sơ bệnh án
@app.route("/generate_qr/<string:phone_number>")
def generate_qr(phone_number):
    if 'username' not in session or session.get('role') != "doctor":
        flash("Bạn không có quyền truy cập chức năng này.", "error")
        return redirect(url_for('login'))

    record = medical_records.get(phone_number)
    if record:
        pdf_path = f"static/pdfs/{record['name']}_qr.pdf"
        generate_pdf_internal(record, pdf_path)

        if not os.path.exists(pdf_path):
            flash("Không tìm thấy file PDF!", "error")
            return redirect(url_for('index'))

        # Tạo link download PDF từ route download_pdf
        pdf_url = url_for('download_pdf', phone_number=phone_number, _external=True)
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(pdf_url)
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        medical_records[phone_number]['qr_code'] = qr_base64
        flash("Mã QR đã được tạo thành công!", "success")
        return redirect(url_for('index'))
    else:
        flash("Không tìm thấy hồ sơ bệnh án!", "error")
        return redirect(url_for('index'))



# Tạo file PDF cho hồ sơ bệnh án
def generate_pdf_internal(record, pdf_path):
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    
    pdf = canvas.Canvas(pdf_path, pagesize=letter)
    pdfmetrics.registerFont(TTFont('DejaVu', 'C:/Users/lapto/Downloads/dejavu-sans/DejaVuSans.ttf'))  
    pdfmetrics.registerFont(TTFont('DejaVu-Bold', 'C:/Users/lapto/Downloads/dejavu-sans/DejaVuSans-Bold.ttf')) 


    pdf.setTitle(f"Hồ sơ bệnh án - {record['name']}")
    pdf.setFont("DejaVu-Bold", 30)  # Đặt font in đậm và kích thước 24 cho tiêu đề
    pdf.drawString(250, 750, f"BỆNH ÁN")

    pdf.setFont("DejaVu", 14)
    pdf.drawString(100, 700, f"Họ và tên: {record['name']}")
    pdf.drawString(100, 680, f"Nhóm máu: {record['blood_type']}")
    pdf.drawString(100, 660, f"Kết quả khám bệnh: {record['diagnosis']}")
    pdf.drawString(100, 640, f"Quá trình chẩn đoán: {record['treatment']}")

    pdf.save()
    

# Đăng xuất
@app.route("/logout")
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
