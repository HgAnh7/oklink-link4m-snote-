import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException
import telebot

BOT_TOKEN = 'TOKEN'
bot = telebot.TeleBot(BOT_TOKEN, skip_pending=True)

XPATH = '/html/body/div/div/div/center/div[1]/div/a'

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

# ── Bước 1: Lấy link4m ──────────────────────────────────────────
def get_link4m(oklink_url):
    driver = create_driver()
    wait = WebDriverWait(driver, 10)
    try:
        driver.get(oklink_url)
        while True:
            try:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, XPATH)))
                try:
                    button.click()
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click()", button)

                wait.until(EC.url_changes(driver.current_url))
                current_url = driver.current_url

                if "link4m.com/go/" in current_url:
                    return current_url

                driver.execute_script("window.history.back()")
                wait.until(EC.element_to_be_clickable((By.XPATH, XPATH)))

            except StaleElementReferenceException:
                continue
    finally:
        driver.quit()

# ── Bước 2: Lấy mã snote từ link4m ─────────────────────────────
def get_snote_id(link4m_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(link4m_url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('title')
    if title:
        return title.get_text().split('|')[0].strip()
    return None

# ── Bước 3: Lấy nội dung snote ──────────────────────────────────
def get_snote_content(note_id):
    url = f'https://snote.vip/notes/{note_id}'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    note_time = soup.find('h5')
    time_text = note_time.get_text().strip() if note_time else 'Không rõ thời gian.'

    content_tag = soup.find('p')
    if content_tag:
        content = content_tag.get_text().strip()
        if content and content != '/':
            return f'Nội dung:\n{content}\n\nThời gian: {time_text}'
        else:
            return f'Note chưa sẵn sàng hoặc hết hạn.\nThời gian: {time_text}'
    return 'Không tìm thấy nội dung.'

# ── Handler Telegram ─────────────────────────────────────────────
@bot.message_handler(func=lambda msg: 'oklink.cfd' in msg.text)
def handle_oklink(message):
    url = message.text.strip()
    waiting_msg = bot.reply_to(message, '⏳ Đang xử lý, vui lòng chờ...')
    try:
        link4m_url = get_link4m(url)
        if not link4m_url:
            bot.delete_message(message.chat.id, waiting_msg.message_id)
            bot.reply_to(message, '❌ Không tìm được link4m.')
            return

        snote_id = get_snote_id(link4m_url)
        if not snote_id:
            bot.delete_message(message.chat.id, waiting_msg.message_id)
            bot.reply_to(message, f'❌ Không lấy được mã snote từ:\n{link4m_url}')
            return

        content = get_snote_content(snote_id)
        bot.delete_message(message.chat.id, waiting_msg.message_id)
        bot.reply_to(message, content)

    except Exception as e:
        bot.delete_message(message.chat.id, waiting_msg.message_id)
        bot.reply_to(message, f'❌ Lỗi: {str(e)}')
        
bot.infinity_polling()
