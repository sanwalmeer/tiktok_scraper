import random
import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime


class TikTokScraper:
    def __init__(self):
        pass

    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")

    def initialize_browser(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--mute-audio")
            chrome_options.add_argument("--disable-audio")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--window-size=1920,1080")

            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            ]
            chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")

            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            return driver
        except Exception as e:
            self.log_message(f"Error initializing browser: {e}")
            return None

    def random_delay(self, min_delay=1, max_delay=3):
        time.sleep(random.uniform(min_delay, max_delay))

    def scroll_to_load_more(self, driver):
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.random_delay(2, 4)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def scrape_tiktok(self, driver, keywords, target_count):
        video_urls = []
        try:
            clean_keywords = keywords.replace(' ', '%20')
            search_url = f"https://www.tiktok.com/search?q={clean_keywords}"
            driver.get(search_url)
            self.random_delay(4, 6)
            self.scroll_to_load_more(driver)

            selectors = ['//a[contains(@href, "/video/")]']
            for selector in selectors:
                videos = driver.find_elements(By.XPATH, selector)
                for video in videos:
                    url = video.get_attribute("href")
                    if url and "tiktok.com" in url and url not in video_urls:
                        video_urls.append(url)
                        if target_count and len(video_urls) >= target_count:
                            break
                if target_count and len(video_urls) >= target_count:
                    break
        except Exception as e:
            self.log_message(f"TikTok scraping failed: {e}")
        return video_urls

    def save_to_json(self, keyword, urls):
        safe_keyword = keyword.replace(" ", "_")
        filename = f"tiktok_results_{safe_keyword}.json"
        output = {
            "keyword": keyword,
            "urls": urls
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4)
        print(f"\n Saved {len(urls)} URLs to '{filename}'")

    def run(self):
        keywords = input("Enter the keywords to search: ")
        count_input = input("Enter number of TikTok URLs to scrape (leave blank for unlimited): ")
        count = int(count_input) if count_input else None

        print(f"\n[INFO] Scraping TikTok for: '{keywords}'")
        driver = self.initialize_browser()
        if not driver:
            self.log_message("Failed to start browser")
            return

        urls = self.scrape_tiktok(driver, keywords, count)
        driver.quit()

        if urls:
            self.save_to_json(keywords, urls)
        else:
            print("❌ No URLs found.")


if __name__ == "__main__":
    scraper = TikTokScraper()
    scraper.run()
