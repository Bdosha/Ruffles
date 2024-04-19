from aiogram import Bot, Dispatcher
from aiogram.filters import Text, Command
from aiogram.types import (CallbackQuery, Message)
from aiogram.types import FSInputFile
from aiogram.exceptions import TelegramBadRequest

from datetime import datetime
from sqlite3 import OperationalError
import database
import structure
import asyncio
import re

BOT_TOKEN: str = 'token'

bot: Bot = Bot(token=BOT_TOKEN)
dp: Dispatcher = Dispatcher()

admins = ['', '']
raffles_admin = ['📅 Ежедневный', '💸 Спонсорский']
raffle_user = ['daily_raffle', 'spons_raffle']

DT_format = '%d-%m-%Y %H:%M'
all_chanels = database.all_chanels()

'''
-1 - отправка ссылки стим
0 - ничего
1 - ежедневный пост
2 - спонсорский пост
3 - дата начала ежедневного
4 - дата начала спонсорского
5 - дата конца ежедневного
6 - дата конца спонсорского
7 - указать канал
8 - указать ответственного
'''


async def end_raffle(id, type):
    info = database.end_raffle(id, type)
    print(" ".join([str(info[4]), str(info[0]), info[1], info[3]]))
    text = info[2].replace(".", "\.").replace("-", "\.").replace("!", "\!").replace("|", "\|")
    try:
        msg = await bot.send_message(chat_id=info[4],
                                     text=f"Вы выйграли в розыгрыше\!\n\n "
                                          f"{text}\n\n"
                                          f"Подтвердите что вы не робот, чтобы забрать приз\!\n"
                                          f"||{info[1][0]}{info[0]}||",
                                     parse_mode='MarkdownV2',
                                     reply_markup=structure.confirm_win(
                                         f'{" ".join([str(info[4]), str(info[0]), info[1], info[3]])}'))
        await asyncio.sleep(3600)
        await msg.edit_text(text='Время подтверждения истекло')
    except:
        return


async def check_start():
    daily = database.get_raffles('daily_raffle')
    spons = database.get_raffles('spons_raffle')

    DT = datetime.now()
    for raffle in daily:
        DT_raffle = datetime.strptime(raffle[2], '%d-%m-%Y %H:%M')
        if DT >= DT_raffle:
            database.start_raffle(raffle[0], 'daily_raffle')
    for raffle in spons:
        DT_raffle = datetime.strptime(raffle[2], '%d-%m-%Y %H:%M')
        if DT >= DT_raffle:

            database.start_raffle(raffle[0], 'spons_raffle')
    await asyncio.sleep(60)
    await check_start()


async def check_end():
    daily = database.get_raffles('active_daily_raffle')
    spons = database.get_raffles('active_spons_raffle')

    DT = datetime.now()
    for raffle in daily:
        if raffle[3] == 'Вручную':
            continue
        DT_raffle = datetime.strptime(raffle[3], '%d-%m-%Y %H:%M')
        if DT >= DT_raffle:
            await end_raffle(raffle[0], 'daily_raffle')

    for raffle in spons:
        if raffle[3] == 'Вручную':
            continue
        DT_raffle = datetime.strptime(raffle[3], '%d-%m-%Y %H:%M')
        if DT >= DT_raffle:
            await end_raffle(raffle[0], 'spons_raffle')
    await asyncio.sleep(60)
    await check_end()


@dp.message(Command(commands=['start']))
async def start_command(message: Message):
    print(message.from_user.id)
    print(message.text)
    print(message)
    if message.text.replace('/start', ''):
        refer = message.text.split()[-1]
        if int(refer) != message.from_user.id:
            database.new_refer(message.text.split()[-1])
    if message.from_user.username in admins:
        await message.answer('Панель администратора', reply_markup=structure.admin)

        await asyncio.gather(check_start(), check_end())

        return
    if database.start_command(message.from_user.id, message.from_user.username):
        if not database.get(message.from_user.id, 'steam', 'user_info'):
            await message.answer(text="укажите ссылку на обмен Steam")
            database.set_using_bot(message.from_user.id, -1)
            return
        await message.answer(text='Панель пользователя',
                             reply_markup=structure.user)
        return
    await message.answer(text='чтобы участвовать в розыгрышах вам нужно пригласить двух друзей\n'
                              f'Ваша реферальная ссылка: https://t.me/Bdosha_testbot?start={message.from_user.id}')


