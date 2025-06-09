import asyncio
from telethon import functions
from hikka import loader, utils

@loader.tds
class ReportModule(loader.Module):
    """Модуль для автоматической отправки жалоб на сообщения в Telegram"""

    strings = {"name": "ReportModule"}

    def __init__(self):
        self.reporting = False
        self.report_task = None

    @loader.command()
    async def reporty(self, message):
        """Начать отправку 50 жалоб на последнее сообщение"""
        if self.reporting:
            await utils.answer(message, "Отправка жалоб уже запущена.")
            return
        self.reporting = True
        self.report_task = asyncio.create_task(self.send_reports(message))
        await utils.answer(message, "Начинаю отправку 50 жалоб.")

    @loader.command()
    async def reportn(self, message):
        """Остановить отправку жалоб"""
        if not self.reporting:
            await utils.answer(message, "Отправка жалоб не запущена.")
            return
        self.reporting = False
        if self.report_task:
            self.report_task.cancel()
        await utils.answer(message, "Отправка жалоб остановлена.")

    async def send_reports(self, message):
        """Функция для отправки жалоб"""
        try:
            for _ in range(50):
                if not self.reporting:
                    break
                async for msg in message.client.iter_messages(message.chat_id, limit=1):
                    if msg.id != message.id:  # Не репортим само сообщение с командой
                        await message.client(functions.messages.ReportRequest(
                            peer=message.chat_id,
                            id=[msg.id],
                            reason='spam'
                        ))
                await asyncio.sleep(1)  # Пауза 1 секунда между жалобами
            await utils.answer(message, "Отправка 50 жалоб завершена.")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            await utils.answer(message, f"Ошибка: {str(e)}")
        finally:
            self.reporting = False
