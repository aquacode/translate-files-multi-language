# stdlib
from datetime import datetime
import json
import os
import os.path
import sys

# third party
from google.cloud import translate
from jproperties import Properties
import click

# globals
CURR_LANGUAGE = None
client = translate.TranslationServiceClient()
GOOGLE_PARENT_PROJECT = None


def printMap(m):
    for k,v in m.items():
        if isinstance(v, dict):
            print(k)
            printMap(v)
        elif isinstance(v, str):
            print("{}: {}".format(k, v))

def convertStr(data, ignore_dicts=False):
    if isinstance(data, str):
        print("translate: {} to language: {}".format(data, CURR_LANGUAGE))
        response = client.translate_text(parent=GOOGLE_PARENT_PROJECT, mime_type="text/plain", target_language_code=CURR_LANGUAGE, contents=[data])
        trans = response.translations
        print("result: {} \n".format(trans[0].translated_text))
        return trans[0].translated_text
    if isinstance(data, list):
        return [convertStr(item, ignore_dicts=True) for item in data]
    if isinstance(data, dict) and not ignore_dicts:
        return {
            key: convertStr(value, ignore_dicts=True) for key, value in data.items()
        }
    return data

def propsTranslator(separator, inputfile, languages):
    global CURR_LANGUAGE
    for curr in languages:
        CURR_LANGUAGE = curr
        props = Properties()
        with open(inputfile, 'rb') as f:
            props.load(f, encoding='utf-8')
            newProps = Properties()
            for k,v in props.items():
                print("translate: {} to language: {}".format(v.data, CURR_LANGUAGE))
                response = client.translate_text(parent=GOOGLE_PARENT_PROJECT, mime_type="text/plain", target_language_code=CURR_LANGUAGE, contents=[v.data])
                trans = response.translations
                print("result: {} \n".format(trans[0].translated_text))
                newProps[k] = trans[0].translated_text

            base = os.path.basename(inputfile)
            filename = os.path.splitext(base)[0]
            with open(filename+separator+CURR_LANGUAGE+'.properties', 'wb') as newF:
                newProps.store(newF, encoding='utf-8')

def jsonTranslator(separator, inputfile, languages):
    global CURR_LANGUAGE
    for curr in languages:
        CURR_LANGUAGE = curr
        print("Translating to language: {}".format(CURR_LANGUAGE))
        with open(inputfile, 'r') as f:
            data = json.load(f, object_hook=convertStr)

        base = os.path.basename(inputfile)
        filename = os.path.splitext(base)[0]
        with open(filename+separator+CURR_LANGUAGE+'.json', 'w') as w:
            print("Writing out translated file")
            json.dump(data, w, ensure_ascii=False, indent=2)

# Class that allows aliases for commands
class CustomMultiCommand(click.Group):
    def command(self, *args, **kwargs):
        def decorator(f):
            if isinstance(args[0], list):
                _args = [args[0][0]] + list(args[1:])
                for alias in args[0][1:]:
                    cmd = super(CustomMultiCommand, self).command(alias, *args[1:], **kwargs)(f)
                    cmd.short_help = "Alias for '{}'".format(_args[0])
            else:
                _args = args
            cmd = super(CustomMultiCommand, self).command(*_args, **kwargs)(f)
            return cmd

        return decorator

# Main Entrypoint Function
@click.group(cls=CustomMultiCommand)
def main():
    pass

@main.command(["translate"])
@click.option("--separator", type=click.Choice(['_', '-'], case_sensitive=False), default="_", show_default=True)
@click.argument("filename", type=click.Path(exists=True))
@click.argument("languages", nargs=-1)
def translate(separator, filename, languages):

    global GOOGLE_PARENT_PROJECT
    creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not creds:
        sys.exit("GOOGLE_APPLICATION_CREDENTIALS is required!")
    proj = os.getenv('GOOGLE_PARENT_PROJECT')
    if not proj:
        sys.exit("GOOGLE_PARENT_PROJECT is required!")
    else:
        GOOGLE_PARENT_PROJECT = proj

    if languages:
        if filename.endswith('json'):
            jsonTranslator(separator, filename, languages)
        elif filename.endswith('properties'):
            propsTranslator(separator, filename, languages)
    else:
        print("Empty list of languages")

if __name__ == '__main__':
    main()
