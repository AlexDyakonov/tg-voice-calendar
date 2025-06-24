import datetime
import logging
from typing import List, Optional

from config import DATABASE_URL
from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())
    last_activity: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now()
    )


class UserRequest(Base):
    __tablename__ = "user_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    telegram_message_id: Mapped[int] = mapped_column(Integer)
    request_type: Mapped[str] = mapped_column(String(50))  # 'voice', 'audio', 'text'
    original_text: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # Для текстовых сообщений
    transcribed_text: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # Расшифрованный текст
    event_extracted: Mapped[bool] = mapped_column(Boolean, default=False)
    event_data: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # JSON с данными события
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())


class DatabaseManager:
    def __init__(self):
        self.engine = create_async_engine(DATABASE_URL, echo=False)
        self.async_session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init_db(self):
        """Инициализация базы данных"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("База данных инициализирована")

    async def close(self):
        """Закрытие соединения с базой данных"""
        await self.engine.dispose()

    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str = None,
        first_name: str = None,
        last_name: str = None,
    ) -> User:
        """Получить или создать пользователя"""
        async with self.async_session() as session:
            # Ищем существующего пользователя
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if user:
                # Обновляем информацию о пользователе
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                user.last_activity = datetime.datetime.now()
                await session.commit()
                logger.info(f"Обновлена информация о пользователе {telegram_id}")
            else:
                # Создаем нового пользователя
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
                logger.info(f"Создан новый пользователь {telegram_id}")

            return user

    async def save_user_request(
        self,
        user_id: int,
        telegram_message_id: int,
        request_type: str,
        original_text: str = None,
        transcribed_text: str = None,
        event_extracted: bool = False,
        event_data: str = None,
    ) -> UserRequest:
        """Сохранить запрос пользователя"""
        async with self.async_session() as session:
            request = UserRequest(
                user_id=user_id,
                telegram_message_id=telegram_message_id,
                request_type=request_type,
                original_text=original_text,
                transcribed_text=transcribed_text,
                event_extracted=event_extracted,
                event_data=event_data,
            )
            session.add(request)
            await session.commit()
            await session.refresh(request)
            logger.info(f"Сохранен запрос пользователя {user_id}, тип: {request_type}")
            return request

    async def get_user_requests(
        self, user_id: int, limit: int = 50
    ) -> List[UserRequest]:
        """Получить последние запросы пользователя"""
        async with self.async_session() as session:
            result = await session.execute(
                select(UserRequest)
                .where(UserRequest.user_id == user_id)
                .order_by(UserRequest.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()

    async def get_user_stats(self, user_id: int) -> dict:
        """Получить статистику пользователя"""
        async with self.async_session() as session:
            # Общее количество запросов
            total_requests = await session.execute(
                select(func.count(UserRequest.id)).where(UserRequest.user_id == user_id)
            )
            total_count = total_requests.scalar()

            # Количество успешно извлеченных событий
            events_extracted = await session.execute(
                select(func.count(UserRequest.id))
                .where(UserRequest.user_id == user_id)
                .where(UserRequest.event_extracted == True)
            )
            events_count = events_extracted.scalar()

            # Количество по типам запросов
            voice_requests = await session.execute(
                select(func.count(UserRequest.id))
                .where(UserRequest.user_id == user_id)
                .where(UserRequest.request_type == "voice")
            )
            voice_count = voice_requests.scalar()

            text_requests = await session.execute(
                select(func.count(UserRequest.id))
                .where(UserRequest.user_id == user_id)
                .where(UserRequest.request_type == "text")
            )
            text_count = text_requests.scalar()

            return {
                "total_requests": total_count,
                "events_extracted": events_count,
                "voice_requests": voice_count,
                "text_requests": text_count,
                "success_rate": (
                    (events_count / total_count * 100) if total_count > 0 else 0
                ),
            }
