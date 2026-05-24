# 📢 Tender Monitor

A Python-based automated tender monitoring system that tracks tender notices from the XMUM website and sends real-time Telegram notifications whenever new tenders are published.

---

## 🚀 Features

- Automated tender notice monitoring
- Real-time Telegram notifications
- Web scraping using BeautifulSoup
- Duplicate tender detection
- Environment variable security handling
- Railway cloud deployment
- GitHub integration
- Automatic logging system
- Error handling and retry mechanism

---

## 🛠 Tech Stack

- Python 3
- requests
- BeautifulSoup4
- python-dotenv
- Telegram Bot API
- Railway
- GitHub

---

## 📂 Project Structure

```text
Tender-Monitor-Showcase/
│
├── BusinessTracker.py
├── requirements.txt
├── Procfile
├── README.md
└── screenshots/
```

---

## ⚙️ How It Works

1. The system monitors the XMUM tender notice page continuously.
2. Tender information is scraped automatically.
3. Existing tenders are compared against previously recorded tenders.
4. Newly detected tenders trigger Telegram notifications.
5. Duplicate tenders are filtered automatically.

---

## 📩 Telegram Notification Example

```text
📢 New Tender Published

📌 TENDER NOTICE XMUM26T1004
📄 Tender Name: Supply and Installation of Projector
🔢 Tender Number: XMUM26T1004
⏰ Closing Date: Wednesday, November 19, 2025 - 17:00
🔗 https://www.xmu.edu.my/tender-notice
```

---

## ☁️ Deployment

This project supports deployment using:

- Railway
- GitHub automatic deployment
- Environment variables for secure credential handling

---

## 🔐 Environment Variables

Sensitive credentials are stored securely using environment variables.

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

---

## ▶️ Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/Tender-Monitor.git
cd Tender-Monitor
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### Run the Application

```bash
python BusinessTracker.py
```

---

## 📚 What I Learned

- Python automation scripting
- Web scraping techniques
- Telegram Bot integration
- Cloud deployment with Railway
- GitHub version control
- Environment variable management
- Logging and monitoring systems
- Error handling and retry logic

---

## 📸 Screenshots

### Telegram Notifications

<img width="1102" height="997" alt="image" src="https://github.com/user-attachments/assets/ef2df17b-4f92-4009-93bc-8293c130c729" />

---

### Railway Deployment

<img width="1450" height="1103" alt="image" src="https://github.com/user-attachments/assets/c4cacebd-eeda-4904-bfdd-57c5c18b25f7" />

---

### GitHub Repository

<img width="1535" height="1041" alt="image" src="https://github.com/user-attachments/assets/d80dff89-5484-4900-8c95-b8f1c78af1a1" />

---

## 💡 Future Improvements

- Web dashboard for tender management
- Database integration
- Email notifications
- Multi-website monitoring
- Advanced tender filtering
- Docker containerization

---

## 👨‍💻 Author

Developed as a portfolio and automation project for monitoring university tender notices efficiently.
