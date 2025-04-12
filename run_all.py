import threading
import subprocess
import schedule
import time
from fake_server import app  # фейковый Flask-сервер для Render

def run_flask():
    app.run(host="0.0.0.0", port=10000)  # открываем порт, чтобы Render не ругался

def run_logger():
    subprocess.run(["python", "multi_log_viewers.py"])

def run_daily():
    print("🟢 Запуск анализа и экспорта...")
    subprocess.run(["python", "analyze_all.py"])
    subprocess.run(["python", "export_to_sheets.py"])
    print("✅ Анализ и экспорт завершены.")

def run_scheduler():
    schedule.every().day.at("23:59").do(run_daily)
    print("⏳ Жду запуска анализа в 23:59...")
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    threading.Thread(target=run_logger).start()
    threading.Thread(target=run_scheduler).start()
