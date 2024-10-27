import pandas as pd
import requests
from docx import Document
import time

def load():
    # Загрузите файл test.csv
    file_path = 'test.csv'
    test_data = pd.read_csv(file_path, sep='\t')  # Укажите разделитель, если это необходимо

    # Сохраните все вопросы и документы в списки
    questions_list = test_data['Вопрос'].tolist()
    documents_list = test_data['Документ'].tolist()

    return questions_list, documents_list

def extract_text_from_docx(file_path):
    text = ""
    doc = Document(file_path)
    
    for para in doc.paragraphs:
        text += para.text + "\n"

    return text

def ask(question, document):
    if "Книга 1" in document:
        text = extract_text_from_docx('Том 1 Инвентаризация Эко Агро.docx')[:3800]
    elif "Книга 2" in document:
        text = extract_text_from_docx('Том 2 ПДВ Эко Агро.docx')[:3800]
    else:
        text = ""

    print(f"---------------\nКонтекст: {text}\n\nЗапрос: {question}\n---------------")

    prompt = {
        "modelUri": "gpt://b1gkom4fdnbic372b11j/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0,
            "maxTokens": 2000,
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты — ИИ-помощник эколога, созданный для оказания помощи в понимании и анализе экологических данных и документов."
            },
            {
                "role": "user",
                "text": f"Контекст документа или файла: {text}\n\nЗапрос пользователя: {question}"
            }
        ]
    }
        
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key AQVNyjlc9mYrrHrPV9FrS9o5Au6fNQnlW9C1Bzu8"
    }

    response = requests.post(url, headers=headers, json=prompt)

    # Извлечение текста ответа из JSON
    response_json = response.json()
    answer = response_json['result']['alternatives'][0]['message']['text'] if 'result' in response_json else 'Нет ответа'

    return answer

def main():
    questions_list, documents_list = load()

    # Открываем файл в режиме записи, что очищает его при каждом запуске
    with open('submission.csv', 'w', encoding='utf-8-sig') as f:
        # Записываем заголовок
        f.write("Номер|Ответ\n")

        for i, (question, document) in enumerate(zip(questions_list, documents_list), start=1):
            answer = ask(question, document)
            # Заменяем символы новой строки на пробел
            answer = answer.replace('\n', ' ').replace('\r', '')  # Убираем новые строки
            # Форматирование строки для записи
            line = f"{i}|\"{answer.strip()}\"\n"  # Используем | как разделитель и оборачиваем ответ в кавычки
            f.write(line)  # Записываем строку в файл
            print(line.strip())  # Печатаем строку без лишних переносов
            time.sleep(3)

if __name__ == '__main__':
    main()
