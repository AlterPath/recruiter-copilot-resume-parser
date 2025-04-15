# Recruiter Copilot: парсер резюме на LLM

[English version](README.en.md)

Модуль хакатонного прототипа Recruiter Copilot (апрель 2025, кейс «Система автоматизированного анализа соответствия компетенций IT-специалистов требованиям рынка»). Это ранняя демо-версия идеи, из которой потом вырос выпускной проект Samsung: [CV-skills-extractor](https://github.com/AlterPath/CV-skills-extractor). Прототип делала команда, в этом репозитории мой модуль, парсер резюме.

## Как работает

1. Текст резюме отправляется в DeepSeek через OpenAI-совместимый клиент (`openai`). Параметры запроса: temperature 0,1 и max_tokens 2000, инструкция требует вернуть строго JSON.
2. Из ответа вырезается JSON между первой `{` и последней `}` и разбирается с сохранением порядка ключей (`OrderedDict`).
3. Результат сливается с эталонным шаблоном. Отсутствующие поля заполняются пустыми значениями, поэтому структура на выходе всегда одинаковая.
4. При ошибке API или разбора возвращается шаблон ошибки с сообщением.

Структура ответа:

```json
{
  "personal_data": {"full_name": null, "date_of_birth": null,
                    "contacts": {"email": null, "phones": [], "telegram": null, "linkedin": null}},
  "education": [{"institution": null, "degree": null, "specialization": null,
                 "start_date": null, "end_date": null, "gpa": null}],
  "skills": {"programming_languages": [], "databases": [], "tools": [], "frameworks": []},
  "experience": [{"company": null, "position": null, "start_date": null, "end_date": null,
                  "description": null, "technologies_used": []}],
  "additional": {"github": null, "portfolio": null, "languages": [], "certificates": []}
}
```

## Запуск

```bash
pip install -r requirements.txt
export DEEPSEEK_API_KEY="ваш ключ"
# необязательно: свой OpenAI-совместимый адрес
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
python resume_parser.py
```

Скрипт разбирает встроенный пример резюме (выдуманный) и печатает JSON.

## Стек

Python, OpenAI SDK, DeepSeek API.

## Лицензия

[MIT](LICENSE)
