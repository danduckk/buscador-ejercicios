"""
Punto de entrada interactivo del buscador de ejercicios.

Flujo:
1. Carga ejercicios.json.
2. Pregunta qué nivel de búsqueda usar (1, 2 o 3).
3. Importa el módulo correspondiente. El nivel 3 (embeddings) se importa
   solo si se elige, porque cargar sentence-transformers tarda varios
   segundos y consume RAM; no queremos pagar ese coste si no hace falta.
4. Pide la consulta y muestra los top 3 con su puntuación.
5. Pregunta cuál ver y muestra enunciado + solución.
"""

import json
import sys
from typing import List, Dict, Tuple


def cargar_ejercicios(ruta: str = "ejercicios.json") -> List[Dict]:
    """Carga la base de ejercicios desde el JSON."""
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def elegir_nivel() -> int:
    """Pide al usuario el nivel de búsqueda (1, 2 o 3) hasta que sea válido."""
    while True:
        print("\n=== BUSCADOR DE EJERCICIOS DE BASH ===")
        print("Niveles de búsqueda:")
        print("  1) Palabras clave (rápido, simple)")
        print("  2) TF-IDF + similitud coseno (mejor relevancia)")
        print("  3) Embeddings semánticos (entiende sinónimos, más lento)")

        opcion = input("Elige nivel [1-3]: ").strip()
        if opcion in {"1", "2", "3"}:
            return int(opcion)
        print("Opción no válida.")


def buscar_con_nivel(nivel: int, consulta: str, ejercicios: List[Dict]) -> List[Tuple[float, Dict]]:
    """Despacha al módulo de búsqueda adecuado.

    Importamos dentro de la función para hacer carga perezosa: solo se
    importa el módulo del nivel elegido. Especialmente importante para
    el nivel 3, que carga un modelo de varios MB.
    """
    if nivel == 1:
        from buscador_keywords import buscar
    elif nivel == 2:
        from buscador_tfidf import buscar
    else:
        from buscador_embeddings import buscar

    return buscar(consulta, ejercicios, top_n=3)


def mostrar_resultados(resultados: List[Tuple[float, Dict]]) -> None:
    """Imprime los top N con su puntuación, id, título y dificultad."""
    print("\n--- Resultados ---")
    for i, (puntuacion, ej) in enumerate(resultados, start=1):
        print(f"  {i}) [{puntuacion:.3f}] #{ej['id']} - {ej['titulo']} ({ej['dificultad']})")


def mostrar_ejercicio(ejercicio: Dict) -> None:
    """Muestra el enunciado y la solución del ejercicio elegido."""
    print("\n" + "=" * 60)
    print(f"#{ejercicio['id']} - {ejercicio['titulo']}")
    print(f"Dificultad: {ejercicio['dificultad']}")
    print(f"Temas: {', '.join(ejercicio['temas'])}")
    print("-" * 60)
    print("ENUNCIADO:")
    print(ejercicio["enunciado"])
    print("-" * 60)
    print("SOLUCIÓN:")
    print(ejercicio["solucion"])
    print("=" * 60)


def main() -> None:
    ejercicios = cargar_ejercicios()

    nivel = elegir_nivel()
    consulta = input("\n¿Qué ejercicio buscas? ").strip()

    if not consulta:
        print("Consulta vacía, saliendo.")
        sys.exit(0)

    resultados = buscar_con_nivel(nivel, consulta, ejercicios)

    if not resultados:
        print("No se han encontrado resultados.")
        sys.exit(0)

    mostrar_resultados(resultados)

    # Pedimos cuál ver. Permitimos dejar vacío para no mostrar ninguno.
    eleccion = input("\n¿Cuál quieres ver? [1-{}] (Enter para salir): ".format(len(resultados))).strip()
    if not eleccion:
        return

    if not eleccion.isdigit() or not (1 <= int(eleccion) <= len(resultados)):
        print("Opción no válida.")
        return

    _, ejercicio_elegido = resultados[int(eleccion) - 1]
    mostrar_ejercicio(ejercicio_elegido)


if __name__ == "__main__":
    main()
