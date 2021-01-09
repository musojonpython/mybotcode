import logging, ssl, telegram
# import ssl
# import telegram
import pymysql
import urllib, json, requests
import datetime
import random
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

db = pymysql.connect(
    host="80.80.218.221",
    user="dev4",
    password="3pLWHbtXWP4U",
    database="dev4"
)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

ADDITION, ACCEPTING, ANOTHER_ADD, BASKET_BUTTON, CHECKING, FULL_INFO, FOODS,ADDITION_LOCATION,  \
KITCHENS, LANGUAGES, LOCATION, PAYING_WITH_LOCATION, PAYING_WITH_CONTACT, FULL_INFO_WITH_LOCATION = range(14)

uzbek, rus, locationidentify = False, False, False
backing, kitchen_num = None, None
Local_TOKEN, category_id = "", ""
kitchen_id, restaurant_id = 0, 0
food_type_id, foods_list_selected = [], []
food_name, user, botss = "", "", ""
full_foods_list = {}


def recive_token(Token, manufacturer_id):
    global Local_TOKEN, restaurant_id

    Local_TOKEN = Token
    restaurant_id = manufacturer_id

    return main()


def main():
    global restaurant_id, Local_TOKEN, botss

    botss = telegram.Bot(token=Local_TOKEN)
    updater = Updater(Local_TOKEN, use_context=True)  # this is polling
    dp = updater.dispatcher  # this is polling
    '''
    updater.start_webhook(listen="0.0.0.0",
                          port=8443,
                          url_path=TOKEN,
                          key='private.key',
                          cert='cert.pem',
                          webhook_url='https://api.telegram.org/bot' + TOKEN)
    '''
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            ADDITION: [
                MessageHandler(Filters.regex('^(⏪Orqaga|⏪Назад)$'), back),
                MessageHandler(Filters.regex('^(📋Savatcha|📋Корзинка)$'), basket),
                MessageHandler(Filters.regex('^(🚖Условия доставки|🚖Yetkazib berish shartlari)$'), contract),
                MessageHandler(Filters.text, numbers)
            ],
            ANOTHER_ADD: [
                MessageHandler(Filters.regex('^(📋Savatcha|📋Корзинка)$'), basket),
                MessageHandler(Filters.regex('^(⏪Orqaga|⏪Назад)$'), back),
                MessageHandler(Filters.regex('^(🚖Условия доставки|🚖Yetkazib berish shartlari)$'), contract),
                MessageHandler(Filters.text, calculate)
            ],
            ACCEPTING: [
                MessageHandler(Filters.regex("^(⛔Yo'q|⛔Нет|✔Xa|✔Да)$"), yes_no_accepting),
            ],
            CHECKING: [
                MessageHandler(Filters.regex("^(🚫Bekor qilish|🚫Отмена)$"), reject),
                MessageHandler(Filters.regex("^(✅Я в подтверждении|✅Tasdiqliman)$"), accepting),
            ],
            FULL_INFO_WITH_LOCATION: [
                MessageHandler(Filters.regex("^(💸Наличная|💸Naqd pul)$"), full_info_with_location),
                MessageHandler(Filters.regex('^(⏪Orqaga|⏪Назад)$'), back),
            ],
            FULL_INFO: [
                MessageHandler(Filters.regex("^(💸Наличная|💸Naqd pul)$"), full_info),
                MessageHandler(Filters.regex('^(⏪Orqaga|⏪Назад)$'), back),
            ],
            PAYING_WITH_LOCATION: [
                MessageHandler(Filters.contact, paying_with_location),
                MessageHandler(Filters.regex('^(⏪Orqaga|⏪Назад)$'), back),
                MessageHandler(Filters.text,  contact)
            ],
            PAYING_WITH_CONTACT: [
                MessageHandler(Filters.contact, paying_with_contact),
                MessageHandler(Filters.regex('^(⏪Orqaga|⏪Назад)$'), back),
            ],
            LOCATION: [
                MessageHandler(Filters.regex("^(🚶O'zim olib ketaman|🚶Самовывоз)$"), contact),
                MessageHandler(Filters.location, location),
                MessageHandler(Filters.regex("^(⏪Назад|⏪Orqaga)$"), back),
                MessageHandler(Filters.text, contact_with_location)
            ],
            ADDITION_LOCATION:[
                MessageHandler(Filters.text, addition_location)
            ],
            BASKET_BUTTON: [
                MessageHandler(Filters.regex('^(🖌Tozalash|🖌Очистить)$'), clear_data),
                MessageHandler(Filters.regex('(⏪Orqaga|⏪Назад)$'), back),
                MessageHandler(Filters.regex('^(🚖Условия доставки|🚖Yetkazib berish shartlari)$'), contract),
                MessageHandler(Filters.regex('^(✳️Buyurtmani  rasmiylashtirish|✳️Оформить заказ)$'),
                               ordering),
                MessageHandler(Filters.text, decrease_count)
            ],
            FOODS: [
                MessageHandler(Filters.regex('^(⏪Orqaga|⏪Назад)$'), back),
                MessageHandler(Filters.regex('^(🚖Условия доставки|🚖Yetkazib berish shartlari)$'), contract),
                MessageHandler(Filters.regex('^(📋Savatcha|📋Корзинка)$'), basket),
                MessageHandler(Filters.text, foods),
            ],
            LANGUAGES: [
                MessageHandler(Filters.regex('^(🇺🇿Uzbek tili🇺🇿)$'), choice_uzbek),
                MessageHandler(Filters.regex('^(🇷🇺Rus tili🇷🇺)$'), choice_rus),
            ],
            KITCHENS: [
                MessageHandler(Filters.regex('(⏪Orqaga|⏪Назад)$'), back),
                MessageHandler(Filters.regex('^(📋Savatcha|📋Корзинка)$'), basket),
                MessageHandler(Filters.regex('^(🚖Условия доставки|🚖Yetkazib berish shartlari)$'), contract),
                MessageHandler(Filters.text, kitchens),
            ],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conv_handler)

    dp.add_error_handler(error)

    # https://api.telegram.org/bot919481604:AAFUctoQbMUIetZcRBcsS6v37NN108O3Uxg/setwebhook?url=https://yourdomain.com/bot.py
    updater.start_polling()  # This is polling

    updater.idle()  # This is polling


