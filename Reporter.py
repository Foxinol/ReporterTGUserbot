# -*- coding: utf-8 -*-
import asyncio
from telethon import functions
from hikka import loader, utils

@loader.tds
class Reporter(loader.Module):
    """Module for automatically reporting messages in Telegram"""

    strings = {"name": "Reporter"}

    def __init__(self):
        self.reporting = False
        self.report_task = None

    @loader.command()
    async def reporty(self, message):
        """Start sending 50 reports on the last message"""
        if self.reporting:
            await utils.answer(message, "Reporting is already running.")
            return
        self.reporting = True
        self.report_task = asyncio.create_task(self.send_reports(message))
        await utils.answer(message, "Starting to send 50 reports.")

    @loader.command()
    async def reportn(self, message):
        """Stop sending reports"""
        if not self.reporting:
            await utils.answer(message, "Reporting is not running.")
            return
        self.reporting = False
        if self.report_task:
            self.report_task.cancel()
        await utils.answer(message, "Reporting stopped.")

    async def send_reports(self, message):
        """Function to send reports"""
        try:
            for _ in range(50):
                if not self.reporting:
                    break
                async for msg in message.client.iter_messages(message.chat_id, limit=1):
                    if msg.id != message.id:  # Don't report the command message
                        await message.client(functions.messages.ReportRequest(
                            peer=message.chat_id,
                            id=[msg.id],
                            reason='spam',
                            message='Automated spam report'
                        ))
                await asyncio.sleep(1)  # 1-second delay between reports
            await utils.answer(message, "Finished sending 50 reports.")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            await utils.answer(message, f"Error: {str(e)}")
        finally:
            self.reporting = False
