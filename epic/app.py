from flask import Flask, request, jsonify 
from flask_cors import CORS 
import json 
import os 
import random 
import smtplib 
import requests 
from email.message import EmailMessage 
 
app = Flask(__name__) 
CORS(app) 
 
DATA_FILE = 'users.json' 
verification_codes = {}  # Kullanıcı e-posta doğrulama kodlarını saklamak için 
 
if not os.path.exists(DATA_FILE): 
    with open(DATA_FILE, 'w') as f: 
        json.dump([], f) 
 
def send_email(to_email, code): 
    from_email = "sahilibrahimli123@gmail.com" 
    from_password = "rbke ytzn tdip vkfm" 
 
    subject = "Hesap Doğrulama Kodu" 
    body = f"Hesabınızı doğrulamak üçün kodunuz: {code}" 
 
    msg = EmailMessage() 
    msg['Subject'] = subject 
    msg['From'] = from_email 
    msg['To'] = to_email 
    msg.set_content(body) 
 
    try: 
        with smtplib.SMTP('smtp.gmail.com', 587) as server: 
            server.starttls() 
            server.login(from_email, from_password) 
            server.send_message(msg) 
            print("E-posta gönderildi.") 
    except Exception as e: 
        print(f"E-posta gönderme hatası: {e}") 
 
def get_external_ip(): 
    try: 
        response = requests.get('https://api.ipify.org?format=json') 
        return response.json().get('ip') 
    except Exception as e: 
        print(f"Harici IP alınamadı: {e}") 
        return None 
 
@app.route('/request_verification_code', methods=['POST']) 
def request_verification_code(): 
    email = request.json.get('email') 
    code = str(random.randint(100000, 999999)) 
    verification_codes[email] = code  # Kullanıcının doğrulama kodunu sakla 
    send_email(email, code) 
    return jsonify(success=True) 
 
@app.route('/register', methods=['POST']) 
def register(): 
    user_data = request.get_json() 
    email = user_data.get('email') 
    verification_code = user_data.get('verification_code')  # Kullanıcının girdiği kod 
    user_ip = get_external_ip() 
    user_data['external_ip'] = user_ip 
 
    # Kullanıcının doğrulama kodunu kontrol et 
    if verification_codes.get(email) != verification_code: 
        return jsonify(success=False, error="Geçersiz doğrulama kodu.") 
 
    # JSON dosyasını oku 
    try: 
        with open(DATA_FILE, 'r') as f: 
            users = json.load(f) 
    except json.JSONDecodeError: 
        users = [] 
 
    # Kullanıcı e-posta kontrolü 
    for user in users: 
        if user['email'] == email: 
            return jsonify(success=False, error="Bu e-posta ile kayıtlı bir kullanıcı var.") 
 
    # Yeni kullanıcıyı ekle 
    users.append(user_data) 
 
    # Güncellenmiş kullanıcı listesini yaz 
    with open(DATA_FILE, 'w') as f: 
        json.dump(users, f, indent=2) 
 
    # Kullanıcı kaydedildikten sonra doğrulama kodunu temizle 
    del verification_codes[email] 
 
    return jsonify(success=True) 
 
if __name__ == '__main__': 
    app.run(port=5000)