import random
import requests
import json 
import os


 
exercicios = [
    "calculate-bmi",
    "convert-a-number-to-a-string",
    "even-or-odd",
    "get-the-mean-of-an-array",
    "calculate-average",
    "square-n-sum",
    "convert-a-boolean-to-a-string",
    "remove-first-and-last-character",
    "square-every-digit",
    "opposite-number",
    "reversed-sequence",
    "makeuppercase",
    "remove-first-and-last-character-part-two",
    "fake-binary",
    "convert-a-string-to-a-number",
    "grasshopper-terminal-game-move-function",
    "grasshopper-debug-sayhello",
    "opposite-number",
    "sum-of-positive",
    "is-n-divisible-by-x-and-y",
    "grasshopper-summation",
    "is-it-a-palindrome",
    "calculate-bmi",
    "convert-a-boolean-to-a-string",
    "string-repeat",
    "counting-sheep",
    "convert-a-boolean-to-a-string",
    "grasshopper-ifelse-syntax-debug",
    "remove-string-spaces",
    "title-case",
    "no-zeros-for-heros",
    "vowel-count",
    "repeat-it",
    "reverse-words",
    "sum-of-two-lowest-positive-integers",
    "number-to-digit-tiers",
    "find-the-odd-int",
    "disemvowel-trolls",
    "shorten-me-cc-link",
    "digital-cypher-vol-2",
    "well-of-ideas-easy-version",
    "validate-code-with-simple-regex",
    "no-loops-1-small-enough",
    "take-a-ten-minute-walk",
    "even-or-odd-which-is-greater",
    "most-frequently-used-words-in-a-text",
    "array-plus-array",
    "counting-duplicates",
    "persistent-bugger",
    "valid-parentheses",
    "no-if-no-but",
    "shortest-word",
    "double-char",
    "highest-and-lowest",
    "alt-ergo-1",
    "who-likes-it",
    "who-likes-it",
    "credit-card-mask",
    "iq-test",
    "simple-pig-latin",
    "make-a-function-that-does-arithmetic",
    "reorder-the-word",
    "find-the-unique-number",
    "money-money-money",
    "vowel-count",
    "odd-or-even",
    "square-every-digit",
    "get-the-middle-character",
    "convert-a-string-to-a-number",
    "sort-and-star",
    "remove-first-and-last-character",
    "get-the-mean-of-an-array",
    "count-odd-numbers-below-n",
    "shortest-word",
    "descending-order",
    "even-or-odd",
    "century-from-year",
    "string-repeat",
    "no-zeros-for-heros",
    "is-it-a-palindrome",
    "square-n-sum",
    "convert-boolean-values-to-strings-yes-or-no",
    "makeuppercase",
    "remove-first-and-last-character",
    "grasshopper-summation",
    "is-it-a-palindrome",
    "l1:-set-alarm",
    "grasshopper-terminal-game-move-function",
    "grasshopper-debug-sayhello",
    "take-a-ten-minute-walk",
    "sum-of-two-lowest-positive-integers",
    "number-to-digit-tiers",
    "no-loops-1-small-enough",
    "digital-cypher-vol-2",
    "validate-code-with-simple-regex",
    "well-of-ideas-easy-version",
    "title-case",
    "repeat-it",
    "shortest-word",
    "descending-order"
]


def random_ex():
    op = random.randint(1, 3)
    while True: 
        try: 
            if(op == 1 or op == 2):
                with open(f'{os.getcwd()}/exs.json', 'r', encoding='utf-8') as arquivo_json:
                    ex_maratona = json.load(arquivo_json)

                dados = random.choice(ex_maratona)  

            else:
                
                ex = random.choice(exercicios) 

                url = 'https://www.codewars.com/api/v1/code-challenges/'+ex

                response = requests.get(url).text
                titulo = json.loads(response)['name']
                descricao = json.loads(response)['description'].replace("~~~","")

                 
                dados = [titulo,descricao]
            break
        except Exception as e:
            print(e)
            continue
    response = [op,dados]
    return response 

def get_conselho():
    while True:
        try:
            url = "	https://api.adviceslip.com/advice"
            
            conselho = json.loads(requests.get(url).text)['slip']['advice']  
            return conselho
        except:
            continue
        
def random_joke():
    url = "https://official-joke-api.appspot.com/random_joke"
    
    piada  = json.loads(requests.get(url).text)
    question = piada['setup']
    response = piada['punchline']  
      
    return [question,response]
# Agora você tem a lista de exercícios em Python.
