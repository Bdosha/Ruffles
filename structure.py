from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)

d = InlineKeyboardButton(
    text='',
    callback_data='')
datetime_pattern = r'^(0[1-9]|[1-2][0-9]|3[0-1])-(0[1-9]|1[0-2])-202\d{1} (2[0-3]|[0-1][0-9]):([0-5][0-9])$'

make_raffle = KeyboardButton(text='🆕 Создать розыгрыш')
active_raffles = KeyboardButton(text='🎁 Розыгрыши')
sponsors = KeyboardButton(text='💸 Для спонсоров')

admin = ReplyKeyboardMarkup(
    keyboard=[[active_raffles, sponsors], [make_raffle]],
    resize_keyboard=True)
user = ReplyKeyboardMarkup(
    keyboard=[[active_raffles, sponsors]],
    resize_keyboard=True)

back = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='⬅️ Выйти')]],
    resize_keyboard=True)

daily_admin = KeyboardButton(
    text='📅 Ежедневный')

sponsor_admin = KeyboardButton(
    text='💸 Спонсорский')

raffle_chouse_admin = ReplyKeyboardMarkup(keyboard=[[daily_admin], [sponsor_admin]],
                                          resize_keyboard=True)

daily_user = InlineKeyboardButton(
    text='📅 Активные розыгрыши',
    callback_data='daily_raffle')

sponsor_user = InlineKeyboardButton(
    text='💸 Спонсорские розыгрыши',
    callback_data='spons_raffle')

raffle_chouse_user = InlineKeyboardMarkup(inline_keyboard=[[daily_user], [sponsor_user]])

spons_uch = InlineKeyboardButton(
    text='Участвовать',
    callback_data='spons_uch')

spons_end = InlineKeyboardButton(
    text='Завершить',
    callback_data='spons_end')

end_key_spons = InlineKeyboardMarkup(inline_keyboard=[[spons_uch], [spons_end]])
key_spons = InlineKeyboardMarkup(inline_keyboard=[[spons_uch]])

daily_uch = InlineKeyboardButton(
    text='Участвовать',
    callback_data='daily_uch')

daily_end = InlineKeyboardButton(
    text='Завершить',
    callback_data='daily_end')
end_key_daily = InlineKeyboardMarkup(inline_keyboard=[[daily_uch], [daily_end]])
key_daily = InlineKeyboardMarkup(inline_keyboard=[[daily_uch]])

fake_uch = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
    text='Участвовать',
    callback_data='fake_uch')]])

time_end = InlineKeyboardButton(
    text='⌛ Завершить по времени',
    callback_data='time_end')

hand_end = InlineKeyboardButton(
    text='✍️ Завершить вручную',
    callback_data='hand_end')

chouse_end = InlineKeyboardMarkup(inline_keyboard=[[time_end], [hand_end]])


def confirm_win(data):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text='Я не робот',
        callback_data=f'confirm_win {data}')]])


main1 = KeyboardButton(text='')

main_menu = ReplyKeyboardMarkup(
    keyboard=[[]],
    resize_keyboard=True)

help_menu = InlineKeyboardMarkup(
    inline_keyboard=[[]])
