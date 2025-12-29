import sqlite3

# Veritabanına bağlan
baglanti = sqlite3.connect('agency.db')
imlec = baglanti.cursor()

# Bütün kullanıcıları seç ve getir
imlec.execute("SELECT * FROM kullanicilar")
veriler = imlec.fetchall()

# Ekrana yazdır
print("\n--- VERİTABANI RAPORU ---")
if len(veriler) == 0:
    print("Henüz hiç kayıt yok.")
else:
    for kisi in veriler:
        # kisi[0]=id, kisi[1]=email, kisi[2]=sifre
        print(f"ID: {kisi[0]} | Email: {kisi[1]} | Şifre: {kisi[2]}")

print("-------------------------\n")

baglanti.close()