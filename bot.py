import telebot as tb
from graph import *
import requests
import dotenv as dt
import os
import random
import pandas as pd
import math

class Button:
    def __init__(self, text: str, transition: str):
        self.text = text
        self.transition = transition

class Menu:
    def __init__(self, buttons: dict[str, Button], text: str):
        self.buttons = buttons
        self.text = text

    def display(self, user_id):
        markup = tb.types.ReplyKeyboardMarkup(resize_keyboard=True)
        for button_inner_name in self.buttons:
            markup.add(tb.types.KeyboardButton(self.buttons[button_inner_name].text))
        bot.send_message(user_id, self.text, reply_markup=markup)

class ButtonsWay:
    task = 0
    choice_button = ''

    def __init__(self, menus: dict[str, Menu], default_menu: str, buttons_mapper: dict[str, str]):
        self.menus = menus
        self.current_menu = {}
        self.default_menu = default_menu
        self.buttons_mapper = buttons_mapper
        ButtonsWay.task = GetTask('0')
        ButtonsWay.choice_button = ''

    def handle_new_user(self, user_id):
        if user_id not in self.current_menu:
            self.current_menu[user_id] = self.default_menu

    def handle_message(self, message):
        user_id = message.from_user.id
        self.handle_new_user(user_id)
        current_menu = self.current_menu[user_id]
        if message.text not in self.buttons_mapper:
            self.menus[current_menu].display(user_id)
            return
        inner_button_name = self.buttons_mapper[message.text]
        if inner_button_name not in self.menus[current_menu].buttons:
            self.menus[current_menu].display(message.from_user.id)
            return
        current_menu = self.menus[current_menu].buttons[inner_button_name].transition
        self.current_menu[user_id] = current_menu
        self.menus[current_menu].display(user_id)

    def get_choice(self, message):
        if self.current_menu[message.from_user.id] == 'random_return' and self.default_menu == 'start_menu':
            ButtonsWay.choice_button = message.text

    def get_task(self, message):
        if self.current_menu[message.from_user.id] == 'random_return' and message.text.isdigit():
            ButtonsWay.task.get_task(message, ButtonsWay.choice_button)
            self.current_menu[message.from_user.id] = 'answer'

    def get_ans(self, message):
        if self.current_menu[message.from_user.id] == 'answer':
            ButtonsWay.task.get_ans(message, ButtonsWay.choice_button)
            self.current_menu[message.from_user.id] = 'random_return'

    def handle_command(self, message):
        self.current_menu = {}
        self.handle_message(message)

    def get_end(self, message):
        self.menus['stat_choice'].display(message.from_user.id)
        self.current_menu[message.from_user.id] = 'stat_choice'

    def get_stat_choice(self, message):
        ButtonsWay.task.get_stat_choice(message)

    def get_delete(self):
        ButtonsWay.task.get_delete()

    def get_stat(self, message, id):
        ButtonsWay.task.get_stat(message, id)

    def settings(self, text):
        ButtonsWay.task.settings(text)

