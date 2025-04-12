import os
import json
import requests
from collections import OrderedDict
from openai import OpenAI

class ResumeParser:
    def __init__(self, api_key):
        self.api_key = api_key
        self.system_prompt = """Ты — профессиональный парсер резюме с безупречной точностью. Анализируй предоставленное резюме и ВОЗВРАЩАЙ ТОЛЬКО JSON без пояснений.
Требования к анализу:
1. Извлекай ВСЕ данные, включая неочевидные (например, подразумеваемые навыки в описании опыта)
2. Если информация отсутствует — указывай null
3. Сохраняй оригинальные формулировки из текста


Формат JSON (сохраняй порядок!):
{
  "personal_data": {
    "full_name": "строка",
    "date_of_birth": "DD.MM.YYYY",
    "contacts": {
      "email": "строка",
      "phones": ["массив строк"],
      "telegram": "строка/null",
      "linkedin": "строка/null"
    }
  },
  "education": [
    {
      "university": "строка",
      "degree": "строка",
      "specialization": "строка",
      "start_date": "MM.YYYY",
      "end_date": "MM.YYYY/null(если 'настоящее время')",
      "gpa": "число/null"
    }
  ],
  "skills": {
    "programming_languages": ["массив"],
    "databases": ["массив"],
    "tools": ["массив"],
    "frameworks": ["массив"]
  },
  "experience": [
    {
      "company": "строка",
      "position": "строка",
      "start_date": "MM.YYYY",
      "end_date": "MM.YYYY/null",
      "description": "строка",
      "technologies_used": ["массив"]
    }
  ],
  "additional": {
    "github": "строка/null",
    "portfolio": "строка/null",
    "languages": ["массив"],
    "certificates": ["массив"]
  }
}"""

    def parse(self, raw_text):
        try:
            response = self._call_api(raw_text)
            if not response.choices:
                return self._error_template("No response from API")
            return self._process_response(response)
        except Exception as e:
            return self._error_template(f"System error: {str(e)}")

    def _call_api(self, text):
        client = OpenAI(api_key=self.api_key, base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Резюме для анализа:\n{text}"}
            ],
            stream=False,
            temperature=0.1,  # Уменьшаем температуру для более предсказуемых ответов
            max_tokens=2000   # Увеличиваем максимальное количество токенов
        )
        return response

    def _process_response(self, response):
        try:
            if not response.choices or not response.choices[0].message:
                return self._error_template("Empty response from API")
                
            content = response.choices[0].message.content.strip()
            if not content:
                return self._error_template("Empty content in response")

            # Находим начало и конец JSON
            start = content.find('{')
            end = content.rfind('}') + 1
            if start == -1 or end == 0:
                return self._error_template("Invalid JSON response")
            json_str = content[start:end]
            
            result = json.loads(json_str, object_pairs_hook=OrderedDict)
            validated = self._validate_structure(result)
            return validated
        except json.JSONDecodeError as e:
            return self._error_template(f"JSON parsing error: {str(e)}")
        except Exception as e:
            return self._error_template(f"Validation error: {str(e)}")

    def _validate_structure(self, data):
        template = OrderedDict([
            ("personal_data", OrderedDict([
                ("full_name", None),
                ("date_of_birth", None),
                ("contacts", OrderedDict([
                    ("email", None),
                    ("phones", []),
                    ("telegram", None),
                    ("linkedin", None)
                ]))
            ])),
            ("education", [OrderedDict([
                ("institution", None),
                ("degree", None),
                ("specialization", None),
                ("start_date", None),
                ("end_date", None),
                ("gpa", None)
            ])]),
            ("skills", OrderedDict([
                ("programming_languages", []),
                ("databases", []),
                ("tools", []),
                ("frameworks", [])
            ])),
            ("experience", [OrderedDict([
                ("company", None),
                ("position", None),
                ("start_date", None),
                ("end_date", None),
                ("description", None),
                ("technologies_used", [])
            ])]),
            ("additional", OrderedDict([
                ("github", None),
                ("portfolio", None),
                ("languages", []),
                ("certificates", [])
            ]))
        ])
        
        return self._merge_structures(template, data)

    def _merge_structures(self, template, data):
        if data is None:
            return template
            
        # Рекурсивное слияние структур с сохранением порядка
        if isinstance(template, OrderedDict) and isinstance(data, dict):
            merged = OrderedDict()
            for key in template:
                merged[key] = self._merge_structures(template[key], data.get(key, None))
            return merged
        elif isinstance(template, list) and isinstance(data, list):
            if not data:  # Если список пустой
                return template
            return [self._merge_structures(template[0], item) for item in data]
        else:
            return data if data is not None else template

    def _error_template(self, message):
        return OrderedDict([
            ("error", message),
            ("data", None)
        ])

# Пример использования
api_key = os.environ["DEEPSEEK_API_KEY"]
parser = ResumeParser(api_key)

resume_text = """Иван Петров 01.01.2003 Контакты: ivan.petrov@example.com +7 900 000-00-00 Образование: технический университет с 09.2022 по настоящее время. Бакалавриат 09.03.01 Информатика и вычислительная техника. Средний балл: 4.4. Опыт: с 02.2025 - практика, разработка бэкенда на FastAPI и PostgreSQL. Навыки: Python, Docker, SQL (PostgreSQL, Redis). GitHub: github.com/example"""

result = parser.parse(resume_text)
print(json.dumps(result, indent=2, ensure_ascii=False, separators=(',', ': ')))