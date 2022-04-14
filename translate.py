import json
import os.path
import copy

__all__ = ['set_language', 'get', 'languages']

def languages() -> list[str]:
    "Returns list of available_languages"
    return copy.copy(available_languages)

def set_language(language: str):
    "Sets provided `language` as target language if it's available"
    global target_language
    assert language in available_languages, f"Provided language `{language}` is not supported"
    target_language = language

def get(message: str) -> str:
    "Returns message translated to current target language"
    return message if target_language == source_language else translations[message]

with open(f'{os.path.dirname(__file__)}/pl.json') as f:
    config = json.load(f)

source_language = config['source']
target_language = config['target']
translations    = config['messages']

available_languages = [source_language, target_language]
