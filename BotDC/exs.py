import json
import os
import random
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXS_JSON_PATH = os.path.join(BASE_DIR, "exs.json")

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
    "sum-of-positive",
    "is-n-divisible-by-x-and-y",
    "grasshopper-summation",
    "is-it-a-palindrome",
    "string-repeat",
    "counting-sheep",
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
    "who-likes-it",
    "credit-card-mask",
    "iq-test",
    "simple-pig-latin",
    "make-a-function-that-does-arithmetic",
    "find-the-unique-number",
    "money-money-money",
    "odd-or-even",
    "get-the-middle-character",
    "sort-and-star",
    "count-odd-numbers-below-n",
    "descending-order",
    "century-from-year",
    "convert-boolean-values-to-strings-yes-or-no",
    "l1:-set-alarm",
]

FALLBACK_CONSELHOS = [
    "Nunca faça deploy na sexta-feira às 18h.",
    "Antes de otimizar o código, faça ele funcionar.",
    "Beba água e faça commits pequenos.",
    "Um problema bem entendido já está metade resolvido.",
    "Não confie em código que funcionou de primeira sem testar.",
]

FALLBACK_PIADAS = [
    ["Por que o programador usa óculos?", "Porque ele não consegue C#!"],
    ["Quantos programadores são necessários para trocar uma lâmpada?", "Nenhum, isso é problema de hardware!"],
    ["O que o código disse para o debugger?", "Pare de me seguir!"],
    ["Por que o Python foi ao psicólogo?", "Porque tinha problemas de indentação emocional."],
]


def _load_local_ex():
    with open(EXS_JSON_PATH, "r", encoding="utf-8") as arquivo_json:
        ex_maratona = json.load(arquivo_json)
    return random.choice(ex_maratona)


def random_ex():
    op = random.randint(1, 3)
    if op in (1, 2):
        try:
            return [op, _load_local_ex()]
        except Exception as e:
            print(f"Erro ao carregar exs.json: {e}")

    for _ in range(3):
        try:
            ex = random.choice(exercicios)
            url = f"https://www.codewars.com/api/v1/code-challenges/{ex}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                payload = resp.json()
                titulo = payload.get("name", ex)
                descricao = payload.get("description", "").replace("~~~", "")[:4000]
                return [3, [titulo, descricao]]
        except Exception as e:
            print(f"Erro ao buscar exercício no Codewars: {e}")

    # Fallback para o JSON local se o Codewars estiver indisponível
    return [1, _load_local_ex()]


def get_conselho() -> str:
    try:
        resp = requests.get("https://api.adviceslip.com/advice", timeout=8)
        if resp.status_code == 200:
            return resp.json()["slip"]["advice"]
    except Exception as e:
        print(f"Erro ao buscar conselho: {e}")
    return random.choice(FALLBACK_CONSELHOS)


def random_joke() -> list[str]:
    try:
        resp = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=8)
        if resp.status_code == 200:
            piada = resp.json()
            return [piada.get("setup", ""), piada.get("punchline", "")]
    except Exception as e:
        print(f"Erro ao buscar piada: {e}")
    return random.choice(FALLBACK_PIADAS)
