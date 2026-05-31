from flask import Flask, request, Response, session, redirect
import requests
import webbrowser
import threading
import os
import hashlib

app = Flask(__name__)
app.secret_key = 'diyaliz-kkds-secret-2024'

SIFRE_HASH = hashlib.sha256('Taha1985.'.encode()).hexdigest()

HTML_DOSYA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'diyaliz-kkds.html')

LOGIN_HTML = '''<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Diyaliz KKDS — Giriş</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: "Segoe UI", sans-serif; background: #0f172a; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
  .kart { background: #1e293b; border-radius: 20px; padding: 40px; width: 100%; max-width: 380px; box-shadow: 0 24px 80px rgba(0,0,0,0.5); }
  .baslik { text-align: center; margin-bottom: 32px; }
  .baslik .ikon { font-size: 48px; display: block; margin-bottom: 10px; }
  .baslik h1 { color: #f8fafc; font-size: 24px; font-weight: 900; }
  .baslik p { color: #475569; font-size: 12px; margin-top: 6px; }
  label { display: block; font-size: 11px; font-weight: 700; color: #475569; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 6px; }
  input { width: 100%; padding: 12px 16px; background: #0f172a; border: 1.5px solid #334155; border-radius: 10px; font-size: 15px; color: #f1f5f9; outline: none; font-family: inherit; margin-bottom: 20px; transition: border-color 0.2s; }
  input:focus { border-color: #3b82f6; }
  button { width: 100%; padding: 13px; background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; border: none; border-radius: 12px; font-size: 15px; font-weight: 800; cursor: pointer; font-family: inherit; }
  button:hover { opacity: 0.9; }
  .hata { background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 10px 14px; color: #991b1b; font-size: 13px; margin-bottom: 16px; display: none; }
  .hata.goster { display: block; }
</style>
</head>
<body>
<div class="kart">
  <div class="baslik">
    <span class="ikon">🫀</span>
    <h1>Diyaliz KKDS</h1>
    <p>Yetkili personel girişi</p>
  </div>
  <form method="POST" action="/giris">
    __HATA__
    <label>Şifre</label>
    <input type="password" name="sifre" placeholder="••••••••••" autofocus>
    <button type="submit">GİRİŞ YAP →</button>
  </form>
</div>
</body>
</html>'''

def giris_kontrol():
    return session.get('giris_yapildi') == True

@app.route('/')
def ana():
    if not giris_kontrol():
        return redirect('/giris')
    with open(HTML_DOSYA, 'r', encoding='utf-8') as f:
        icerik = f.read()
    icerik = icerik.replace(
        'https://yasamlab.iltelis.com/Integration/Integration.asmx',
        '/proxy/lab'
    )
    return icerik

@app.route('/giris', methods=['GET'])
def giris_sayfasi():
    return LOGIN_HTML.replace('__HATA__', '')

@app.route('/giris', methods=['POST'])
def giris_yap():
    sifre = request.form.get('sifre', '')
    if hashlib.sha256(sifre.encode()).hexdigest() == SIFRE_HASH:
        session['giris_yapildi'] = True
        return redirect('/')
    else:
        hata = '<div class="hata goster">❌ Şifre hatalı, tekrar deneyin.</div>'
        return LOGIN_HTML.replace('__HATA__', hata), 401

@app.route('/cikis')
def cikis():
    session.clear()
    return redirect('/giris')

@app.route('/proxy/lab', methods=['POST'])
def proxy_lab():
    if not giris_kontrol():
        return Response('Yetkisiz', status=401)
    try:
        soap_body = request.get_data()
        headers = {
            'Content-Type': 'application/soap+xml; charset=utf-8',
            'SOAPAction': 'http://tempuri.org/HastaSonuclariKimlikNO',
        }
        res = requests.post(
            'https://yasamlab.iltelis.com/Integration/Integration.asmx',
            data=soap_body,
            headers=headers,
            timeout=30,
            verify=False
        )
        response = Response(res.content, status=res.status_code)
        response.headers['Content-Type'] = 'text/xml; charset=utf-8'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as e:
        return Response(f'Hata: {str(e)}', status=500)

@app.route('/proxy/lab', methods=['OPTIONS'])
def proxy_lab_options():
    response = Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, SOAPAction'
    return response

def tarayici_ac():
    import time
    time.sleep(1)
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    print("=" * 50)
    print("  Diyaliz KKDS - Proxy Sunucu Başlatıldı")
    print("=" * 50)
    print("  Tarayıcı otomatik açılıyor...")
    print("  Kapatmak için: Ctrl+C")
    print("=" * 50)
    t = threading.Thread(target=tarayici_ac)
    t.daemon = True
    t.start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
