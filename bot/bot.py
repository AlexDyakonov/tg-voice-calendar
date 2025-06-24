import asyncio
import io
import json
import logging

from calendar_creator import CalendarCreator
from config import TELEGRAM_BOT_TOKEN
from database import DatabaseManager
from event_extractor import EventExtractor
from telegram import InputFile, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from yandex_speechkit import YandexSpeechKit

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class VoiceToTextBot:
    """Telegram бот для преобразования голосовых сообщений в текст"""

    def __init__(self):
        self.speechkit = YandexSpeechKit()
        self.event_extractor = EventExtractor()
        self.calendar_creator = CalendarCreator()
        self.db_manager = DatabaseManager()
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """Настройка обработчиков команд и сообщений"""
        # Команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("example", self.example_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("history", self.history_command))

        # Обработчики сообщений
        self.application.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        self.application.add_handler(MessageHandler(filters.AUDIO, self.handle_audio))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text)
        )

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        # Регистрируем или обновляем пользователя
        user_info = update.effective_user
        db_user = await self.db_manager.get_or_create_user(
            telegram_id=user_info.id,
            username=user_info.username,
            first_name=user_info.first_name,
            last_name=user_info.last_name,
        )

        welcome_message = (
            f"🎤 Привет, {user_info.first_name or 'пользователь'}! Я умный голосовой календарь-бот!\n\n"
            "🔊 **Что я умею:**\n"
            "• Преобразую голосовые сообщения в текст\n"
            "• Извлекаю события из текста (дату, время, описание)\n"
            "• Создаю .ics файлы для добавления в календарь\n"
            "• Сохраняю историю ваших запросов\n\n"
            "📝 Просто отправьте голосовое сообщение типа:\n"
            '"Во вторник в 17:00 встреча с другом"\n\n'
            "ℹ️ Используйте /help для подробной справки\n"
            "💡 Используйте /example для примеров фраз\n"
            "📊 Используйте /stats для просмотра статистики\n"
            "📝 Используйте /history для просмотра истории запросов"
        )
        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_message = (
            "🔧 **Как пользоваться ботом:**\n\n"
            "1️⃣ Отправьте голосовое сообщение с описанием события\n"
            "2️⃣ Бот распознает речь и извлечет информацию о событии\n"
            "3️⃣ Получите .ics файл для добавления в календарь\n\n"
            "⏰ **Типы событий:**\n"
            '• С конкретным временем ("в 17:00") - событие на 1 час\n'
            "• Без времени - событие на весь день\n\n"
            "📋 **Поддерживаемые форматы:**\n"
            "• Голосовые сообщения Telegram\n"
            "• Аудиофайлы\n"
            "• Текстовые сообщения\n\n"
            "🕐 **Поддерживаемые временные форматы:**\n"
            '• "в 17:00", "в 17 часов"\n'
            '• "во вторник", "в пятницу"\n'
            '• "25.12.2024", "15 января"\n\n'
            "📝 **Типы событий:**\n"
            "• Встречи, собрания, звонки\n"
            "• Презентации, лекции, семинары\n"
            "• Дедлайны, экзамены\n"
            "• Дни рождения, праздники\n\n"
            "🌍 **Язык:** Русский\n\n"
            "❓ **Команды:**\n"
            "/start - Начать работу\n"
            "/help - Показать справку\n"
            "/example - Примеры фраз\n"
            "/stats - Показать статистику использования\n"
            "/history - Показать историю последних запросов"
        )
        await update.message.reply_text(help_message, parse_mode="Markdown")

    async def example_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /example"""
        example_message = (
            "💡 **Примеры фраз для голосовых сообщений:**\n\n"
            "🕐 **С указанием времени:**\n"
            '• "Во вторник в 17:00 встреча с другом"\n'
            '• "В пятницу в 14 часов презентация проекта"\n'
            '• "Завтра в 9:30 звонок с клиентом"\n\n'
            "📅 **С указанием даты:**\n"
            '• "25 декабря день рождения мамы"\n'
            '• "15.01.2025 сдача отчета"\n'
            '• "В следующий понедельник собрание команды"\n\n'
            "📝 **Простые события (на весь день):**\n"
            '• "Встреча с врачом"\n'
            '• "Экзамен по математике"\n'
            '• "Конференция по IT"\n'
            '• "День рождения мамы"\n'
            '• "Отпуск"\n\n'
            "🎯 **Совет:** Говорите четко и включайте:\n"
            "• Тип события (встреча, звонок, экзамен)\n"
            "• Время (если известно)\n"
            "• День/дату (если известна)\n"
            "• Краткое описание"
        )
        await update.message.reply_text(example_message, parse_mode="Markdown")

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /stats"""
        user_info = update.effective_user

        # Регистрируем пользователя если его нет
        db_user = await self.db_manager.get_or_create_user(
            telegram_id=user_info.id,
            username=user_info.username,
            first_name=user_info.first_name,
            last_name=user_info.last_name,
        )

        # Получаем статистику
        stats = await self.db_manager.get_user_stats(db_user.id)

        stats_message = (
            f"📊 **Ваша статистика:**\n\n"
            f"📝 Всего запросов: {stats['total_requests']}\n"
            f"✅ Успешно извлечено событий: {stats['events_extracted']}\n"
            f"🎤 Голосовых сообщений: {stats['voice_requests']}\n"
            f"💬 Текстовых сообщений: {stats['text_requests']}\n"
            f"📈 Процент успеха: {stats['success_rate']:.1f}%\n\n"
            f"📅 Зарегистрированы: {db_user.created_at.strftime('%d.%m.%Y')}\n"
            f"🕐 Последняя активность: {db_user.last_activity.strftime('%d.%m.%Y %H:%M')}"
        )

        await update.message.reply_text(stats_message, parse_mode="Markdown")

    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /history"""
        user_info = update.effective_user

        # Регистрируем пользователя если его нет
        db_user = await self.db_manager.get_or_create_user(
            telegram_id=user_info.id,
            username=user_info.username,
            first_name=user_info.first_name,
            last_name=user_info.last_name,
        )

        # Получаем последние 10 запросов
        requests = await self.db_manager.get_user_requests(db_user.id, limit=10)

        if not requests:
            await update.message.reply_text(
                "📝 История запросов пуста. Отправьте первое голосовое сообщение!"
            )
            return

        history_message = "📝 **Последние 10 запросов:**\n\n"

        for i, req in enumerate(requests, 1):
            req_type_emoji = {"voice": "🎤", "audio": "🎵", "text": "💬"}.get(
                req.request_type, "❓"
            )

            text_preview = ""
            if req.transcribed_text:
                text_preview = (
                    req.transcribed_text[:50] + "..."
                    if len(req.transcribed_text) > 50
                    else req.transcribed_text
                )
            elif req.original_text:
                text_preview = (
                    req.original_text[:50] + "..."
                    if len(req.original_text) > 50
                    else req.original_text
                )

            status_emoji = "✅" if req.event_extracted else "❌"

            history_message += (
                f"{i}. {req_type_emoji} {req.created_at.strftime('%d.%m %H:%M')} {status_emoji}\n"
                f"   `{text_preview}`\n\n"
            )

        await update.message.reply_text(history_message, parse_mode="Markdown")

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик голосовых сообщений"""
        try:
            # Регистрируем пользователя если его нет
            user_info = update.effective_user
            db_user = await self.db_manager.get_or_create_user(
                telegram_id=user_info.id,
                username=user_info.username,
                first_name=user_info.first_name,
                last_name=user_info.last_name,
            )

            # Отправляем сообщение о начале обработки
            processing_message = await update.message.reply_text(
                "🎧 Обрабатываю голосовое сообщение..."
            )

            # Получаем файл голосового сообщения
            voice_file = await update.message.voice.get_file()

            # Скачиваем аудиоданные
            audio_data = await voice_file.download_as_bytearray()

            # Распознаем речь
            recognized_text = await self.speechkit.recognize_audio(bytes(audio_data))

            if recognized_text:
                # Обновляем сообщение о обработке
                await processing_message.edit_text(
                    "🔍 Анализирую текст и извлекаю событие..."
                )

                # Пытаемся извлечь событие из текста
                event_info = self.event_extractor.extract_event(recognized_text)
                event_extracted = bool(event_info)
                event_data = (
                    json.dumps(event_info, ensure_ascii=False, default=str)
                    if event_info
                    else None
                )

                # Сохраняем запрос в базу данных
                await self.db_manager.save_user_request(
                    user_id=db_user.id,
                    telegram_message_id=update.message.message_id,
                    request_type="voice",
                    transcribed_text=recognized_text,
                    event_extracted=event_extracted,
                    event_data=event_data,
                )

                if event_info:
                    # Создаем .ics файл
                    ics_content = self.calendar_creator.create_ics_file(event_info)

                    if ics_content:
                        # Удаляем сообщение о обработке
                        await processing_message.delete()

                        # Отправляем информацию о событии
                        event_text = self.calendar_creator.format_event_info(event_info)
                        await update.message.reply_text(
                            event_text, parse_mode="Markdown"
                        )

                        # Отправляем .ics файл
                        filename = self.calendar_creator.create_filename(event_info)
                        await update.message.reply_document(
                            document=InputFile(
                                io.BytesIO(ics_content), filename=filename
                            ),
                            caption="📎 Файл календаря готов! Добавьте его в свой календарь.",
                        )

                        logger.info(
                            f"Создано событие для пользователя {update.effective_user.id}: {event_info['description']}"
                        )
                    else:
                        await processing_message.edit_text(
                            "❌ Не удалось создать файл календаря. Попробуйте позже."
                        )
                else:
                    # Если событие не извлечено, показываем просто распознанный текст
                    await processing_message.edit_text(
                        f"📝 **Распознанный текст:**\n\n{recognized_text}\n\n"
                        "⚠️ Не удалось извлечь информацию о событии. "
                        "Попробуйте более четко указать время, дату и тип события."
                    )

                logger.info(
                    f"Успешно обработано голосовое сообщение от пользователя {update.effective_user.id}"
                )
            else:
                # Сохраняем неудачную попытку в базу данных
                await self.db_manager.save_user_request(
                    user_id=db_user.id,
                    telegram_message_id=update.message.message_id,
                    request_type="voice",
                    transcribed_text=None,
                    event_extracted=False,
                    event_data=None,
                )

                await processing_message.edit_text(
                    "❌ Не удалось распознать речь. Попробуйте еще раз с более четким произношением."
                )
                logger.warning(
                    f"Не удалось распознать голосовое сообщение от пользователя {update.effective_user.id}"
                )

        except Exception as e:
            logger.error(f"Ошибка при обработке голосового сообщения: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке голосового сообщения. Попробуйте позже."
            )

    async def handle_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик аудиофайлов"""
        try:
            # Регистрируем пользователя если его нет
            user_info = update.effective_user
            db_user = await self.db_manager.get_or_create_user(
                telegram_id=user_info.id,
                username=user_info.username,
                first_name=user_info.first_name,
                last_name=user_info.last_name,
            )

            # Проверяем размер файла (ограничение Yandex SpeechKit - обычно до 1MB)
            if update.message.audio.file_size > 1024 * 1024:  # 1MB
                await update.message.reply_text(
                    "❌ Файл слишком большой. Максимальный размер: 1MB"
                )
                return

            # Отправляем сообщение о начале обработки
            processing_message = await update.message.reply_text(
                "🎵 Обрабатываю аудиофайл..."
            )

            # Получаем аудиофайл
            audio_file = await update.message.audio.get_file()

            # Скачиваем аудиоданные
            audio_data = await audio_file.download_as_bytearray()

            # Распознаем речь
            recognized_text = await self.speechkit.recognize_audio(bytes(audio_data))

            if recognized_text:
                # Сохраняем запрос в базу данных
                await self.db_manager.save_user_request(
                    user_id=db_user.id,
                    telegram_message_id=update.message.message_id,
                    request_type="audio",
                    transcribed_text=recognized_text,
                    event_extracted=False,  # Для аудиофайлов пока не извлекаем события автоматически
                    event_data=None,
                )

                # Удаляем сообщение о обработке
                await processing_message.delete()

                # Отправляем результат
                result_message = f"📝 **Распознанный текст:**\n\n{recognized_text}"
                await update.message.reply_text(result_message, parse_mode="Markdown")

                logger.info(
                    f"Успешно обработан аудиофайл от пользователя {update.effective_user.id}"
                )
            else:
                # Сохраняем неудачную попытку в базу данных
                await self.db_manager.save_user_request(
                    user_id=db_user.id,
                    telegram_message_id=update.message.message_id,
                    request_type="audio",
                    transcribed_text=None,
                    event_extracted=False,
                    event_data=None,
                )

                await processing_message.edit_text(
                    "❌ Не удалось распознать речь в аудиофайле."
                )
                logger.warning(
                    f"Не удалось распознать аудиофайл от пользователя {update.effective_user.id}"
                )

        except Exception as e:
            logger.error(f"Ошибка при обработке аудиофайла: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке аудиофайла. Попробуйте позже."
            )

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        text = update.message.text.strip()

        # Регистрируем пользователя если его нет
        user_info = update.effective_user
        db_user = await self.db_manager.get_or_create_user(
            telegram_id=user_info.id,
            username=user_info.username,
            first_name=user_info.first_name,
            last_name=user_info.last_name,
        )

        # Отправляем сообщение о начале обработки
        processing_message = await update.message.reply_text(
            "🔍 Анализирую текст и ищу событие..."
        )

        try:
            # Пытаемся извлечь событие из текста
            event_info = self.event_extractor.extract_event(text)
            event_extracted = bool(event_info)
            event_data = (
                json.dumps(event_info, ensure_ascii=False, default=str)
                if event_info
                else None
            )

            # Сохраняем запрос в базу данных
            await self.db_manager.save_user_request(
                user_id=db_user.id,
                telegram_message_id=update.message.message_id,
                request_type="text",
                original_text=text,
                event_extracted=event_extracted,
                event_data=event_data,
            )

            if event_info:
                # Создаем .ics файл
                ics_content = self.calendar_creator.create_ics_file(event_info)

                if ics_content:
                    # Удаляем сообщение о обработке
                    await processing_message.delete()

                    # Отправляем информацию о событии
                    event_text = self.calendar_creator.format_event_info(event_info)
                    await update.message.reply_text(event_text, parse_mode="Markdown")

                    # Отправляем .ics файл
                    filename = self.calendar_creator.create_filename(event_info)
                    await update.message.reply_document(
                        document=InputFile(io.BytesIO(ics_content), filename=filename),
                        caption="📎 Файл календаря готов! Добавьте его в свой календарь.",
                    )

                    logger.info(
                        f"Создано событие из текста для пользователя {update.effective_user.id}: {event_info['description']}"
                    )
                else:
                    await processing_message.edit_text(
                        "❌ Не удалось создать файл календаря. Попробуйте позже."
                    )
            else:
                await processing_message.edit_text(
                    "⚠️ Не удалось найти информацию о событии в вашем сообщении.\n\n"
                    "💡 Попробуйте указать:\n"
                    "• Тип события (встреча, звонок, экзамен)\n"
                    '• Время (например: "в 17:00")\n'
                    '• День или дату (например: "во вторник" или "25.12")\n\n'
                    "🎤 Или отправьте голосовое сообщение для лучшего распознавания!"
                )

        except Exception as e:
            logger.error(f"Ошибка при обработке текстового сообщения: {e}")
            await processing_message.edit_text(
                "❌ Произошла ошибка при анализе текста. Попробуйте позже."
            )

    async def run(self):
        """Запуск бота"""
        logger.info("Запуск бота...")

        # Инициализируем базу данных
        await self.db_manager.init_db()

        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()

        try:
            # Ожидаем завершения работы
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Получен сигнал завершения...")
        finally:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            await self.db_manager.close()


async def main():
    """Главная функция"""
    bot = VoiceToTextBot()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
