import csv
import os
import json
from datetime import datetime, time, date
from collections import defaultdict
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import traceback

# --- Настройки ---
log_dir = "viewer_log"
today = date.today()
today_str = today.isoformat()

spreadsheet_id = "1QmClQwBNKZB5I4tFzhNrXd4uhJFt-s7sh7O6St4E1mk"
sheet_title = "Статистика по аккаунтам"

# --- Временные блоки ---
intervals = [
    ("00:00–03:59", time(0, 0), time(3, 59)),
    ("04:00–07:59", time(4, 0), time(7, 59)),
    ("08:00–11:59", time(8, 0), time(11, 59)),
    ("12:00–15:59", time(12, 0), time(15, 59)),
    ("16:00–19:59", time(16, 0), time(19, 59)),
    ("20:00–23:59", time(20, 0), time(23, 59)),
]

def safe_int(val):
    try:
        return int(val)
    except:
        return 0

def delta(values):
    if len(values) >= 2:
        return max(0, values[-1] - values[0])
    return 0

def analyze_file(filepath):
    stats = {label: {"👥": 0, "💰": 0, "👍": 0, "👎": 0, "👤": 0} for label, _, _ in intervals}
    viewers_blocks = defaultdict(list)
    tokens_blocks = defaultdict(list)
    likes_blocks = defaultdict(list)
    dislikes_blocks = defaultdict(list)
    followers_blocks = defaultdict(list)

    with open(filepath, 'r') as file:
        reader = csv.reader(file)
        header = next(reader, None)
        index_map = {col.lower(): i for i, col in enumerate(header)}

        for row in reader:
            try:
                timestamp = datetime.fromisoformat(row[index_map['timestamp']])
                if timestamp.date().isoformat() != today_str:
                    continue
                if row[index_map['status']].strip().upper() != "ONLINE":
                    continue

                viewers = safe_int(row[index_map['num_viewers']])
                tokens = safe_int(row[index_map['token_balance']])
                likes = safe_int(row[index_map['votes_up']])
                dislikes = safe_int(row[index_map['votes_down']])
                followers = safe_int(row[index_map['num_followers']])
            except:
                continue

            t = timestamp.time()
            for label, start, end in intervals:
                if start <= t <= end:
                    viewers_blocks[label].append(viewers)
                    tokens_blocks[label].append(tokens)
                    likes_blocks[label].append(likes)
                    dislikes_blocks[label].append(dislikes)
                    followers_blocks[label].append(followers)
                    break

    for label, _, _ in intervals:
        stats[label]["👥"] = max(viewers_blocks[label]) if viewers_blocks[label] else 0
        stats[label]["💰"] = delta(tokens_blocks[label])
        stats[label]["👍"] = delta(likes_blocks[label])
        stats[label]["👎"] = delta(dislikes_blocks[label])
        stats[label]["👤"] = delta(followers_blocks[label])
    return stats


def export_to_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if not credentials_json:
            raise Exception("Переменная окружения GOOGLE_CREDENTIALS_JSON не установлена.")

        credentials_info = json.loads(credentials_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, scope)
        client = gspread.authorize(creds)
        sh = client.open_by_key(spreadsheet_id)
    except Exception:
        print("❌ Ошибка подключения:")
        traceback.print_exc()
        return

    try:
        ws = sh.worksheet(sheet_title)
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=sheet_title, rows="1000", cols="50")

    accounts = []
    stats_all = {}

    for filename in sorted(os.listdir(log_dir)):
        if filename.endswith(".csv"):
            account = os.path.splitext(filename)[0]
            accounts.append(account)
            stats_all[account] = analyze_file(os.path.join(log_dir, filename))

    existing_rows = ws.get_all_values()
    date_positions = [i for i, row in enumerate(existing_rows) if row and row[0] == today_str]

    if date_positions:
        start_row = max(date_positions) + len(intervals) + 2
    else:
        start_row = len(existing_rows) + 2 if existing_rows else 1

    start_col = 1
    for account in accounts:
        # Название аккаунта сверху
        account_title = [f"🟢 {account}"]
        account_range = gspread.utils.rowcol_to_a1(start_row, start_col)
        ws.update(account_range, [account_title])

        # Заголовок таблицы
        header = ["Дата", "Смена", "👥 Зрители", "💰 Токены", "👍 Лайки", "👎 Дизлайки", "👤 Фолловеры"]
        header_range = gspread.utils.rowcol_to_a1(start_row + 1, start_col)
        ws.update(header_range, [header])

        # Данные по аккаунту
        rows = []
        for label, _, _ in intervals:
            stats = stats_all.get(account, {}).get(label, {"👥": 0, "💰": 0, "👍": 0, "👎": 0, "👤": 0})
            row = [today_str, label, stats["👥"], stats["💰"], stats["👍"], stats["👎"], stats["👤"]]
            rows.append(row)

        data_range = gspread.utils.rowcol_to_a1(start_row + 2, start_col)
        ws.update(data_range, rows)

        start_col += 8  # смещение на следующий аккаунт

    print(f"✅ Данные успешно загружены в '{sheet_title}' с отступом между днями.")


# 🚀 Запуск
if __name__ == "__main__":
    export_to_google_sheets()