if __name__ == '__main__':
    main()


def accepting(update, context):
    global full_foods_list, user, \
        locationidentify, botss, uzbek, restaurant_id

    date = datetime.datetime.now()
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")
    telegramId = year + month + day

    for x in range(18):
        number = random.randint(0, 9)
        telegramId += str(number)

    created = datetime.datetime.now()
    created = str(created).split(".")
    created = created[0]

    chat_id = update.message.chat_id
    latitude = "NULL"
    longitude = "NULL"
    address = "NULL"

    if locationidentify:
        locationlonglat = context.user_data['location']
        address = context.user_data['address']
        user_address = context.user_data['addition_location']
        locationlonglat = locationlonglat.split(" ")
        latitude = locationlonglat[2]
        longitude = locationlonglat[5]
        deliveryMethodId = 16
    else:
        deliveryMethodId = 15

    phone = context.user_data['contact']
    name = context.user_data['first_name']
    date = datetime.datetime.now()
    time = date.strftime("%X")
    restaurantId = restaurant_id

    type_of_payment = context.user_data['type_of_payment']
    if type_of_payment == "💸Naqd pul":
        paymentMethodId = 18
    else:
        paymenttypechoices = [20, 21, 19, 24]
        paymentMethodId = random.choice(paymenttypechoices)

    languageId = "ru"
    if uzbek:
        text = "<b>📝 Buyutmangiz qabul qilindi</b>"
        languageId = "uz"
    else:
        text = "<b>📝 Ваш заказ был размещен</b>"

    categoryIds = full_foods_list['category_id']
    productIds = full_foods_list['productid']

    # logger.info(f"Information about categoryIds {categoryIds} and productsId {productIds}")
    # productId = product_id

    db = pymysql.connect(
        host="80.80.218.221",
        user="telegrambot",
        password="3pLWHbtXWP4U",
        database="telegram"
    )

    botNo = 167
    step = 10
    status = 5
    updates = created
    calls = [0, 1]
    dontcall = random.choice(calls)
    logger.info("Just above sql code in accepting function")
    cursor = db.cursor()
    sql = "INSERT INTO orders (created, telegramId, botNo, " \
          "chatId, latitude, longitude, phone, name, time, restaurantId, " \
          "paymentMethodId, deliveryMethodId, step, status, categoryId, " \
          "languageId, productId, address, updates, dont_call, useraddress)" \
          " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    logger.info(f"SQl code inside accepting function {sql}")
    val = (created, telegramId, botNo, chat_id, latitude, longitude, phone, name, time, restaurantId,
           paymentMethodId, deliveryMethodId, step, status, categoryIds, languageId, productIds, address,
           updates, dontcall, user_address)
    logger.info(f"SQl code inside accepting function {sql} and {val}")

    try:
        cursor.execute(sql, val)
        db.commit()
        logger.info("Data was saved")
    except:
        db.rollback()
        logger.info("Data was not saved")

    cursor = db.cursor()
    sql = f"SELECT id, telegramId, chatId, AS clientChatId, longitude AS lon, " \
          f"latitude AS lat, phone, name, time, paymentMethodId,deliveryMethodId, " \
          f"address, user_address, dont_call FROM orders WHERE telegramId={telegramId} "
    cursor.execute(sql)
    results = cursor.fetchall()

    db = pymysql.connect(
        host="80.80.218.221",
        user="dev4",
        password="3pLWHbtXWP4U",
        database="dev4"
    )
    m = len(full_foods_list['sum'])

    for n in range(m):
        cursor = db.cursor()
        sql = "INSERT INTO TelegramCart (telegeram_id, product_id, variants, configurable_id, quantity, price)" \
              "VALUES (%s, %s, %s, %s, %s, %s)"
        # val = {telegramId, productIds[n], variants, conigurable_id, quantity[n], prices[n]}
        try:
            cursor.execute(sql, val)
            db.commit()
            logger.info("Data was saved")
        except:
            db.rollback()
            logger.info("Data was not saved")
    # sum = 0
    # for x in range(m):
    #     sum += int(full_foods_list['sum'][x])
    # summa = str(sum)
    # delivery = int(context.user_data['delivery_price'])
    # total = int(summa) + int(delivery)
    # foods = ""
    # m = len(full_foods_list['food'])
    #
    # for x in range(m):
    #     foods += (f"{full_foods_list['food'][x]} {full_foods_list['count'][x]} x "
    #               f"{full_foods_list['cost'][x]} = {full_foods_list['sum'][x]};\n")
    #
    # botss.send_message(chat_id=chat_id, text=text, parse_mode=telegram.ParseMode.HTML)
    # getorder = ()
    # url = f"https://dev.bringo.uz/api/createOrder?..."
    # ssl._create_default_https_context = ssl._create_unverified_context

    # page = urllib.request.urlopen(url)
    # page = json.load(page)
    # delivery = str(page["price"])

    full_foods_list = {}
    return start(update, context)


