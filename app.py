from flask import Flask, render_template, request, Response, jsonify
import pikepdf
import io
import time
import re
import base64
import json

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

@app.route('/stream-recover', methods=['POST'])
def stream_recover():
    pdf_file = request.files['pdf']
    mode = request.form.get('mode', 'name_digits')
    hint = request.form.get('hint', '').strip().upper()
    hint = re.sub(r'[^A-Z0-9]', '', hint)
    pdf_bytes = pdf_file.read()

    def generate():
        start_time = time.time()
        found_password = None
        unlocked_bytes = None

        try:
            search_prefixes = []
            if mode == 'name_digits':
                if len(hint) >= 4:
                    for i in range(len(hint) - 3):
                        chunk = hint[i:i+4]
                        if chunk not in search_prefixes:
                            search_prefixes.append(chunk)
                for name in COMMON_NAMES:
                    if name not in search_prefixes:
                        search_prefixes.append(name)

                for prefix in search_prefixes:
                    for n in range(10000):
                        test_pass = f"{prefix}{n:04d}"
                        
                        # Send live scanning log to frontend
                        yield f"data: {json.dumps({'status': 'testing', 'pass': test_pass})}\n\n"

                        try:
                            with pikepdf.open(io.BytesIO(pdf_bytes), password=test_pass) as pdf:
                                out_stream = io.BytesIO()
                                pdf.save(out_stream)
                                found_password = test_pass
                                unlocked_bytes = out_stream.getvalue()
                                break
                        except:
                            continue
                    if found_password:
                        break
            else: # 8-Digit mode
                for n in range(100000000):
                    test_pass = f"{n:08d}"
                    if n % 50 == 0: # Stream every 50th attempt for smooth speed
                        yield f"data: {json.dumps({'status': 'testing', 'pass': test_pass})}\n\n"
                    try:
                        with pikepdf.open(io.BytesIO(pdf_bytes), password=test_pass) as pdf:
                            out_stream = io.BytesIO()
                            pdf.save(out_stream)
                            found_password = test_pass
                            unlocked_bytes = out_stream.getvalue()
                            break
                    except:
                        continue
                    if found_password:
                        break

            elapsed = round(time.time() - start_time, 2)
            if found_password:
                encoded_pdf = base64.b64encode(unlocked_bytes).decode('utf-8')
                yield f"data: {json.dumps({'status': 'success', 'password': found_password, 'elapsed': elapsed, 'pdf_data': encoded_pdf})}\n\n"
            else:
                yield f"data: {json.dumps({'status': 'failed', 'message': 'Password not found'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
