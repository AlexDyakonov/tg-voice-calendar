import datetime as dt
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import dateparser
from natasha import (
    PER,
    Doc,
    MorphVocab,
    NamesExtractor,
    NewsEmbedding,
    NewsMorphTagger,
    NewsNERTagger,
    NewsSyntaxParser,
    Segmenter,
)

logger = logging.getLogger(__name__)


class EventExtractor:
    """Класс для извлечения событий из текста с помощью Natasha"""

    def __init__(self):
        try:
            # Инициализация компонентов Natasha
            logger.info("Инициализация Natasha компонентов...")
            self.segmenter = Segmenter()
            self.morph_vocab = MorphVocab()

            self.emb = NewsEmbedding()
            self.morph_tagger = NewsMorphTagger(self.emb)
            self.syntax_parser = NewsSyntaxParser(self.emb)
            self.ner_tagger = NewsNERTagger(self.emb)

            self.names_extractor = NamesExtractor(self.morph_vocab)
            logger.info("Natasha компоненты успешно инициализированы")
        except Exception as e:
            logger.error(f"Ошибка при инициализации Natasha: {e}")
            # Устанавливаем None для компонентов, если инициализация не удалась
            self.segmenter = None
            self.morph_vocab = None
            self.emb = None
            self.morph_tagger = None
            self.syntax_parser = None
            self.ner_tagger = None
            self.names_extractor = None

        # Словарь дней недели
        self.weekdays = {
            "понедельник": 0,
            "пн": 0,
            "вторник": 1,
            "вт": 1,
            "среда": 2,
            "среду": 2,
            "ср": 2,
            "четверг": 3,
            "чт": 3,
            "пятница": 4,
            "пятницу": 4,
            "пт": 4,
            "суббота": 5,
            "субботу": 5,
            "сб": 5,
            "воскресенье": 6,
            "воскресенье": 6,
            "вс": 6,
        }

        # Паттерны для времени
        self.time_patterns = [
            r"в\s+(\d{1,2})\s+(\d{1,2})",  # в 15 30, в 17 0 0 (с пробелами от speechkit)
            r"в\s+(\d{1,2})\s+(?:часов?|вечера|утра|дня|ночи)",  # в 5 вечера, в 17 часов
            r"в\s+(\d{1,2})\.(\d{2})",  # в 19.00
            r"в\s+(\d{1,2}):(\d{2})",  # в 17:00
            r"(\d{1,2})\s+(\d{1,2})\s+(?:встреча|звонок|собрание|презентация|мероприятие)",  # 15 30 встреча
            r"(\d{1,2})\s+(?:часов?|вечера|утра|дня|ночи)",  # 5 вечера, 17 часов
            r"(\d{1,2})\.(\d{2})",  # 19.00
            r"(\d{1,2}):(\d{2})",  # 17:00
        ]

        # Паттерны для дат
        self.date_patterns = [
            r"(\d{1,2})\.(\d{1,2})\.(\d{4})",  # 25.12.2024
            r"(\d{1,2})\.(\d{1,2})(?!\d)",  # 25.12 (но не 19.00)
            r"(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)",
        ]

        # Словарь месяцев
        self.months = {
            "января": 1,
            "февраля": 2,
            "марта": 3,
            "апреля": 4,
            "мая": 5,
            "июня": 6,
            "июля": 7,
            "августа": 8,
            "сентября": 9,
            "октября": 10,
            "ноября": 11,
            "декабря": 12,
        }

        # Ключевые слова для событий
        self.event_keywords = [
            "встреча",
            "собрание",
            "конференция",
            "звонок",
            "созвон",
            "презентация",
            "доклад",
            "лекция",
            "семинар",
            "тренинг",
            "интервью",
            "собеседование",
            "дедлайн",
            "сдача",
            "экзамен",
            "день рождения",
            "праздник",
            "мероприятие",
            "событие",
        ]

    def extract_event(self, text: str) -> Optional[Dict]:
        """
        Извлекает информацию о событии из текста

        Args:
            text: Текст для анализа

        Returns:
            Словарь с информацией о событии или None
        """
        try:
            text = text.lower().strip()
            logger.info(f"Анализируем текст: {text}")

            # Извлекаем компоненты события
            event_time = self._extract_time(text)
            event_date = self._extract_date(text)
            event_description = self._extract_description(text)

            logger.info(
                f"Извлечено - время: {event_time}, дата: {event_date}, описание: {event_description}"
            )

            if not event_description:
                logger.warning("Не удалось извлечь описание события")
                return None

            # Если не найдена дата, используем сегодня или ближайший день недели
            if not event_date:
                event_date = self._extract_weekday(text)
                if not event_date:
                    event_date = datetime.now().date()
                    logger.info(f"Дата не найдена, используем сегодня: {event_date}")
            else:
                logger.info(f"Используем найденную дату: {event_date}")

            # Если не найдено время, создаем событие на весь день
            if not event_time:
                logger.info("Время не найдено, создаем событие на весь день")
                # Для события на весь день используем полночь
                event_datetime = datetime.combine(event_date, dt.time(0, 0))
                is_all_day = True
            else:
                logger.info(f"Используем найденное время: {event_time}")
                # Создаем datetime объект с конкретным временем
                event_datetime = datetime.combine(event_date, event_time)
                is_all_day = False

            # Если событие в прошлом, переносим на следующий день/неделю
            if event_datetime < datetime.now():
                if self._has_weekday(text):
                    # Если указан день недели, переносим на следующую неделю
                    event_datetime += timedelta(days=7)
                    logger.info(
                        f"Событие в прошлом, перенесено на следующую неделю: {event_datetime}"
                    )
                elif "завтра" not in text and "сегодня" not in text:
                    # Переносим только если не указано явно "завтра" или "сегодня"
                    event_datetime += timedelta(days=1)
                    logger.info(
                        f"Событие в прошлом, перенесено на завтра: {event_datetime}"
                    )
                else:
                    logger.info(
                        f"Событие запланировано на указанную дату: {event_datetime}"
                    )

            event_info = {
                "datetime": event_datetime,
                "description": event_description,
                "original_text": text,
                "is_all_day": is_all_day,
            }

            logger.info(f"Извлечено событие: {event_info}")
            return event_info

        except Exception as e:
            logger.error(f"Ошибка при извлечении события: {e}")
            return None

    def _extract_time(self, text: str) -> Optional[dt.time]:
        """Извлекает время из текста"""
        # Специальные паттерны для Yandex SpeechKit формата
        # "17 0 0", "15 30", "в 15 30" и т.д.
        speechkit_patterns = [
            r"в\s+(\d{1,2})\s+(\d{1,2})\s+(?:0+|встреча|звонок|собрание)",  # в 15 30 встреча
            r"(\d{1,2})\s+(\d{1,2})\s+(?:0+|встреча|звонок|собрание)",  # 15 30 встреча
            r"в\s+(\d{1,2})\s+0+\s+0*",  # в 17 0 0
            r"(\d{1,2})\s+0+\s+0*",  # 17 0 0 (без "в")
        ]

        # Сначала проверяем специальные паттерны для speechkit
        for pattern in speechkit_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    if len(match.groups()) == 2:
                        hour, minute = int(match.group(1)), int(match.group(2))
                        # Если второе число больше 59, возможно это не минуты
                        if minute > 59:
                            continue
                    else:
                        hour = int(match.group(1))
                        minute = 0

                    if 0 <= hour <= 23 and 0 <= minute <= 59:
                        logger.info(
                            f"Найдено время (формат speechkit): {hour:02d}:{minute:02d}"
                        )
                        return dt.time(hour, minute)
                except ValueError:
                    continue

        # Затем проверяем обычные паттерны
        for pattern in self.time_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    if len(match.groups()) == 2:
                        hour, minute = int(match.group(1)), int(match.group(2))
                        # Проверяем, что это действительно время, а не дата
                        # Если минута > 59, это скорее всего дата (например, 24.06)
                        if minute > 59:
                            continue
                    else:
                        hour = int(match.group(1))
                        minute = 0

                        # Проверяем контекст для определения времени дня
                        if "вечера" in text:
                            if hour < 12:  # Если указано "5 вечера", то это 17:00
                                hour += 12
                        elif "утра" in text:
                            if hour == 12:  # "12 утра" = 00:00
                                hour = 0
                        elif "дня" in text:
                            if hour < 12:  # "2 дня" = 14:00
                                hour += 12
                        elif "ночи" in text:
                            if (
                                hour != 12 and hour < 6
                            ):  # "2 ночи" = 02:00, но "12 ночи" = 00:00
                                pass  # оставляем как есть
                            elif hour == 12:
                                hour = 0

                    if 0 <= hour <= 23 and 0 <= minute <= 59:
                        logger.info(f"Найдено время: {hour:02d}:{minute:02d}")
                        return dt.time(hour, minute)
                except ValueError:
                    continue

        return None

    def _extract_date(self, text: str) -> Optional[dt.date]:
        """Извлекает дату из текста"""
        # Проверяем специальные слова для дат
        if "завтра" in text:
            tomorrow = datetime.now().date() + timedelta(days=1)
            logger.info(f"Найдено слово 'завтра', дата: {tomorrow}")
            return tomorrow

        if "сегодня" in text:
            today = datetime.now().date()
            logger.info(f"Найдено слово 'сегодня', дата: {today}")
            return today

        if "послезавтра" in text:
            day_after_tomorrow = datetime.now().date() + timedelta(days=2)
            logger.info(f"Найдено слово 'послезавтра', дата: {day_after_tomorrow}")
            return day_after_tomorrow

        # Сначала пробуем dateparser
        try:
            parsed_date = dateparser.parse(text, languages=["ru"])
            if parsed_date:
                logger.info(f"Dateparser найден дата: {parsed_date.date()}")
                return parsed_date.date()
        except:
            pass

        # Затем используем регулярные выражения
        for pattern in self.date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    if len(match.groups()) == 3:  # ДД.ММ.ГГГГ
                        day, month, year = (
                            int(match.group(1)),
                            int(match.group(2)),
                            int(match.group(3)),
                        )
                        return datetime(year, month, day).date()
                    elif len(match.groups()) == 2:
                        if match.group(2).isdigit():  # ДД.ММ
                            day, month = int(match.group(1)), int(match.group(2))
                            # Проверяем, что это дата, а не время
                            if month <= 12 and day <= 31:
                                year = datetime.now().year
                                logger.info(
                                    f"Найдена дата: {day:02d}.{month:02d}.{year}"
                                )
                                return datetime(year, month, day).date()
                        else:  # ДД месяц
                            day = int(match.group(1))
                            month_name = match.group(2)
                            if month_name in self.months:
                                month = self.months[month_name]
                                year = datetime.now().year
                                return datetime(year, month, day).date()
                except ValueError:
                    continue

        return None

    def _extract_weekday(self, text: str) -> Optional[dt.date]:
        """Извлекает день недели и возвращает ближайшую дату"""
        for weekday_name, weekday_num in self.weekdays.items():
            if weekday_name in text:
                today = datetime.now().date()
                days_ahead = weekday_num - today.weekday()
                if days_ahead <= 0:  # Если день уже прошел на этой неделе
                    days_ahead += 7
                return today + timedelta(days=days_ahead)

        return None

    def _has_weekday(self, text: str) -> bool:
        """Проверяет, содержит ли текст день недели"""
        return any(weekday in text for weekday in self.weekdays.keys())

    def _extract_description(self, text: str) -> Optional[str]:
        """Извлекает описание события из текста"""
        # Используем Natasha для анализа текста, если она доступна
        main_words = []
        if all(
            [self.segmenter, self.morph_tagger, self.syntax_parser, self.ner_tagger]
        ):
            try:
                doc = Doc(text)
                doc.segment(self.segmenter)
                doc.tag_morph(self.morph_tagger)
                doc.parse_syntax(self.syntax_parser)
                doc.tag_ner(self.ner_tagger)

                # Ищем существительные и глаголы
                for token in doc.tokens:
                    if token.pos in ["NOUN", "VERB"] and len(token.text) > 2:
                        main_words.append(token.text)
            except Exception as e:
                logger.error(f"Ошибка при анализе с Natasha: {e}")
                main_words = []

        # Ищем ключевые слова событий
        for keyword in self.event_keywords:
            if keyword in text:
                # Пытаемся извлечь контекст вокруг ключевого слова
                parts = text.split(keyword)
                if len(parts) > 1:
                    # Берем слово + контекст после него
                    context = parts[1].strip()
                    if context:
                        # Очищаем от временных меток и дат
                        context = self._clean_description(context)
                        if context:
                            return f"{keyword} {context}".strip()
                    return keyword

        # Если не найдены ключевые слова, используем найденные основные слова
        if main_words:
            description = " ".join(main_words[:3])  # Берем первые 3 значимых слова
            return self._clean_description(description)

        # В крайнем случае возвращаем очищенный исходный текст
        cleaned_text = self._clean_description(text)
        return cleaned_text if cleaned_text else "Событие"

    def _clean_description(self, text: str) -> str:
        """Очищает описание от временных меток и служебных слов"""
        try:
            # Удаляем временные паттерны
            for pattern in self.time_patterns + self.date_patterns:
                text = re.sub(pattern, "", text)

            # Удаляем дни недели
            for weekday in self.weekdays.keys():
                text = text.replace(weekday, "")

            # Удаляем специальные слова
            special_words = ["завтра", "сегодня", "послезавтра"]
            for word in special_words:
                text = text.replace(word, "")

            # Удаляем предлоги и служебные слова
            stop_words = [
                "в",
                "на",
                "во",
                "с",
                "у",
                "к",
                "от",
                "до",
                "за",
                "под",
                "над",
                "при",
                "о",
                "об",
            ]
            words = text.split()
            filtered_words = [
                word for word in words if word not in stop_words and len(word) > 1
            ]

            return " ".join(filtered_words).strip()
        except Exception as e:
            logger.error(f"Ошибка в _clean_description: {e}")
            return text.strip()
