from flask import Flask, request, render_template_string, send_from_directory
import os
import socket
import qrcode
import webbrowser
from io import BytesIO
import base64
import PyPDF2

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variable to store the latest uploaded file
latest_file = None

# Get local IP address
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

# Generate QR code as base64 string
def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str

# Estimate ink usage and cost from PDF
def estimate_ink_cost(file_path):
    try:
        with open(file_path, 'rb') as f:
            pdf = PyPDF2.PdfReader(f)
            total_chars = 0
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    total_chars += len(text.replace(" ", "").replace("\n", ""))  # Count non-space characters

            # Assume a full A4 page has ~3000 characters (approx. for 12pt font, single-spaced)
            full_page_chars = 3000
            toner_per_page = 1  # 1g toner per full A4 black page
            cost_per_gram = 2  # 2 rupees per gram of toner

            # Calculate toner usage and cost
            pages_equivalent = total_chars / full_page_chars
            toner_used = pages_equivalent * toner_per_page
            cost = toner_used * cost_per_gram
            return round(cost, 2), total_chars
    except Exception as e:
        print(f"Error estimating ink cost: {e}")
        return 2.0, 0  # Default to 2 rupees if estimation fails

# HTML for client (phone) upload page
CLIENT_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>File Upload</title>
    <style>
        body { font-family: Arial, sans-serif; background: url('https://images.pexels.com/photos/2253573/pexels-photo-2253573.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2') no-repeat center center fixed; background-size: cover; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { background: rgba(255, 255, 255, 0.9); padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); text-align: center; max-width: 400px; width: 100%; }
        h1 { color: #333; margin-bottom: 20px; }
        input[type="file"] { margin: 10px 0; }
        input[type="submit"] { background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; transition: background-color 0.3s; }
        input[type="submit"]:hover { background-color: #45a049; }
        p { color: #666; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Upload a File</h1>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Upload">
        </form>
        {% if message %}
            <p>{{ message }}</p>
        {% endif %}
    </div>
</body>
</html>
'''

# HTML for host (PC) page
HOST_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>File Transfer Host</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body { font-family: Arial, sans-serif; background: url('https://images.pexels.com/photos/2253573/pexels-photo-2253573.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2') no-repeat center center fixed; background-size: cover; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { background: rgba(255, 255, 255, 0.9); padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); text-align: center; max-width: 500px; width: 100%; }
        h1 { color: #333; margin-bottom: 20px; }
        h2 { color: #555; margin-top: 20px; }
        p { color: #666; margin: 10px 0; }
        button { background-color: #008CBA; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; transition: background-color 0.3s; margin-top: 15px; }
        button:hover { background-color: #007B9A; }
        .logo { max-width: 100px; margin-bottom: 20px; }
        .qr-code { margin: 20px 0; max-width: 200px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>File Transfer Host</h1>
        <img src="{{ url_for('static', filename='Logoo.jpg') }}" alt="Logo" class="logo">
        <p>Scan the QR code with your phone to connect:</p>
        <img src="data:image/png;base64,{{ qr_code }}" alt="QR Code" class="qr-code">
        <h2>Latest Uploaded File:</h2>
        <p>{{ latest_file if latest_file else "No files uploaded yet" }}</p>
        {% if latest_file %}
            <button onclick="window.open('/payment/{{ latest_file }}', '_blank')">Print File</button>
        {% endif %}
    </div>
</body>
</html>
'''

# HTML for payment page with UPI QR code
PAYMENT_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Payment Required</title>
    <style>
        body { font-family: Arial, sans-serif; background: url('https://images.pexels.com/photos/2253573/pexels-photo-2253573.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2') no-repeat center center fixed; background-size: cover; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { background: rgba(255, 255, 255, 0.9); padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); text-align: center; max-width: 600px; width: 100%; }
        h1 { color: #333; margin-bottom: 20px; }
        p { color: #666; margin: 10px 0; }
        button { background-color: #008CBA; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; transition: background-color 0.3s; margin-top: 15px; }
        button:hover { background-color: #007B9A; }
        img { max-width: 200px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Payment Required</h1>
        <p>File: {{ filename }}</p>
        <p>Estimated Cost: ₹{{ cost }} (based on {{ chars }} characters)</p>
        <p>Scan the QR code to pay via UPI:</p>
        <img src="data:image/png;base64,{{ payment_qr }}" alt="UPI QR Code">
        <button onclick="window.open('/print/{{ filename }}', '_blank')">Proceed to Print</button>
        <p>(Click after completing payment)</p>
    </div>
</body>
</html>
'''

# HTML for print page with paper type and finish selection
PRINT_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Print Document</title>
    <style>
        body { font-family: Arial, sans-serif; background: url('https://images.pexels.com/photos/2253573/pexels-photo-2253573.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2') no-repeat center center fixed; background-size: cover; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { background: rgba(255, 255, 255, 0.9); padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); text-align: center; max-width: 600px; width: 100%; }
        h1 { color: #333; margin-bottom: 20px; }
        select { padding: 10px; margin: 10px 5px; border-radius: 5px; width: 180px; }
        button { background-color: #008CBA; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; transition: background-color 0.3s; margin-top: 15px; }
        button:hover { background-color: #007B9A; }
        iframe { width: 100%; height: 50vh; margin-top: 20px; border: none; }
    </style>
    <script>
        function updateFinishOptions() {
            var paperSize = document.getElementById('paperSize').value;
            var finishSelect = document.getElementById('finishType');
            if (paperSize === 'A3') {
                finishSelect.value = 'Matte';
                finishSelect.options[1].disabled = true;
            } else {
                finishSelect.options[1].disabled = false;
            }
        }
        function printDocument() {
            var iframe = document.getElementById('fileIframe');
            iframe.contentWindow.print();
            setTimeout(function() { fetch('/delete/{{ filename }}'); }, 1000); // Delete file after 1s
        }
    </script>
</head>
<body onload="updateFinishOptions()">
    <div class="container">
        <h1>Print Document</h1>
        <p>Select Paper Size and Finish:</p>
        <select id="paperSize" onchange="updateFinishOptions()">
            <option value="A4">A4 (210 x 297 mm)</option>
            <option value="A3">A3 (297 x 420 mm)</option>
        </select>
        <select id="finishType">
            <option value="Matte">Matte</option>
            <option value="Glossy">Glossy</option>
        </select>
        <br>
        <button onclick="printDocument()">Print</button>
        <iframe id="fileIframe" src="/file/{{ filename }}"></iframe>
    </div>
</body>
</html>
'''

# Client upload route
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global latest_file
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template_string(CLIENT_HTML, message='No file part')
        file = request.files['file']
        if file.filename == '':
            return render_template_string(CLIENT_HTML, message='No file selected')
        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            latest_file = file.filename
            return render_template_string(CLIENT_HTML, message=f'File {file.filename} uploaded successfully!')
    return render_template_string(CLIENT_HTML)

# Host status route
@app.route('/host')
def host_page():
    ip = get_local_ip()
    url = f'http://{ip}:5000/'
    qr_code = generate_qr_code(url)
    return render_template_string(HOST_HTML, qr_code=qr_code, latest_file=latest_file)

# Payment route
@app.route('/payment/<filename>')
def payment_page(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    cost, chars = estimate_ink_cost(file_path)
    upi_id = "your-upi-id@upi"  # Replace with your UPI ID
    upi_url = f"upi://pay?pa={upi_id}&pn=PrintPayment&am={cost}&cu=INR"
    payment_qr = generate_qr_code(upi_url)
    return render_template_string(PAYMENT_HTML, filename=filename, cost=cost, chars=chars, payment_qr=payment_qr)

# Serve the file for printing
@app.route('/file/<filename>')
def serve_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Print route
@app.route('/print/<filename>')
def print_file(filename):
    return render_template_string(PRINT_HTML, filename=filename)

# Delete file route
@app.route('/delete/<filename>')
def delete_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        global latest_file
        if latest_file == filename:
            latest_file = None
    return '', 204  # No content response

if __name__ == '__main__':
    app.static_folder = 'static'  # Set static folder for logo
    ip = get_local_ip()
    host_url = f'http://{ip}:5000/host'
    webbrowser.open(host_url)
    app.run(host='0.0.0.0', port=5000, debug=False)