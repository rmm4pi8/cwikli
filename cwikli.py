#!/bin/env python3

# a cli interface to en.wiktionary.org
# requires python 3.6 for proper unicode support on windows cli

import sys, argparse, requests
from bs4 import BeautifulSoup

def note(lang):
  if lang == 'grc':
    print('Greek text must be input in Greek characters.  Accents are mandatory; inflected forms are not supported. Search will work correctly even if the characters do not display correctly.')
    print('Greek characters can be input by keyboard character mapping, on-screen-keyboard, or copy/paste -- see goo.gl/LhUuXC for help on Windows.')
  elif lang == 'de':
    print('German text must be input in German characters with modern spelling and correct capitalization.  Augmented and inflected forms are generally supported.  Search will work correctly even if the characters do not display correctly.')
    print('German characters can be input by keyboard character mapping, on-screen-keyboard, or copy/paste -- see goo.gl/LhUuXC for help on Windows.')
  elif lang == 'la':
    print('Latin supports almost all inflected forms.  Do not use macrons.')

def getdefn(word, lang):
  # scrape Wiktionary
  try:
    wikipage_raw = requests.get('http://en.wiktionary.org/wiki/' + word, timeout=1)
    wikipage_raw.raise_for_status()
  except requests.exceptions.TooManyRedirects:
    sys.exit('This Wiktionary page is broken.')
  except requests.exceptions.Timeout:
    sys.exit('Wiktionary is responding too slowly.')
  except requests.exceptions.ConnectionError:
    sys.exit('Could not connect to en.wiktionary.org')
  except requests.exceptions.HTTPError:
    print('This word is not on en.wiktionary.org -- try entering the uninflected or unaugmented form instead, and make sure that any non-Roman characters are entered correctly.')
    note(lang)
    return 
  
  # parse the results  
  try:
    wikipage_parsed = BeautifulSoup(wikipage_raw.content, 'html.parser')
  except HTMLParser.HTMLParseError:
    sys.exit('This Wiktionary page is malformed.')
    
  # strip the quotes
  for ul in wikipage_parsed('ul'):
    ul.decompose()
  # strip the usage examples
  for dd in wikipage_parsed('dd'):
    dd.decompose()
  
  # find the headwords
  try:
    headwords = wikipage_parsed.find_all('strong', lang=lang)
  except KeyError:
    sys.exit('This Wiktionary page does not look like we expected.')
  except AttributeError:
    sys.exit('en.wiktionary.org may not define this word in your target language, or you have entered an incorrect language code.')

  for headword in headwords:
    # print the part of speech
    try:
      print(headword.parent.find_previous('span', class_='mw-headline')['id'])
    except KeyError:
      sys.exit('This Wiktionary page does not look like we expected.')
    except AttributeError:
      sys.exit('This Wiktionary page does not look like we expected.')
      
    # print the corresponding definitions
    try:
      print(headword.parent.find_next('ol').get_text(" ", strip=True))
    except AttributeError:
      sys.exit('This Wiktionary page does not look like we expected.')

# parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument('-l', '--lang', metavar='lang', type=str, help='the two letter language code for modern languages, la for Latin, or grc for Greek')
parser.add_argument('-w', '--word', metavar='word', type=str, help='the word; inflected forms work often but not always.  Input non-Roman characters by any native method--search will work correctly even if they do not display correctly.  Accents are mandatory.')
args = parser.parse_args()

# run in one-time mode
if args.lang and args.word:
  getdefn(args.word, args.lang)
  sys.exit()
# get language if not given as an argument
elif args.lang:
  lang = args.lang
else:
  print('Welcome to cwikli, the command line Wiktionary scraper.')
  lang = input('Enter the two letter language code for modern languages, la for Latin, or grc for Greek: ')
  note(lang)
# run in repeated input mode
while not args.word:
  try:
    word = input('Enter a word, or Ctrl-c to exit or change languages: ')
  except KeyboardInterrupt:
    sys.exit(1)
  getdefn(word, lang) 