def addition_location(update, context):
    address_text = update.message.text

    context.user_data['addition_location'] = str(address_text)

    return contact_with_location(update, context)


def back(update, context):
    global backing, full_foods_list, uzbek, rus

    if backing == 'language':
        return start(update, context)

    if backing == "backet":
        return basket(update, context)

    if backing == "Type_of_food":
        return foods(update, context)

    if backing == 'kitchen' and uzbek:
        return choice_uzbek(update, context)

    if backing == 'kitchen' and rus:
        return choice_rus(update, context)

    if backing == 'food':
        return kitchens(update, context)

    if backing == 'number' and uzbek:
        context.user_data.clear()
        full_foods_list = {}
        update.message.reply_text("Savatchangiz bo'm bo'sh ⚠")
        return kitchens(update, context)

    if backing == 'number' and rus:
        context.user_data.clear()
        full_foods_list = {}
        update.message.reply_text("Ваш корзина пуста⚠")

        return kitchens(update, context)

    if backing == "location":
        return ordering(update, context)

    if backing == "paying_with_location":
        return contact_with_location(update, context)

    if backing == "paying_with_contact":
        return contact(update, context)


def basket(update, context):
    global uzbek, full_foods_list, backing

    backing = "Type_of_food"
    user_data = context.user_data
    # user_data = full_foods_list["food"]
    m = len(user_data)

    if m < 4:
        if uzbek:
            update.message.reply_text("Sizning savatchangiz bo'm bo'sh ⚠")
        else:
            update.message.reply_text("Ваш корзина пуста⚠")
    else:
        if uzbek:
            text1 = "<b>Sizning savatchada:\n</b>"
            text2 = '⏪Orqaga'
            text3 = '✳️Buyurtmani  rasmiylashtirish'
            text4 = '🖌Tozalash'
            text5 = '<b>Mahsulotigizni tekshiring</b>'
            text6 = " so'm"
            text7 = "Jami"
            text8 = "'❌ <b>nomi</b>' - mahsulotni 1taga kamaytirish uchun"
            text9 = "'🖌<b>Tozalash</b>' - to'liq savatchani tozalash"
        else:
            text1 = "<b>Ваша корзина:\n</b>"
            text2 = '⏪Назад'
            text3 = '✳️Оформить заказ'
            text4 = '🖌Очистить'
            text5 = 'Проверьте ваш продукт'
            text6 = ' сум'
            text7 = 'Итого'
            text8 = "'❌<b>название</b>' - уменьшить товар на 1"
            text9 = "'🖌<b>Чистка</b>'- чистка полной корзины"

        num = int(len(full_foods_list['kitchen']))
        new_food_list = []
        new_list = []
        full_text = text1
        generalsum = 0
        new_food_list = [[text2], [text3]]

        for x in range(0, num):
            cost = str(full_foods_list['cost'][x])
            headcost = cost[:-5]
            othercost = cost[-5:]
            cost = headcost + " " + othercost

            generalcost = str(full_foods_list['sum'][x])
            headcost = generalcost[:-3]
            othercost = generalcost[-3:]
            generalcost = headcost + " " + othercost

            full_text += f"<b> {full_foods_list['food'][x]} </b>\n {full_foods_list['count'][x]} x {cost} {text6} = {generalcost} {text6} \n"
            tx = f"❌ {full_foods_list['food'][x]} ({full_foods_list['count'][x]} ta)"

            generalsum += int(full_foods_list['sum'][x])
            new_list.append(tx)
            new_food_list.append(new_list)
            new_list = []

        generalsum = str(generalsum)
        headcost = generalsum[:-3]
        othercost = generalsum[-3:]
        generalsum = headcost + " " + othercost

        full_text += f"<b>{text7}: </b> {generalsum} {text6}"
        full_text = str(full_text)
        new_food_list.append([text4])

        chat_id = update.message.chat_id
        reply_markup = telegram.ReplyKeyboardMarkup(new_food_list, one_time_keyboard=False, resize_keyboard=True)

        botss.send_message(chat_id=chat_id, text=full_text, parse_mode=telegram.ParseMode.HTML)
        botss.send_message(chat_id=chat_id, text=text8 + "\n" + text9, parse_mode=telegram.ParseMode.HTML,
                           reply_markup=reply_markup)

        return BASKET_BUTTON


