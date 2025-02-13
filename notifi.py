import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import os
from typing import List, Dict

# Configuration
class Config:
    URL = "https://www.new.ggu.ac.in/notifications/3/0/"
    STORAGE_FILE = "notifications_data.json"
    CACHE_FILE = "last_processed.json"
    TELEGRAM_BOT_TOKEN = "7605032829:AAGflMyQvUA0cMHfks_YmyUP2hNwoXGt570"
    TELEGRAM_CHANNEL_ID = "-1002387146666"
    CHECK_INTERVAL = 300  # 5 minutes
    MAX_NOTIFICATIONS = 5

class NotificationBot:
    def __init__(self):
        self.config = Config()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})
        
    def _load_cache(self) -> List[str]:
        """Load previously processed notification IDs"""
        try:
            if os.path.exists(self.config.CACHE_FILE):
                with open(self.config.CACHE_FILE, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading cache: {e}")
            return []

    def _save_cache(self, processed_ids: List[str]):
        """Save processed notification IDs"""
        try:
            with open(self.config.CACHE_FILE, 'w') as f:
                json.dump(processed_ids, f)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def scrape_notifications(self) -> List[Dict]:
        """Scrape latest notifications"""
        try:
            response = self.session.get(self.config.URL)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            table = soup.find("table", class_="table")
            if not table:
                raise ValueError("Notification table not found")

            notifications = []
            rows = table.find_all("tr")[1:self.config.MAX_NOTIFICATIONS + 1]

            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 4:
                    continue

                notification = {
                    "id": cols[0].text.strip(),
                    "title": cols[1].text.strip(),
                    "date": cols[2].text.strip(),
                    "link": cols[3].find("a")["href"].strip() if cols[3].find("a") else "No Link"
                }
                
                # Make relative URLs absolute
                if notification["link"].startswith("/"):
                    notification["link"] = f"https://www.new.ggu.ac.in{notification['link']}"
                
                notifications.append(notification)

            return notifications

        except Exception as e:
            print(f"Error scraping notifications: {e}")
            return []

    def send_telegram_message(self, message: str):
        """Send message to Telegram channel"""
        try:
            url = f"https://api.telegram.org/bot{self.config.TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": self.config.TELEGRAM_CHANNEL_ID,
                "text": message,
                "parse_mode": "HTML"
            }
            response = self.session.post(url, json=payload)
            response.raise_for_status()
        except Exception as e:
            print(f"Error sending Telegram message: {e}")

    def format_notification(self, notification: Dict) -> str:
        """Format notification for Telegram message"""
        return (
            f"🔔 <b>New Notification</b>\n\n"
            f"<b>{notification['title']}</b>\n"
            f"📅 Date: {notification['date']}\n"
            f"🔗 <a href='{notification['link']}'>View Document</a>"
        )

    def run(self):
        """Main bot loop"""
        print("Starting notification bot...")
        processed_ids = self._load_cache()

        while True:
            try:
                print(f"Checking for new notifications at {datetime.now()}")
                notifications = self.scrape_notifications()
                
                # Process only new notifications
                new_notifications = [n for n in notifications if n["id"] not in processed_ids]
                
                if new_notifications:
                    print(f"Found {len(new_notifications)} new notifications")
                    
                    # Send newest notifications first
                    for notification in reversed(new_notifications):
                        message = self.format_notification(notification)
                        self.send_telegram_message(message)
                        processed_ids.append(notification["id"])
                        time.sleep(1)  # Avoid hitting Telegram API limits
                    
                    # Keep only the latest MAX_NOTIFICATIONS IDs in cache
                    processed_ids = processed_ids[-self.config.MAX_NOTIFICATIONS:]
                    self._save_cache(processed_ids)
                else:
                    print("No new notifications found")

                time.sleep(self.config.CHECK_INTERVAL)

            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(60)  # Wait a minute before retrying on error

if __name__ == "__main__":
    bot = NotificationBot()
    bot.run()