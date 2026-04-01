import os
import argparse
from urllib.parse import urlparse, parse_qs

import requests
from youtube_transcript_api import YouTubeTranscriptApi


def extrair_video_id(valor: str) -> str:
    valor = valor.strip()

    if "youtube.com" in valor or "youtu.be" in valor:
        parsed_url = urlparse(valor)

        if parsed_url.netloc.endswith("youtu.be"):
            return parsed_url.path.strip("/")

        if "watch" in parsed_url.path:
            return parse_qs(parsed_url.query).get("v", [""])[0]

    return valor


def pesquisar_video(query: str, api_key: str, max_results: int = 5) -> list[dict]:
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": api_key,
        "relevanceLanguage": "pt",
    }

    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    resultados = []
    for item in data.get("items", []):
        video_id = item.get("id", {}).get("videoId", "")
        snippet = item.get("snippet", {})

        if video_id:
            resultados.append(
                {
                    "video_id": video_id,
                    "titulo": snippet.get("title", ""),
                    "canal": snippet.get("channelTitle", ""),
                }
            )

    return resultados


def obter_transcricao(video_id: str, idiomas=None) -> str:
    if idiomas is None:
        idiomas = ["pt", "pt-BR", "pt-PT", "en"]

    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id, languages=idiomas)

    partes = []
    for trecho in transcript:
        texto = trecho.text.strip() if hasattr(trecho, "text") else str(trecho).strip()
        if texto:
            partes.append(texto)

    return "\n".join(partes)


def main():
    parser = argparse.ArgumentParser(
        description="Busca um vídeo no YouTube e salva a transcrição em arquivo txt"
    )
    parser.add_argument("--url", help="URL do YouTube ou ID do vídeo")
    parser.add_argument("--search", help="Termo de busca para encontrar o vídeo")
    parser.add_argument("--pick", type=int, default=1, help="Qual resultado escolher")
    parser.add_argument(
        "--output",
        default="transcricao.txt",
        help="Arquivo de saída da transcrição",
    )
    args = parser.parse_args()

    video_id = None

    if args.url:
        video_id = extrair_video_id(args.url)

    elif args.search:
        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Defina a variável de ambiente YOUTUBE_API_KEY para pesquisar vídeos."
            )

        resultados = pesquisar_video(args.search, api_key)

        if not resultados:
            raise RuntimeError("Nenhum vídeo encontrado para a busca.")

        print("\nResultados encontrados:\n")
        for i, item in enumerate(resultados, start=1):
            print(f"{i}. {item['titulo']} | {item['canal']} (ID: {item['video_id']})")

        indice = args.pick - 1
        if indice < 0 or indice >= len(resultados):
            raise ValueError("Valor inválido para --pick.")

        video_id = resultados[indice]["video_id"]

    else:
        raise RuntimeError("Use --url ou --search.")

    texto = obter_transcricao(video_id)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(texto)

    print(f"\nTranscrição salva em: {args.output}")
    print(f"video_id: {video_id}")
    print("\nPrévia da transcrição:\n")
    print(texto[:1200])


if __name__ == "__main__":
    main()