def calculate(update, context):
    global full_foods_list, uzbek, backing

    backing = "calculate"

    text = update.message.text
    cost = str(context.user_data['cost'])
    cost = cost.split(".")
    cost = int(cost[0])

    s = int(text) * cost  # how to connect with database
    context.user_data['count'] = text
    txt = text + ' * ' + str(cost) + ' = ' + str(s)
    context.user_data['sum'] = s
    user_data = context.user_data

    for x in user_data.keys():
        full_foods_list.setdefault(x, []).append(user_data[x])
    user_data = context.user_data
    text = context.user_data['type of food']

    if uzbek:
        update.message.reply_text("Yana narsa qo'shasizmi? Shuni o'zi bo'lsa Savatcha ni bosing 📋")
        return choice_uzbek(update, context)
    else:
        update.message.reply_text("Хотите что-то ещё, если нет то нажмите Корзинка 📋")
        return choice_rus(update, context)


def cancel(update, context):
    global uzbek

    # user = update.message.from_user
    if uzbek:
        text = 'Xaridingiz uchun tashakkur!'
    else:
        text = 'Спасибо за покупку!'

    update.message.reply_text(text,
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def choice_uzbek(update, context):
    global rus, uzbek, backing, \
        restaurant_id, full_foods_list

    backing = 'language'
    rus, uzbek = False, True

    time = datetime.datetime.now()
    time = time.strftime("%X")

    cursor = db.cursor()
    sql = f"SELECT * FROM StoreManufacturer WHERE id='{str(restaurant_id)}'"
            # f" and (work_start <= '{time}' and work_finish >= '{time}')")
    cursor.execute(sql)
    results = cursor.fetchall()
    new_list = []

    if results:
        for result in results:
            new_list.append(result[1])
        new_list = making_buttons(new_list)

        if uzbek:
            update.message.reply_text('Oshxonani tanglang⤵️', reply_markup=ReplyKeyboardMarkup(new_list,
                                                                one_time_keyboard=False,resize_keyboard=True))
            return KITCHENS
    else:
        update.message.reply_text("Oshxona hali ish vaqtini boshlagani yo'q")


def choice_rus(update, context):
    global rus, uzbek, backing, restaurant_id, full_foods_list

    backing = 'language'
    rus = True
    uzbek = False

    time = datetime.datetime.now()
    time = time.strftime("%X")

    cursor = db.cursor()
    sql = (f"SELECT * FROM StoreManufacturer WHERE id='{str(restaurant_id)}' and (work_start <= '{time}'"
           f" and work_finish >= '{time}')")
    cursor.execute(sql)
    results = cursor.fetchall()
    new_list = []

    if results:
        for result in results:
            new_list.append(result[1])
        new_list = making_buttons(new_list)

        if rus:
            update.message.reply_text('Выберите заведение⤵️', reply_markup=ReplyKeyboardMarkup(new_list,
                                         one_time_keyboard=False, resize_keyboard=True))
            return KITCHENS
    else:
        update.message.reply_text("Кухня еще не началась!")


def contact_with_location(update, context):
    global backing, rus, backing
    backing = "location"

    if rus:
        text = "📱Отправьте  ваш номер телефона"
        text1 = "📱Отправляю мой номер"
        text2 = "⏪Назад"

    else:
        text = "📱Nomeringizni jo'nating"
        text1 = "Mening raqamimni jo'natish"
        text2 = "⏪Orqaga"

    chat_id = update.message.chat_id
    contact_keyboard = telegram.KeyboardButton(text=text1, request_contact=True)
    custom_keyboard = [[contact_keyboard], [text2]]

    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=False, resize_keyboard=True)
    botss.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

    return PAYING_WITH_LOCATION


def contract(update, context):
    global uzbek

    if uzbek:
        text = "🚚Etkazib berish narxi: 3 km gacha 8000 so'm, +1 km 1000 so'm"
    else:
        text = "🚚Цена доставки: до 3 км - 8000 сум, каждый доп. км - 1000 сум"

    update.message.reply_text(text)


def contact(update, context):
    global rus, backing, locationidentify
    backing = "location"
    locationidentify = False

    if rus:
        text = "📱Отправьте  ваш номер телефона"
        text1 = "📱Отправляю мой номер"
        text2 = "⏪Назад"

    else:
        text = "📱Nomeringizni jo'nating"
        text1 = "Mening raqamimni jo'natish"
        text2 = "⏪Orqaga"

    chat_id = update.message.chat_id
    contact_keyboard = telegram.KeyboardButton(text=text1, request_contact=True)
    custom_keyboard = [[contact_keyboard], [text2]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=False,
                                                resize_keyboard=True)
    botss.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

    return PAYING_WITH_CONTACT


def clear_data(update, context):
    global uzbek, full_foods_list

    context.user_data.clear()
    full_foods_list = {}

    if uzbek:
        text = "Savat tozalandi"
        update.message.reply_text(text)
        return choice_uzbek(update, context)

    else:
        text = "Корзинка очищена"
        update.message.reply_text(text)
        return choice_rus(update, context)


