document.addEventListener("DOMContentLoaded", () => {
    
    // 1. MOBİL MENÜYÜ ÇALIŞTIR
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }

    // 2. LOGİN SAYFASINDAKİ KAYIT FORMUNU BAŞLANGIÇTA GİZLE
    const registerForm = document.getElementById('register-form');
    if (registerForm) { registerForm.style.display = 'none'; }

    // 3. ÖDEME SAYFASI FONKSİYONLARINI BAŞLAT
    setupPaymentPage();
    loadOrderDetails(); 
});

// --- FİYAT HESAPLAMA VE EKRANA YAZMA (ÖDEME SAYFASI İÇİN) ---
function loadOrderDetails() {
    // Adres çubuğundaki ?plan=... ve &price=... bilgisini okur
    const params = new URLSearchParams(window.location.search);
    const plan = params.get('plan');
    const price = params.get('price');

    // Eğer plan ve fiyat bilgisi varsa ekrana yazar
    if (plan && price) {
        const priceNum = parseFloat(price);
        const tax = priceNum * 0.20; // %20 KDV
        const total = priceNum + tax;

        // HTML'deki yerleri bul
        const planNameEl = document.getElementById('plan-name');
        const planPriceEl = document.getElementById('plan-price');
        const planTaxEl = document.getElementById('plan-tax');
        const planTotalEl = document.getElementById('plan-total');

        // Yazıları değiştir
        if(planNameEl) planNameEl.innerText = plan + " PLAN";
        if(planPriceEl) planPriceEl.innerText = '₺' + priceNum.toLocaleString('tr-TR');
        if(planTaxEl) planTaxEl.innerText = '₺' + tax.toLocaleString('tr-TR');
        if(planTotalEl) planTotalEl.innerText = '₺' + total.toLocaleString('tr-TR');
    }
}

// --- LOGİN VE KAYIT FORMU ARASINDA GEÇİŞ ---
function switchForm(formType) {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const btns = document.querySelectorAll('.toggle-btn');
    const title = document.getElementById('form-title');

    if (!loginForm || !registerForm) return;

    if (formType === 'register') {
        loginForm.style.display = 'none'; loginForm.classList.remove('active-form');
        registerForm.style.display = 'block'; registerForm.classList.add('active-form');
        if(btns.length > 1) { btns[0].classList.remove('active'); btns[1].classList.add('active'); }
        if(title) title.innerText = "Partner Başvurusu";
    } else {
        registerForm.style.display = 'none'; registerForm.classList.remove('active-form');
        loginForm.style.display = 'block'; loginForm.classList.add('active-form');
        if(btns.length > 1) { btns[1].classList.remove('active'); btns[0].classList.add('active'); }
        if(title) title.innerText = "Hoş Geldiniz";
    }
}

// --- KREDİ KARTI FORMATLAMA (BOŞLUK BIRAKMA) ---
function setupPaymentPage() {
    const cardNumberInput = document.querySelector('input[placeholder="0000 0000 0000 0000"]');
    const dateInput = document.querySelector('input[placeholder="AA/YY"]');
    const cvcInput = document.querySelector('input[placeholder="123"]');
    const payBtn = document.querySelector('.btn-pay');

    if (!cardNumberInput) return;

    // Kart Numarası (4 hanede bir boşluk)
    cardNumberInput.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, '').substring(0, 16);
        e.target.value = value.match(/.{1,4}/g)?.join(' ') || value;
    });

    // Tarih (AA/YY formatı)
    dateInput.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length >= 2) e.target.value = value.substring(0, 2) + '/' + value.substring(2, 4);
        else e.target.value = value;
    });

    // CVC (Sadece rakam)
    cvcInput.addEventListener('input', (e) => e.target.value = e.target.value.replace(/\D/g, '').substring(0, 3));

    // Ödeme Butonu Animasyonu
    if (payBtn) {
        payBtn.addEventListener('click', () => {
            if(cardNumberInput.value.length < 19 || dateInput.value.length < 5 || cvcInput.value.length < 3) {
                alert("Lütfen kart bilgilerinizi eksiksiz giriniz."); return;
            }
            payBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> İşleniyor...';
            payBtn.style.background = '#ccc';
            setTimeout(() => {
                payBtn.innerHTML = '<i class="fas fa-check"></i> ÖDEME BAŞARILI';
                payBtn.style.background = '#4caf50'; payBtn.style.color = '#fff';
                alert("Ödemeniz alındı!");
            }, 2000);
        });
    }
}