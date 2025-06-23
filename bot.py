import logging
import asyncio
import io
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from yandex_speechkit import YandexSpeechKit
from config import TELEGRAM_BOT_TOKEN

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class VoiceToTextBot:
    """Telegram бот для преобразования голосовых сообщений в текст"""
    
    def __init__(self):
        self.speechkit = YandexSpeechKit()
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Настройка обработчиков команд и сообщений"""
        # Команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Обработчики сообщений
        self.application.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        self.application.add_handler(MessageHandler(filters.AUDIO, self.handle_audio))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_message = (
            "🎤 Привет! Я бот для преобразования голосовых сообщений в текст.\n\n"
            "📝 Просто отправьте мне голосовое сообщение, и я переведу его в текст "
            "с помощью Yandex SpeechKit!\n\n"
            "ℹ️ Используйте /help для получения дополнительной информации."
        )
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_message = (
            "🔧 **Как пользоваться ботом:**\n\n"
            "1️⃣ Отправьте голосовое сообщение\n"
            "2️⃣ Дождитесь обработки\n"
            "3️⃣ Получите текстовую расшифровку\n\n"
            "📋 **Поддерживаемые форматы:**\n"
            "• Голосовые сообщения Telegram\n"
            "• Аудиофайлы\n\n"
            "🌍 **Язык распознавания:** Русский\n\n"
            "❓ **Команды:**\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать эту справку"
        )
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик голосовых сообщений"""
        try:
            # Отправляем сообщение о начале обработки
            processing_message = await update.message.reply_text("🎧 Обрабатываю голосовое сообщение...")
            
            # Получаем файл голосового сообщения
            voice_file = await update.message.voice.get_file()
            
            # Скачиваем аудиоданные
            audio_data = await voice_file.download_as_bytearray()
            
            # Распознаем речь
            recognized_text = await self.speechkit.recognize_audio(bytes(audio_data))
            
            if recognized_text:
                # Удаляем сообщение о обработке
                await processing_message.delete()
                
                # Отправляем результат
                result_message = f"📝 **Распознанный текст:**\n\n{recognized_text}"
                await update.message.reply_text(result_message, parse_mode='Markdown')
                
                logger.info(f"Успешно обработано голосовое сообщение от пользователя {update.effective_user.id}")
            else:
                await processing_message.edit_text(
                    "❌ Не удалось распознать речь. Попробуйте еще раз с более четким произношением."
                )
                logger.warning(f"Не удалось распознать голосовое сообщение от пользователя {update.effective_user.id}")
                
        except Exception as e:
            logger.error(f"Ошибка при обработке голосового сообщения: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке голосового сообщения. Попробуйте позже."
            )
    
    async def handle_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик аудиофайлов"""
        try:
            # Проверяем размер файла (ограничение Yandex SpeechKit - обычно до 1MB)
            if update.message.audio.file_size > 1024 * 1024:  # 1MB
                await update.message.reply_text(
                    "❌ Файл слишком большой. Максимальный размер: 1MB"
                )
                return
            
            # Отправляем сообщение о начале обработки
            processing_message = await update.message.reply_text("🎵 Обрабатываю аудиофайл...")
            
            # Получаем аудиофайл
            audio_file = await update.message.audio.get_file()
            
            # Скачиваем аудиоданные
            audio_data = await audio_file.download_as_bytearray()
            
            # Распознаем речь
            recognized_text = await self.speechkit.recognize_audio(bytes(audio_data))
            
            if recognized_text:
                # Удаляем сообщение о обработке
                await processing_message.delete()
                
                # Отправляем результат
                result_message = f"📝 **Распознанный текст:**\n\n{recognized_text}"
                await update.message.reply_text(result_message, parse_mode='Markdown')
                
                logger.info(f"Успешно обработан аудиофайл от пользователя {update.effective_user.id}")
            else:
                await processing_message.edit_text(
                    "❌ Не удалось распознать речь в аудиофайле."
                )
                logger.warning(f"Не удалось распознать аудиофайл от пользователя {update.effective_user.id}")
                
        except Exception as e:
            logger.error(f"Ошибка при обработке аудиофайла: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке аудиофайла. Попробуйте позже."
            )
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        await update.message.reply_text(
            "📝 Я умею работать только с голосовыми сообщениями и аудиофайлами.\n"
            "🎤 Отправьте мне голосовое сообщение для преобразования в текст!"
        )
    
    async def run(self):
        """Запуск бота"""
        logger.info("Запуск бота...")
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

async def main():
    """Главная функция"""
    bot = VoiceToTextBot()
    await bot.run()

if __name__ == '__main__':
    asyncio.run(main()) 