def decrease_count(update, context):
    global full_foods_list, uzbek

    string = str(update.message.text)
    m = string.rfind("(")
    name = str(string[2:m - 1])

    n = string.rfind(")")
    food_num = int(string[m+1:n-3])
    listoffoods = full_foods_list['food']

    p = -1
    numberoffood = 0

    for listoffood in listoffoods:
        p = p + 1
        if listoffood == name:
            numberoffood = p
            break

    food_num = food_num - 1
    if food_num == 0:
        for x in full_foods_list.keys():
            del full_foods_list[x][numberoffood]

    else:
        full_foods_list['count'][numberoffood] = food_num
        cost = str(full_foods_list['cost'][numberoffood])
        cost = cost.split(".")
        cost = int(cost[0])
        full_foods_list['sum'][numberoffood] = food_num * cost

    if len(full_foods_list['food']) == 0:
        context.user_data.clear()
        if uzbek:
            return choice_uzbek(update, context)
        else:
            return choice_rus(update, context)
    return basket(update, context)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def full_info_with_location(update, context):
    global uzbek, restaurant_id

    text = update.message.text
    context.user_data['type_of_payment'] = text

    if uzbek:
        text = "<b>Sizning buyurtmangiz: </b>"
        text1 = "<b>Telefon raqamingiz: </b>"
        text2 = "<b>Manzilingiz: </b>"
        text3 = "<b>Oshxona: </b>"
        text4 = "<b>To'lov turi: </b>"
        text5 = "<b>Summa: </b>"
        text6 = "<b>Yetkazish: </b>"
        text7 = "<b>Jami: </b>"
        text8 = " so'm"
        text9 = "Buyurtmani tasdiqlash uchun qo'ng'iroq qilishsinmi? ⤵️"
        text10 = "✔Xa"
        text11 = "⛔Yo'q"
        text12 = "<b>To'liq manzilingiz: </b>"
    else:
        text = "<b>Ваш заказ: </b>"
        text1 = "<b>Ваш номер телефона: </b>"
        text2 = "<b>Ваш адрес: </b>"
        text3 = "<b>Кухня: </b>"
        text4 = "<b>Тип оплаты: </b>"
        text5 = "<b>Summa: </b>"
        text6 = "<b>Доставить: </b>"
        text7 = "<b>Общий: </b>"
        text8 = " сум"
        text9 = "Позвоните для подтверждения вашего заказа? ⤵️"
        text10 = "✔Да"
        text11 = "⛔Нет"
        text12 = "<b>Ваш полный адрес: </b>"

    contact = context.user_data['contact']
    address = context.user_data['address']
    kitchen = context.user_data['kitchen']
    type_of_payment = context.user_data['type_of_payment']
    addition_loc = context.user_data['addition_location']
    locationlanlat = str(context.user_data['location'])
    longlat = locationlanlat.split(" ")
    lat = longlat[2]
    long = longlat[5]

    url = f"https://dev.bringo.uz/api/delivaryPrice?lat={lat}&lng={long}&manId={restaurant_id}"
    ssl._create_default_https_context = ssl._create_unverified_context

    page = urllib.request.urlopen(url)
    page = json.load(page)
    delivery = str(page["price"])
    context.user_data['delivery_price'] = delivery
    full_foods_list['delivery_price'] = delivery
    sum = 0
    m = len(full_foods_list['sum'])

    for x in range(m):
        sum += int(full_foods_list['sum'][x])

    summa = str(sum)
    total = int(summa) + int(delivery)
    total = str(total)
    foods = ""
    m = len(full_foods_list['food'])

    head_cost = summa[:-5]
    other_cost = summa[-5:]
    summa = head_cost + " " + other_cost

    head_cost = total[:-3]
    other_cost = total[-3:]
    total = head_cost + " " + other_cost

    head_cost = delivery[:-3]
    other_cost = delivery[-3:]
    delivery = head_cost + " " + other_cost
    generalsumm = ""

    for x in range(m):
        cost = str(full_foods_list['cost'][x])
        head_cost = cost[:-5]
        other_cost = cost[-5:]
        cost = head_cost + " " + other_cost

        generalsumm = str(full_foods_list['sum'][x])
        head_cost = generalsumm[:-3]
        other_cost = generalsumm[-3:]
        generalsumm = head_cost + " " + other_cost

        foods += (f"<b>{full_foods_list['food'][x]} </b> {full_foods_list['count'][x]} x "
                  f"{cost} = {generalsumm} {text8} ;\n")

    full_info_text = (f"{text} \n {text1} {contact} \n {text2} {address} \n {text12} "
                      f"{addition_loc} \n {text3} {kitchen} \n {text4} {type_of_payment} \n"
                      f"{foods} {text5} {generalsumm} {text8} \n {text6} {delivery} {text8} \n "
                      f"{text7} {total} {text8}")

    chat_id = update.message.chat_id
    botss.send_message(chat_id=chat_id, text=full_info_text, parse_mode=telegram.ParseMode.HTML)
    custom_keyboard = [[text10, text11]]

    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=False,
                                                resize_keyboard=True)
    botss.send_message(chat_id=chat_id, text=text9, reply_markup=reply_markup)

    return ACCEPTING