@dp.message(Text(text='💸 Для спонсоров'))
async def sub_help(message: Message):
    await message.answer('Прайслист')


@dp.message(Text(text='🎁 Розыгрыши'))
async def sub_help(message: Message):
    await message.answer('выберите вид розыгрыша', reply_markup=structure.raffle_chouse_user)


@dp.callback_query(Text(text='daily_raffle'))
async def sub_sub(callback: CallbackQuery):
    raffles = database.get_raffles('active_daily_raffle')
    await callback.answer()
    keys = structure.key_daily
    if callback.from_user.username in admins:
        keys = structure.end_key_daily
    if not raffles:
        await callback.message.answer(text='На данный момент розыгрышей нет')
        return
    for raffle in raffles:
        text = f'{raffle[1]}\n\n' \
               f'Итоги: {raffle[3].replace("-", ".")}\n\n' \
               f'||d{raffle[0]}||'

        await callback.message.answer_photo(photo=FSInputFile(path=f"daily_raffle\\{raffle[0]}.jpg"),
                                            caption=text.replace(".", "\.").replace("-", "\.").replace("!", "\!").replace("|", "\|"),
                                            parse_mode='MarkdownV2',
                                            reply_markup=keys)


@dp.callback_query(Text(text='spons_raffle'))
async def sub_sub(callback: CallbackQuery):
    raffles = database.get_raffles('active_spons_raffle')
    await callback.answer()
    keys = structure.key_spons
    if callback.from_user.username in admins:
        keys = structure.end_key_spons
    if not raffles:
        await callback.message.answer(text='На данный момент розыгрышей нет')
        return
    for raffle in raffles:
        text = f'{raffle[1]}\n\n' \
               f'Итоги: {raffle[3].replace("-", ".")}\n\n' \
               f'||s{raffle[0]}||'
        await callback.message.answer_photo(photo=FSInputFile(path=f"spons_raffle\\{raffle[0]}.jpg"),
                                            caption=text.replace(".", "\.").replace("-", "\.").replace("!", "\!").replace("|", "\|"),
                                            parse_mode='MarkdownV2',
                                            reply_markup=keys)


@dp.callback_query(lambda callback: 'confirm_win' in callback.data)
async def sub_sub(callback: CallbackQuery):
    info = callback.data.split()[1:]
    print(info)
    if callback.from_user.id != int(info[0]):
        await callback.answer()
        return
    url = database.get(callback.from_user.id, 'steam', 'user_info')
    raffle = database.get_end_raffle(info[1], info[2])
    if not raffle:
        await callback.message.edit_text(text='Розыгрыш завершен')
        return
    try:

        await bot.send_message(chat_id=info[3],
                               text=f'Пользователь @{callback.from_user.username} выиграл в розыгрыше {raffle[0][2]}\n\n'
                                    f'Отправьте приз по ссылке: {url}')
        await callback.message.answer(text='Информация о выйгрыше передана модератору, ожидайте')
    except:
        await callback.message.answer(
            text=f'Ошибка в передаче сообщения модератору, попробуйте написать напрямую: @{database.get(info[3], "username", "user_info")}\n\n'
                 f'Пользователь @{callback.from_user.username} выиграл в розыгрыше {raffle[0][2]}\n\n'
                 f'Отправьте приз по ссылке: {url}'
        )
    database.full_end(info[1], info[2])


@dp.message(Text(text='⬅️ Выйти'))
async def sub_help(message: Message):
    if not message.from_user.username in admins:
        return
    try:
        database.back(message.from_user.id,
                      raffle_user[database.get(message.from_user.id, 'using', 'user_info') % 2 - 1])
    except OperationalError:
        pass
    await message.answer('вы вышли в меню', reply_markup=structure.admin)


@dp.message(Text(text='🆕 Создать розыгрыш'))
async def sub_help(message: Message):
    if not message.from_user.username in admins:
        return
    try:
        database.back(message.from_user.id,
                      raffle_user[database.get(message.from_user.id, 'using', 'user_info') % 2 - 1])
    except OperationalError:
        database.set_using_bot(message.from_user.id, 0)
    await message.answer('Определите вид розыгрыша', reply_markup=structure.raffle_chouse_admin)


