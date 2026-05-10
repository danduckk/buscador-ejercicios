"""
Nivel 3: Búsqueda semántica con embeddings.

Mejora sobre el nivel 2 (TF-IDF):
- Un embedding es un vector denso que representa el SIGNIFICADO de un
  texto, no las palabras concretas. Por eso "archivo" y "fichero" caen
  en zonas cercanas del espacio vectorial: el modelo entiende que son
  sinónimos.
- Usamos el modelo "paraphrase-multilingual-MiniLM-L12-v2" porque es
  multilingüe (soporta español sin problemas), pequeño (~120 MB) y
  bastante rápido.

Detalle de optimización:
- Calcular embeddings es lo más caro de todo el pipeline. Como los
  ejercicios cambian poco y la consulta cambia siempre, cacheamos en
  disco los embeddings de los ejercicios con pickle. Solo recalculamos
  si cambia el número de ejercicios (heurística simple para detectar
  modificaciones en ejercicios.json).
"""

import json
import os
import pickle
from typing import List, Dict, Tuple

# Forzamos modo offline si el modelo ya está descargado en el caché de
# HuggingFace (~/.cache/huggingface/). Estas variables tienen que
# configurarse ANTES de importar sentence_transformers/transformers,
# porque las leen al importarse.
#
# La heurística: si el directorio de caché existe, asumimos que el modelo
# está descargado y activamos el modo offline. Así evitamos warnings y
# fallos por intentar comprobar actualizaciones sin conexión.
# La primera ejecución (sin caché) NO activa offline, para permitir la
# descarga inicial.
_HF_CACHE = os.path.expanduser("~/.cache/huggingface")
if os.path.isdir(_HF_CACHE):
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


MODELO = "paraphrase-multilingual-MiniLM-L12-v2"
CACHE_PATH = "embeddings_cache.pkl"


def texto_ejercicio(ejercicio: Dict) -> str:
    """Mismo formato de texto que en el nivel 2: título + enunciado + temas."""
    return " ".join([
        ejercicio.get("titulo", ""),
        ejercicio.get("enunciado", ""),
        " ".join(ejercicio.get("temas", [])),
    ])


def cargar_o_calcular_embeddings(
    ejercicios: List[Dict],
    modelo: SentenceTransformer,
) -> np.ndarray:
    """Devuelve los embeddings de los ejercicios, usando caché si es válida.

    El caché guarda una tupla (num_ejercicios, embeddings). Si el número
    actual no coincide con el del caché, recalculamos. Es una heurística
    sencilla; para producción habría que hashear el contenido también.
    """
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "rb") as f:
            num_cache, embeddings_cache = pickle.load(f)

        # Caché válida: misma cantidad de ejercicios → asumimos sin cambios
        if num_cache == len(ejercicios):
            return embeddings_cache

    # Caché ausente o invalidada: calculamos desde cero
    print("Calculando embeddings de los ejercicios (primera vez puede tardar)...")
    textos = [texto_ejercicio(e) for e in ejercicios]
    embeddings = modelo.encode(textos, convert_to_numpy=True, show_progress_bar=False)

    # Guardamos para siguientes ejecuciones
    with open(CACHE_PATH, "wb") as f:
        pickle.dump((len(ejercicios), embeddings), f)

    return embeddings


def buscar(consulta: str, ejercicios: List[Dict], top_n: int = 3) -> List[Tuple[float, Dict]]:
    """Busca semánticamente los ejercicios más parecidos a la consulta."""
    # Cargar el modelo es lento (varios segundos la primera vez), así que
    # lo hacemos dentro de buscar() solo cuando hace falta
    modelo = SentenceTransformer(MODELO)

    embeddings_ejercicios = cargar_o_calcular_embeddings(ejercicios, modelo)

    # Encode acepta string suelto pero devolvemos la consulta como matriz 1xN
    # para que cosine_similarity funcione directamente
    embedding_consulta = modelo.encode([consulta], convert_to_numpy=True)

    similitudes = cosine_similarity(embedding_consulta, embeddings_ejercicios)[0]

    # A diferencia de TF-IDF, aquí la similitud rara vez es 0 (los embeddings
    # son densos), así que devolvemos directamente los top_n sin filtrar
    resultados: List[Tuple[float, Dict]] = [
        (float(sim), ej) for sim, ej in zip(similitudes, ejercicios)
    ]
    resultados.sort(key=lambda x: x[0], reverse=True)
    return resultados[:top_n]


def main() -> None:
    with open("ejercicios.json", "r", encoding="utf-8") as f:
        ejercicios = json.load(f)

    consulta = input("¿Qué quieres buscar? ")
    resultados = buscar(consulta, ejercicios)

    if not resultados:
        print("Sin resultados.")
        return

    print(f"\nTop {len(resultados)} resultados:")
    for similitud, ej in resultados:
        print(f"  [{similitud:.3f}] #{ej['id']} - {ej['titulo']} ({ej['dificultad']})")


if __name__ == "__main__":
    main()
