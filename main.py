import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler, ConversationHandler
import json
from random import shuffle

import requests

from flask import Flask
from data import db_session
from data.students import Student
from data.teachers import Teacher
from data.toddlers import Teacher_toddler
from data.tests import Teacher_test
from sqlalchemy import select


TOKEN = 'token'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

'''начало работы'''


async def start(update, context):
    reply_keyboard = [['учитель', 'ученик']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text('начинаем работу! вы учитель или ученик?', reply_markup=markup)
    return 1


async def choose(update, context):  # 1
    if update.message.text.lower() == 'учитель':
        context.user_data['who'] = 'teacher'
        reply_keyboard = [['/create_test', '/add_student', '/get_answers']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text('выберите, что хотите сделать.', reply_markup=markup)
        return ConversationHandler.END
    elif update.message.text.lower() == 'ученик':
        context.user_data['who'] = 'student'
        reply_keyboard = [['/solve_test']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text('вы ученик. сейчас вы можете проходить тесты', reply_markup=markup)
        print('student')
        return ConversationHandler.END
    else:
        await update.message.reply_text('введите корректно')
        return 1


'''начало блока учителя'''


async def create_test(update, context):
    if context.user_data['who'] == 'teacher':
        await update.message.reply_text('введите название теста.', reply_markup=ReplyKeyboardRemove())
        return 1
    else:
        await update.message.reply_text('вы не учитель')


async def teacher_first(update, context):  # 1 принимаем название теста
    context.user_data['filename'] = update.message.text
    # Сохраняем учителя в бд
    # Потом сохраняем тест учителю

    teacher = Teacher()
    teacher.username = update.effective_user.username

    test_name = context.user_data["filename"]
    test = Teacher_test(name=test_name)

    db_sess = db_session.create_session()
    exists = db_sess.query(Teacher.id).filter_by(username=teacher.username).first() is not None
    if not exists:
        db_sess.add(teacher)

    _teacher = db_sess.query(Teacher).filter(Teacher.username == teacher.username).first()
    _teacher.tests.append(test)
    db_sess.commit()
    await update.message.reply_text('введите количество вопросов')
    return 2


async def teacher_second(update, context):  # 2 создаем пустой список из словарей вопросов-ответов
    context.user_data['current_question'] = 0
    context.user_data['questions'] = [{'question': None, 'correct': None, 'picture': None} for i in
                                      range(int(update.message.text))]
    await update.message.reply_text('введите текст первого вопроса')
    print(context.user_data['questions'])
    return 3


async def teacher_third(update, context):  # 3 принимаем вопрос, записываем в user_data
    context.user_data['questions'][context.user_data['current_question']]['question'] = update.message.text
    print(context.user_data['questions'])
    await update.message.reply_text(
        'если в этом вопросе будет картинка, введите да.\nесли нет, введите правильный ответ на этот вопрос')
    return 4


async def teacher_four(update, context):  # 4 принимаем правильный ответ, записываем в user_data
    if update.message.text.lower() == 'да':
        return 5
    context.user_data['questions'][context.user_data['current_question']]['correct'] = update.message.text
    print(context.user_data['questions'])
    context.user_data['current_question'] += 1

    if context.user_data['current_question'] >= len(context.user_data['questions']):  # завершаем и сохраняем в json
        await update.message.reply_text('сохраняем ваш тест...')
        with open(f'bot_tests/{context.user_data["filename"]}.json', 'w', encoding='utf-8') as file:
            json.dump({"test": context.user_data['questions']}, file, ensure_ascii=False)
        await update.message.reply_text('ваш тест сохранен. можете создать ещё один, начав работу с ботом заново.')
        print(context.user_data)
        return ConversationHandler.END
    else:  # продолжаем принимать вопросы
        await update.message.reply_text(f'введите текст вопроса {context.user_data["current_question"] + 1}')
        return 3


async def getting_photo(update, context):  # 5 загрузка фото
    file = (await context.bot.get_file(update.message.photo[-1]))
    with open(f"bot_tests/pictures/{context.user_data['filename']}{context.user_data['current_question']}.jpg",
              'wb') as f:
        with requests.get(file.file_path) as response:
            f.write(response.content)
        print(context.user_data)
        context.user_data['questions'][context.user_data['current_question']]['picture'] = True
    print('getting photo..')
    return 4


async def add_student(update, context):  # как добавить ученика в бд
    await update.message.reply_text('введите username ученика и его фамилию')
    return 1


async def first(update, context):
    username, surname = update.message.text.split()
    # context.user_data[f'{username}'] = surname
    # Сохраняем учителя в бд
    # Потом сохраняем тест учителю

    teacher = Teacher()
    teacher.username = update.effective_user.username

    toddler_name = surname
    toddler = Teacher_toddler(name=toddler_name)

    db_sess = db_session.create_session()
    exists = db_sess.query(Teacher.id).filter_by(username=teacher.username).first() is not None
    if not exists:
        db_sess.add(teacher)

    _teacher = db_sess.query(Teacher).filter(Teacher.username == teacher.username).first()
    _teacher.toddlers.append(toddler)
    db_sess.commit()

    return ConversationHandler.END


async def get_answers(update, context):
    if context.user_data['who'] == 'teacher':
        await update.message.reply_text('посмотрим ответы. введите название теста.')
        # смотрим ответы...
        return 1


async def get_answers1(update, context):
    test_file_name = update.message.text
    teacher_username = update.effective_user.username

    db_sess = db_session.create_session()
    teacher = db_sess.query(Teacher).filter(Teacher.username == teacher_username).first()
    print(teacher, teacher.toddlers)
    for toddler in teacher.toddlers:
        name = toddler.name
        print(name, test_file_name)
        res = db_sess.query(Student.points).filter_by(test=test_file_name, surname=name).first()
        if res is not None:
            # print(name, res)
            await update.message.reply_text(name + ' ' + str(res))
        else:
            await update.message.reply_text('не найдено(')
    db_sess.commit()
    return ConversationHandler.END


'''здесь начало блока ученика'''


async def solve_test(update, context):  # начало ученика
    print('starting')
    if context.user_data['who'] == 'student':
        await update.message.reply_text('введите вашу фамилию', reply_markup=ReplyKeyboardRemove())
        return 0
    else:
        await update.message.reply_text('вы не ученик')
        return ConversationHandler.END


async def register(update, context):
    surname = update.message.text
    context.user_data['surname'] = surname
    await update.message.reply_text('теперь введите название теста')
    return 1


async def student_first(update, context):  # открываем файл с тестом, перемешиваем вопросы
    file_name = update.message.text
    user_s_surname = context.user_data['surname']
    db_sess = db_session.create_session()
    exists = db_sess.query(Student.id).filter_by(surname=user_s_surname, test=file_name).first() is not None
    if exists:
        # проверка, если он проходил этот тест
        await update.message.reply_text('вы уже проходили этот тест')
        return ConversationHandler.END
    else:
        try:
            with open(f'bot_tests/{file_name}.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            context.user_data['data'] = data
            context.user_data['fname'] = file_name
            print(data)
            context.user_data['order'] = list(range(len(data['test'])))
            shuffle(context.user_data['order'])
            context.user_data['now'] = 0
            context.user_data['count'] = 0
            await update.message.reply_text(
                f"первый вопрос: {context.user_data['data']['test'][context.user_data['order'][context.user_data['now']]]['question']}")
            if context.user_data['data']['test'][context.user_data['order'][context.user_data['now']]]['picture']:
                fname = context.user_data['fname'] + str(context.user_data['order'][context.user_data['now']])
                await context.bot.send_photo(chat_id=update.effective_chat.id,
                                             photo=open(f'bot_tests/pictures/{fname}.jpg', 'rb'))
            return 2

        except Exception as e:
            print(e)
            await update.message.reply_text('ошибка. введите заново')
            return 1


async def student_second(update, context):  # проверяем правильность ответа
    if update.message.text == context.user_data['data']['test'][context.user_data['order'][context.user_data['now']]][
        'correct']:
        context.user_data['count'] += 1
    context.user_data['now'] += 1
    if context.user_data['now'] >= len(context.user_data['data']['test']):
        await update.message.reply_text(f"ваш счет {context.user_data['count']}")
        return ConversationHandler.END
    await update.message.reply_text(f"следующий вопрос\n"
                                    f"""{context.user_data['data']['test'][context.user_data['order']
                                    [context.user_data['now']]]['question']}""")
    if context.user_data['data']['test'][context.user_data['order'][context.user_data['now']]]['picture']:
        fname = context.user_data['fname'] + str(context.user_data['order'][context.user_data['now']])
        await context.bot.send_photo(chat_id=update.effective_chat.id,
                                     photo=open(f'bot_tests/pictures/{fname}.jpg', 'rb'))
    return 2


async def stop(update, context):
    await update.message.reply_text("вы вышли из диалога командой /stop")
    return ConversationHandler.END


def main():
    db_session.global_init("db/blogs.db")
    application = Application.builder().token(TOKEN).build()

    start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    application.add_handler(start_handler)

    creating_handler = ConversationHandler(
        entry_points=[CommandHandler('create_test', create_test)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, teacher_first)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, teacher_second)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, teacher_third)],
            4: [MessageHandler(filters.TEXT & ~filters.COMMAND, teacher_four)],
            5: [MessageHandler(filters.PHOTO, getting_photo)]
        },

        fallbacks=[CommandHandler('stop', stop)])
    application.add_handler(creating_handler)

    adding_student_handler = ConversationHandler(
        entry_points=[CommandHandler('add_student', add_student)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first)]
        },

        fallbacks=[CommandHandler('stop', stop)])
    application.add_handler(adding_student_handler)

    getting_answers = ConversationHandler(
        entry_points=[CommandHandler('get_answers', get_answers)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_answers1)],
        },

        fallbacks=[CommandHandler('stop', stop)])
    application.add_handler(getting_answers)

    student_handler = ConversationHandler(
        entry_points=[CommandHandler('solve_test', solve_test)],

        states={
            0: [MessageHandler(filters.TEXT & ~filters.COMMAND, register)],
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, student_first)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, student_second)],
        },

        fallbacks=[CommandHandler('stop', stop)])
    application.add_handler(student_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
