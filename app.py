from flask import Flask, request, jsonify
from summarize import transcribe_audio, summarize_transcript, create_pdf
import os

app = Flask(__name__)
UPLOAD_FOLDER = "static/hasil"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return "✅ Server Rangkuman Aktif!"

@app.route("/run", methods=["POST"])
def jalankan():
    if "audio" not in request.files:
        return jsonify({"error": "❌ File audio tidak ditemukan"}), 400

    audio_file = request.files["audio"]
    path = os.path.join(UPLOAD_FOLDER, "audio.wav")
    audio_file.save(path)

    # 1. Transkripsi
    transkrip = transcribe_audio(path)
    if not transkrip or "❌" in transkrip:
        return jsonify({"error": "Gagal melakukan transkripsi."}), 500

    # 2. Ringkasan
    ringkasan = summarize_transcript()
    if not ringkasan or "❌" in ringkasan:
        return jsonify({"error": "Gagal membuat ringkasan."}), 500

    # 3. PDF
    pdf_path = create_pdf()

    return jsonify({
        "message": "✅ Transkripsi dan ringkasan berhasil.",
        "transkrip": transkrip,
        "ringkasan": ringkasan,
        "pdf_url": pdf_path
    })

if __name__ == "__main__":
    app.run()
