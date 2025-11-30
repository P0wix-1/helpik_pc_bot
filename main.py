import telebot
import sqlite3
import conf
import time
from datetime import date

bot = telebot.TeleBot(conf.key)
timer={}
users_id = {}

#user_id
def start():
    us=conf.users+conf.admin
    for a in us:
        timer.setdefault(a,"")
    conn = sqlite3.connect('Quest.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_id")
    result = cursor.fetchall()
    for num in result:
        users_id.setdefault(num[0], num[1])
    conn.commit()
    conn.close()

# Работа с БД
def watch_quests(user):
    if user not in conf.admin+conf.users:
        return "Нет прав"
    conn = sqlite3.connect('Quest.db')
    cursor = conn.cursor()
    cursor.execute("SELECT rowid, * FROM Quest WHERE priority > 0")
    output = cursor.fetchall()
    #cursor.execute("SELECT rowid, * FROM Quest WHERE priority > 0 AND (User = ? or User = '')", (user,))
    conn.commit()
    conn.close()
    result=""
    for i in output:
        if i[4]=='':
            result+=f"{i[0]}) {i[2]}(**{i[1]}**)\n"
        else:
            result+=f"{i[0]}) {i[2]}(**{i[1]}**) - {i[4]}\n"
    return result

def description_quest(num):
    try:
        conn = sqlite3.connect('Quest.db')
        cursor = conn.cursor()
        cursor.execute("SELECT rowid, * FROM Quest WHERE rowid = ?", (int(num),))
        result = cursor.fetchone()
        conn.commit()
        conn.close()
        return f"Имя: {result[2]}\nПриоритет: **{result[1]}**\nВыполняет: **{result[4]}**\nДата: **{result[5]}**\nОписание: {result[3]}"
    except Exception as e:
        print(e)
        return "Заявка не найдена"

def quest_create(quest_text):
    if len(quest_text)!=3 or 0>int(quest_text[0]) or 5<int(quest_text[0]):
        return "Error"
    conn = sqlite3.connect('Quest.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Quest VALUES (?, ?, ?, '', ?)", (int(quest_text[0]), quest_text[1], quest_text[2], str(date.today())))
    cursor.execute("SELECT last_insert_rowid()")
    last=cursor.fetchone()
    if int(quest_text[0])>4:
        if push(last[0]):
            conn.commit()
        else:
            return "Error"
    else:
        conn.commit()
    conn.close()
    return "Complete"

def delete_quest(item):
    try:
        conn = sqlite3.connect('Quest.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Quest WHERE rowid = ?', (item,))
        conn.commit()
        conn.close()
        return "Complete"
    except Exception as e:
        print(e)
        return "Error"

def change_quest(item, arg, value):
    try:
        conn = sqlite3.connect('Quest.db')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE Quest SET {arg} = ? WHERE rowid = ?", (value, item, ))
        conn.commit()
        conn.close()
        return "Complete"
    except Exception as e:
        print(e)
        return "Error"

def push(quest):
    try:
        for username in conf.users:
            bot.send_message(f"{users_id[username]}", f"Срочная заявка под номером {quest}")
        return True
    except Exception as e:
        print(e)
        return False

def user_id(username, userid):
    conn = sqlite3.connect('Quest.db')
    cursor = conn.cursor()
    cursor.execute("SELECT True FROM user_id WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.commit()
        conn.close()
        return "Такой пользователь уже есть в таблице"
    else:
        cursor.execute("INSERT INTO user_id VALUES (?, ?)", (username, userid))
        conn.commit()
        conn.close()
        return "Пользователь добавлен"

def quest_close(num, username):
    try:
        conn = sqlite3.connect('Quest.db')
        cursor = conn.cursor()
        cursor.execute("SELECT User FROM Quest WHERE rowid = ?",(num,))
        if username in cursor.fetchone() or cursor.fetchone()[0]=='':
            cursor.execute(f"UPDATE Quest SET Priority = 0 WHERE rowid = ?", (num,))
            conn.commit()
            conn.close()
        else:
            cursor.close()
            return "Error"
        return "Complete"
    except Exception as e:
        print(e)
        return "Error"


#common func
@bot.message_handler(commands=['start'])
def new(message):
    if message.chat.username in conf.admin:
        user_id(message.chat.username, message.chat.id)
        bot.send_message(message.chat.id, "Админ, вот все заявки:\n" + watch_quests(message.chat.username), parse_mode='Markdown')
    elif message.chat.username in conf.users:
        user_id(message.chat.username, message.chat.id)
        bot.send_message(message.chat.id, "Сотрудник, вот заявки:\n" + watch_quests(message.chat.username), parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "Посетите наш магазин\n" + conf.lint_to_shop)


#Admin func
@bot.message_handler(commands=['new_quest'])
def new_quest(message):
    if message.chat.username not in conf.admin:
        print("Попытка получить доступ к админ функциям")
        return False
    bot.send_message(message.chat.id, "Напишите вашу заявку по образцу(/help):")
    bot.register_next_step_handler(message, new_quest_next)

def new_quest_next(message):
    bot.send_message(message.chat.id, quest_create(message.text.split("\n")))

@bot.message_handler(commands=['delete_quest'])
def delete(message):
    if message.chat.username not in conf.admin:
        print("Попытка получить доступ к админ функциям")
        return False
    bot.send_message(message.chat.id, "Напишите номер заявки:")
    bot.register_next_step_handler(message, delete2)

def delete2(message):
    bot.send_message(message.chat.id, delete_quest(message.text))

@bot.message_handler(commands=['change_priority'])
def change_priority(message):
    if message.chat.username not in conf.admin:
        print("Попытка получить доступ к админ функциям")
        return False
    bot.send_message(message.chat.id, "Напишите номер заявки и новый приоритет('num'-'priority')")
    bot.register_next_step_handler(message, change_priority2)

def change_priority2(message):
    text=message.text
    text=text.split("-")
    if len(text)==2 and (text[1] in ['1','2','3','4','5']):
        bot.send_message(message.chat.id, change_quest(text[0], "priority", text[1]))
    else:
        bot.send_message(message.chat.id, "Error")


#User func
@bot.message_handler(commands=['change_worker'])
def change_worker(message):
    bot.send_message(message.chat.id, "Напишите номер заявки:")
    bot.register_next_step_handler(message, change_worker2)

def change_worker2(message):
    bot.send_message(message.chat.id, change_quest(int(message.text),"User", message.chat.first_name))

@bot.message_handler(commands=['close_quest'])
def close_quest(message):
    bot.send_message(message.chat.id, "Напишите номер заявки:")
    bot.register_next_step_handler(message, close_quest2)

def close_quest2(message):
    bot.send_message(message.chat.id, quest_close(message.text, message.chat.first_name))

@bot.message_handler(commands=['check_in'])
def close_quest(message):
    user_time=0
    if timer[message.chat.username]=="":
        timer[message.chat.username].append(time.localtime())
        bot.send_message(message.chat.id, "Вы отмечены, удачной работы")
    else:
        user_time=timer[message.chat.username]-time.localtime()

@bot.message_handler(content_types=['text'])
def description(message):
    bot.send_message(message.chat.id, description_quest(message.text), parse_mode='Markdown')

if __name__=="__main__":
    start()

bot.polling()