import asyncio, tarfile, logging, sqlite3, configparser
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes, MessageHandler, filters, CallbackQueryHandler

import xml.etree.ElementTree as ET
import datetime


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
conn = sqlite3.connect("data.db")
cursor = conn.cursor()


def database_query(query):    
    cursor.execute(query)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    variant = query.data
    query.answer()    
    if variant == '3':
        await check_device(update, context)
    if variant == '5':
        await check_system(update, context)
    if variant == '6':
        await find_system_by_report(update, context)
    if variant == '8':
        await add_new_device(update, context)
    if variant == '9':
        #TODO результаты проверки
        await continue_work(update, context)
    if variant == '10':
        await find_system_by_name(update, context)
        await check_config(update, context)
    if variant == '12':
        await check_device_list(update, context)
        
        #await query.edit_message_text(text="Введите название устройства в системе")
        #context.bot.send_message(chat_id=update.effective_chat.id, text="Добавьте файл отчета")
    #await query.edit_message_text(text=f"Выбранный вариант: {variant}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет, чем помочь?")
    keyboard = [
        [InlineKeyboardButton("Проверить устройчтво", callback_data='3'),
        InlineKeyboardButton("Проверить систему", callback_data='5'),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Сделайте выбор:', reply_markup=reply_markup)


async def continue_work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Вам помочь чем-то ещё?")
    keyboard = [
        [InlineKeyboardButton("Проверить устройчтво", callback_data='3'),
        InlineKeyboardButton("Проверить систему", callback_data='5'),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Сделайте выбор:', reply_markup=reply_markup)


async def check_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Как вы хотите найти систему?")
    keyboard = [
        [InlineKeyboardButton("Найти систему по отчету", callback_data='6'),
        InlineKeyboardButton("Найти систему по названию", callback_data='10'),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Сделайте выбор:', reply_markup=reply_markup)


def parse_tar(input_file_name, output_file_name):
    with tarfile.open("C:\\Users\\User\\Desktop\\hakaton\\AlexandriasTeam_PEH\\temp\\"+input_file_name) as f:
        for line in f.getnames():
            if line == output_file_name:
                f.extract(line, "C:\\Users\\User\\Desktop\\hakaton\\AlexandriasTeam_PEH\\temp\\")


async def check_system_sql(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sys_name = update.message.text
    database_query("SELECT name FROM SYSTEMS")
    for system_name in cursor.fetchall():
        if system_name == sys_name:
            add_new_device()


async def check_device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Добавьте файл отчета")
    #TODO вывод данных, и предложение продолжить.
    await send_arch(update, context)
    await continue_work(update, context)


async def find_system_by_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Найдена система: ")
    #TODO парсер
    await check_config(update, context)


async def find_system_by_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите название системы")
    #TODO ввод названия
    #Поиск системы


async def add_new_device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите название устройства в системе")
    #TODO add dev_name
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Добавьте файл отчета")
    #TODO send report
    
    keyboard = [
        [InlineKeyboardButton("Да", callback_data='8'),
        InlineKeyboardButton("Нет", callback_data='9'),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Добавить еще устройство?', reply_markup=reply_markup)


async def check_device_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #TODO список устройств вывод 
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Добавьте файл отчета")
    await send_arch(update, context)
    #TODO закидываем файл
    keyboard = [
        [InlineKeyboardButton("Да", callback_data='12'),
        InlineKeyboardButton("Нет", callback_data='9'),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Добавить еще устройство?', reply_markup=reply_markup) 


async def check_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Создать вариант конфигурации?")
    keyboard = [
        [InlineKeyboardButton("Добавить новое устройство", callback_data='8'),
        InlineKeyboardButton("Список устройств", callback_data='12'),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Сделайте выбор:', reply_markup=reply_markup)


async def send_arch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arch_id = update.message.document.file_id
    newFile = await context.bot.get_file(arch_id)
    await newFile.download_to_drive(custom_path="C:\\Users\\User\\Desktop\\hakaton\\AlexandriasTeam_PEH\\temp\\text.tar")
    line_list=[]
    parse_tar("text.tar", "package.tar.gz")
    parse_tar("package.tar.gz", "arc_view.txt")
    parse_tar("package.tar.gz", "license.xml")
    parse_tar("package.tar.gz", "date.txt")
    with open("C:\\Users\\User\\Desktop\\hakaton\\AlexandriasTeam_PEH\\temp\\arc_view.txt", encoding='UTF-8') as f:
        for line in f:
            if line.strip():
                line_list.append(line)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=line_list[0])

    root_node = ET.parse('temp\\license.xml').getroot()      
    sn_tag = root_node.find('sn')
    sn_text = sn_tag.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text=sn_text)

    file_date = open('temp\\date.txt').read()
    log_date = datetime.datetime.strptime(file_date.strip(), '%a %b %d %H:%M:%S %Z %Y')
    str_time = log_date.strftime("%d/%m/%Y %H:%M:%S")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=str_time)

    #await context.bot.get_file(file_id=update.message.document.file_id)
     

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("config.ini")
    application = ApplicationBuilder().token(config["param1"]["TOKEN"]).build()
    start_handler = CommandHandler('start', start)
    send_arch_handler = CommandHandler('send_arch', send_arch)

    tar_file_handler = MessageHandler(filters.Document.FileExtension("tar"), callback=send_arch)
    targz_file_handler = MessageHandler(filters.Document.TARGZ, callback=send_arch)

    application.add_handler(start_handler)
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(tar_file_handler)
    application.add_handler(targz_file_handler)
    application.add_handler(send_arch_handler)
    application.run_polling()

