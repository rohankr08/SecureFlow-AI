# 🔐 SecureFlow AI

> OCR-Based Fraud Detection System using Flask, OpenCV, and Tesseract OCR

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black?logo=flask)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?logo=opencv)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue?logo=sqlite)

---

## 📖 Project Overview

SecureFlow AI is a Flask-based web application developed to detect fraudulent transaction screenshots using OCR (Optical Character Recognition). The system extracts transaction details from uploaded screenshots using **Tesseract OCR**, processes the image using **OpenCV**, and applies rule-based validation to classify transactions as **Genuine**, **Suspicious**, or **Fraudulent**.

---

## ✨ Features

- 📤 Upload transaction screenshots
- 🔍 OCR text extraction using Tesseract OCR
- 🖼️ Image preprocessing with OpenCV
- 🤖 Rule-based fraud detection
- 💾 SQLite database for transaction history
- 📊 Interactive dashboard
- ⚡ Fast and user-friendly interface

---

## 🛠️ Technologies Used

- Python
- Flask
- OpenCV
- Tesseract OCR (pytesseract)
- SQLite
- HTML
- CSS
- JavaScript

---

## 📂 Project Structure

```text
SecureFlow-AI
│
├── app/
│   ├── app.py
│   └── templates/
│       ├── index.html
│       └── dashboard.html
│
├── data/
├── models/
├── src/
│   ├── analysis.py
│   └── predict.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🚀 Installation

### Clone the Repository

```bash
git clone https://github.com/rohankr08/SecureFlow-AI.git
```

### Move to Project Folder

```bash
cd SecureFlow-AI
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
python app.py
```

---

## 📊 Workflow

1. Upload Transaction Screenshot
2. Image Preprocessing using OpenCV
3. OCR Text Extraction
4. Transaction Data Validation
5. Fraud Detection
6. Display Result on Dashboard

---


## 👨‍💻 Author

**Rohan Kumar**


