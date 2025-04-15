# Recruiter Copilot: LLM Resume Parser

[Русская версия](README.md)

A module of the Recruiter Copilot hackathon prototype (April 2025, case "Automated analysis of IT specialists' competencies against market requirements"). It is an early demo of the idea that later grew into a Samsung capstone project: [CV-skills-extractor](https://github.com/AlterPath/CV-skills-extractor). The prototype was built by a team; this repository holds my module, the resume parser.

## How it works

1. The resume text goes to DeepSeek through an OpenAI-compatible client (`openai`). The request uses temperature 0.1 and max_tokens 2000, and the instruction asks for strict JSON only.
2. The JSON between the first `{` and the last `}` is cut out of the answer and parsed with key order preserved (`OrderedDict`).
3. The result is merged into a reference template. Missing fields get empty values, so the output always has the same structure.
4. On an API or parsing error, an error template with a message is returned.

Output structure:

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

## Quick start

```bash
pip install -r requirements.txt
export DEEPSEEK_API_KEY="your key"
# optional: your own OpenAI-compatible endpoint
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
python resume_parser.py
```

The script parses a built-in sample resume (fictional) and prints the JSON.

## Tech stack

Python, OpenAI SDK, DeepSeek API.

## License

[MIT](LICENSE)
