# -*- coding: utf-8 -*-
import telebot
from django.conf import settings

from survey.questions import QUESTIONS
from .models import Respondent

bot = telebot.TeleBot(settings.TOKEN, num_threads=5)
number_of_questions = len(QUESTIONS)
start_command = "/start"
survey_command = "survey"
restart_command = "restart"
finish_command = "finish"
no_command = "tidak"

@bot.message_handler()
def handler(message):
    registrant, _ = Respondent.objects.get_or_create(
        user_id=message.from_user.id,
        defaults={
            "first_name": message.from_user.first_name or "",
            "last_name": message.from_user.last_name or "",
            "username": message.from_user.username or "",
        }
    )

    response = registrant.responses.filter(completed=False).last()
    if not response:
        if message.text in [survey_command, restart_command]:
            response = registrant.responses.create()
            return survey_handler(message, response, registrant)
        else:
            return unknown_replay(message)
    else:
        if message.text == "Tidak":
            response.completed = True
            response.save(update_fields=["completed"])
            bot.send_message(message.from_user.id, "Terima kasih untuk tidak mengikuti survey, anda pasti akan menyesal seumur hidup anda \U0001F609", reply_markup=markup_choices([], message))
        else:
            return survey_handler(message, response, registrant)

def unknown_replay(message):
    print(message)
    if message.text == "/start":
        bot.send_message(message.from_user.id, "Salamt kenal, saya Bot yang menguntungkan kinerja mamas iqbal \U0001F602", reply_markup=markup_choices([], message))
    elif message.text == "finish":
        bot.send_message(message.from_user.id, "Terima kasih untuk duah mengikuti survey yang sebenarnya tidak jelas ini, anda pasti akan bahagia tujuh turunan \U0001F607", reply_markup=markup_choices([], message))
    else:
        bot.send_message(message.from_user.id, "Yuk bantu Monica biar paham yang kamu maksud yah \U0001F60A", reply_markup=markup_choices([], message))

def survey_handler(message, response, registrant):
    if number_of_questions >= response.step >= 1:
        prev_question = QUESTIONS[response.step - 1]["text"]
        response.details[prev_question] = message.text
        response.save(update_fields=["details"])

    if response.step >= number_of_questions:
        response.completed = True
        response.save(update_fields=["completed"])
        bot.send_message(
            registrant.user_id,
            "oke ulangi survey",
            reply_markup=markup_choices([restart_command, finish_command], message)
        )
        return

    question = QUESTIONS[response.step]
    text = question["text"]
    choices = question.get("choices") or []

    bot.send_message(registrant.user_id, text, reply_markup=markup_choices(choices, message))

    response.step += 1
    response.save(update_fields=["step"])

def markup_choices(choices, message):
    if not choices or message.text == 'finish':
        return telebot.types.ReplyKeyboardRemove(selective=False)

    markup = telebot.types.ReplyKeyboardMarkup(True, False)
    for choice in choices:
        markup.add(telebot.types.KeyboardButton(choice))

    return markup