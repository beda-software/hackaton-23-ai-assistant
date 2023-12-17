import json
import logging
import re


def minify_json_string(value: str):
    remove_new_line = value.replace("\n", "")
    result = re.search(r"```.+```", remove_new_line).group()
    result = result.replace("```json", "")
    result = result.replace("```", "")
    logging.error("RESULT %s", result)
    return json.loads(result)
