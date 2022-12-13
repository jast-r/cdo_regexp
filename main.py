import re
import fastapi
from pydantic import BaseModel

class TextHandlerRequest(BaseModel):
    text: str

class TextHandlerResponse(BaseModel):
    handled_text: str

app = fastapi.FastAPI()

@app.post("/handler/text")
def text_handler(request: TextHandlerRequest):
    return TextHandlerResponse(handled_text=process_text(request.text))


def process_text(text: str) -> str:
    text = _add_spaces(text)
    text = _remove_spaces(text)
    text = _remove_duplicates(text)
    text = _fix_capitalization(text)

    text = text.strip()

    if text[0].islower():
        text = text[0].upper() + text[1:]
      
    if not text.endswith((".", "?", "!")):
        text += "."

    return text.replace("\\", "")


def _add_spaces(text: str) -> str:
    put_space_after = r"[,\.;:\?!\)\]\}\"']"
    put_space_near = r"[—]"

    text = re.sub(put_space_after, lambda m: m.group(0) + " ", text)
    text = re.sub(put_space_near, lambda m: " " + m.group(0) + " ", text)

    return text


def _remove_spaces(text: str) -> str:
    remove_spaces_before = r"\s+([,\.;:\?!\)\]\}])"
    remove_spaces_after = r"([\(\[\{'\"])\s+"
    quotes = r"[\"']\s*([^\"]*?)\s*[\"']"
    dash = r"\s*(-)\s*"

    text = re.sub(remove_spaces_before, r"\1", text)
    text = re.sub(remove_spaces_after, r"\1", text)
    text = re.sub(
        quotes,
        lambda m: "%s%s%s" % (m.group(0)[0], m.group(1), m.group(0)[-1]),
        text,
    )
    text = re.sub(dash, r"\1", text)

    return text


def _fix_capitalization(text: str) -> str:
    text = text.capitalize()

    punctuation_marks = r"([\.\?!])\s+(.)"

    text = re.sub(punctuation_marks, lambda m: m.group(1) + " " + m.group(2).upper(), text)

    return text


def _remove_duplicates(text: str) -> str:
    punctuation_marks_duplicates = r"(\W)(?=\1)"
    text = re.sub(punctuation_marks_duplicates, "", text)

    return text

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)