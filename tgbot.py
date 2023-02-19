import logging
import typing
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified, MessageCantBeDeleted, CantInitiateConversation, BadRequest

from db import add_user, get_users, validate_user, add_delivery, add_delivery_msg, get_delivery_id, get_delivery_msg, \
    delete_delivery, get_user, delete_user, get_admin, add_admin, validate_admin, get_admins, delete_admin

API_TOKEN = '2124982820:AAG-zVvET6Pcn9sDPiqIYLheaeos5w8T6dI'
#bot_admin = [123465599, 1456342195]
bot_admin = get_admins()
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

admin_cb = CallbackData('admin', 'action')  # user:<action>
review_admin_cb = CallbackData('reviewadmin', 'action')  # reviewadmin:<action>
user_cb = CallbackData('user', 'action')  # user:<action>
review_cb = CallbackData('review', 'action')  # review:<action>
delivery_cb = CallbackData('delivery', 'action')  # delivery:<action>


def get_review_admin_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton('Accept', callback_data=review_admin_cb.new(action='accept')),
               types.InlineKeyboardButton('Reject', callback_data=review_admin_cb.new(action='reject')))
    return markup


def get_admin_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton('Ok', callback_data=admin_cb.new(action='ok')),
               types.InlineKeyboardButton('Cancel', callback_data=admin_cb.new(action='cancel')))
    return markup


def get_review_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton('Accept', callback_data=review_cb.new(action='accept')),
               types.InlineKeyboardButton('Reject', callback_data=review_cb.new(action='reject')))
    return markup


def get_user_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton('Ok', callback_data=user_cb.new(action='ok')),
               types.InlineKeyboardButton('Cancel', callback_data=user_cb.new(action='cancel')))
    return markup


def get_delivery_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton('Attend', callback_data=delivery_cb.new(action='attend')))
    return markup


# @dp.message_handler(commands='del', chat_type=['private'])
# async def deli(message: types.Message):
#     delivery_id = add_delivery()
#     for admin in bot_admin:
#         msg = await bot.send_message(admin[0], "Delivery is here!", parse_mode="MARKDOWN",
#                                      reply_markup=get_delivery_keyboard())
#         add_delivery_msg(delivery_id, admin[0], msg.message_id)

# ----------------Users--------------#
@dp.message_handler(commands='users', chat_type=['private'])
async def list_users(message: types.Message):
    pid = message.from_user.id
    users_txt = '*Current Users:*\n\n'
    users = get_users()
    for user in users:
        users_txt += f"`{user[0]}`  |   [{user[1]} {user[2] or ''}](tg://user?id={user[0]})\n"
    await bot.send_message(pid, users_txt, parse_mode="MARKDOWN")


@dp.message_handler(commands='addme', chat_type=['private'])
async def add_me(message: types.Message):
    pid = message.from_user.id
    f_name = message.from_user.first_name
    l_name = message.from_user.last_name

    tag = f"[{f_name} {l_name or ''}](tg://user?id={pid})"
    text = f"{tag} requested access!"

    for admin in bot_admin:
        await bot.send_message(admin[0], text, parse_mode="MARKDOWN", reply_markup=get_review_keyboard())


