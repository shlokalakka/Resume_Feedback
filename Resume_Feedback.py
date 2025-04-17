# AI Resume Feedback Agent - Full Pipeline

import os
import re
import smtplib
import tempfile
import email
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import PyPDF2
from dotenv import load_dotenv
load_dotenv()
import docx
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ========== CONFIG ==========
EMAIL_ADDRESS = os.getenv("AGENT_EMAIL")
EMAIL_PASSWORD = os.getenv("AGENT_PASSWORD")
IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"
PORT = 587
JOBS_DESCRIPTION = "Looking for candidates with Python, NLP, ML experience. Must have clean formatting and 1+ year in AI-related roles."

# ========== STEP 1: Resume Collection ==========
def fetch_resumes(folder="INBOX", limit=10):
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    mail.select(folder)
    _, data = mail.search(None, 'ALL')
    emails = data[0].split()[-limit:]

    resumes = []
    for num in emails:
        _, msg_data = mail.fetch(num, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                sender = msg['from']
                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                    filename = part.get_filename()
                    if filename and (filename.endswith(".pdf") or filename.endswith(".docx")):
                        file_data = part.get_payload(decode=True)
                        filepath = os.path.join("resumes", f"{re.sub(r'[<>:@]', '_', sender)}_{filename}")
                        with open(filepath, "wb") as f:
                            f.write(file_data)
                        resumes.append((sender, filepath))
    return resumes

# ========== STEP 2: Resume Scoring ==========
def extract_text_from_resume(filepath):
    if filepath.endswith(".pdf"):
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            return " ".join([page.extract_text() or "" for page in reader.pages])
    elif filepath.endswith(".docx"):
        doc = docx.Document(filepath)
        return " ".join([p.text for p in doc.paragraphs])
    return ""

def score_resume(text):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([text, JOBS_DESCRIPTION])
    match_score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    years_exp = len(re.findall(r'\d+\+?\s+years?', text.lower()))
    has_ai = bool(re.search(r'\b(machine learning|ai|deep learning|nlp|neural)\b', text.lower()))
    clean_formatting = len(text.split()) > 100  # simple proxy

    total_score = (match_score * 50) + (years_exp * 10) + (20 if has_ai else 0) + (20 if clean_formatting else 0)

    return {
        "match_score": round(match_score * 100, 2),
        "years_exp": years_exp,
        "has_ai": has_ai,
        "formatting": clean_formatting,
        "total_score": int(total_score)
    }

# ========== STEP 3: Email Feedback ==========
def send_feedback_email(to_email, name, score_data):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = "Your Resume Score & Feedback"

    feedback = f"""
Hi {name},

Thanks for submitting your resume. Here is your personalized feedback:

CV Score: {score_data['total_score']} / 100
- JD Match Score: {score_data['match_score']}%
- Years of Experience: {score_data['years_exp']}
- Relevant AI Experience: {"Yes" if score_data['has_ai'] else "No"}
- Formatting Quality: {"Good" if score_data['formatting'] else "Needs Improvement"}

We're excited by your interest and wish you the best!

Warmly,
The Resume AI Agent Team
"""
    msg.attach(MIMEText(feedback, 'plain'))

    with smtplib.SMTP(SMTP_SERVER, PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

# ========== MAIN PIPELINE ==========
def run_pipeline():
    os.makedirs("resumes", exist_ok=True)
    log = []
    resumes = fetch_resumes()

    for sender, filepath in resumes:
        text = extract_text_from_resume(filepath)
        score_data = score_resume(text)
        send_feedback_email(sender, sender.split('@')[0], score_data)
        log.append({"email": sender, "file": filepath, **score_data})

    df = pd.DataFrame(log)
    df.to_csv("processing_log.csv", index=False)
    print("✔️ Resume pipeline completed. Logs saved to processing_log.csv")

if __name__ == "__main__":
    run_pipeline()
