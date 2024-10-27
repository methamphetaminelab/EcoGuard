import os
import requests
import telebot
from telebot import types
from docx import Document
from PyPDF2 import PdfReader
from pytesseract import image_to_string
from PIL import Image
from io import BytesIO
import config

bot = telebot.TeleBot(config.BOT_TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Я - EcoGuard, твой личный AI помощник.\nДля начала - пришлите мне файл формата Word (.docx) или PDF (.pdf).')

@bot.message_handler(content_types=['document'])
def handle_document(message):
    user_id = message.chat.id
    if user_id not in user_data:
        user_data[user_id] = {'extracted_text': "", 'image_files': [], 'file_name': ""}

    document = message.document
    user_data[user_id]['file_name'] = document.file_name
    try:
        if user_data[user_id]['file_name'].endswith('.pdf'):
            file_info = bot.get_file(document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            with open(user_data[user_id]['file_name'], 'wb') as new_file:
                new_file.write(downloaded_file)

            processing_message = bot.send_message(user_id, f"Анализирую документ {user_data[user_id]['file_name']}..")
            user_data[user_id]['extracted_text'] = extract_text_from_pdf(user_data[user_id]['file_name'])
            print(user_data[user_id]['extracted_text'])
            bot.edit_message_text(
                chat_id=user_id,
                message_id=processing_message.message_id,
                text=f"Документ '{user_data[user_id]['file_name']}' успешно проанализирован. Теперь вы можете задать интересующие вас вопросы. Для этого просто напишите что-нибудь в чат."
            )

        elif user_data[user_id]['file_name'].endswith('.docx'):
            file_info = bot.get_file(document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            with open(user_data[user_id]['file_name'], 'wb') as new_file:
                new_file.write(downloaded_file)

            processing_message = bot.send_message(user_id, f"Анализирую документ {user_data[user_id]['file_name']}..")
            user_data[user_id]['extracted_text'] = extract_text_from_docx(user_data[user_id]['file_name'])
            print(user_data[user_id]['extracted_text'])
            bot.edit_message_text(
                chat_id=user_id,
                message_id=processing_message.message_id,
                text=f"Документ '{user_data[user_id]['file_name']}' успешно проанализирован. Теперь вы можете задать интересующие вас вопросы. Для этого просто напишите что-нибудь в чат."
            )

        else:
            bot.send_message(user_id, "Пожалуйста, отправьте файл в формате Word (.docx) или PDF (.pdf).")

        if user_data[user_id]['image_files']:
            for image_file in user_data[user_id]['image_files']:
                text_from_image = process_image(image_file)
                user_data[user_id]['extracted_text'] += "\n" + text_from_image
            user_data[user_id]['image_files'].clear()
    except Exception as e:
        print(e)
        bot.send_message(user_id, f"Произошла ошибка: {e}")

@bot.message_handler(func=lambda message: not message.document)
def handle_text(message):
    user_id = message.chat.id

    if user_id not in user_data or not user_data[user_id]['extracted_text']:
        bot.send_message(user_id, "Пожалуйста, сначала загрузите документ для анализа.")
        return

    extracted_text = user_data[user_id]['extracted_text']
    user_message = message.text
    processing_message = bot.send_message(user_id, "Формирую ответ..")
    response_text = query_yandex_gpt(truncate_text(extracted_text), user_message, user_id)

    send_long_message(user_id, response_text)
    bot.edit_message_text(chat_id=user_id, message_id=processing_message.message_id, text="Ответ отправлен.")

def send_long_message(chat_id, text):
    while len(text) > 0:
        chunk = text[:4096] 
        bot.send_message(chat_id, chunk)
        text = text[4096:] 

def extract_text_from_pdf(file_path):
    text = ""
    reader = PdfReader(file_path)
    image_files = []
    
    for page in reader.pages:
        text += page.extract_text() or ""
        
        if '/XObject' in page['/Resources']:
            xObject = page['/Resources']['/XObject'].get_object()
            for obj in xObject:
                if xObject[obj]['/Subtype'] == '/Image':
                    img_data = xObject[obj].get_data()
                    img = Image.open(BytesIO(img_data))
                    img_file = f"./image_{obj[1:]}.png"
                    img.save(img_file)
                    image_files.append(img_file)

    for image_file in image_files:
        text_from_image = process_image(image_file)
        text += "\n" + text_from_image
    
    return text

def extract_text_from_docx(file_path):
    text = ""
    doc = Document(file_path)
    
    for para in doc.paragraphs:
        text += para.text + "\n"

    return text

def process_image(image_path):
    return image_to_string(Image.open(image_path), lang='rus')

def truncate_text(text, max_tokens=3800):
    text = text[:max_tokens]
    return text
    
def query_yandex_gpt(extracted_text, user_message, user_id):
    file_name = user_data[user_id]['file_name']
    max_chars = 3800
    responses = []

    chunks = [extracted_text[i:i + max_chars] for i in range(0, len(extracted_text), max_chars)]

    for chunk in chunks:
        messages = [
            {
                "role": "system",
                "text": "Ты — ИИ-помощник эколога, созданный для оказания помощи в понимании и анализе экологических данных и документов."
            },
            {
                "role": "user",
                "text": f"Название документа или файла: {file_name}\nКонтекст документа или файла: {chunk}\n\nЗапрос пользователя: {user_message}"
            }
        ]
        
        response = requests.post(
            config.YANDEX_GPT_API_URL,
            headers={
                "Authorization": f"Bearer {config.IAM_TOKEN}",
                "x-folder-id": config.FOLDER_ID
            },
            json={
                "modelUri": "ds://bt1uidi1ttg0a8o5efh2",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0,
                    "maxTokens": 2000,
                },
                "messages": messages
            },
        )
        
        if response.status_code != 200:
            return f"Произошла ошибка: {response.text}"
        else:
            response_text = response.json()["result"]["alternatives"][0]["message"]["text"]
            responses.append(response_text)

    full_response = "\n".join(responses)
    return full_response



if __name__ == '__main__':
    print("Запущено")
    bot.polling(none_stop=True)
