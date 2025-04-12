import threading
import subprocess
import schedule
import time

def run_logger():
    subprocess.run(["python", "multi_log_viewers.py"])

def run_daily():
    print("🟢 Запуск анализа и экспорта...")
    subprocess.run(["python", "analyze_all.py"])
    subprocess.run(["python", "export_to_sheets.py"])
    print("✅ Готово.")

def run_scheduler():
    schedule.every().day.at("23:59").do(run_daily)
    print("⏳ Жду запуска в 23:59...")
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    threading.Thread(target=run_logger).start()
    threading.Thread(target=run_scheduler).start()
