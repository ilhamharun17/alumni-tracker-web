from flask import Flask, render_template, request
import difflib

app = Flask(__name__)

# Data Master (Sistem mengambil data alumni dari master)
MASTER_ALUMNI = [
    {"id": 1, "nama_asli": "Muhammad Rizky", "prodi": "Informatika", "tahun_lulus": 2020, "status": "Belum Dilacak", "info": "-"},
    {"id": 2, "nama_asli": "Siti Aminah", "prodi": "Ilmu Komunikasi", "tahun_lulus": 2019, "status": "Belum Dilacak", "info": "-"},
    {"id": 3, "nama_asli": "Budi Santoso", "prodi": "Teknik Mesin", "tahun_lulus": 2021, "status": "Belum Dilacak", "info": "-"}
]

# Simulasi Hasil Pencarian dari Web (LinkedIn, Scholar, dll)
MOCK_WEB_RESULTS = [
    {"nama": "M. Rizky", "afiliasi": "UMM", "role": "Software Engineer", "tahun": 2022, "sumber": "LinkedIn"},
    {"nama": "Muhammad Rizky", "afiliasi": "Universitas Brawijaya", "role": "Dosen", "tahun": 2021, "sumber": "Google Scholar"},
    {"nama": "Siti Aminah", "afiliasi": "Universitas Muhammadiyah Malang", "role": "Jurnalis", "tahun": 2021, "sumber": "LinkedIn"}
]

# Fungsi Disambiguasi dan Scoring
def hitung_kemiripan(alumnus, kandidat):
    score = 0.0
    
    # 1. Kecocokan Nama (Bobot maks 0.4)
    kemiripan_nama = difflib.SequenceMatcher(None, alumnus["nama_asli"].lower(), kandidat["nama"].lower()).ratio()
    if kemiripan_nama > 0.8:
        score += 0.4
    elif kemiripan_nama > 0.5:
        score += 0.2
        
    # 2. Kecocokan Afiliasi / Konteks (Bobot 0.3)
    afiliasi_kandidat = kandidat["afiliasi"].lower()
    if "umm" in afiliasi_kandidat or "muhammadiyah malang" in afiliasi_kandidat:
        score += 0.3
        
    # 3. Kecocokan Timeline (Bobot 0.3)
    if kandidat["tahun"] >= alumnus["tahun_lulus"]:
        score += 0.3
        
    return score

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        target_id = int(request.form.get('alumni_id'))
        
        # Cari data alumni berdasarkan ID
        alumnus = next((al for al in MASTER_ALUMNI if al['id'] == target_id), None)
        
        if alumnus:
            best_candidate = None
            highest_score = 0
            
            # Melakukan pengecekan ke hasil pencarian
            for kandidat in MOCK_WEB_RESULTS:
                skor = hitung_kemiripan(alumnus, kandidat)
                if skor > highest_score:
                    highest_score = skor
                    best_candidate = kandidat
            
            # Menetapkan Status Alumni Berdasarkan Temuan
            if highest_score >= 0.7:
                alumnus['status'] = f"Teridentifikasi"
                alumnus['info'] = f"Confidence: {highest_score*100:.0f}% | {best_candidate['role']} di {best_candidate['sumber']}"
            elif highest_score >= 0.4:
                alumnus['status'] = f"Perlu Verifikasi Manual"
                alumnus['info'] = f"Skor meragukan ({highest_score*100:.0f}%). Cek: {best_candidate['nama']} ({best_candidate['afiliasi']})"
            else:
                alumnus['status'] = "Tidak Ditemukan"
                alumnus['info'] = "Tidak ada kecocokan di sumber publik."

    return render_template('index.html', alumni_data=MASTER_ALUMNI)

if __name__ == '__main__':
    app.run(debug=True)