def full_info(update, context):
    global uzbek, full_foods_list

    text = update.message.text
    context.user_data['type_of_payment'] = text

    if uzbek:
        text  = "<b>Sizning buyurtmangiz: </b>"
        text1 = "<b>Telefon raqamingiz: </b>"
        text3 = "<b>Oshxona: </b>"
        text4 = "<b>To'lov turi: </b>"
        text5 = "<b>Summa: </b>"
        text7 = "<b>Jami: </b>"
        text8 = " so'm"
        text9 = "Buyurtmani tasdiqlash uchun qo'ng'iroq qilishsinmi? ⤵️"
        text10 = "✔Xa"
        text11 = "⛔Yo'q"

    else:
        text  = "<b>Ваш заказ: </b>"
        text1 = "<b>Ваш номер телефона: </b>"
        text3 = "<b>Кухня: </b>"
        text4 = "<b>Тип оплаты: </b>"
        text5 = "<b>Summa: </b>"
        text7 = "<b>Общий: </b>"
        text8 = " сум"
        text9 = "Позвоните для подтверждения вашего заказа? ⤵️"
        text10 = "✔Да"
        text11 = "⛔Нет"

    contact = context.user_data['contact']
    # address = context.user_data['location']
    kitchen = context.user_data['kitchen']
    type_of_payment = context.user_data['type_of_payment']

    sum = 0
    m = len(full_foods_list['sum'])

    for x in range(m):
        sum += int(full_foods_list['sum'][x])

    summa = str(sum)
    total = summa
    head_cost = summa[:-3]
    other_cost = summa[-3:]
    summa = head_cost + " " + other_cost

    head_cost = total[:-3]
    other_cost = total[-3:]
    total = head_cost + " " + other_cost
    foods = ""
    m = len(full_foods_list['food'])

    for x in range(m):
        cost = str(full_foods_list['cost'][x])
        head_cost = cost[:-5]
        other_cost = cost[-5:]
        cost = head_cost + " " + other_cost

        generalcost = str(full_foods_list['sum'][x])
        head_cost = generalcost[:-3]
        other_cost = generalcost[-3:]
        generalcost = head_cost + " " + other_cost

        foods += (f"<b> {str(full_foods_list['food'][x])} </b> {str(full_foods_list['count'][x])} x "
                  f"{cost} = {generalcost} {text8} ;\n")

    full_info_text = (f"{text} \n {text1} {contact} \n {text3} {kitchen} \n {text4} {type_of_payment} \n"
                      f" {foods} {text5} {summa} {text8} \n {text7} {total} {text8}")

    chat_id = update.message.chat_id
    botss.send_message(chat_id=chat_id, text=full_info_text, parse_mode=telegram.ParseMode.HTML)

    custom_keyboard = [[text10, text11]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=False,
                                                resize_keyboard=True)
    botss.send_message(chat_id=chat_id, text=text9, reply_markup=reply_markup)

    return ACCEPTING


def foods(update, context):
    global uzbek, backing, food_name, category_id, \
        foods_list_selected, food_type_id

    if backing != 'number':
        text = update.message.text
        context.user_data['type of food'] = text
        user_data = context.user_data
        food_name = text

    backing = 'food'
    lang = 10

    if rus:
        lang = 1

    cursor = db.cursor()
    sql = (f"SELECT id FROM StoreCategory WHERE id IN ( SELECT object_id FROM "
           f"StoreCategoryTranslate WHERE NAME = '{food_name}') AND parent = '{category_id}'")
    logger.info(f"sql code {sql}")
    cursor.execute(sql)
    results = cursor.fetchone()
    # logger.info(f"in Food function inforation about category id = {results[0]}")
    # categoryId = ""
    # for result in results:
    #     categoryId = str(result[0])

    context.user_data["category_id"] = str(results[0])

    cursor = db.cursor()
    sql = (f"SELECT name, id from StoreProductTranslate WHERE language_id={lang} AND object_id IN "
           f"(SELECT id FROM StoreProduct WHERE id IN (SELECT product FROM StoreProductCategoryRef "
           f"WHERE category IN (SELECT id FROM StoreCategory WHERE id IN ( SELECT object_id FROM "
           f"StoreCategoryTranslate WHERE NAME = '{food_name}') AND parent = '{category_id}' ) GROUP BY product ) ) ")
    cursor.execute(sql)
    results = cursor.fetchall()
    new_list = []

    for result in results:
        new_list.append(result[0])
        foods_list_selected.append(result[1])

    if uzbek:
        text3 = "Mahsulotni tanlang: ⤵️"
    else:
        text3 = "Выберите продукт: ⤵"

    new_list = making_buttons(new_list)
    update.message.reply_text(text3, reply_markup=ReplyKeyboardMarkup(new_list,
                                                one_time_keyboard=False, resize_keyboard=True))
    return ADDITION


def kitchens(update, context):
    global uzbek, backing, kitchen_num,  kitchen_id, category_id

    if backing != 'food' or backing != 'number':
        text = update.message.text
        context.user_data['kitchen'] = text
        user_data = context.user_data

    backing = 'kitchen'

    cursor = db.cursor()
    sql = f"SELECT category_id FROM StoreManufacturerCategoryRef WHERE manufacturer_id ='{restaurant_id}'"
    cursor.execute(sql)
    resluts = cursor.fetchone()
    category_id = str(resluts[0])
    cursor = db.cursor()
    sql = f"SELECT name FROM StoreCategoryTranslate WHERE object_id IN" \
          f"( SELECT id FROM StoreCategory WHERE parent='{category_id}') and language_id= 9"
    cursor.execute(sql)
    resluts = cursor.fetchall()
    another_list = []

    for reslut in resluts:
        another_list.append(reslut[0])

    if uzbek:
        text4 = 'Ovqatlarni tanlang:⤵️'
    else:
        text4 = 'Выберите категорию:⤵️'

    another_list = making_buttons(another_list)
    update.message.reply_text(text4, reply_markup=ReplyKeyboardMarkup(another_list,
                                    one_time_keyboard=False, resize_keyboard=True))
    return FOODS