@dp.callback_query_handler(review_cb.filter(action=['accept']))
async def accept(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    chat_id = query.message.chat.id
    msg_id = query.message.message_id
    requested_user = query.message.entities[0]['user']
    requested_user_tag = f"[{requested_user.first_name} {requested_user.last_name or ''}](tg://user?id={requested_user.id})"
    status = ''

    if validate_user(requested_user.id):
        status = "User already exist!"
    else:
        status = "Accepted!"
        add_user(requested_user.id, requested_user.first_name, requested_user.last_name, requested_user.username)
    await query.answer("User Accepted!")
    await bot.edit_message_text("*Requested By*: " + requested_user_tag + "\n*Status*: " + status, chat_id, msg_id,
                                parse_mode="MARKDOWN", reply_markup=None)


@dp.callback_query_handler(review_cb.filter(action=['reject']))
async def reject(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    chat_id = query.message.chat.id
    msg_id = query.message.message_id

    await query.answer("Rejected!")
    await bot.edit_message_text(query.message.text + "\n" + "Rejected!", chat_id, msg_id,
                                parse_mode="MARKDOWN", reply_markup=None)


@dp.message_handler(commands='revoke', chat_type=['private'])
async def revoke(message: types.Message):
    pid = message.from_user.id
    users_txt = '*Revoke access of user?*\n'
    message_data = message.text.split(' ')
    print(message_data)
    if len(message_data) == 2:
        user = get_user(message_data[1])
        if user:
            users_txt += f"`{user[0]}`  |   [{user[1]} {user[2] or ''}](tg://user?id={user[0]})\n"
            await bot.send_message(pid, users_txt, parse_mode="MARKDOWN", reply_markup=get_user_keyboard())
        else:
            users_txt = "User doesnt exist!"
            await bot.send_message(pid, users_txt, parse_mode="MARKDOWN")
    else:
        text = f"*Usage:*\n/revoke <User1>"
        await bot.send_message(pid, text, parse_mode="MARKDOWN")


@dp.callback_query_handler(user_cb.filter(action=['ok']))
async def ok(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    chat_id = query.message.chat.id
    msg_id = query.message.message_id
    requested_user = query.message.entities[2]['user']
    requested_user_tag = f"[{requested_user.first_name} {requested_user.last_name or ''}](tg://user?id={requested_user.id})"
    delete_user(str(requested_user.id))
    await query.answer("User deleted!")
    await bot.edit_message_text(f"`{requested_user.id}` | " + requested_user_tag + "\n*Status:* Access Revoked!",
                                chat_id, msg_id,
                                parse_mode="MARKDOWN", reply_markup=None)


@dp.callback_query_handler(user_cb.filter(action=['cancel']))
async def cancel(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    chat_id = query.message.chat.id
    msg_id = query.message.message_id
    await query.answer("Canceled!")
    await bot.edit_message_text(query.message.text + "\n*Status:* Operation Cancelled!", chat_id, msg_id,
                                parse_mode="MARKDOWN", reply_markup=None)

# -----------------Admins -----------------

@dp.message_handler(commands='intiateadmin', chat_type=['private'])
async def add_me(message: types.Message):
    pid = message.from_user.id
    f_name = message.from_user.first_name
    l_name = message.from_user.last_name
    username = message.from_user.username

    text = f"admin initiated!"
    add_admin(pid, f_name, l_name, username)
    await bot.send_message(pid, text, parse_mode="MARKDOWN", reply_markup=get_review_keyboard())

@dp.message_handler(commands='admins', chat_type=['private'])
async def list_admins(message: types.Message):
    pid = message.from_user.id
    users_txt = '*Current Admins:*\n\n'
    admins = get_admins()

    for admin in admins:
        users_txt += f"`{admin[0]}`  |   [{admin[1]} {admin[2] or ''}](tg://user?id={admin[0]})\n"
    await bot.send_message(pid, users_txt, parse_mode="MARKDOWN")


@dp.message_handler(commands='addasadmin', chat_type=['private'])
async def add_as_admin(message: types.Message):
    pid = message.from_user.id
    f_name = message.from_user.first_name
    l_name = message.from_user.last_name

    tag = f"[{f_name} {l_name or ''}](tg://user?id={pid})"
    text = f"{tag} requested admin access!"

    for admin in bot_admin:
        await bot.send_message(admin[0], text, parse_mode="MARKDOWN", reply_markup=get_review_admin_keyboard())


@dp.callback_query_handler(review_admin_cb.filter(action=['accept']))
async def accept(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    global bot_admin
    chat_id = query.message.chat.id
    msg_id = query.message.message_id
    requested_admin = query.message.entities[0]['user']
    requested_admin_tag = f"[{requested_admin.first_name} {requested_admin.last_name or ''}](tg://user?id={requested_admin.id})"
    status = ''

    if validate_admin(requested_admin.id):
        status = "Admin already exist!"
    else:
        status = "Accepted!"
        add_admin(requested_admin.id, requested_admin.first_name, requested_admin.last_name, requested_admin.username)
        bot_admin = get_admins()
    await query.answer("Admin Accepted!")
    await bot.edit_message_text("*Requested By*: " + requested_admin_tag + "\n*Status*: " + status, chat_id, msg_id,
                                parse_mode="MARKDOWN", reply_markup=None)


@dp.callback_query_handler(review_admin_cb.filter(action=['reject']))
async def reject_admin(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    chat_id = query.message.chat.id
    msg_id = query.message.message_id
    await query.answer("Rejected!")
    await bot.edit_message_text(query.message.text + "\n" + "Rejected!", chat_id, msg_id,
                                parse_mode="MARKDOWN", reply_markup=None)


@dp.message_handler(commands='revokeadmin', chat_type=['private'])
async def revoke_admin(message: types.Message):
    pid = message.from_user.id
    admin_txt = '*Revoke access of admin?*\n'
    message_data = message.text.split(' ')
    print(message_data)
    if len(message_data) == 2:
        admin = get_admin(message_data[1])
        if admin:
            admin_txt += f"`{admin[0]}`  |   [{admin[1]} {admin[2] or ''}](tg://user?id={admin[0]})\n"
            await bot.send_message(pid, admin_txt, parse_mode="MARKDOWN", reply_markup=get_admin_keyboard())
        else:
            admin_txt = "Admin doesnt exist!"
            await bot.send_message(pid, admin_txt, parse_mode="MARKDOWN")
    else:
        text = f"*Usage:*\n/revokeadmin <Admin1>"
        await bot.send_message(pid, text, parse_mode="MARKDOWN")


@dp.callback_query_handler(admin_cb.filter(action=['ok']))
async def ok_admin(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    chat_id = query.message.chat.id
    msg_id = query.message.message_id
    requested_admin = query.message.entities[2]['user']
    requested_admin_tag = f"[{requested_admin.first_name} {requested_admin.last_name or ''}](tg://user?id={requested_admin.id})"
    delete_admin(str(requested_admin.id))
    await query.answer("Admin deleted!")
    await bot.edit_message_text(f"`{requested_admin.id}` | " + requested_admin_tag + "\n*Status:* Access Revoked!",
                                chat_id, msg_id,
                                parse_mode="MARKDOWN", reply_markup=None)


@dp.callback_query_handler(admin_cb.filter(action=['cancel']))
async def cancel_admin(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    chat_id = query.message.chat.id
    msg_id = query.message.message_id
    await query.answer("Canceled!")
    await bot.edit_message_text(query.message.text + "\n*Status:* Operation Cancelled!", chat_id, msg_id,
                                parse_mode="MARKDOWN", reply_markup=None)

@dp.callback_query_handler(delivery_cb.filter(action=['attend']))
async def reject(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    chat_id = query.message.chat.id
    msg_id = query.message.message_id
    user_id = query.from_user.id
    user_fname = query.from_user.first_name
    user_lname = query.from_user.last_name

    attend_tag = f"[{user_fname} {user_lname or ''}](tg://user?id={user_id})"

    delivery_id = get_delivery_id(str(chat_id), str(msg_id))
    if delivery_id:
        msgs = get_delivery_msg(delivery_id)
        delete_delivery(delivery_id)
        await query.answer("Attending!")
        for msg in msgs:
            await bot.edit_message_text(query.message.text + "\n" + "*Status*: Attending!\n" + "*By*: " + attend_tag,
                                        msg[0], msg[1],
                                        parse_mode="MARKDOWN", reply_markup=None)
    else:
        await query.answer("Someone already attended!")
        await bot.edit_message_reply_markup(chat_id, msg_id, reply_markup=None)


@dp.callback_query_handler(review_cb.filter(action=['reject']))
async def reject(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    chat_id = query.message.chat.id
    msg_id = query.message.message_id

    await query.answer("Rejected!")
    await bot.edit_message_text(query.message.text + "\n" + "Rejected!", chat_id, msg_id,
                                parse_mode="MARKDOWN", reply_markup=None)


@dp.errors_handler(exception=MessageNotModified)
async def message_not_modified_handler(update, error):
    return True  # errors_handler must return True if error was handled correctly


@dp.errors_handler(exception=MessageCantBeDeleted)
async def message_not_deleted_handler(update, error):
    return True  # errors_handler must return True if error was handled correctly


@dp.errors_handler(exception=CantInitiateConversation)
async def message_cannot_send_handler(update, error):
    return True  # errors_handler must return True if error was handled correctly


@dp.errors_handler(exception=BadRequest)
async def message_cannot_send_handler(update, error):
    return True  # errors_handler must return True if error was handled correctly


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
