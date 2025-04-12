import requests
import csv
import time
import os
from datetime import datetime

# 🧑‍🤝‍🧑 Аккаунты: username и token
accounts = [
    {"username": "anabel054", "token": "ZCQ7E7j7HCnMvrCZI6PWGZbu"},
    {"username": "kira0541", "token": "EgqLLMoI0KMopWGu8d5wxKlm"},
    {"username": "bright_diamonds_054", "token": "DSEvoKMvfZQv7ck6hcC60IzT"},
    {"username": "sweetdesiree_", "token": "vgnO3gFesv0m9JSnDjgU84u8"},
    {"username": "anabel2054", "token": "q2RNTb4oyusmo3jJvPLnvKtf"},
]

delay_seconds = 5 * 60  # каждые 5 минут
log_dir = "viewer_log"

os.makedirs(log_dir, exist_ok=True)

def init_csv(filepath):
    if not os.path.exists(filepath) or os.stat(filepath).st_size == 0:
        with open(filepath, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                'timestamp',
                'num_viewers',
                'status',
                'token_balance',
                'votes_up',
                'votes_down',
                'num_followers'
            ])

print("⏳ Запущен логгер для нескольких аккаунтов...\n")

while True:
    for acc in accounts:
        try:
            username = acc["username"]
            token = acc["token"]
            url = f'https://chaturbate.com/statsapi/?username={username}&token={token}'
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                timestamp = datetime.now().isoformat()
                time_online = data.get('time_online', -1)

                if time_online == -1:
                    status = "OFFLINE"
                    viewers = "-"
                    token_balance = "-"
                    votes_up = "-"
                    votes_down = "-"
                    followers = "-"
                    print(f"[{timestamp}] {username}: OFFLINE")
                else:
                    status = "ONLINE"
                    viewers = data.get("num_viewers", 0)
                    token_balance = data.get("token_balance", 0)
                    votes_up = data.get("votes_up", 0)
                    votes_down = data.get("votes_down", 0)
                    followers = data.get("num_followers", 0)
                    print(f"[{timestamp}] {username} | 👥 {viewers} | 💰 {token_balance} | 👍 {votes_up} | 👎 {votes_down} | 👤 {followers}")

                log_path = os.path.join(log_dir, f"{username}.csv")
                init_csv(log_path)

                with open(log_path, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        timestamp,
                        viewers,
                        status,
                        token_balance,
                        votes_up,
                        votes_down,
                        followers
                    ])

            else:
                print(f"❌ [{username}] Ошибка {response.status_code}: {response.text}")

        except Exception as e:
            print(f"⚠️ [{username}] Ошибка: {e}")

    print(f"\n⏱ Пауза {delay_seconds // 60} минут...\n")
    time.sleep(delay_seconds)