def location(update, context):
    global another_info, locationidentify, uzbek

    another_info = True
    locationidentify = True

    user = update.message.from_user
    user_location = update.message.location
    lat = user_location.latitude
    long = user_location.longitude

    context.user_data['location'] = "latitude = " + str(user_location.latitude) + " longitude = " + str(
        user_location.longitude)

    page = urllib.request.urlopen(f"https://geocode-maps.yandex.ru/1.x/?apikey="
                                  f"cba0604f-814b-4d44-9b9f-06e6ddc1926e&format=json&geocode={long},{lat}")
    page = json.loads(page.read())
    region = dict(page["response"]["GeoObjectCollection"]["featureMember"][2]["GeoObject"])
    region = region["metaDataProperty"]["GeocoderMetaData"]["text"]
    region = region.split(",")
    region = region[2]

    page = dict(page["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"])
    address = page["metaDataProperty"]["GeocoderMetaData"]["text"]
    address = address.split(",")
    address = str(address[2] + " , " + address[3])
    address1 = f"{region}, {address}"
    context.user_data['address'] = address1
    address = f"<b>🚩{region}, {address} ... </b>\n"

    if uzbek:
        text = "<b>Iltimos manzilingizni to'liq kiriting </b>🏢 (ko'cha, uy, xonadon)"
    else:
        text = "<b>Пожалуйста, введите свой полный адрес </b>🏢 (улица, дом, квартира)"

    text = address + text
    chat_id = update.message.chat_id
    reply_markup = telegram.ReplyKeyboardRemove()
    botss.sendMessage(chat_id=chat_id, text=text, reply_markup=reply_markup,
                      parse_mode=telegram.ParseMode.HTML)

    return ADDITION_LOCATION


def making_buttons(data):
    addinglist, ready_list = [], []
    n = 0
    for x in data:
        n = n + 1
        addinglist.append(x)

        if len(x) <= 20:
            if n == 3:
                ready_list.append(addinglist)
                addinglist = [];     n = 0

        elif len(x) >= 21 and len(x) <= 40:
            if n == 2 or n == 3:
                ready_list.append(addinglist)
                addinglist = [];     n = 0

        elif len(x) >= 41:
            if n == 1:
                ready_list.append(addinglist)
                addinglist = [];     n = 0

    ready_list.append(addinglist)

    if uzbek:
        text = ['⏪Orqaga', '📋Savatcha']
        text3 = ['🚖Yetkazib berish shartlari']
    else:
        text = ['⏪Назад', '📋Корзинка']
        text3 = ['🚖Условия доставки']

    ready_list.append(text)
    ready_list.append(text3)

    return ready_list


def numbers(update, context):
    global uzbek, backing, food_name, food_type_id,\
        restaurant_id, foods_list_selected

    backing = 'number'
    text = update.message.text
    food_name = text
    context.user_data['food'] = text
    user_data = context.user_data
    chat_id = update.message.chat_id

    if uzbek:
        text1 = '⏪Orqaga'
        text2 = '📋Savatcha'
        text3 = "Taom sonini tanlang yoki klaviaturadan kiriting ⤵️"
        text4 = "so'm"
    else:
        text1 = '⏪Назад'
        text2 = '📋Корзинка'
        text3 = "Выберите или введите количество продукта ⤵"
        text4 = "сум"

    tuples = str(tuple(foods_list_selected))
    cursor = db.cursor()
    sql = "SELECT * FROM StoreProductTranslate WHERE name = '" + text + "' and id IN " + tuples
    cursor.execute(sql)
    results = cursor.fetchall()
    other_list = []

    for result in results:
        other_list = list(result)

    object_id = str(other_list[1])
    name = str(other_list[3])
    ingredient = str(other_list[9])

    cursor = db.cursor()
    sql = "SELECT * FROM StoreProduct WHERE id = '" + object_id + "'"
    cursor.execute(sql)
    results = cursor.fetchall()
    other_list = []

    for result in results:
        other_list = list(result)

    product_id = str(other_list[0])
    context.user_data['productid'] = product_id
    cost = str(other_list[5])
    posuda = int(other_list[38])
    paket = int(other_list[39])
    cost = cost.split(".")
    cost = int(cost[0])
    cost = str(posuda + paket + cost)
    context.user_data['cost'] = cost

    head_cost = cost[:-5]
    other_cost = cost[-5:]
    cost = head_cost + " " + other_cost

    info = f"<b> {name} </b>\n {ingredient} .\n {cost} {text4}"

    # fullpath = f"https://bot.bringo.uz/images/{product_id}.jpg"
    # fullpath = "https://bot.bringo.uz/images/noimage.jpg"
    # logger.info(f"image {product_id} and fullpath {fullpath}")

    botss.send_photo(chat_id=chat_id, photo=open("test/hot dog.jpg", 'rb'), caption=info,
                     parse_mode=telegram.ParseMode.HTML)

    reply_keyboard = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9'], [text1, text2]]
    update.message.reply_text(text3, reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                         one_time_keyboard=False, resize_keyboard=True))

    return ANOTHER_ADD


