import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Конфигурация бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_LINK = os.getenv('CHANNEL_LINK')
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME')
YANDEX_DISK_LINK = os.getenv('YANDEX_DISK_LINK')
PROCESSING_LINK = os.getenv("PROCESSING_LINK")
POLITICS_LINK = os.getenv("POLITICS_LINK")

# Создаем клавиатуры
consent_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Согласен", callback_data="consent")]
])

get_material_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Забрать подарок 🎁", callback_data="get_material")]
])

check_subscription_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription")]
])

# Клавиатура для скачивания с Яндекс.Диска
download_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("📥 Скачать материал", url=YANDEX_DISK_LINK)]
])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    text = (
        "👋 Добро пожаловать!\n\n"
        "Вас приветствует бот-помощник Татьяны Ручкиной.\n\n"
        "Для продолжения работы и получения доступа к материалам необходимо нажать на кнопку ниже.\n\n"
        "Этим действием вы подтверждаете <a href='{process_link}'>свое согласие на обработку персональных данных</a> в соответствии с <a href='{politics_link}'>Политикой обработки персональных данных</a>\n\n"
        "Нажмите на кнопку 👇"
    ).format(process_link=PROCESSING_LINK, politics_link=POLITICS_LINK)
    
    await update.message.reply_text(
        text, 
        reply_markup=consent_keyboard,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на инлайн кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "consent":
        text = (
            "📋 <b>ИНСТРУКЦИЯ ПО ПОЛУЧЕНИЮ ПОДАРКА</b>\n\n"
            "▫️ <b>Шаг 1.</b> Подпишитесь на канал:\n"
            "   👉 <a href='{channel_link}'>Энергия и стройность с Татьяной Ручкиной</a>\n\n"
            "▫️ <b>Шаг 2.</b> Вернитесь в бот и нажмите кнопку:\n"
            "   🎁 <i>«Забрать подарок»</i>\n\n"
            "✨ <b>Результат:</b> Мгновенный доступ к материалу\n"
            "   📌 «3 варианта ужинов для вечерней сытости и лёгкости после 40»\n"
        ).format(channel_link=CHANNEL_LINK)
        await query.message.reply_text(
            text, 
            reply_markup=get_material_keyboard, 
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
    
    elif query.data == "get_material":
        user_id = query.from_user.id
        
        # Проверяем подписку на канал
        try:
            chat_member = await context.bot.get_chat_member(
                chat_id=CHANNEL_USERNAME, 
                user_id=user_id
            )
            
            # Статусы, которые считаются подпиской
            valid_statuses = ["member", "administrator", "creator"]
            
            if chat_member.status in valid_statuses:
                # Пользователь подписан - выдаем ссылку на Яндекс.Диск
                text = (
                    "🎉 Поздравляем! Вы получили доступ к подарку!\n\n"
                    "📚 «3 варианта ужинов для вечерней сытости и лёгкости после 40»\n\n"
                    "⬇️ Нажмите кнопку ниже для мгновенного скачивания:"
                )
                
                # Отправляем фото с поздравлением и кнопкой скачивания
                try:
                    await query.message.reply_text(
                        text,
                        reply_markup=download_keyboard,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                except FileNotFoundError:
                    # Если фото не найдено, отправляем текст с кнопкой
                    await query.message.reply_text(
                        text,
                        reply_markup=download_keyboard,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
            else:
                # Пользователь не подписан
                text = (
                    "❌ Вы не подписаны на канал!\n\n"
                    "Пожалуйста, подпишитесь на канал <a href='{channel_link}'>Энергия и стройность с Татьяной Ручкиной</a> и нажмите кнопку ниже для проверки."
                ).format(channel_link=CHANNEL_LINK)
                await query.message.reply_text(
                    text,
                    reply_markup=check_subscription_keyboard,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
                
        except Exception as e:
            # Если бот не может проверить подписку
            logging.error(f"Ошибка проверки подписки: {e}")
            text = (
                "⚠️ Не могу проверить подписку.\n\n"
                "Пожалуйста, убедитесь что подписались на канал <a href='{channel_link}'>Энергия и стройность с Татьяной Ручкиной</a> и нажмите кнопку ниже.\n\n"
                "<i>Если проблема повторяется, администратору нужно добавить бота в канал как администратора.</i>"
            ).format(channel_link=CHANNEL_LINK)
            await query.message.reply_text(
                text,
                reply_markup=check_subscription_keyboard,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
    
    elif query.data == "check_subscription":
        user_id = query.from_user.id
        
        # Повторная проверка подписки
        try:
            chat_member = await context.bot.get_chat_member(
                chat_id=CHANNEL_USERNAME, 
                user_id=user_id
            )
            
            valid_statuses = ["member", "administrator", "creator"]
            
            if chat_member.status in valid_statuses:
                text = (
                    "✅ Отлично! Подписка подтверждена!\n\n"
                    "🎉 Теперь вы можете получить ваш подарок!\n\n"
                    "📚 «3 варианта ужинов для вечерней сытости и лёгкости после 40»\n\n"
                    "⬇️ Нажмите кнопку ниже для скачивания:"
                )
                await query.message.reply_text(
                    text,
                    reply_markup=download_keyboard,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
            else:
                text = (
                    "❌ Вы все еще не подписаны на канал!\n\n"
                    "Пожалуйста, подпишитесь на канал <a href='{channel_link}'>Энергия и стройность с Татьяной Ручкиной</a> и нажмите кнопку ниже для проверки."
                ).format(channel_link=CHANNEL_LINK)
                await query.edit_message_text(
                    text,
                    reply_markup=check_subscription_keyboard,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
                
        except Exception as e:
            logging.error(f"Ошибка проверки подписки: {e}")
            text = (
                "⚠️ Все еще не могу проверить подписку.\n\n"
                "Пожалуйста, убедитесь что подписались на канал <a href='{channel_link}'>Энергия и стройность с Татьяной Ручкиной</a> и попробуйте снова."
            ).format(channel_link=CHANNEL_LINK)
            await query.edit_message_text(
                text,
                reply_markup=check_subscription_keyboard,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )


def main():
    """Основная функция запуска бота"""
    # Проверяем наличие токена
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN не найден в переменных окружения!")
        return
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Запускаем бота
    print("Бот запущен! Для остановки нажмите Ctrl+C")
    application.run_polling()

if __name__ == "__main__":
    main()