import os
from asgiref.sync import sync_to_async
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'botproject.settings')

import django
django.setup()  

from dotenv import load_dotenv
load_dotenv()

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from core.models import Person
from django.core.files.base import ContentFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'botproject.settings')
django.setup()

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Bot config (aiogram 3.7+ syntax)
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

class Form(StatesGroup):
    first_name = State()
    last_name = State()
    photo = State()
    description = State()
    facts = State()

@router.message(F.text == "/start")
async def start(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer("Привет! Введи имя человека:")
    await state.set_state(Form.first_name)

@router.message(Form.first_name)
async def get_first(msg: types.Message, state: FSMContext):
    await state.update_data(first_name=msg.text)
    await msg.answer("Теперь фамилию (или '-' если не нужно):")
    await state.set_state(Form.last_name)

@router.message(Form.last_name)
async def get_last(msg: types.Message, state: FSMContext):
    last = '' if msg.text.strip() == '-' else msg.text
    await state.update_data(last_name=last)
    await msg.answer("Отправь фото:")
    await state.set_state(Form.photo)

@router.message(Form.photo, F.photo)
async def get_photo(msg: types.Message, state: FSMContext):
    photo = msg.photo[-1]
    file = await bot.download(photo.file_id)
    photo_data = file.read()
    await state.update_data(photo=photo_data)
    await msg.answer("Теперь опиши человека:")
    await state.set_state(Form.description)

@router.message(Form.description)
async def get_desc(msg: types.Message, state: FSMContext):
    await state.update_data(description=msg.text)
    await msg.answer("Последний шаг — факты о человеке:")
    await state.set_state(Form.facts)

@router.message(Form.facts)
async def get_facts(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    person = Person(
        first_name=data["first_name"],
        last_name=data["last_name"],
        description=data["description"],
        facts=msg.text,
    )
    await sync_to_async(person.photo.save)("photo.jpg", ContentFile(data["photo"]), save=True)
    await sync_to_async(person.save)()

    await msg.answer(f"✅ Анкета <b>{person.first_name}</b> сохранена!")
    await state.clear()

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