class GetTask:
    count = [[0, 0, 0] for _ in range(27)]
    length = [[0, 0, 0] for _ in range(27)]
    number = 0
    book = ''
    stat = [[0, 0, 0] for _ in range(27)]
    num_stat = [[0, 0, 0] for _ in range(27)]
    good = [[False, False, False] for _ in range(27)]
    id = 0
    num = 0
    pol = '(а)'
    k = 0

    def __init__(self, ans: str):
        self.ans = ans
        GetTask.count = [[0, 0, 0] for _ in range(27)]
        GetTask.length = [[0, 0, 0] for _ in range(27)]
        GetTask.number = 0
        GetTask.book = ''
        GetTask.stat = [[0, 0, 0] for _ in range(27)]
        GetTask.num_stat = [[0, 0, 0] for _ in range(27)]
        GetTask.good = [[False, False, False] for _ in range(27)]
        GetTask.id = 0
        GetTask.num = 0
        GetTask.pol = '(а)'
        GetTask.k = 0

    def settings(self, pol):
        if pol == 'М':
            GetTask.pol = ''
        elif pol == 'Ж':
            GetTask.pol = 'а'
        else:
            GetTask.pol = '(а)'

    def get_stat(self, message, id):
        number = int(message.text)
        if GetTask.num_stat[number - 1][id] != 0:
            bot.send_message(message.from_user.id, f'Ты решил{GetTask.pol} верно {round(GetTask.stat[number - 1][id] / GetTask.num_stat[number - 1][id] * 100, 2)}% задач ({GetTask.stat[number - 1][id]} из {GetTask.num_stat[number - 1][id]})!')
        else:
            bot.send_message(message.from_user.id, 'Пока что ты не решил' + GetTask.pol + ' ни одной задачи.')

    def file(self, format, row, name, f, message):
        bot.send_message(message.from_user.id, 'Пожалуйста, дождись загрузки всех файлов, это может занять несколько секунд! 😌')
        file_link = f[row][GetTask.count[GetTask.number - 1][GetTask.id]]
        response = requests.get(file_link)
        with open(name + format, 'wb') as file:
            file.write(response.content)
        with open(name + format, 'rb') as file:
            bot.send_document(message.from_user.id, document=file)
        os.remove(name + format)

    def book_file(self, command):
        if command == 'Сайт Решу ЕГЭ':
            GetTask.book = 'ege.xlsx'
            GetTask.id = 1
        if command == 'Сайт К.Полякова':
            GetTask.book = 'polyakov.xlsx'
            GetTask.id = 0
        if command == 'Задачи из разных источников':
            GetTask.book = 'random.xlsx'
            GetTask.id = 2

    def get_number(self, num):
        GetTask.number = int(num)
        return GetTask.number

    def get_task(self, message, command):
        self.book_file(command)
        self.get_number(message.text)
        GetTask.number = int(message.text)
        f = pd.read_excel(GetTask.book, dtype=str)
        GetTask.length[GetTask.number - 1][GetTask.id] = f['Task_' + str(GetTask.number)].notnull().sum()
        send_text = f'`{f["Task_" + str(GetTask.number)][GetTask.count[GetTask.number - 1][GetTask.id]]}`'
        bot.send_message(message.from_user.id, send_text, parse_mode='Markdown')
        if 'Photo_' + str(GetTask.number) in f and not (GetTask.book == 'ege.xlsx'):
            row = 'Photo_' + str(GetTask.number)
            file_link = f[row][GetTask.count[GetTask.number - 1][GetTask.id]]
            response = requests.get(file_link)
            bot.send_photo(message.from_user.id, photo=response.content)
        if (GetTask.number == 1 or GetTask.number == 3) and GetTask.book == 'ege.xlsx':
            bot.send_photo(message.from_user.id, open(f['Photo_' + str(GetTask.number)][GetTask.count[GetTask.number - 1][GetTask.id]], 'rb'))
        if GetTask.number == 27:
            format = '.txt'
            name = 'file_A'
            row = 'Link_27_A'
            self.file(format, row, name, f, message)
            name = 'file_B'
            row = 'Link_27_B'
            self.file(format, row, name, f, message)
        if 'Link_' + str(GetTask.number) in f:
            format = '.xls'
            if GetTask.number == 17 or GetTask.number == 24 or GetTask.number == 26:
                format = '.txt'
            if GetTask.number == 10:
                format = '.docx'
            name = 'file'
            row = 'Link_' + str(GetTask.number)
            self.file(format, row, name, f, message)
        self.ans = str(f['Ans_' + str(GetTask.number)][GetTask.count[GetTask.number - 1][GetTask.id]])
        GetTask.count[GetTask.number - 1][GetTask.id] += 1
        if GetTask.count[GetTask.number - 1][GetTask.id] <= GetTask.length[GetTask.number - 1][GetTask.id]:
            GetTask.num_stat[GetTask.number - 1][GetTask.id] += 1

    def get_ans(self, message, command):
        self.book_file(command)
        if str(message.text) != self.ans:
            answer = 'К сожалению, ты неверно решил' + GetTask.pol + ' эту задачу. Вот верный ответ: ' + '\n' + str(self.ans)
            bot.send_message(message.from_user.id, answer)
        else:
            GetTask.stat[GetTask.number - 1][GetTask.id] += 1
            bot.send_message(message.from_user.id, 'Поздравляю! Ты верно решил' + GetTask.pol + ' задачу!!')
        if GetTask.count[GetTask.number - 1][GetTask.id] >= GetTask.length[GetTask.number - 1][GetTask.id]:
            GetTask.good[GetTask.number - 1][GetTask.id] = True
        else:
            bot.send_message(message.from_user.id, 'Выбери номер от 1 до 27')
            GetTask.good[GetTask.number - 1][GetTask.id] = False

    def get_stat_choice(self, message):
        bot.send_message(message.from_user.id, f'Ты решил{GetTask.pol} {GetTask.stat[GetTask.number - 1][GetTask.id] / GetTask.length[GetTask.number - 1][GetTask.id] * 100}% задач ({GetTask.stat[GetTask.number - 1][GetTask.id]} из {GetTask.length[GetTask.number - 1][GetTask.id]})!')

    def get_delete(self):
        GetTask.count[GetTask.number - 1][GetTask.id] = 0
        GetTask.stat[GetTask.number - 1][GetTask.id] = 0
        GetTask.good[GetTask.number - 1][GetTask.id] = False
        GetTask.num_stat[GetTask.number - 1][GetTask.id] = 0
        GetTask.length[GetTask.number - 1][GetTask.id] = 0



