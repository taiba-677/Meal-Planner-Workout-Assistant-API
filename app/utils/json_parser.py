import json
import re


def safe_parse_json(text: str):
    """
    Cleans and safely parses LLM output into JSON.
    Handles:
    - Markdown code fences (```json ... ```)
    - Extra trailing text after the JSON object (JSONDecodeError: Extra data)
    - Leading/trailing whitespace
    """

    if not text:
        raise ValueError("Empty response from model")

    text = text.strip()

    # Remove markdown fences
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)
    text = text.strip()

    # First try a direct parse (fastest path)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    if start == -1:
        start = text.find("[")
    if start == -1:
        raise ValueError("No JSON object found in model response")

    open_char  = text[start]
    close_char = "}" if open_char == "{" else "]"
    depth = 0
    in_string = False
    escape_next = False

    for i, ch in enumerate(text[start:], start=start):
        if escape_next:
            escape_next = False
            continue
        if ch == "\\" and in_string:
            escape_next = True
            continue
        if ch == '"' and not escape_next:
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == open_char:
            depth += 1
        elif ch == close_char:
            depth -= 1
            if depth == 0:
                candidate = text[start:i + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON format from model: {str(e)}")

    raise ValueError("Incomplete JSON object in model response")