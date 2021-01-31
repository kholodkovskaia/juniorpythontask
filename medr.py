#!/usr/bin/env python3

import os
import datetime
import json
import requests

# Получение задач пользоватей
def get_user_tasks(id):
    try:
        response = requests.get("https://json.medrating.org/todos")
    except (requests.exceptions.RequestException):
        print("Пожалуйста, проверьте подключение к сети!")
    tasks = response.json()
    user_tasks = "[ "
    for task in tasks:
        if "userId" in task:
            if task["userId"] == id:
                user_tasks += json.dumps(task) + ","
    user_tasks = user_tasks[:-1] + "]"
    return json.loads(user_tasks)


# Получение завершенных и оставшихся задач
def get_completed_tasks(completed, tasks):
    completed_tasks = "[ "
    for task in tasks: 
        if task["completed"] == completed:
            if len(task["title"]) > 48 :
                task["title"] = task["title"][:48] + "..."
            completed_tasks += json.dumps(task) + ","
    completed_tasks = completed_tasks[:-1] + "]"
    return json.loads(completed_tasks)


# Создание папки tasks
def make_folder():
    if not os.path.exists('tasks'):
        os.mkdir("tasks") 
        

# Проверка на наличие файла	
def check_file(user, current_time):
    if os.path.isfile("tasks/" + user["username"] + ".txt"):			
        old_file = os.path.realpath("tasks/" + \
                                    user["username"] + ".txt")
        new_file_date = current_time.strftime('%Y-%m-%d') + "T"+ \
                        current_time.strftime('%H-%M')
        new_file = os.path.realpath("tasks/old_" + user["username"] + \
                                    "_" + new_file_date + ".txt")
        try:
            os.rename(old_file, new_file)
        except:
            print("Пожалуйста, запустите скрипт еще раз через минуту!")


# Разбор пользовательских данных
def parse_data(user, current_time):
    if "company" in user and "name" in user["company"]:
        data  = "Отчёт для " + user["company"]["name"] + ".\n"
    else:
        data = "У пользователя не указана компания, в которой он работает.\n"
    if "name" in user:
        data += user["name"]
    else:
        data += "У пользователя не указано его полное имя.\n"
    if "email" in user:
        data += " <" + user["email"] + "> "
    else:
        data += "<У пользователя не указан email>"
    data += current_time.strftime('%d.%m.%Y %H:%M') + "\n"
    tasks = get_user_tasks(user["id"])
    if len(tasks) > 0:
        data += "Всего задач: " + str(len(tasks)) + "\n\n"
        completed_tasks = get_completed_tasks(True, tasks)
        uncompleted_tasks = get_completed_tasks(False, tasks)
        data += "Завершённые задачи (" + str(len(completed_tasks)) + "):\n"
        for task in completed_tasks:
            data+= task["title"] + "\n"
        data += "\nОставшиеся задачи (" + str(len(uncompleted_tasks)) + "):\n"
        for task in uncompleted_tasks:
            data += task["title"] + "\n"
    else:
        print("У пользователя нет задач")
    return data


# Запись на диск
def write_to_disk(user, data):
    try:
        with open("tasks/" + user["username"] + ".txt", 'w',
                  encoding="utf-8") as f:
            f.write(data)
            f.close()
    except IOError:
        print ("Произошла ошибка при записи на диск!")


# Главная функция
def main():
    try:
        response = requests.get("https://json.medrating.org/users")
    except (requests.exceptions.RequestException ):
        print("Пожалуйста, проверьте подключение к сети!")
    make_folder()
    users = response.json()
    current_time = datetime.datetime.now()
    for user in users:
        if "username" in user:
            check_file(user, current_time)
            data = parse_data(user, current_time)
            write_to_disk(user, data)

main()