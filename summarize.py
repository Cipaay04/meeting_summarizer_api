# summarize.py
import os
import whisper
from transformers import pipeline
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

TRANSCRIPT_PATH = "static/hasil/transkrip_full.txt"
SUMMARY_PATH = "static/hasil/ringkasan.txt"
PDF_PATH = "static/hasil/hasil_meeting.pdf"

os.makedirs("static/hasil", exist_ok=True)

def transcribe_audio(audio_path):
    model = whisper.load_model("tiny")
    result = model.transcribe(audio_path, language="indonesian")
    with open(TRANSCRIPT_PATH, "w", encoding="utf-8") as f:
        f.write(result["text"])
    return result["text"]

def summarize_transcript():
    if not os.path.exists(TRANSCRIPT_PATH):
        raise FileNotFoundError("File transkrip_full.txt tidak ditemukan.")

    with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
        full_text = f.read()

    summarizer = pipeline("summarization", model="cahya/t5-base-indonesian-summarization-cased")
    chunks = [full_text[i:i+1024] for i in range(0, len(full_text), 1024)]
    summaries = []

    for chunk in chunks:
        summary = summarizer(chunk, max_length=200, min_length=30, do_sample=False)[0]['summary_text']
        summaries.append(summary)

    combined = "\n".join(summaries)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        f.write(combined)
    return combined

def create_pdf():
    if not os.path.exists(SUMMARY_PATH):
        raise FileNotFoundError("File ringkasan.txt tidak ditemukan.")

    with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    doc = SimpleDocTemplate(PDF_PATH, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=60, bottomMargin=40)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='JudulUtama', fontSize=18, leading=22, alignment=1, spaceAfter=20))
    styles.add(ParagraphStyle(name='Isi', fontSize=11, leading=16))

    elements = [Paragraph("Rangkuman", styles['JudulUtama']), Spacer(1, 12)]
    for line in content.strip().split("\n"):
        if line.strip():
            elements.append(Paragraph(line.strip(), styles['Isi']))
            elements.append(Spacer(1, 6))

    doc.build(elements)
    return PDF_PATH
