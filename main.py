import asyncio, tarfile, logging, sqlite3, configparser
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes, MessageHandler, filters, CallbackQueryHandler, ConversationHandler


import xml.etree.ElementTree as ET
import datetime
import re
import json


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BUTTON, WRITE_NEW_SYSTEM, WRITE_NEW_DEV, SEND_DOCS_TAR, CHECK_CONFIG, CONT_WORK, ADD_REP, ADD_DEV = range(8)

conn = sqlite3.connect("data.db")
cursor = conn.cursor()

name_system = ''



def database_query(query, dt, type):    
    cursor.execute(query, dt)
    if type == "INSERT":
            conn.commit()
    if type == "SELECT":
            cursor.fetchall()


def convert_to_binary_data(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    variant = query.data
    query.answer()

    if variant == '3':
        await check_device(update, context)
        return SEND_DOCS_TAR
    if variant == '5':
        await check_system(update, context)
    if variant == '6':
        await find_system_by_report(update, context)
    if variant == '8':
        await add_new_device(update, context)
        return WRITE_NEW_DEV
    if variant == '9':
        #TODO результаты проверки
        await continue_work(update, context)
    if variant == '10':
        await find_system_by_name(update, context)
        return WRITE_NEW_SYSTEM
    if variant == '12':
       await check_device_list(update, context)
       return SEND_DOCS_TAR
       
        
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
    return BUTTON


async def continue_work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Вам помочь чем-то ещё?")
    keyboard = [
        [InlineKeyboardButton("Проверить устройчтво", callback_data='3'),
        InlineKeyboardButton("Проверить систему", callback_data='5'),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Сделайте выбор:', reply_markup=reply_markup)
    return BUTTON


async def check_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Как вы хотите найти систему?")
    keyboard = [
        [InlineKeyboardButton("Найти систему по отчету", callback_data='6'),
        InlineKeyboardButton("Найти систему по названию", callback_data='10'),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Сделайте выбор:', reply_markup=reply_markup)


def parse_tar(input_file_name, output_file_name):
    with tarfile.open(config["param2"]["TEMP_DIR"]+input_file_name) as f:
        for line in f.getnames():
            if line == output_file_name:
                f.extract(line, config["param2"]["TEMP_DIR"])


async def check_system_sql(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sys_name = update.message.text
    database_query("SELECT name FROM SYSTEMS")
    for system_name in cursor.fetchall():
        if system_name == sys_name:
            add_new_device()    


async def check_device(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Добавьте файл отчета")
    #TODO вывод данных, и предложение продолжить.



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

async def add_report_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    


async def add_more_devices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
        InlineKeyboardButton("Да", callback_data='12'),
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
    return BUTTON

async def create_new_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name_system = update.message.text
    sqlite_insert_blob_query = """ INSERT INTO SYSTEMS
                                  ( name, version) VALUES ( ?, ?)"""
    data_tuple = (name_system, '1')                              
    database_query(sqlite_insert_blob_query, data_tuple, "INSERT")
    #await check_config(update, context)
    return WRITE_NEW_DEV
    


async def create_new_device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arch_id = update.message.document.file_id
    newFile = await context.bot.get_file(arch_id)
    await newFile.download_to_drive(custom_path=config["param2"]["TEMP_DIR"]+"text.tar")
    line_list=[]
    parse_tar("text.tar", "package.tar.gz")
    parse_tar("package.tar.gz", "arc_view.txt")
    parse_tar("package.tar.gz", "license.xml")
    parse_tar("package.tar.gz", "date.txt")
    with open(config["param2"]["TEMP_DIR"]+"arc_view.txt", encoding='UTF-8') as f:
        for line in f:
            if line.strip():
                line_list.append(line)
                
    root_node = ET.parse(config["param2"]["TEMP_DIR"]+"license.xml").getroot()      
    sn_tag = root_node.find('sn')
    sn_text = sn_tag.text    

    file_date = open(config["param2"]["TEMP_DIR"]+"date.txt").read()
    log_date = datetime.datetime.strptime(file_date.strip(), '%a %b %d %H:%M:%S %Z %Y')
    str_time = log_date.strftime("%d/%m/%Y %H:%M:%S")

    st = update.message.text
    sqlite_insert_blob_query = """ INSERT INTO DEVICES
                                  ( systemid,  name, file, data) VALUES ( ?, ?, ?, ?)"""
    cursor.execute("""SELECT id FROM SYSTEMS WHERE name = ?""", (name_system))
    res = cursor.fetchone()
    data_tuple = (res, sn_text, convert_to_binary_data(config["param2"]["TEMP_DIR"]+"text.tar"), str_time )                              
    database_query(sqlite_insert_blob_query, data_tuple, "INSERT")


async def send_arch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    arch_id = update.message.document.file_id
    newFile = await context.bot.get_file(arch_id)
    await newFile.download_to_drive(custom_path=config["param2"]["TEMP_DIR"]+"text.tar")
    line_list=[]
    parse_tar("text.tar", "package.tar.gz")
    parse_tar("package.tar.gz", "arc_view.txt")
    parse_tar("package.tar.gz", "license.xml")
    parse_tar("package.tar.gz", "date.txt")
    with open(config["param2"]["TEMP_DIR"]+"arc_view.txt", encoding='UTF-8') as f:
        for line in f:
            if line.strip():
                line_list.append(line)
    #await context.bot.send_message(chat_id=update.effective_chat.id, text=line_list[0])

    root_node = ET.parse(config["param2"]["TEMP_DIR"]+"license.xml").getroot()      
    sn_tag = root_node.find('sn')
    sn_text = sn_tag.text
    #await context.bot.send_message(chat_id=update.effective_chat.id, text=sn_text)
    

    file_date = open(config["param2"]["TEMP_DIR"]+"date.txt").read()
    log_date = datetime.datetime.strptime(file_date.strip(), '%a %b %d %H:%M:%S %Z %Y')
    str_time = log_date.strftime("%d/%m/%Y %H:%M:%S")
    #await context.bot.send_message(chat_id=update.effective_chat.id, text=str_time)
    sqlite_insert_blob_query = """ INSERT INTO SingleDEVICES
                                  ( name, file, data) VALUES ( ?, ?, ?)"""
    data_tuple = (sn_text, convert_to_binary_data(config["param2"]["TEMP_DIR"]+"text.tar"), str_time)                              
    database_query(sqlite_insert_blob_query, data_tuple, "INSERT")
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Серийный номер устройства: " +sn_text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Дата: " +str_time)

    await validate_rules(update, context, line_list)
    #await context.bot.get_file(file_id=update.message.document.file_id)
    #await continue_work(update, context)
    #return CONT_WORK
     
async def validate_rules(update: Update, context: ContextTypes.DEFAULT_TYPE, line_list):
    with open("rules.json", 'r') as f:
        data = json.load(f)
        for value in data.keys():
            for line in line_list:
                example = re.search(value, line, re.I)
                if (example):
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=line)
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=data.get(value))
 


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    application = ApplicationBuilder().token(config["param1"]["TOKEN"]).build()
    start_handler = CommandHandler('start', start)
    send_arch_handler = CommandHandler('send_arch', send_arch)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            BUTTON:[
                CallbackQueryHandler(button)
            ],
            SEND_DOCS_TAR:[
                MessageHandler(
                    filters.Document.FileExtension("tar"), send_arch
                )
            ],
            WRITE_NEW_SYSTEM:[
                MessageHandler(filters.TEXT, create_new_system)
            ],
            WRITE_NEW_DEV:[
                MessageHandler(filters.Document.FileExtension("tar"), create_new_device)
            ],
            CHECK_CONFIG:[
                CommandHandler("check_config", check_config)
            ],
            CONT_WORK:[
                CommandHandler("continue_work", continue_work)
            ],
            ADD_REP:[
                CommandHandler("add_report_file", add_report_file)
            ],
            ADD_DEV:[
                CommandHandler("add_more_devices", add_more_devices)
            ],
        },
        fallbacks=[CommandHandler("start", start)]
    )

    tar_file_handler = MessageHandler(filters.Document.FileExtension("tar"), callback=send_arch)
    targz_file_handler = MessageHandler(filters.Document.TARGZ, callback=send_arch)

    #application.add_handler(start_handler)    
    application.add_handler(conv_handler)
    #application.add_handler(CallbackQueryHandler(button))
    #application.add_handler(tar_file_handler)
    #application.add_handler(targz_file_handler)
    #application.add_handler(send_arch_handler)
    application.run_polling()

