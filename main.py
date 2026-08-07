import os
import requests
import telebot
from bs4 import BeautifulSoup
from urllib.parse import urlparse

BOT_TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)


def get_link4m(alias):
	cookies = {
		'csrfToken': '29ff1df9360de0f1fd3b0d637c33c82158c68d6ff58e19a439fc7341d3100451fb6e79a73b9be603783c3ba22146248d7751517c7bd4823e87518ada0fda4b81',
		'user_id_7247': 'Q2FrZQ%3D%3D.Y2I3NjM2ZTE0NmQzZDEzZTFkZmRlMmVmYmVmZDFmY2RhYTg2NTA2NGRkZmY0ZTgyYmZmNTQ3MGZkMGY5ZDJkYzKhP5dmOrjplRx1HQ%2FqugEVEOFzPo5xT9p5xsHi5xzM1GNqfr6cCYsne88Q0qBe0YI4GnnBDecRxcCL8vZMoDdUr8UuJvSnvx8YSIERVc%2FHuv3sBbuno3XoUm2Gv4hCyZyJHsdma1XyQLuLMeg5gDZNCJDXJ2TTLHAVDEAnShGIjEiZ2lPM4catmsmezv7W22%2FsQS%2F6MI%2B56kcViHBDHyHhz1ScTHoVSvcHZy3bqaY7DMZdoXUePA4AdebDCcr3TXYbZivmcAkFBvwkbPUc3Ptt%2F3sMSiRBUwOmF35Gw9Ai%2FieNRosLm8DkzqfFAQ1x5zBdjglC2EVYcHr4WlzebjI%3D',
	}
	headers = {
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
		'x-csrf-token': '29ff1df9360de0f1fd3b0d637c33c82158c68d6ff58e19a439fc7341d3100451fb6e79a73b9be603783c3ba22146248d7751517c7bd4823e87518ada0fda4b81',
		'x-requested-with': 'XMLHttpRequest',
	}
	params = {
		'alias': alias,  # ID lấy từ url người dùng gửi vào bot
	}
	response = requests.post(
		'https://vuotlink.xyz/links/gosl/',
		params=params,
		cookies=cookies,
		headers=headers,
	)
	data = response.json()
	return data.get('url')


def get_snote_id(link4m_url):
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
	response = requests.get(link4m_url, headers=headers)
	response.raise_for_status()
	soup = BeautifulSoup(response.text, 'html.parser')
	title = soup.find('title')
	if title:
		return title.get_text().split('|')[0].strip()
	return None


def get_snote_content(note_id):
	url = f'https://note2s.im/api/notes/{note_id}'
	
	headers = {
		'User-Agent': 'Mozilla/5.0'
	}
	response = requests.get(url, headers=headers)
	data = response.json()

	note = data.get('note')
	if not note:
		return 'Không tìm thấy nội dung. \nPhiên bản có thể đã cập nhật.'
		
	title = note.get('title') #

	html = note.get('content')
	soup = BeautifulSoup(html, 'html.parser')
	content = soup.a['href'] #
	
	return f'Content:\n{content}\n\nTitle: {title}'

@bot.message_handler(func=lambda m: True)
def handle_message(message):
	vuotlink_url = message.text.strip()  # https://vuotlink.xyz/PvDl -> PvDl là alias
	alias = urlparse(vuotlink_url).path.strip('/')

	link4m_url = get_link4m(alias)
	note_id = get_snote_id(link4m_url)
	result = get_snote_content(note_id)
	bot.reply_to(message, result)

bot.infinity_polling()
