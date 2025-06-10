import asyncio
from telethon import functions
from telethon.tl.types import InputReportReasonSpam
from hikka import loader, utils

@loader.tds
class Reporter(loader.Module):
    """Модуль для автоматической отправки репортов на сообщения в Telegram"""

    strings = {"name": "Reporter"}

    def __init__(self):
        self.reporting = False
        self.report_task = None
        self.spinner_task = None
        self.progress_message = None

    @loader.command()
    async def reporty(self, message):
        """Начать отправку 50 репортов на последнее сообщение или сообщение, на которое дан ответ"""
        if self.reporting:
            await utils.answer(message, "Репорты уже отправляются.")
            return
        self.reporting = True
        self.report_task = asyncio.create_task(self.send_reports(message))
        await utils.answer(message, "Начинаю отправку 50 репортов.")

    @loader.command()
    async def reportn(self, message):
        """Остановить отправку репортов"""
        if not self.reporting:
            await utils.answer(message, "Репорты не отправляются.")
            return
        self.reporting = False
        if self.report_task:
            self.report_task.cancel()
        if self.spinner_task:
            self.spinner_task.cancel()
            self.spinner_task = None
        if self.progress_message:
            await self.progress_message.edit("Отправка репортов остановлена.")
        await utils.answer(message, "Отправка репортов остановлена.")

    async def send_reports(self, message):
        """Функция для отправки репортов"""
        try:
            # Определяем сообщение для репорта
            if message.is_reply:
                target_msg = await message.get_reply_message()
            else:
                # Берем последнее сообщение перед командой
                async for msg in message.client.iter_messages(message.chat_id, limit=2):
                    if msg.id != message.id:
                        target_msg = msg
                        break
                else:
                    await utils.answer(message, "Нет сообщения для репорта.")
                    return

            # Отправляем начальное сообщение со спиннером
            self.progress_message = await utils.answer(message, "Отправка репортов: |")
            # Запускаем задачу спиннера
            self.spinner_task = asyncio.create_task
