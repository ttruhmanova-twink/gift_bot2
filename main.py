import logging
import json
import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_LINK = os.getenv('CHANNEL_LINK')
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME')
YANDEX_DISK_LINK = os.getenv('YANDEX_DISK_LINK')
PROCESSING_LINK = os.getenv("PROCESSING_LINK")
POLITICS_LINK = os.getenv("POLITICS_LINK")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # ID администратора

# Файл для хранения данных пользователей
USERS_FILE = "users.json"

def load_users():
    """Загружает список пользователей из файла"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_user(user_data):
    """Сохраняет пользователя в файл"""
    users = load_users()
    
    # Проверяем, есть ли уже такой пользователь
    for user in users:
        if user['user_id'] == user_data['user_id']:
            return  # Пользователь уже есть
    
    users.append(user_data)
    
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def get_users_text():
    """Формирует текст со списком пользователей"""
    users = load_users()
    
    if not users:
        return "📭 Пока никто не забрал подарок"
    
    text = f"🎁 <b>Список пользователей, забравших подарок</b>\n\n"
    text += f"📊 <b>Всего:</b> {len(users)}\n"
    text += "─" * 30 + "\n\n"
    
    for i, user in enumerate(users, 1):
        text += f"<b>{i}.</b> "
        text += f"🆔 {user['user_id']}\n"
        if user.get('username'):
            text += f"   📝 @{user['username']}\n"
        if user.get('first_name'):
            text += f"   👤 {user['first_name']} {user.get('last_name', '')}\n"
        text += f"   📅 {user['date']}\n\n"
    
    return text

# Инициализация бота и диспетчера (исправленный вариант)
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Создаем клавиатуры
consent_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Согласен", callback_data="consent")]
    ]
)

get_material_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Забрать подарок 🎁", callback_data="get_material")]
    ]
)

check_subscription_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subscription")]
    ]
)

# Клавиатура для скачивания с Яндекс.Диска
download_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📥 Скачать материал", url=YANDEX_DISK_LINK)]
    ]
)

# Админ-клавиатура
def get_admin_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_users")],
        ]
    )

@dp.message(Command("start"))
async def start(message: Message):
    """Обработчик команды /start"""
    user = message.from_user
    
    # Если это админ - показываем дополнительную клавиатуру
    if user.id == ADMIN_ID:
        text = (
            "👋 Добро пожаловать, администратор!\n\n"
            "Вас приветствует бот-помощник Татьяны Ручкиной.\n\n"
            "Выберите действие:"
        )
        await message.answer(
            text,
            reply_markup=get_admin_keyboard()
        )
    else:
        text = (
            "👋 Добро пожаловать!\n\n"
            "Вас приветствует бот-помощник Татьяны Ручкиной.\n\n"
            "Для продолжения работы и получения доступа к материалам необходимо нажать на кнопку ниже.\n\n"
            "Этим действием вы подтверждаете <a href='{process_link}'>свое согласие на обработку персональных данных</a> в соответствии с <a href='{politics_link}'>Политикой обработки персональных данных</a>\n\n"
            "Нажмите на кнопку 👇"
        ).format(process_link=PROCESSING_LINK, politics_link=POLITICS_LINK)
        
        await message.answer(
            text, 
            reply_markup=consent_keyboard,
            disable_web_page_preview=True
        )

@dp.callback_query(F.data.in_(["admin_users", "admin_stats"]))
async def admin_handlers(callback: CallbackQuery):
    """Обработчик админских кнопок"""
    user = callback.from_user
    
    if user.id != ADMIN_ID:
        await callback.answer("У вас нет прав администратора", show_alert=True)
        return
    
    if callback.data == "admin_users":
        text = get_users_text()
        await callback.message.answer(
            text,
            parse_mode=ParseMode.HTML,
            # disable_web_page_preview=True
        )
    
    elif callback.data == "admin_stats":
        users = load_users()
        text = (
            "📊 **Статистика бота**\n\n"
            f"👥 Всего забрали подарок: **{len(users)}**\n"
            "─" * 20 + "\n"
        )
        await callback.message.answer(
            text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    await callback.answer()

@dp.callback_query(F.data == "consent")
async def consent_handler(callback: CallbackQuery):
    """Обработчик согласия"""
    text = (
        "📋 <b>ЧТОБЫ ПОЛУЧИТЬ ПОДАРОК</b>\n\n"
        "👇 Просто нажмите на кнопку ниже:\n"
    ).format(channel_link=CHANNEL_LINK)
    
    await callback.message.answer(
        text, 
        reply_markup=get_material_keyboard,
        disable_web_page_preview=True
    )
    await callback.answer()

@dp.callback_query(F.data == "get_material")
async def get_material_handler(callback: CallbackQuery):
    """Обработчик получения материала"""
    user = callback.from_user
    user_id = user.id
    
    # Сохраняем информацию о пользователе
    user_data = {
        'user_id': user_id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name if user.last_name!= 'None' else "",
        'date': callback.message.date.strftime("%Y-%m-%d %H:%M")
    }
    save_user(user_data)
    
    # Проверяем подписку на канал
    try:
        
        # Пользователь подписан - выдаем ссылку
        text = (
            "🎉 Поздравляем! Вы получили доступ к подарку!\n\n"
            "📚 «Как пройти правильный чекап после 40»\n\n"
            "⬇️ Нажмите кнопку ниже для скачивания:"
        )
        
        await callback.message.answer(
            text,
            reply_markup=download_keyboard,
            disable_web_page_preview=True
        )
            
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        text = (
            "⚠️ Не могу проверить подписку.\n\n"
            "Пожалуйста, убедитесь что подписались на канал <a href='{channel_link}'>Энергия и стройность с Татьяной Ручкиной</a> и нажмите кнопку ниже.\n\n"
            "<i>Если проблема повторяется, администратору нужно добавить бота в канал как администратора.</i>"
        ).format(channel_link=CHANNEL_LINK)
        await callback.message.answer(
            text,
            reply_markup=check_subscription_keyboard,
            disable_web_page_preview=True
        )
    
    await callback.answer()

async def main():
    """Основная функция запуска бота"""
    # Проверяем наличие токена
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не найден в переменных окружения!")
        return
    
    logger.info("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
