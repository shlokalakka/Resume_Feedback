# 🧠 AI Resume Feedback Agent

An automated pipeline that collects resumes, evaluates them against a job description, and emails personalized feedback to each candidate — all in one go.

## 🚀 Features

- ✅ Collects resumes (PDF/DOCX) from Gmail
- ✅ Extracts and scores resumes using TF-IDF & cosine similarity
- ✅ Evaluates formatting, AI-related experience, and years of work
- ✅ Sends a personalized email back to each candidate
- ✅ Logs results in a CSV and stores all resumes locally

## 📦 Technologies Used

- Python
- IMAP / SMTP (for Gmail integration)
- `PyPDF2`, `python-docx` (resume parsing)
- `scikit-learn` (TF-IDF + similarity scoring)
- `pandas` (logging)
- `smtplib`, `imaplib` (email handling)

## 🛠️ How It Works

1. Fetches resumes from your Gmail inbox
2. Extracts text from each resume
3. Scores resumes using:
   - JD Match (TF-IDF)
   - Years of experience
   - AI-relevant keywords
   - Formatting quality
4. Sends an email to the candidate with:
   - Total score
   - Breakdown of strengths
   - Optional next steps or encouragement
5. Saves a local copy of the resume and log

