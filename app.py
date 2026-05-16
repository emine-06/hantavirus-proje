from flask import Flask, render_template, request, redirect, session, jsonify
import datetime

app = Flask(__name__)
app.secret_key = 'hanta_gizli_anahtar' # Oturum takibi için şart

# --------------------------------------------------------
# 🗂️ GEÇİCİ BELLEK (Render'da Tıkır Tıkır Çalışır)
# --------------------------------------------------------
# Localhost derdi olmadan, Render'a yüklediğinde de tıkır tıkır
# çalışması için verileri şimdilik bu listelerde tutuyoruz canım.
aktif_kullanicilar = []
test_sonuclari = []

# --------------------------------------------------------
# SAYFA ROTAMIZ (ROUTES) - GİRİŞ VE PANEL
# --------------------------------------------------------

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    
    # Giriş yapan kullanıcıyı listeye ekliyoruz (Admin görsün diye)
    giris_zamani = datetime.datetime.now().strftime("%H:%M:%S")
    aktif_kullanicilar.append({'email': email, 'saat': giris_zamani})
    
    session['user_id'] = email
    return redirect('/index')

@app.route('/index')
def index_page():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('index.html')

@app.route('/test')
def test_page():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('test.html')

# 🚀 TEST SONUÇLARINI BELLEĞE KAYDEDEN ROTAMIZ
@app.route('/testi-kaydet', methods=['POST'])
def testi_kaydet():
    if 'user_id' not in session:
        return jsonify({'durum': 'hata', 'mesaj': 'Oturum açık değil!'}), 401

    try:
        veri = request.get_json()
        risk_puani = veri.get('puan')
        risk_durumu = veri.get('durum')
        cozum_zamani = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        
        # Test sonucunu kimin çözdüğüyle birlikte listeye kaydediyoruz
        test_sonuclari.append({
            'kullanici': session['user_id'],
            'puan': risk_puani,
            'durum': risk_durumu,
            'tarih': cozum_zamani
        })
        
        return jsonify({'durum': 'basarili', 'mesaj': 'Sonuç başarıyla kaydedildi!'})
    except Exception as e:
        return jsonify({'durum': 'hata', 'mesaj': str(e)}), 500

# --------------------------------------------------------
# 👑 GİZLİ ADMİN PANELİ (Sadece Tarayıcıya /admin yazınca açılır)
# --------------------------------------------------------
@app.route('/admin')
def admin_panel():
    # Sözel Mantık: Giriş yapanları ve test sonuçlarını HTML şablonuna gönderiyoruz
    return render_template('admin.html', kullanicilar=aktif_kullanicilar, sonuclar=test_sonuclari)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)