def ordering(update, context):
    global backing, uzbek

    backing = 'backet'
    chat_id = update.message.chat_id

    if uzbek:
        text = "📍 Iltimos, lokatsiya jo'nating yoki 🚶 O'zim olib ketamanni tanlang"
        text0 = "📍 Lokatsiyani jo'natish"
        text1 = "🚶O'zim olib ketaman"
        text2 = "⏪Orqaga"

    else:
        text = "📍 Пожалуйста, отправьте локацию или 🚶 выберите Самовывоз"
        text0 = "📍 Отправьте локацию"
        text1 = "🚶Самовывоз"
        text2 = "⏪Назад"

    location_keyboard = telegram.KeyboardButton(text=text0, request_location=True)
    custom_keyboard = [[location_keyboard], [text1], [text2]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard,
                                                one_time_keyboard=False, resize_keyboard=True)

    update.message.reply_text(text, reply_markup=reply_markup)

    return LOCATION


def paying_with_location(update, context):
    global uzbek, backing

    backing = "paying_with_location"
    text = str(update.message.contact['phone_number'])
    context.user_data['contact'] = text
    chat_id = update.message.chat_id

    if uzbek:
        text = "Tulov turini tanlang ⤵️"
        text1 = "💸Naqd pul"
        text2 = "⏪Назад"
    else:
        text = "Выберите тип оплаты ⤵️"
        text1 = "💸Наличная"
        text2 = "⏪Orqaga"

    custom_keyboard = [[text1], [text2]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard,
                                                one_time_keyboard=False, resize_keyboard=True)
    botss.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

    return FULL_INFO_WITH_LOCATION


def paying_with_contact(update, context):
    global uzbek, backing

    backing = "paying_with_contact"
    text = str(update.message.contact['phone_number'])
    context.user_data['contact'] = text
    chat_id = update.message.chat_id

    if uzbek:
        text = "Tulov turini tanlang ⤵️"
        text1 = "💸Naqd pul"
        text2 = "⏪Orqaga"
    else:
        text = "Выберите тип оплаты ⤵️"
        text1 = "💸Наличная"
        text2 = "⏪Назад"

    custom_keyboard = [[text1], [text2]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard,
                                                one_time_keyboard=False, resize_keyboard=True)
    botss.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

    return FULL_INFO


def start(update, context):
    global user, restaurant_id, backing, \
        uzbek, rus, full_foods_list

    chat_id = update.message.chat_id
    context.user_data.clear()
    full_foods_list = {}

    if backing == 'language' and uzbek:
        botss.send_message(chat_id=chat_id, text="Sizning savatchangiz bo'm bo'sh⚠")

    if backing == 'language' and rus:
        botss.send_message(chat_id=chat_id, text = "Ваш корзина пуста⚠")

    cursor = db.cursor()
    sql = "SELECT * FROM StoreManufacturerImage where manufacturer_id ='" + str(restaurant_id) + "'"
    cursor.execute(sql)
    results = cursor.fetchone()
    url = results[0]

    reply_keyboard = [['🇺🇿Uzbek tili🇺🇿', '🇷🇺Rus tili🇷🇺']]
    user = update.message.from_user
    context.user_data["first_name"] = user.first_name

    tx = "Asalomu Alaykum! \n Здравствуйте <b>" + user.first_name + "!</b>\n🇺🇿Tilini tanlang \n🇷🇺Выберите язык"

    reply_markup = telegram.ReplyKeyboardMarkup(reply_keyboard,
                                                one_time_keyboard=False, resize_keyboard=True)
    info = "Uzbek cultural foods "

    botss.send_photo(chat_id=chat_id, photo=open("test/samsa.jpg", 'rb'), caption=info)
    botss.send_message(chat_id=chat_id, text=tx,
                       parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)

    return LANGUAGES


def reject(update, context):
    global full_foods_list, uzbek

    if uzbek:
        text = "Sizning buyutmangiz bekor qilindi"
    else:
        text = "Ваш заказ был отменен"

    chat_id = update.message.chat_id
    context.user_data.clear()
    full_foods_list = {}
    botss.send_message(chat_id=chat_id, text=text)

    return start(update, context)


def yes_no_accepting(update, context):
    global uzbek

    if uzbek:
        text = "O'z buyurtmangizni tasdiqlang"
        text1 = "🚫Bekor qilish"
        text2 = "✅Tasdiqliman"

    else:
        text = "Пожалуйста, подтвердите ваш заказ"
        text1 = "🚫Отмена"
        text2 = "✅Я в подтверждении"

    chat_id = update.message.chat_id
    custom_keyboard = [[text1, text2]]
    repy_markup = telegram.ReplyKeyboardMarkup(custom_keyboard,
                                               one_time_keyboard=False, resize_keyboard=True)
    botss.send_message(chat_id=chat_id, text=text, reply_markup=repy_markup)

    return CHECKING