@bot.message_handler(commands=['start'])

def get_start(message):
    bot.send_message(message.from_user.id, 'Привет! Я бот, который поможет тебе в подготовке к экзамену! 💻')
    graph.handle_command(message)

@bot.message_handler(content_types=['text'])

def text_handler(message):
    book_id = ''
    num = 0
    if graph.current_menu[message.from_user.id] != 'answer' and graph.current_menu[message.from_user.id] != 'random_return' and graph.current_menu[message.from_user.id] != 'number_stat':
        if message.text not in graph.buttons_mapper:
            bot.send_message(message.from_user.id, 'Хм, я тебя не понимаю( Попробуй еще раз!')
            return
    if not message.text.isdigit() and graph.current_menu[message.from_user.id] != 'answer' and graph.current_menu[message.from_user.id] != 'statistic_watch':
        graph.handle_message(message)
        graph.get_choice(message)
        book_id = graph.choice_button
    graph.task.book_file(book_id)
    id = graph.task.id
    if message.text in graph.buttons_mapper and graph.buttons_mapper[message.text] == 'random':
        graph.task.id = 2
    elif message.text in graph.buttons_mapper and graph.buttons_mapper[message.text] == 'polyakov':
        graph.task.id = 0
    elif message.text in graph.buttons_mapper and graph.buttons_mapper[message.text] == 'decide_ege':
        graph.task.id = 1
    if graph.current_menu[message.from_user.id] == 'start_menu' and message.text in ['М', 'Ж', 'Оставить в секрете']:
        graph.settings(message.text)
    print(graph.current_menu)
    print(message.text)
    if graph.current_menu[message.from_user.id] == 'random_return':
        if message.text.isdigit() and not(1 <= int(message.text) <= 27):
            bot.send_message(message.from_user.id, 'Хм, я тебя не понимаю( Попробуй еще раз!')
            return
        if message.text.isdigit() and graph.task.good[graph.task.number - 1][id] == False:
            graph.get_task(message)
        if message.text.isdigit() and graph.task.good[num - 1][id] == True:
            graph.get_end(message)
    elif graph.current_menu[message.from_user.id] == 'answer':
        graph.get_ans(message)
    num = graph.task.number
    if graph.current_menu[message.from_user.id] == 'number_stat':
        if (message.text.isdigit() and not(1 <= int(message.text) <= 27)):
            bot.send_message(message.from_user.id, 'Хм, я тебя не понимаю( Попробуй еще раз!')
            return
        elif message.text.isdigit():
            graph.get_stat(message, id)
    if graph.current_menu[message.from_user.id] == 'count':
        bot.send_photo(message.from_user.id, photo=open('count.png', 'rb'))
    if message.text not in graph.buttons_mapper and graph.current_menu[message.from_user.id] not in ['choice_delete', 'choice', 'return_stat', 'stat_choice', 'start_menu', 'number_stat'] and graph.task.good[num - 1][id] == True:
        graph.get_end(message)
    if message.text in graph.buttons_mapper and graph.buttons_mapper[message.text] == 'data_delete':
        graph.get_delete()
        graph.task.num = graph.task.number
    if graph.current_menu[message.from_user.id] == 'return_stat':
        graph.get_stat_choice(message)
    if graph.current_menu[message.from_user.id] == 'use':
        bot.send_photo(message.from_user.id, photo=open('for_ege.png', 'rb'))

if __name__ == '__main__':
    bot.polling(none_stop=True)
