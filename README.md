# Laboratorio #4 - Teoria de la Computacion   
Link del video explicativo en Youtube: https://youtu.be/9AhDi45CJV8
Usos del programa:

1. Convierte la expresion regular a **postfix** (Shunting Yard, reutilizado del `Ejercicio 4` del Lab 2 -> `regex_shunting_yard.py`).
2. Construye el **arbol sintactico** a partir del postfix (igual que en el Lab 3; `+` y `?` se expanden a su forma base `a.a*` y `a|eps` antes de construir el arbol.
3. Construye el **AFN por el metodo de Thompson**, recorriendo el arbol en depth-first (post-orden): cada nodo hoja (`a` o `ε`) genera un fragmento con un estado inicial y uno de aceptacion, y cada operador combina los fragmentos de sus hijos siguiendo las reglas de union (`|`), concatenacion (`.`) y cerradura de Kleene (`*`).
4. **Despliega el AFN** en texto (lista de transiciones en la consola/reporte) y dibujado (PNG generado con Graphviz) para consulta.
5. **Simula la cadena** sobre el AFN calculando epsilon-clausuras y movimientos por simbolo.
6. Responde **"si" o "no"** sobre la aceptacion de la cadena.

## Requisitos

- **Python 3** .
- **Graphviz** (el comando `dot`) para generar el dibujo del AFN. Si no esta instalado, el programa sigue funcionando igual (imprime el AFN en texto), solo no genera el `.png`.

Verificar si Graphviz esta instalado:

```bash
dot -V
```

Si no aparece una version, instalar con:

- **macOS** (con [Homebrew](https://brew.sh)):
  ```bash
  brew install graphviz
  ```
- **Windows**: descargar el instalador desde [graphviz.org/download](https://graphviz.org/download/).
- **Linux (Debian/Ubuntu)**:
  ```bash
  sudo apt install graphviz
  ```

## Como correr el programa

Desde una terminal, ubicado en la carpeta del programa:

```bash
python3 lab4.py
```

Esto lee `input.txt` y por cada expresion regular imprime en la terminal (y guarda en `output/reporte.txt`):

- El postfix (Shunting Yard).
- El AFN de Thompson en texto (estados, inicial, aceptacion y transiciones).
- La ruta del dibujo del AFN (`output/afn_a.png`, `afn_b.png`, `afn_c.png`, `afn_d.png`.)
- La simulacion paso a paso  de cada cadena de prueba y la respuesta final ("si"/"no").
- Un resumen  con todas las cadenas probadas y su resultado.

También se puede correr con un archivo de entrada distinto:

```bash
python3 lab4.py otro_input.txt
```

## Formato de `input.txt`

```
REGEX: <expresion regular>
CADENA: <cadena a probar>
CADENA: <otra cadena a probar>
```

- Puede haber varias lineas `CADENA:` por cada `REGEX:` (para ver, con el mismo automata, casos aceptados y rechazados).
- Una `CADENA:` vacia, `eps` o `ε` representa la cadena vacia.
- Dentro de la expresion regular, `eps` tambien se interpreta como `ε`.
- Lineas que empiezan con `#` son comentarios.

## Expresiones regulares procesadas

Las 4 expresiones pedidas en el enunciado, cada una con cadenas aceptadas y rechazadas de prueba:

- `(a*|b*)+`
- `((eps|a)|b*)*`
- `(a|b)*abb(a|b)*`
- `0?(1?)?0*`
