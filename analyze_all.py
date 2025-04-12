import csv
import os
from datetime import datetime, time, date
from collections import defaultdict

log_dir = "viewer_log"
today_str = date.today().isoformat()

intervals = [
    (time(0, 0), time(3, 59)),
    (time(4, 0), time(7, 59)),
    (time(8, 0), time(11, 59)),
    (time(12, 0), time(15, 59)),
    (time(16, 0), time(19, 59)),
    (time(20, 0), time(23, 59)),
]

def safe_int(val):
    try:
        return int(val)
    except:
        return None

def delta_positive(values):
    """Только положительное изменение"""
    if len(values) >= 2:
        return max(0, values[-1] - values[0])
    return 0

def delta_any(values):
    """Любое изменение (может быть отрицательным)"""
    if len(values) >= 2:
        return values[-1] - values[0]
    return 0

def analyze_file(filepath):
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

                if None in (viewers, tokens, likes, dislikes, followers):
                    continue
            except:
                continue

            t = timestamp.time()
            for start, end in intervals:
                if start <= t <= end:
                    label = f"{start.strftime('%H:%M')}–{end.strftime('%H:%M')}"
                    viewers_blocks[label].append(viewers)
                    tokens_blocks[label].append(tokens)
                    likes_blocks[label].append(likes)
                    dislikes_blocks[label].append(dislikes)
                    followers_blocks[label].append(followers)
                    break

    result = {}
    for start, end in intervals:
        label = f"{start.strftime('%H:%M')}–{end.strftime('%H:%M')}"
        result[label] = {
            "viewers": max(viewers_blocks[label]) if viewers_blocks[label] else 0,
            "earned_tokens": delta_positive(tokens_blocks[label]),
            "likes": delta_positive(likes_blocks[label]),
            "dislikes": delta_positive(dislikes_blocks[label]),
            "followers": delta_any(followers_blocks[label]),
        }
    return result

# 🖨️ Печать результата
print(f"📊 Сводка за {today_str} (только ONLINE):")
print("===============================================================")
for filename in os.listdir(log_dir):
    if not filename.endswith('.csv'):
        continue
    filepath = os.path.join(log_dir, filename)
    account = os.path.splitext(filename)[0]
    result = analyze_file(filepath)
    print(f"\n🟢 {account}")
    for label, data in result.items():
        print(
            f"{label} | 👥 Зрителей: {data['viewers']} | 💰 Токены: {data['earned_tokens']} | "
            f"👍 Лайков: {data['likes']} | 👎 Дизлайков: {data['dislikes']} | 👤 Фолловеров: {data['followers']}"
        )
