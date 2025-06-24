#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных
"""

import asyncio
import logging

from database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Инициализация базы данных"""
    logger.info("Начинаем инициализацию базы данных...")

    db_manager = DatabaseManager()

    try:
        await db_manager.init_db()
        logger.info("✅ База данных успешно инициализирована!")
    except Exception as e:
        logger.error(f"❌ Ошибка при инициализации базы данных: {e}")
    finally:
        await db_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
