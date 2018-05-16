from django import template
import re

wikiWord = re.compile(r"\[\[([A-Za-z0-9_]+)\]\]")

register = template.Library()

@register.filter
def wikify(text):
    return wikiWord.sub(r'''
    <a href="/wiki/\1/">\1</a>
    ''', text)