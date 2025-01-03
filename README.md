EcoGuard: AI-помощник для анализа экологических документов

EcoGuard — это Telegram-бот, созданный для помощи экологам и исследователям в анализе текстовых данных и изображений в документах. Бот использует Yandex GPT для генерации ответов на вопросы, основанных на содержании загруженных документов (PDF и DOCX).
Начало работы
Требования

    Python 3.7+
    Установленные библиотеки:
        requests
        pyTelegramBotAPI
        python-docx
        PyPDF2
        Pillow
        pytesseract
        pandas


Установка

    Клонируйте репозиторий:

    bash

git clone https://github.com/yourusername/ecoguard.git
cd ecoguard

Установите зависимости:

bash

pip install -r requirements.txt

Настройте переменные для доступа к Yandex Cloud и Telegram API в файле config.py:

python

    BOT_TOKEN = 'ваш_токен_телеграм_бота'
    YANDEX_GPT_API_URL = 'https://api.yandex.cloud/v1/some_endpoint'
    IAM_TOKEN = 'ваш_IAM_токен'
    FOLDER_ID = 'ваш_ID_папки'
    MODEL_URI = 'ваш_ID_модели'

Запуск

Запустите бота командой:

bash

python bot.py

Основные функции
Команда /start

Отправьте /start, чтобы получить приветственное сообщение и инструкцию для отправки документов на анализ.
Обработка документов

EcoGuard поддерживает файлы формата PDF и DOCX. Бот:

    Извлекает текст из документов.
    Обрабатывает изображения, если они содержатся в PDF файле, распознавая текст с помощью OCR.
    Отправляет уведомление об успешной обработке и готовности ответить на вопросы по содержимому документа.

Вопросы на основе документов

После обработки документа пользователь может отправлять текстовые сообщения, и бот будет формировать ответы, используя Yandex GPT на основе загруженного контента.
Структура кода

    start_message — Обработчик команды /start, который приветствует пользователя и объясняет, как отправить документ для анализа.
    handle_document — Обрабатывает загруженные документы, извлекает текст и изображения, сохраняет их локально и готовит данные для Yandex GPT.
    handle_text — Обрабатывает текстовые сообщения пользователя, проверяет наличие загруженного документа и отправляет запрос к Yandex GPT.
    extract_text_from_pdf — Извлекает текст из PDF файлов, включая обработку изображений с помощью OCR.
    extract_text_from_docx — Извлекает текст из DOCX файлов.
    process_image — Выполняет распознавание текста на изображениях, используя OCR.
    truncate_text — Обрезает текст до указанного количества токенов для оптимальной обработки.
    query_yandex_gpt — Формирует и отправляет запрос к Yandex GPT для получения ответа.

Пример config.py

python

BOT_TOKEN = 'ваш_токен_телеграм_бота'
YANDEX_GPT_API_URL = 'https://api.yandex.cloud/v1/some_endpoint'
IAM_TOKEN = 'ваш_IAM_токен'
FOLDER_ID = 'ваш_ID_папки'
