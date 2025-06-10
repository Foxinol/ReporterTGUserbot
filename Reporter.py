import asyncio
from telethon import functions
from telethon.tl.types import InputReportReasonSpam
from telethon import TelegramClient
from telethon.sessions import StringSession
from hikka import loader, utils

@loader.tds
class Reporter(loader.Module):
    """Модуль для автоматической отправки репортов на сообщения в Telegram с поддержкой прокси"""

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
                async for msg in message.client.iter_messages(message.chat_id, limit=2):
                    if msg.id != message.id:
                        target_msg = msg
                        break
                else:
                    await utils.answer(message, "Нет сообщения для репорта.")
                    return

            # Отправляем начальное сообщение со спиннером
            self.progress_message = await utils.answer(message, "Отправка репортов: |")
            self.spinner_task = asyncio.create_task(self.update_spinner())

            for _ in range(50):
                if not self.reporting:
                    break
                await message.client(functions.messages.ReportRequest(
                    peer=message.chat_id,
                    id=[target_msg.id],
                    reason=InputReportReasonSpam(),
                    message='Автоматический репорт на спам'
                ))
                await asyncio.sleep(1)  # Задержка для предотвращения лимитов

            if self.progress_message:
                await self.progress_message.edit("Отправка 50 репортов завершена.")
        except Exception as e:
            if self.progress_message:
                await self.progress_message.edit(f"Ошибка: {str(e)}")
            else:
                await utils.answer(message, f"Ошибка: {str(e)}")
        finally:
            self.reporting = False
            if self.spinner_task:
                self.spinner_task.cancel()
                self.spinner_task = None
            self.progress_message = None

    async def update_spinner(self):
        """Функция для обновления спиннера"""
        spinner = ['|', '/', '-', '\\']
        i = 0
        try:
            while True:
                if self.progress_message:
                    await self.progress_message.edit(f"Отправка репортов: {spinner[i % 4]}")
                i += 1
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass

# Настройка клиента с прокси
async def main():
    api_id = YOUR_API_ID  # Замените на ваш API ID
    api_hash = 'YOUR_API_HASH'  # Замените на ваш API Hash
    session_str = 'YOUR_SESSION_STRING'  # Замените на вашу сессионную строку

    # Настройки прокси (SOCKS5)
    proxy = {
        'proxy_type': 'socks5',
        'addr': '127.0.0.1',  # Адрес прокси-сервера
        'port': 9050,         # Порт прокси-сервера
        'username': None,     # Имя пользователя (если требуется)
        'password': None,     # Пароль (если требуется)
        'rdns': True          # Разрешение DNS через прокси
    }

    # Инициализация клиента
    client = TelegramClient(StringSession(session_str), api_id, api_hash, proxy=proxy)
    await client.start()
    print("Клиент запущен с прокси.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
