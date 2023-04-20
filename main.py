import asyncio, tarfile, logging, sqlite3, configparser
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, MenuButton
from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes, MessageHandler, filters, CallbackQueryHandler


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
conn = sqlite3.connect("data.db")
cursor = conn.cursor()

def database_query(query):    
    cursor.execute(query)

async def button(update: Update, _):
    query = update.callback_query
    variant = query.data
    query.answer()
    
    await query.edit_message_text(text=f"Выбранный вариант: {variant}", reply_markup=check_device)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет, чем помочь?")
    keyboard = [
        [InlineKeyboardButton("Проверить устройчтво", callback_data='1'),
        InlineKeyboardButton("Проверить систему", callback_data='2'),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Сделайте выбор:', reply_markup=reply_markup)


def parse_tar(input_file_name, output_file_name):
    with tarfile.open("/home/art/HAckaton/dw/"+input_file_name) as f:
        for line in f.getnames():
            if line == output_file_name:
                f.extract(line, "/home/art/HAckaton/dw/")

async def check_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sys_name = update.message.text
    database_query("SELECT name FROM SYSTEMS")
    for system_name in cursor.fetchall():
        if system_name == sys_name:
            add_new_device()

async def check_device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Добавьте файл отчета")


async def send_arch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arch_id = update.message.document.file_id
    newFile = await context.bot.get_file(arch_id)
    await newFile.download_to_drive(custom_path="/home/art/HAckaton/dw/text.tar")
    line_list=[]
    parse_tar("text.tar", "package.tar.gz")
    parse_tar("package.tar.gz", "arc_view.txt")
    with open("/home/art/HAckaton/dw/arc_view.txt", encoding='UTF-8') as f:
        for line in f:
            if line.strip():
                line_list.append(line)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=line_list[0])
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

