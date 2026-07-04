from flask import Flask, render_template, request
import sqlite3
import pytesseract
import re
import cv2
import os
import uuid

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__, template_folder='templates')

# ---------- DB ----------
def init_db():
    conn = sqlite3.connect('transactions.db')
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount TEXT,
        status TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- HOME ----------
@app.route('/')
def home():
    conn = sqlite3.connect('transactions.db')
    c = conn.cursor()
    data = c.execute("SELECT * FROM transactions").fetchall()

    total = len(data)
    fraud = sum(1 for d in data if d[2] == "FRAUD")
    genuine = total - fraud

    conn.close()

    return render_template('index.html',
                           data=data,
                           total=total,
                           fraud=fraud,
                           genuine=genuine)

# ---------- VERIFY ----------
@app.route('/verify', methods=['POST'])
def verify():
    txn_id = request.form['txn_id']
    file = request.files['file']

    # Server safe filename (Overwrite fix)
    filename = str(uuid.uuid4()) + ".png"
    filepath = filename
    file.save(filepath)

    try:
        # ---------- OCR (Aapka Original aur Safe Logic) ----------
        img = cv2.imread(filepath)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        gray = cv2.GaussianBlur(gray, (3,3), 0)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        text = pytesseract.image_to_string(thresh)
        clean_text = text.lower()

        # ---------- ID MATCH ----------
        id_match = txn_id.lower() in clean_text
        match_status = "ID matches screenshot ✅" if id_match else "ID mismatch ❌"

        # ---------- FINAL AMOUNT DETECTION (Aapka Original Logic - No changes) ----------
        amount = "Not Found"

        # 1️⃣ ₹ with commas (₹20,000)
        match = re.search(r'₹\s?([\d,]+\.?\d*)', clean_text)
        if match:
            amount = match.group(1).replace(",", "")

        # 2️⃣ Context-based
        if amount == "Not Found":
            match = re.search(r'(paid|debited|sent)[^\d]{0,10}([\d,]+\.?\d*)', clean_text)
            if match:
                amount = match.group(2).replace(",", "")

        # 3️⃣ "Amount" keyword
        if amount == "Not Found":
            match = re.search(r'amount[^\d]{0,10}([\d,]+\.?\d*)', clean_text)
            if match:
                amount = match.group(1).replace(",", "")

        # 4️⃣ Safe fallback (avoid txn IDs)
        if amount == "Not Found":
            numbers = re.findall(r'[\d,]{3,}', clean_text)
            valid = [n for n in numbers if len(n.replace(",", "")) <= 6]
            if valid:
                amount = valid[0].replace(",", "")

        # ---------- TIME DETECTION (IMPROVED - Ab dono chalenge) ----------
        time = "Not Found"
        
        # Naya pattern: 12:30, 09:15 AM, 14:45:00 sab pakdega
        time_pattern = r'\b(?:[01]?\d|2[0-3]):[0-5]\d(?:[:][0-5]\d)?\s*(?:am|pm|a\.m\.|p\.m\.|hrs)?\b'
        time_match = re.search(time_pattern, clean_text)
        
        if time_match:
            time = time_match.group()
        else:
            # Agar upar wala fail hua toh aapka purana basic logic (Safe side ke liye)
            match = re.search(r'\d{1,2}:\d{2}', clean_text)
            if match:
                time = match.group()

        # ---------- DATE DETECTION (Bonus) ----------
        date = "Not Found"
        date_pattern = r'\b(?:\d{1,2}[-/\s\.](?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|[a-z]+)[-/\s\.]\d{2,4}|\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})\b'
        date_match = re.search(date_pattern, clean_text)
        if date_match:
            date = date_match.group()

        # ---------- FEATURES ----------
        has_upi = any(k in clean_text for k in ["upi", "gpay", "paytm", "phonepe"])
        has_success = any(k in clean_text for k in ["success", "completed", "credited", "debited"])
        has_amount = amount != "Not Found"
        has_txn = any(k in clean_text for k in ["txn", "transaction", "utr", "ref"])

        # ---------- SCORING ----------
        score = 0

        if id_match: score += 4
        if has_success: score += 3
        if has_upi: score += 2
        if has_amount: score += 2
        if has_txn: score += 1

        # ---------- CONFIDENCE ----------
        confidence = int((score / 12) * 100)

        if id_match and has_success and has_amount:
            confidence += 10

        confidence = min(confidence, 100)

        # ---------- RESULT ----------
        if score >= 8:
            final_result = "GENUINE"
        elif score >= 4:
            final_result = "SUSPICIOUS"
        else:
            final_result = "FRAUD"

        # ---------- REASONS ----------
        reasons = []
        if not id_match: reasons.append("Transaction ID mismatch")
        if not has_success: reasons.append("No success confirmation")
        if not has_upi: reasons.append("UPI not detected")
        if not has_amount: reasons.append("Amount not detected")

        # ---------- SAVE ----------
        conn = sqlite3.connect('transactions.db')
        c = conn.cursor()
        c.execute("INSERT INTO transactions (amount, status) VALUES (?, ?)", (amount, final_result))
        conn.commit()

        data = c.execute("SELECT * FROM transactions").fetchall()
        conn.close()

        total = len(data)
        fraud = sum(1 for d in data if d[2] == "FRAUD")
        genuine = total - fraud

        # Note: Aapko HTML me {{ date }} use karna hoga agar date dikhani hai toh.
        return render_template(
            'index.html',
            verify_result=True,
            txn_id=txn_id,
            match_status=match_status,
            final_result=final_result,
            confidence=confidence,
            amount=amount,
            time=time,
            date=date,
            extracted_text=text,
            reasons=reasons,
            total=total,
            fraud=fraud,
            genuine=genuine,
            data=data
        )

    finally:
        # File delete taaki memory full na ho
        if os.path.exists(filepath):
            os.remove(filepath)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)