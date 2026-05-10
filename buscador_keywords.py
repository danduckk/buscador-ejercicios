"""
Nivel 1: Búsqueda por palabras clave (keyword matching).

Enfoque más sencillo:
- Tokenizamos la consulta y los ejercicios (título + enunciado + temas)
  pasando todo a minúsculas y quitando acentos.
- Calculamos cuántos tokens de la consulta aparecen también en el ejercicio.
- La puntuación es la fracción de tokens de la consulta que han hecho match.

Limitaciones (que motivan los siguientes niveles):
- No entiende sinónimos: "fichero" y "archivo" son tokens distintos.
- Trata todas las palabras igual de importantes (no pesa por relevancia).
- No tiene en cuenta el contexto ni el orden de las palabras.
"""

import json
import re
import unicodedata
from typing import List, Dict, Tuple


# Stopwords típicas en español. Las quitamos porque aparecen en casi todo
# y no aportan información para distinguir un ejercicio de otro.
STOPWORDS_ES = {
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    "de", "del", "al", "a", "y", "o", "u", "en", "con", "por",
    "para", "que", "se", "es", "son", "este", "esta", "estos", "estas",
    "como", "cual", "cuando", "donde", "lo", "le", "su", "sus",
    "mi", "tu", "te", "me", "no", "si", "ya", "muy", "mas", "pero",
    "haz", "hacer", "crea", "crear", "haga", "tenga", "tener",
    "script", "ejercicio", "programa",
}


def normalizar(texto: str) -> str:
    """Pasa a minúsculas y elimina acentos.

    NFD descompone cada vocal acentuada en (vocal, acento) y luego
    filtramos los caracteres de tipo combining mark (Mn). Así "á" → "a".
    """
    texto = texto.lower()
    descompuesto = unicodedata.normalize("NFD", texto)
    sin_acentos = "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")
    return sin_acentos


def tokenizar(texto: str) -> set:
    """Convierte un texto en un conjunto de tokens útiles.

    - Normaliza (minúsculas + sin acentos).
    - Extrae secuencias alfanuméricas con regex.
    - Filtra stopwords y palabras de <= 2 letras (suelen ser ruido).
    """
    texto = normalizar(texto)
    # [a-z0-9]+ captura "palabras" tras la normalización
    tokens = re.findall(r"[a-z0-9]+", texto)
    return {t for t in tokens if len(t) > 2 and t not in STOPWORDS_ES}


def tokens_ejercicio(ejercicio: Dict) -> set:
    """Construye el conjunto de tokens de un ejercicio.

    Combinamos título, enunciado y temas. Los temas son palabras clave
    ya curadas, así que nos interesa especialmente que cuenten.
    """
    partes = [
        ejercicio.get("titulo", ""),
        ejercicio.get("enunciado", ""),
        " ".join(ejercicio.get("temas", [])),
    ]
    texto = " ".join(partes)
    return tokenizar(texto)


def buscar(consulta: str, ejercicios: List[Dict], top_n: int = 3) -> List[Tuple[float, Dict]]:
    """Devuelve los top_n ejercicios más relevantes para la consulta.

    Puntuación: |tokens_consulta ∩ tokens_ejercicio| / |tokens_consulta|.
    Es decir, el porcentaje de palabras de la consulta que han aparecido
    en el ejercicio. Va de 0.0 a 1.0.
    """
    tokens_q = tokenizar(consulta)

    # Si la consulta está vacía tras filtrar stopwords, no hay nada que hacer
    if not tokens_q:
        return []

    resultados: List[Tuple[float, Dict]] = []
    for ej in ejercicios:
        tokens_e = tokens_ejercicio(ej)
        coincidencias = tokens_q & tokens_e
        puntuacion = len(coincidencias) / len(tokens_q)

        # Solo devolvemos ejercicios con al menos un token coincidente
        if puntuacion > 0:
            resultados.append((puntuacion, ej))

    # Ordenamos de mayor a menor puntuación y cogemos los top_n
    resultados.sort(key=lambda x: x[0], reverse=True)
    return resultados[:top_n]


def main() -> None:
    """Mini interfaz por consola para probar el buscador de forma aislada."""
    with open("ejercicios.json", "r", encoding="utf-8") as f:
        ejercicios = json.load(f)

    consulta = input("¿Qué quieres buscar? ")
    resultados = buscar(consulta, ejercicios)

    if not resultados:
        print("Sin resultados.")
        return

    print(f"\nTop {len(resultados)} resultados:")
    for puntuacion, ej in resultados:
        print(f"  [{puntuacion:.2f}] #{ej['id']} - {ej['titulo']} ({ej['dificultad']})")


if __name__ == "__main__":
    main()
