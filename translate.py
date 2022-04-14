import json

__all__ = ['set_language', 'get']

source_language = 'en'
target_language = 'en'

def set_language(language: str):
    global target_language
    target_language = language

def get(message: str) -> str:
    return message if target_language == source_language else translations[message]

with open('translation.json') as f:
    config = json.load(f)
    source_language = config['source']
    target_language = config['target']
    translations = config['messages']
