"""
Nivel 2: Búsqueda con TF-IDF + similitud coseno.

Mejora sobre el nivel 1 (keywords):
- TF-IDF pesa cada palabra: una palabra que aparece en TODOS los ejercicios
  (p.ej. "fichero") pesa poco; una rara y específica (p.ej. "palindromo")
  pesa mucho. Así los matches relevantes destacan.
- Con ngram_range=(1, 2) capturamos también bigramas como "leer fichero",
  que aportan más contexto que palabras sueltas.
- La similitud coseno mide el ángulo entre los vectores de consulta y
  ejercicio: 1.0 = idénticos, 0.0 = sin relación.

Limitaciones que motivan el nivel 3:
- Sigue siendo léxico: "archivo" y "fichero" no se reconocen como sinónimos
  porque son tokens distintos.
"""

import json
from typing import List, Dict, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Lista hardcoded porque sklearn no trae stopwords en español de serie.
# Replicamos la idea del nivel 1 pero como lista (lo que espera sklearn).
STOPWORDS_ES = [
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    "de", "del", "al", "a", "y", "o", "u", "en", "con", "por",
    "para", "que", "se", "es", "son", "este", "esta", "estos", "estas",
    "como", "cual", "cuando", "donde", "lo", "le", "su", "sus",
    "mi", "tu", "te", "me", "no", "si", "ya", "muy", "mas", "pero",
    "haz", "hacer", "crea", "crear", "haga", "tenga", "tener",
    "script", "ejercicio", "programa",
]


def texto_ejercicio(ejercicio: Dict) -> str:
    """Concatena los campos de un ejercicio en un solo string.

    El vectorizador trabaja con texto plano, así que juntamos título,
    enunciado y temas en una única cadena por ejercicio.
    """
    return " ".join([
        ejercicio.get("titulo", ""),
        ejercicio.get("enunciado", ""),
        " ".join(ejercicio.get("temas", [])),
    ])


def buscar(consulta: str, ejercicios: List[Dict], top_n: int = 3) -> List[Tuple[float, Dict]]:
    """Busca los ejercicios más similares a la consulta usando TF-IDF.

    Truco clave: vectorizamos consulta + ejercicios JUNTOS con un único
    fit_transform. Si vectorizáramos por separado, el vocabulario y los
    pesos IDF serían distintos en cada llamada y los vectores no serían
    comparables.
    """
    textos_ejercicios = [texto_ejercicio(e) for e in ejercicios]

    # El último elemento del corpus es la consulta; los anteriores son ejercicios
    corpus = textos_ejercicios + [consulta]

    vectorizador = TfidfVectorizer(
        stop_words=STOPWORDS_ES,
        ngram_range=(1, 2),  # unigramas y bigramas
        min_df=1,            # acepta términos que aparezcan al menos 1 vez
        lowercase=True,
    )
    matriz = vectorizador.fit_transform(corpus)

    # Separamos: la última fila es la consulta, el resto son los ejercicios
    vector_consulta = matriz[-1]
    matriz_ejercicios = matriz[:-1]

    # cosine_similarity devuelve una matriz; con [0] sacamos el array 1D
    # de similitudes consulta-vs-ejercicios
    similitudes = cosine_similarity(vector_consulta, matriz_ejercicios)[0]

    # Empaquetamos cada similitud con su ejercicio y filtramos las > 0
    resultados: List[Tuple[float, Dict]] = [
        (float(sim), ej)
        for sim, ej in zip(similitudes, ejercicios)
        if sim > 0
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
