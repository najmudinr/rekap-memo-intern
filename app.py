import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import os
import base64
import json


app = Flask(__name__)

# Path ke file credentials Firebase JSON yang diunduh
cred = credentials.Certificate("C:/Users/ASUS/rekap-memo/firebase-credentials.json")
firebase_admin.initialize_app(cred)

#Decode JSON Credential string
firebase_cred_json = os.getenv("FIREBASE_CREDENTIALS")
if firebase_cred_json:
    cred_dict = json.loads(base64.b64decode(firebase_cred_json))
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

# Inisialisasi Firestore
db = firestore.client()

# Rute Admin untuk menambahkan memo baru
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # Ambil data dari form dan buat memo dictionary
        memo = {
            'nomor_memo': request.form['nomor_memo'],
            'pembuat_memo': request.form['pembuat_memo'],
            'asal_memo': request.form['asal_memo'],
            'tujuan_memo': request.form['tujuan_memo'],
            'perihal_pengajuan': request.form['perihal_pengajuan'],
            'tanggal_pengajuan': datetime.strptime(request.form['tanggal_pengajuan'], '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M') if request.form.get('tanggal_pengajuan') else '',
            'tanggal_avp': datetime.strptime(request.form.get('tanggal_avp'), '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M') if request.form.get('tanggal_avp') else '',
            'tanggal_vp': datetime.strptime(request.form.get('tanggal_vp'), '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M') if request.form.get('tanggal_vp') else '',
            'diterima_avp': datetime.strptime(request.form.get('diterima_avp'), '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M') if request.form.get('diterima_avp') else '',
            'diterima_vp': datetime.strptime(request.form.get('diterima_vp'), '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M') if request.form.get('diterima_vp') else '',
            'status': request.form['status'],
            'tindak_lanjut': request.form['tindak_lanjut'],
            'pic_terkait': request.form['pic_terkait'],
            'arsip_dokumen': request.form['arsip_dokumen'],
            'keterangan': request.form['keterangan']
        }
        
        # Simpan memo ke Firestore
        db.collection('memos').add(memo)

        return redirect(url_for('admin_dashboard'))

    return render_template('admin.html')


# Route untuk dashboard utama
@app.route('/')
def dashboard():
    # Ambil semua memo dari Firestore
    memos_ref = db.collection('memos')
    memos = [doc.to_dict() for doc in memos_ref.stream()]
    return render_template('dashboard.html', memos=memos)


# Route untuk dashboard admin dengan tombol edit
@app.route('/admin/dashboard')
def admin_dashboard():
    # Ambil semua memo dari Firestore
    memos_ref = db.collection('memos')
    memos = [{'id': doc.id, **doc.to_dict()} for doc in memos_ref.stream()]  # Sertakan ID dokumen
    return render_template('admin_dashboard.html', memos=memos)


# Route untuk mengedit memo
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_memo(id):
    print(f"Received ID : {id}")
    memo_ref = db.collection('memos').document(id)
    memo_doc = memo_ref.get()

    if not memo_doc.exists:
        print("Memo not found")
        return "Memo not found", 404

    memo = memo_doc.to_dict()
    memo['id'] = id  # Sertakan ID dalam dictionary untuk akses di template

    if request.method == 'POST':
        # Update memo dengan data baru dari form
        memo_update = {
            'nomor_memo': request.form['nomor_memo'],
            'pembuat_memo': request.form['pembuat_memo'],
            'asal_memo': request.form['asal_memo'],
            'tujuan_memo': request.form['tujuan_memo'],
            'perihal_pengajuan': request.form['perihal_pengajuan'],
            'tanggal_pengajuan': datetime.strptime(request.form['tanggal_pengajuan'], '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M') if request.form.get('tanggal_pengajuan') else '',
            'tanggal_avp': datetime.strptime(request.form.get('tanggal_avp'), '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M') if request.form.get('tanggal_avp') else '',
            'tanggal_vp': datetime.strptime(request.form.get('tanggal_vp'), '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M') if request.form.get('tanggal_vp') else '',
            'diterima_avp': datetime.strptime(request.form.get('diterima_avp'), '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M') if request.form.get('diterima_avp') else '',
            'diterima_vp': datetime.strptime(request.form.get('diterima_vp'), '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M') if request.form.get('diterima_vp') else '',
            'status': request.form['status'],
            'tindak_lanjut': request.form['tindak_lanjut'],
            'pic_terkait': request.form['pic_terkait'],
            'arsip_dokumen': request.form['arsip_dokumen'],
            'keterangan': request.form['keterangan']
        }
        
        # Update memo di Firestore
        memo_ref.update(memo_update)

        return redirect(url_for('admin_dashboard'))

    return render_template('edit_memo.html', memo=memo)

if __name__ == '__main__':
    app.run(debug=True)
