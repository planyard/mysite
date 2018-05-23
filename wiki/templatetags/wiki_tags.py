from django import template
import re

wikiWord = re.compile(r"\[\[([A-Za-z0-9_]+)\]\]")
wikiFile = re.compile(r"\[\{([-A-Za-z0-9._]+)\}\]")

register = template.Library()

@register.filter
def wikify(text):
    text = wikiWord.sub(r'''
    <a href="/wiki/\1/">\1</a>
    ''', text)
    text = wikiFile.sub(r'''
    <image src="/media/uploads/\1/"/>
    ''', text)
    return text

