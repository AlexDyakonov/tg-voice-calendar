import requests
import json
import logging
from typing import Optional
from config import YANDEX_API_KEY, YANDEX_FOLDER_ID

logger = logging.getLogger(__name__)

class YandexSpeechKit:
    """Класс для работы с Yandex SpeechKit API"""
    
    def __init__(self):
        self.api_key = YANDEX_API_KEY
        self.folder_id = YANDEX_FOLDER_ID
        self.recognize_url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
    
    async def recognize_audio(self, audio_data: bytes) -> Optional[str]:
        """
        Распознает речь из аудиоданных
        
        Args:
            audio_data: Байты аудиофайла
            
        Returns:
            Распознанный текст или None в случае ошибки
        """
        try:
            headers = {
                'Authorization': f'Api-Key {self.api_key}',
            }
            
            params = {
                'topic': 'general',
                'lang': 'ru-RU',
                'format': 'oggopus',
                'sampleRateHertz': '48000',
                'folderId': self.folder_id,
            }
            
            # Отправляем POST запрос с аудиоданными
            response = requests.post(
                self.recognize_url,
                headers=headers,
                params=params,
                data=audio_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    recognized_text = result['result']
                    logger.info(f"Успешно распознан текст: {recognized_text}")
                    return recognized_text
                else:
                    logger.error(f"Нет результата в ответе: {result}")
                    return None
            else:
                logger.error(f"Ошибка API: {response.status_code}, {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Ошибка при запросе к Yandex SpeechKit: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при распознавании речи: {e}")
            return None 