# Buscador de Ejercicios de Bash

Buscador interactivo en Python para localizar ejercicios de bash a partir
de un enunciado en lenguaje natural. La gracia del proyecto es que
implementa **tres niveles de búsqueda con complejidad creciente**, para
ver cómo cada técnica mejora sobre la anterior.

Pensado como apoyo para repasar la asignatura de Sistemas Operativos /
Linux de 1º DAM (especialmente bash scripting).

## Estructura

```
buscador-ejercicios/
├── ejercicios.json          # Base de conocimiento
├── buscador_keywords.py     # Nivel 1: palabras clave
├── buscador_tfidf.py        # Nivel 2: TF-IDF + similitud coseno
├── buscador_embeddings.py   # Nivel 3: embeddings semánticos
├── main.py                  # Menú interactivo
├── run.sh                   # Lanzador (activa el venv y ejecuta main.py)
├── requirements.txt
└── README.md
```

## Primera vez en un ordenador nuevo

Si te traes el proyecto a otro PC (Linux/macOS), sigue estos pasos en
orden. Solo hay que hacerlo **una vez**.

### 1. Requisitos previos

- **Python 3.10 o superior** (`python3 --version` para comprobarlo).
- **git** (si vas a clonar el repo).
- **Conexión a internet** para la primera ejecución (necesaria para
  instalar dependencias y, si vas a usar el nivel 3, descargar el modelo).
  Después funciona offline.

### 2. Conseguir el código

```bash
# Opción A: clonar el repo
git clone <url-del-repo> buscador-ejercicios
cd buscador-ejercicios

# Opción B: copiar la carpeta a mano (USB, scp, lo que prefieras)
cd ruta/donde/lo/copiaste/buscador-ejercicios
```

### 3. Crear el entorno virtual e instalar dependencias

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> Esto descargará varios cientos de MB (`torch`, `sentence-transformers`
> y dependencias CUDA si tienes GPU). Tarda unos minutos la primera vez.

### 4. (Opcional) Pre-descargar el modelo del nivel 3

Si vas a usar el nivel 3 y quieres trabajar offline después, lánzalo
**con conexión** una primera vez para que descargue el modelo
(`paraphrase-multilingual-MiniLM-L12-v2`, ~120 MB) y genere el caché
de embeddings:

```bash
./run.sh
# Elige nivel 3, escribe cualquier consulta y deja que termine
```

A partir de aquí, el modelo queda cacheado en `~/.cache/huggingface/`
y `buscador_embeddings.py` activa automáticamente el modo offline.

### 5. Uso normal a partir de ahora

```bash
./run.sh
```

`run.sh` se encarga de usar el Python del venv, así que **no** necesitas
acordarte de hacer `source .venv/bin/activate` cada vez.

## Uso

```bash
./run.sh
```

El script te preguntará:
1. Qué nivel de búsqueda usar (1, 2 o 3).
2. Tu consulta (p.ej. "como leer un archivo línea a línea").
3. Cuál de los top 3 resultados quieres ver. Te muestra enunciado y
   solución.

### Ejecutar un nivel suelto

Cada buscador tiene su propio `main()` para probarlo aislado (recuerda
activar el venv primero, o llamar directamente al python del venv):

```bash
.venv/bin/python buscador_keywords.py
.venv/bin/python buscador_tfidf.py
.venv/bin/python buscador_embeddings.py
```

## Cómo añadir ejercicios

Edita `ejercicios.json` y añade un nuevo objeto al array siguiendo el
esquema:

```json
{
  "id": 16,
  "titulo": "Título corto y descriptivo",
  "temas": ["lista", "de", "palabras_clave"],
  "dificultad": "facil | media | dificil",
  "enunciado": "Lo que pediría un examen...",
  "solucion": "#!/bin/bash\n..."
}
```

> Si añades o quitas ejercicios y estás usando el nivel 3, el caché
> (`embeddings_cache.pkl`) se invalidará automáticamente la próxima
> ejecución, porque cambia el número de ejercicios.

## Comparativa de los tres niveles

| Aspecto | Nivel 1: Keywords | Nivel 2: TF-IDF | Nivel 3: Embeddings |
|---|---|---|---|
| Idea | ¿Qué palabras de la consulta aparecen literalmente en el ejercicio? | Pesa cada palabra por su rareza global y mide ángulo entre vectores. | Compara el SIGNIFICADO del texto, no las palabras. |
| Sinónimos | No los detecta | No los detecta | Los detecta ("archivo" ≈ "fichero") |
| Velocidad | Muy rápido | Rápido | Lento la 1ª vez (carga modelo); rápido después con caché |
| Dependencias | Solo stdlib | scikit-learn | sentence-transformers (~120 MB de modelo) |
| Cuándo usarlo | Pruebas rápidas, vocabulario controlado | Búsquedas tipo "buscador clásico" | Consultas con lenguaje natural variado |
| Limitación principal | Trata todas las palabras igual | Sigue siendo léxico (no entiende sinónimos) | Más recursos / latencia |

### Ejemplo ilustrativo

Consulta: **"abrir un archivo y contar las filas"**

- **Nivel 1**: probablemente NO encuentre el ejercicio "Contar líneas
  de un fichero", porque "archivo"/"fichero" y "filas"/"líneas" son
  tokens distintos.
- **Nivel 2**: igual de mal por la misma razón, aunque podría rescatarlo
  si "contar" pesa lo bastante.
- **Nivel 3**: lo encuentra sin problema, porque entiende que las dos
  frases significan lo mismo.

## Notas de implementación

- Los comentarios del código están en español y explican el **qué** y el
  **por qué** de cada decisión, no detalles obvios de sintaxis.
- Los tres buscadores comparten la firma:
  `buscar(consulta, ejercicios, top_n=3) -> List[Tuple[float, Dict]]`
  para que sean intercambiables desde `main.py`.
- El nivel 3 se importa de forma perezosa en `main.py` (solo cuando se
  elige), para no pagar el coste de cargar el modelo si no hace falta.
