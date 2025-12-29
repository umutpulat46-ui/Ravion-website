import sqlite3
import hashlib
import os
from flask import Flask, render_template, request, session, redirect, url_for

# HTML ve CSS dosyaların ana klasörde olduğu için bu ayarları böyle bırakıyoruz
app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')

# BU ÇOK ÖNEMLİ! Giriş kartlarını (session) imzalamak için gizli anahtar.
app.secret_key = "buna_cok_zor_bir_sifre_yaz_ravion_123"

# --- PATRON AYARI ---
# Buraya kendi yönetici mailini yaz. Sadece bu mail Admin Paneline girebilir.
PATRON_EMAIL = "umutpulat46@gmail.com" 

def veritabani_kur():
    baglanti = sqlite3.connect('agency.db')
    imlec = baglanti.cursor()
    # Kullanıcılar tablosu yoksa oluştur
    imlec.execute('''
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            telefon TEXT NOT NULL,
            sifre TEXT NOT NULL
        )
    ''')
    baglanti.commit()
    baglanti.close()

# Uygulama başlarken veritabanını kontrol et
veritabani_kur()

# --- SAYFA YÖNLENDİRMELERİ ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login.html')
def login_page():
    return render_template('login.html')

@app.route('/payment.html')
def payment():
    return render_template('payment.html')

# --- GÜVENLİ PATRON PANELİ ---
@app.route('/admin')
def admin():
    # 1. Kontrol: Giriş yapmış mı?
    if 'giris_yapti' not in session:
        return redirect('/login.html')
    
    # 2. Kontrol: Giren kişi GERÇEKTEN Patron mu? 🛑
    if session.get('kullanici_adi') != PATRON_EMAIL:
        return f"""
        <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
            <h1 style="color: red;">YETKİSİZ ALAN! ⛔️</h1>
            <p>Burası sadece yöneticiler içindir.</p>
            <p>Siz Müşteri Paneline yönlendiriliyorsunuz...</p>
            <meta http-equiv="refresh" content="3;url=/profil" />
        </div>
        """

    # Patron ise verileri göster
    baglanti = sqlite3.connect('agency.db')
    imlec = baglanti.cursor()
    imlec.execute("SELECT * FROM kullanicilar")
    veriler = imlec.fetchall()
    baglanti.close()
    return render_template('admin.html', liste=veriler)

# --- YENİ: MÜŞTERİ PANELİ (Herkesin Girebildiği Yer) ---
@app.route('/profil')
def profil_sayfasi():
    if 'giris_yapti' not in session:
        return redirect('/login.html')
        
    kullanici = session.get('kullanici_adi')
    
    return f"""
    <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
        <h1 style="color: #333;">Merhaba, {kullanici} 👋</h1>
        <p>Ravion Digital Müşteri Paneline Hoş Geldiniz.</p>
        <hr style="width: 50%;">
        <h3>Siparişleriniz</h3>
        <p>Henüz aktif bir siparişiniz yok.</p>
        <br><br>
        <a href="/logout" style="background-color: red; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Çıkış Yap</a>
    </div>
    """

# --- KAYIT OLMA İŞLEMİ ---
@app.route('/register', methods=['POST'])
def register():
    gelen_email = request.form.get('email')
    gelen_telefon = request.form.get('phone')
    gelen_sifre = request.form.get('password')
    
    # Şifreleme İşlemi (Tuzlama)
    tuz = os.urandom(16).hex() 
    birlestirilmis = tuz + gelen_email + gelen_sifre 
    hash_objesi = hashlib.sha256(birlestirilmis.encode())
    sifreli_hal = hash_objesi.hexdigest()
    kaydedilecek_veri = f"{tuz}:{sifreli_hal}"
    
    baglanti = sqlite3.connect('agency.db')
    imlec = baglanti.cursor()
    imlec.execute("INSERT INTO kullanicilar (email, telefon, sifre) VALUES (?, ?, ?)", (gelen_email, gelen_telefon, kaydedilecek_veri))
    baglanti.commit()
    baglanti.close()
    
    return f"""
    <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
        <h1 style="color: green;">KAYIT BAŞARILI! ✅</h1>
        <p>Giriş sayfasına yönlendiriliyorsunuz...</p>
        <meta http-equiv="refresh" content="2;url=/login.html" />
    </div>
    """

# --- GİRİŞ YAPMA İŞLEMİ (AKILLI KAPI) ---
@app.route('/login', methods=['POST'])
def login_kontrol():
    gelen_email = request.form.get('email')
    gelen_sifre = request.form.get('password')
    
    baglanti = sqlite3.connect('agency.db')
    imlec = baglanti.cursor()
    imlec.execute("SELECT * FROM kullanicilar WHERE email = ?", (gelen_email,))
    kullanici = imlec.fetchone()
    baglanti.close()
    
    if kullanici:
        kayitli_veri = kullanici[3] 
        tuz, kayitli_sifre = kayitli_veri.split(':')
        
        kontrol_verisi = tuz + gelen_email + gelen_sifre
        kontrol_hash = hashlib.sha256(kontrol_verisi.encode()).hexdigest()
        
        if kontrol_hash == kayitli_sifre:
            # Giriş Başarılı!
            session['giris_yapti'] = True
            session['kullanici_adi'] = gelen_email
            
            # İŞTE BURASI AYRIM NOKTASI (TRAFİK POLİSİ) 👮‍♂️
            if gelen_email == PATRON_EMAIL:
                return redirect('/admin')  # Patron doğruca ofise
            else:
                return redirect('/profil') # Müşteri bekleme salonuna
            
        else:
            return "<h1 style='color:red; text-align:center;'>HATA: Şifre Yanlış! ❌</h1>"
    else:
        return "<h1 style='color:red; text-align:center;'>HATA: Böyle bir kullanıcı yok! ❌</h1>"

# --- ÇIKIŞ YAPMA ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# --- ÖDEME ALMA ---
@app.route('/odeme-yap', methods=['POST'])
def odeme_yap():
    kart_isim = request.form.get('card_name')
    return f"""
    <div style="text-align: center; margin-top: 50px; font-family: sans-serif; background-color: #f0fdf4; padding: 50px;">
        <h1 style="color: green; font-size: 48px;">ÖDEME BAŞARILI! ✅</h1>
        <p style="font-size: 20px;">Tebrikler <b>{kart_isim}</b>, ödemeniz güvenli bir şekilde alındı.</p>
        <p>Hizmetlerimizden yararlanmaya hemen başlayabilirsiniz.</p>
        <br>
        <a href="/" style="background-color: green; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 18px;">Ana Sayfaya Dön</a>
    </div>
    """

if __name__ == '__main__':
    app.run(debug=True, port=5000)