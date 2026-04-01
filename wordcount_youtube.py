import re
import sys
from collections import Counter

REGEX_ONLY_PALAVRAS = re.compile(r"\w+", re.UNICODE)

def main():
    if len(sys.argv) < 2:
        print("Uso: python wordcount_youtube.py arquivo.txt")
        sys.exit(1)

    arquivo = sys.argv[1]

    with open(arquivo, "r", encoding="utf-8") as f:
        texto = f.read().lower()

    palavras = REGEX_ONLY_PALAVRAS.findall(texto)
    contagem = Counter(palavras)

    for palavra, qtd in contagem.most_common():
        print(f"{palavra}\t{qtd}")

if __name__ == "__main__":
    main()