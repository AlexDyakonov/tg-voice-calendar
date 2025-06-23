import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from icalendar import Calendar, Event, vText
import uuid
import io

logger = logging.getLogger(__name__)

class CalendarCreator:
    """Класс для создания iCalendar файлов"""
    
    def __init__(self):
        pass
    
    def create_ics_file(self, event_info: Dict) -> Optional[bytes]:
        """
        Создает .ics файл для события
        
        Args:
            event_info: Словарь с информацией о событии
            
        Returns:
            Байты .ics файла или None в случае ошибки
        """
        try:
            # Создаем календарь
            cal = Calendar()
            cal.add('prodid', '-//Voice Calendar Bot//Voice Calendar Bot//RU')
            cal.add('version', '2.0')
            cal.add('calscale', 'GREGORIAN')
            cal.add('method', 'PUBLISH')
            
            # Создаем событие
            event = Event()
            
            # Уникальный идентификатор события
            event.add('uid', str(uuid.uuid4()))
            
            # Время создания
            event.add('dtstamp', datetime.now())
            
            # Время начала события
            start_time = event_info['datetime']
            event.add('dtstart', start_time)
            
            # Время окончания (по умолчанию +1 час)
            end_time = start_time + timedelta(hours=1)
            event.add('dtend', end_time)
            
            # Описание события
            event.add('summary', vText(event_info['description']))
            
            # Дополнительное описание
            description_text = f"Событие создано из голосового сообщения:\n\"{event_info['original_text']}\""
            event.add('description', vText(description_text))
            
            # Статус события
            event.add('status', 'CONFIRMED')
            
            # Прозрачность (показывать как занятое время)
            event.add('transp', 'OPAQUE')
            
            # Добавляем событие в календарь
            cal.add_component(event)
            
            # Конвертируем в байты
            ics_content = cal.to_ical()
            
            logger.info(f"Создан .ics файл для события: {event_info['description']}")
            return ics_content
            
        except Exception as e:
            logger.error(f"Ошибка при создании .ics файла: {e}")
            return None
    
    def create_filename(self, event_info: Dict) -> str:
        """
        Создает имя файла для события
        
        Args:
            event_info: Словарь с информацией о событии
            
        Returns:
            Имя файла
        """
        try:
            # Берем дату и время
            dt = event_info['datetime']
            date_str = dt.strftime('%Y-%m-%d_%H-%M')
            
            # Очищаем описание для имени файла
            description = event_info['description']
            # Удаляем специальные символы
            safe_description = ''.join(c for c in description if c.isalnum() or c in (' ', '-', '_')).strip()
            # Ограничиваем длину
            safe_description = safe_description[:30]
            
            filename = f"{date_str}_{safe_description}.ics"
            return filename
            
        except Exception as e:
            logger.error(f"Ошибка при создании имени файла: {e}")
            return f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ics"
    
    def format_event_info(self, event_info: Dict) -> str:
        """
        Форматирует информацию о событии для отображения пользователю
        
        Args:
            event_info: Словарь с информацией о событии
            
        Returns:
            Отформатированная строка с информацией о событии
        """
        try:
            dt = event_info['datetime']
            
            # Форматируем дату и время
            date_str = dt.strftime('%d.%m.%Y')
            time_str = dt.strftime('%H:%M')
            weekday_names = [
                'Понедельник', 'Вторник', 'Среда', 'Четверг',
                'Пятница', 'Суббота', 'Воскресенье'
            ]
            weekday = weekday_names[dt.weekday()]
            
            info_text = (
                f"📅 **Событие создано:**\n\n"
                f"📝 **Описание:** {event_info['description']}\n"
                f"📆 **Дата:** {weekday}, {date_str}\n"
                f"🕐 **Время:** {time_str}\n"
                f"⏱️ **Продолжительность:** 1 час\n\n"
                f"💬 **Исходный текст:** \"{event_info['original_text']}\""
            )
            
            return info_text
            
        except Exception as e:
            logger.error(f"Ошибка при форматировании информации о событии: {e}")
            return f"Событие: {event_info.get('description', 'Неизвестное событие')}" 