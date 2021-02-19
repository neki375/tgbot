import os
import json
import urllib3
import telebot
import requests
from globals import conf
from datetime import datetime


conf = conf()
urllib3.disable_warnings()
weather_token = conf["weather_token"]
telegram_token = conf["telegram_token"]
money_token = conf["money_token"]
keyboard1 = telebot.types.ReplyKeyboardMarkup()
bot = telebot.TeleBot(telegram_token)



def date_format(time):
	dt_object = datetime.fromtimestamp(time)
	return dt_object.strftime("%H:%M:%S")


def get_course_of_money(money_token, value1, count:int, value2="RUB"):
	print("{}{}{}".format(value1, count, value2))
	count = int(count)
	money_url= "https://currate.ru/api/?get=rates&pairs={}&key={}".format("{}{}".format(value1, value2), money_token)
	http = urllib3.PoolManager()
	res = requests.get(money_url, verify=False)
	data = res.json()
	info = {}
	if len(data["data"]) > 0:
		for k,v in data["data"].items():
			info["name"] = k
			info["value"] = float(v) * count if count else v
		if count:
			if count >= 1:
				return "В {} {} {} рублей".format(count, value1, info["value"])
		else:
			return "В 1 {} {} рублей".format(value1, info["value"])
	return "К сожалению у меня нет курса этой валюты или валюта не существует"


def get_details(data):
	temp = data["main"]["temp"]
	feels_temp = data["main"]["feels_like"]
	weather = data["weather"][0]["description"]
	wind = data["wind"]["speed"]
	sunrise = date_format(data["sys"]["sunrise"])
	sunset = date_format(data["sys"]["sunset"])
	return {
		"temp": temp,
		"feels_temp": feels_temp,
		"weather": weather,
		"wind": wind,
		"sunrise": sunrise,
		"sunset": sunset
	}


def get_weather(weather_token, city):
	print(city)
	weather_url = "http://api.openweathermap.org/data/2.5/weather?q={city}&lang=ru&appid={weather_token}&units=metric".format(
		city=city, 
		weather_token=weather_token
	)
	res = requests.get(weather_url)
	data = res.json()
	print(data)
	if "message" in data:
		return "Такого города не существует"
	details = get_details(data)
	info = "В городе {} сейчас {}° \nОщущается как {}° \n{}\nСкорость ветра {} м/с\nВосход солнца в {}\nЗакат в {}".format(
		city.capitalize(),
		details["temp"],
		details["feels_temp"],
		details["weather"].capitalize(),
		details["wind"],
		details["sunrise"],
		details["sunset"]

	)

	return info


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, введи имя города в котором тебя интересует погода например Москва')
    bot.send_message(message.chat.id, 'Или валюту чтобы узнать ее курс к рублю например USD или USD 20 где 20 это количество USD')
    bot.send_message(message.chat.id, 'Хочешь пасхалку?? Напиши боту путин')


# @bot.message_handler(commands=['list'])
# def start_message(message):
#     bot.send_message(message.chat.id, 'Список доступных валют можно посмотреть здесь {}')


@bot.message_handler(content_types=['text'])
def send_text(message):
	if message.text.lower() == 'путин':
		print(message.text.lower())
		bot.send_sticker(message.chat.id, 'CAADAgADZgkAAnlc4gmfCor5YbYYRAI')
	else:
		if len(message.text.split()) < 2 and len(message.text) > 3:
			info = get_weather(weather_token, message.text)
			bot.send_message(message.chat.id, "{}".format(info))
		else:
			if len(message.text.split()) >= 2:
				string = message.text.split()
				try:
					string[1] = int(string[1])
				except Exception as e:
					bot.send_message(message.chat.id, "{}".format("{} не является числом".format(string[1])))
					return
				value = get_course_of_money(money_token, string[0], string[1])
				bot.send_message(message.chat.id, "{}".format(value))
			
			else:
				value = get_course_of_money(money_token, message.text, count=1)
				bot.send_message(message.chat.id, "{}".format(value))


@bot.message_handler(content_types=['sticker'])
def sticker_id(message):
    print(message)


if __name__ == "__main__":
	bot.polling()
