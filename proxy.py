from flask import Flask, request, Response
import requests
import webbrowser
import threading
import os

app = Flask(__name__)

HTML_DOSYA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'diyaliz-kkds.html')

@app.route('/')
def ana():
    with open(HTML_DOSYA, 'r', encoding='utf-8') as f:
        icerik = f.read()
    # HTML'deki Yaşam Lab URL'sini proxy URL'siyle değiştir
    icerik = icerik.replace(
        'https://yasamlab.iltelis.com/Integration/Integration.asmx',
        '/proxy/lab'
    )
    return icerik

@app.route('/proxy/lab', methods=['POST'])
def proxy_lab():
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
        # Debug: XML yanıtını dosyaya kaydet
        debug_dosya = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'debug_yanit.xml')
        with open(debug_dosya, 'wb') as f:
            f.write(res.content)
        print(f"\n[DEBUG] Yanıt kaydedildi: {debug_dosya}")
        print(f"[DEBUG] Yanıt boyutu: {len(res.content)} byte")
        print(f"[DEBUG] İlk 500 karakter:\n{res.content[:500]}\n")

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