@dp.message(Text(text=raffles_admin))
async def sub_sub(message: Message):
    if not message.from_user.username in admins:
        return
    database.set_using_bot(message.from_user.id, raffles_admin.index(message.text) + 1)
    await message.answer('Напишите пост розыгрыша', reply_markup=structure.back)


@dp.callback_query(Text(text='spons_uch'))
async def sub_sub(callback: CallbackQuery):
    table = callback.message.caption.split('\n')[-1]
    if not table in database.all_tables():
        await callback.answer(text='Розыгрыш закончился', show_alert=True)
        await callback.message.delete()
        return
    channel = database.get(table[1:], 'channel', 'active_spons_raffle')

    try:
        user = await bot.get_chat_member(chat_id=channel, user_id=callback.from_user.id)
    except TelegramBadRequest:
        await callback.answer(text=f'Сначала нужно подписаться на {channel}', show_alert=True)
        return
    if user.status == 'left':
        await callback.answer(text=f'Сначала нужно подписаться на {channel}', show_alert=True)
        return
    if not database.new_member(callback.from_user.id, callback.from_user.username, table):
        await callback.answer(text='Вы УЖЕ участвуете в розыгрыше!', show_alert=True)
        return

    await callback.answer(text='Теперь вы участвуете в розыгрыше!', show_alert=True)


@dp.callback_query(Text(text='fake_uch'))
async def sub_sub(callback: CallbackQuery):
    await callback.answer(text='Тестовая кнопка поста', show_alert=True)


@dp.callback_query(Text(text='daily_uch'))
async def sub_sub(callback: CallbackQuery):
    table = callback.message.caption.split('\n')[-1]
    if not table in database.all_tables():
        await callback.answer(text='Розыгрыш закончился', show_alert=True)
        await callback.message.delete()
        return
    if not database.new_member(callback.from_user.id, callback.from_user.username, table):
        await callback.answer(text='Вы УЖЕ участвуете в розыгрыше!', show_alert=True)
        return
    await callback.answer(text='Теперь вы участвуете в розыгрыше!', show_alert=True)


@dp.callback_query(Text(text=['daily_end', 'spons_end']))
async def sub_sub(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text='Розыгрыш завершен', show_alert=True)

    await end_raffle(callback.message.caption.split('\n')[-1][1:], callback.data.replace('_end', '_raffle'))


@dp.message(lambda message: message.photo and message.caption)  # добавление поста в розыгрыш
async def handle_photo(message: Message):
    using = database.get(message.from_user.id, 'using', 'user_info')
    if not using in [1, 2] \
            or not message.from_user.username in admins:
        await message.answer(text='неизвестная команда')
        return

    post_id = database.set_post(message.from_user.id, message.caption, raffle_user[using - 1])
    photo = message.photo[-1]
    photo_path = f"{raffle_user[using - 1]}\\{post_id}.jpg"

    await bot.download(photo, photo_path)
    await message.answer('Укажите дату и время начала розыгрыша в формате "dd-mm-yyyy hh:mm"')
    database.set_using_bot(message.from_user.id, using + 2)
    database.set(message.from_user.id, 'post_id', 'user_info', post_id)


@dp.message(lambda message: bool(re.match(structure.datetime_pattern, message.text)))
async def handle_photo(message: Message):
    using = int(database.get(message.from_user.id, 'using', 'user_info'))
    post = database.get(message.from_user.id, 'post_id', 'user_info')
    if not message.from_user.username in admins:
        return
    text = message.text
    if using in [3, 4]:
        print(text)
        print(post, 'begin', raffle_user[using % 2 - 1], text)
        database.set(post, 'begin', raffle_user[using % 2 - 1], text)
        await message.answer(text='выберите вариант завершения поста', reply_markup=structure.chouse_end)
    elif using in [5, 6]:
        database.set(post, 'end', raffle_user[using % 2 - 1], text)
        if using == 5:
            post = database.get_post(post, 'daily_raffle')
            database.set(post[0], 'moder', 'daily_raffle', '95878747')
            database.set(post[0], 'channel', 'daily_raffle', 'пися')
            text = [f'Готово:\nПост будет опубликован {post[2]}', f'{post[1]}\n\nИтоги:  {post[3]}\n\n||d{post[0]}||']
            await message.answer(text=text[0], reply_markup=structure.admin)
            await message.answer_photo(photo=FSInputFile(path=f"daily_raffle\\{post[0]}.jpg"),
                                       caption=text[1].replace(".", "\.").replace("-", "\.").replace("!", "\!").replace("|", "\|"),
                                       parse_mode='MarkdownV2',
                                       reply_markup=structure.fake_uch)
        else:
            await message.answer(text="укажите канал спонсора через @ или через его id")
            database.set_using_bot(message.from_user.id, 7)
    else:
        await message.answer(text='неизвестная команда')


