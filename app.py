from flask import Flask, render_template, request, jsonify
from pypdf import PdfReader, PdfWriter
import io
import time
import re
import base64

app = Flask(__name__)

COMMON_NAMES = [
    "AMIT", "ANIL", "ARUN", "AJAY", "ABHI", "AKAS", "AMAN", "ANSH", "ANUP", "ASHU", 
    "DEEP", "DEVA", "DINE", "GAUR", "GURU", "HARI", "HEMA", "INDU", "JAYA", "JAYE", 
    "JYOT", "KAMA", "KAPI", "KIRA", "KUNA", "LALU", "MADH", "MANO", "MEEN", "MOHA", 
    "MUKA", "NEER", "NITI", "PANK", "PAWA", "PIYU", "POOJ", "PRAD", "PRAK", "PRAM", 
    "RAHU", "RAJA", "RAJE", "RAKE", "RAMA", "RANI", "RAVI", "RISH", "ROHA", "ROHI", 
    "SACH", "SAME", "SANJ", "SANT", "SARA", "SATI", "SHIV", "SHYA", "SONU", "SUMI", 
    "SUNI", "SURA", "TARA", "UMES", "VIKA", "VIMA", "VINO", "VIVE", "YOGE", "KUMA", 
    "SING", "MISH", "SHAR", "VERM", "GUPT", "YADA", "PATE", "CHAU", "KHAN",
    "RAWA", "NEGI", "BISH", "SAIN", "DHIL", "SIDD", "KAUR", "BALA", "ALOK", "ASIF",
    "BABU", "BALI", "BINK", "CHET", "DAKS", "ESHA", "FAIZ", "GOPL", "HARS", "ISHA",
    "JNAT", "KAVS", "LOKS", "MAHE", "NARE", "OMPR", "PRAT", "QASH", "RASH", "SUDH"
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recover', methods=['POST'])
def recover():
    if 'pdf' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'}), 400

    pdf_file = request.files['pdf']
    mode = request.form.get('mode', 'name_digits')
    hint = request.form.get('hint', '').strip().upper()
    hint = re.sub(r'[^A-Z0-9]', '', hint)

    pdf_bytes = pdf_file.read()
    found_password = None
    unlocked_bytes = None
    start_time = time.time()

    try:
        if mode == 'name_digits':
            search_prefixes = []
            if len(hint) >= 4:
                for i in range(len(hint) - 3):
                    search_prefixes.append(hint[i:i+4])
            
            search_prefixes.extend(COMMON_NAMES)
            search_prefixes = list(dict.fromkeys(search_prefixes))

            for prefix in search_prefixes:
                for n in range(10000):
                    test_pass = f"{prefix}{n:04d}"
                    try:
                        reader = PdfReader(io.BytesIO(pdf_bytes))
                        if reader.is_encrypted:
                            if reader.decrypt(test_pass):
                                writer = PdfWriter()
                                for page in reader.pages:
                                    writer.add_page(page)
                                out_stream = io.BytesIO()
                                writer.write(out_stream)
                                found_password = test_pass
                                unlocked_bytes = out_stream.getvalue()
                                break
                    except:
                        continue
                if found_password:
                    break
        else:  # 8-Digit Numeric Mode
            for n in range(100000000):
                test_pass = f"{n:08d}"
                try:
                    reader = PdfReader(io.BytesIO(pdf_bytes))
                    if reader.is_encrypted:
                        if reader.decrypt(test_pass):
                            writer = PdfWriter()
                            for page in reader.pages:
                                writer.add_page(page)
                            out_stream = io.BytesIO()
                            writer.write(out_stream)
                            found_password = test_pass
                            unlocked_bytes = out_stream.getvalue()
                            break
                except:
                    continue
                if found_password:
                    break
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

    elapsed = round(time.time() - start_time, 2)

    if found_password:
        encoded_pdf = base64.b64encode(unlocked_bytes).decode('utf-8')
        return jsonify({
            'success': True, 
            'password': found_password, 
            'elapsed': elapsed,
            'pdf_data': encoded_pdf
        })
    else:
        return jsonify({'success': False, 'message': 'Password not found in dictionary matrix.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