@dp.message(lambda message: 'https://steamcommunity.com/tradeoffer/new/' in message.text)
async def handle_photo(message: Message):
    using = int(database.get(message.from_user.id, 'using', 'user_info'))
    if using != -1:
        await message.answer(text='неизвестная команда')
    database.set(message.from_user.id, 'steam', 'user_info', message.text)
    await message.answer(text='ссылка на обмен прикреплена', reply_markup=structure.user)
    database.set_using_bot(message.from_user.id, 0)


@dp.callback_query(Text(text='hand_end'))
async def sub_sub(callback: CallbackQuery):
    using = database.get(callback.from_user.id, 'using', 'user_info')
    post = database.get(callback.from_user.id, 'post_id', 'user_info')
    if not using in [3, 4] \
            or not callback.from_user.username in admins:
        return
    database.set(post, 'end', raffle_user[using % 2 - 1], 'Вручную')

    if using == 3:
        post = database.get_post(post, 'daily_raffle')

        text = [f'Готово:\nПост будет опубликован {post[2]}', f'{post[1]}\n\nИтоги:  {post[3]}\n\n||d{post[0]}||']
        await callback.message.answer(text=text[0], reply_markup=structure.admin)
        await callback.message.answer_photo(photo=FSInputFile(path=f"daily_raffle\\{post[0]}.jpg"),
                                            caption=text[1].replace(".", "\.").replace("-", "\.").replace("|", "\|"),
                                            parse_mode='MarkdownV2',
                                            reply_markup=structure.fake_uch)
    else:
        await callback.message.answer(text="укажите канал спонсора через @ или через его id")
        database.set_using_bot(callback.from_user.id, 7)
    await callback.answer()


@dp.callback_query(Text(text='time_end'))
async def sub_sub(callback: CallbackQuery):
    using = database.get(callback.from_user.id, 'using', 'user_info')
    if not using in [3, 4] \
            or not callback.from_user.username in admins:
        return
    database.set_using_bot(callback.from_user.id, using + 2)
    await callback.message.answer('Напишите конец "dd-mm-yyyy hh:mm"')
    await callback.answer()


@dp.message()
async def handle_photo(message: Message):
    using = database.get(message.from_user.id, 'using', 'user_info')
    post = database.get(message.from_user.id, 'post_id', 'user_info')
    if message.from_user.username in admins:
        if using == 7:
            try:
                user = await bot.get_chat_member(chat_id=message.text, user_id=6189281736)
            except TelegramBadRequest:
                await message.answer(text='Бот не является админом этого канала!')
                return
            if user.status != 'administrator':
                await message.answer(text='Бот не является админом этого канала!')
                return
            database.set(post, 'channel', 'spons_raffle', message.text)
            await message.answer(text="Укажите менеджера")
            database.set_using_bot(message.from_user.id, 8)
            return
        if using == 8:
            print(message.text[1:])
            moder = database.check_moder(message.text[1:])
            print(moder)
            if not moder:
                await message.answer('Модератор не зарегистрирован в системе')
                return
            database.set(post, 'moder', 'spons_raffle', moder[0][0])
            post = database.get_post(post, 'spons_raffle')
            text = [f'Готово:\n'
                    f'Пост будет опубликован {post[2]}\n'
                    f'Канал спонсора: {post[4]}\n'
                    f'Модератор: {post[5]}',
                    f'{post[1]}\n\nИтоги:  {post[3]}\n\n||s{post[0]}||']
            await message.answer(text=text[0], reply_markup=structure.admin)
            await message.answer_photo(photo=FSInputFile(path=f"spons_raffle\\{post[0]}.jpg"),
                                       caption=text[1].replace(".", "\.").replace("-", "\.").replace("!", "\!").replace("|", "\|"),
                                       parse_mode='MarkdownV2',
                                       reply_markup=structure.fake_uch)
            database.set_using_bot(message.from_user.id, 0)
            return
    await message.answer('неизвестная команда')


if __name__ == '__main__':
    print('Бот запущен')
    dp.run_polling(bot)
