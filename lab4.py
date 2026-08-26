#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 4 - Teoria de la Computacion    Natanael Girón
"""

import sys
import subprocess
import itertools
from pathlib import Path
from collections import defaultdict

import regex_shunting_yard as sy

OP_LABEL = {"STAR": "*", "CONCAT": ".", "UNION": "|"}


# Normalizacion de entrada + adaptador de postfix (string -> tokens)

def normalize_expr(expr):
    return expr.replace("eps", "ε").replace(" ", "")


def normalize_cadena(raw):
    """Cadena vacia explicita: campo vacio, 'eps' o 'ε'."""
    c = raw.strip()
    if c in ("", "eps", "ε"):
        return ""
    return c


def postfix_str_to_tokens(postfix_str):
    tokens = []
    for c in postfix_str:
        if c in sy.PRECEDENCIA:
            tokens.append((c, c))
        elif c == "ε":
            tokens.append(("EPS", c))
        else:
            tokens.append(("LIT", c))
    return tokens


#  Nodo del arbol sintactico + construccion desde postfix

class Node:
    _uid = itertools.count(1)

    def __init__(self, kind, value=None, left=None, right=None):
        self.id = next(Node._uid)
        self.kind = kind            # LIT, EPS, STAR, CONCAT, UNION
        self.value = value
        self.left = left
        self.right = right

    def clone(self):
        return Node(self.kind, value=self.value,
                    left=self.left.clone() if self.left else None,
                    right=self.right.clone() if self.right else None)


def build_tree(postfix):
    """Postfix -> arbol sintactico. '+' y '?' se expanden a su forma base
    (a+ = a.a*,  a? = a|eps) para que el arbol solo tenga los operadores
    para los que el metodo de Thompson define una regla: '|', '.' y '*'."""
    stack = []
    for kind, val in postfix:
        if kind == "LIT":
            stack.append(Node("LIT", value=val))
        elif kind == "EPS":
            stack.append(Node("EPS"))
        elif kind == "*":
            child = stack.pop()
            stack.append(Node("STAR", left=child))
        elif kind == "+":                       # a+ = a . a*
            child = stack.pop()
            stack.append(Node("CONCAT", left=child,
                              right=Node("STAR", left=child.clone())))
        elif kind == "?":                        # a? = a | eps
            child = stack.pop()
            stack.append(Node("UNION", left=child, right=Node("EPS")))
        elif kind == ".":
            right = stack.pop()
            left = stack.pop()
            stack.append(Node("CONCAT", left=left, right=right))
        elif kind == "|":
            right = stack.pop()
            left = stack.pop()
            stack.append(Node("UNION", left=left, right=right))
        else:
            raise ValueError(f"Token postfix desconocido: {kind}")
    if len(stack) != 1:
        raise ValueError("Expresion postfix invalida (arbol no se reduce a una raiz)")
    return stack[0]


# Construccion de Thompson (recorrido depth-first / post-orden del arbol)
# Usando referencias del lab anterior

class NFA:
    def __init__(self):
        self.transitions = defaultdict(list)   # estado -> [(simbolo|None, destino)]
        self.num_states = 0

    def new_state(self):
        s = self.num_states
        self.num_states += 1
        return s

    def add_edge(self, src, symbol, dst):
        self.transitions[src].append((symbol, dst))


def thompson(node, nfa):
    """Devuelve (estado_inicial, estado_aceptacion) del fragmento de N(node)."""
    if node.kind == "LIT":
        i, f = nfa.new_state(), nfa.new_state()
        nfa.add_edge(i, node.value, f)
        return i, f

    if node.kind == "EPS":
        i, f = nfa.new_state(), nfa.new_state()
        nfa.add_edge(i, None, f)
        return i, f

    if node.kind == "CONCAT":
        s1, a1 = thompson(node.left, nfa)
        s2, a2 = thompson(node.right, nfa)
        nfa.add_edge(a1, None, s2)
        return s1, a2

    if node.kind == "UNION":
        s1, a1 = thompson(node.left, nfa)
        s2, a2 = thompson(node.right, nfa)
        i, f = nfa.new_state(), nfa.new_state()
        nfa.add_edge(i, None, s1)
        nfa.add_edge(i, None, s2)
        nfa.add_edge(a1, None, f)
        nfa.add_edge(a2, None, f)
        return i, f

    if node.kind == "STAR":
        s1, a1 = thompson(node.left, nfa)
        i, f = nfa.new_state(), nfa.new_state()
        nfa.add_edge(i, None, s1)
        nfa.add_edge(i, None, f)
        nfa.add_edge(a1, None, s1)
        nfa.add_edge(a1, None, f)
        return i, f

    raise ValueError(f"Nodo desconocido para Thompson: {node.kind}")


def build_nfa(root):
    nfa = NFA()
    start, accept = thompson(root, nfa)
    return nfa, start, accept


# Desplegamos el AFN: en texto y lo dibujamos usando Graphviz

def nfa_text_report(nfa, start, accept):
    lines = [f"Estados: {nfa.num_states}  (q0..q{nfa.num_states - 1})"]
    lines.append(f"Estado inicial:    q{start}")
    lines.append(f"Estado aceptacion: q{accept}")
    lines.append("Transiciones:")
    for s in range(nfa.num_states):
        for sym, t in sorted(nfa.transitions.get(s, []), key=lambda e: (e[0] is None, e[0] or "")):
            simbolo = "ε" if sym is None else sym
            lines.append(f"  q{s} --{simbolo}--> q{t}")
    return lines


def draw_nfa(nfa, start, accept, title, png_path):
    """Genera el PNG del AFN con Graphviz, pasandole el .dot por stdin
    (no se guarda ningun archivo .dot en disco)."""
    lines = ["digraph AFN {", '  rankdir=LR;', '  fontname="Helvetica";',
             f'  label="{title}"; labelloc=t;', '  node [shape=circle, fontname="Helvetica"];',
             '  edge [fontname="Helvetica"];',
             '  __start [shape=none, label=""];']
    lines.append(f'  q{accept} [shape=doublecircle];')
    lines.append(f'  __start -> q{start};')

    for s in range(nfa.num_states):
        for sym, t in nfa.transitions.get(s, []):
            simbolo = "ε" if sym is None else sym
            lines.append(f'  q{s} -> q{t} [label="{simbolo}"];')

    lines.append("}")
    dot_source = "\n".join(lines)

    try:
        subprocess.run(["dot", "-Tpng", "-o", str(png_path)],
                        input=dot_source.encode("utf-8"),
                        check=True, capture_output=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


# 5. Simulacion del AFN sobre una cadena

def epsilon_closure(states, nfa):
    stack = list(states)
    closure = set(states)
    while stack:
        s = stack.pop()
        for sym, t in nfa.transitions.get(s, []):
            if sym is None and t not in closure:
                closure.add(t)
                stack.append(t)
    return closure


def simulate(nfa, start, accept, cadena):
    """Devuelve (acepta: bool, pasos: list[str]) simulando cadena sobre el AFN."""
    pasos = []
    actual = epsilon_closure({start}, nfa)
    pasos.append(f"  ε-clousure(q{start}) = {{{', '.join('q'+str(s) for s in sorted(actual))}}}")

    for ch in cadena:
        movidos = {t for s in actual for sym, t in nfa.transitions.get(s, []) if sym == ch}
        actual = epsilon_closure(movidos, nfa)
        conjunto = "{" + ", ".join("q" + str(s) for s in sorted(actual)) + "}"
        pasos.append(f"  con '{ch}' -> {conjunto}")
        if not actual:
            break

    acepta = accept in actual
    return acepta, pasos


# Se lee el archivo de entrada

def parse_input(path):
    """Devuelve lista de (regex, [cadenas]) preservando el orden del archivo."""
    bloques = []
    actual = None

    with open(path, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.upper().startswith("REGEX:"):
                actual = (line.split(":", 1)[1].strip(), [])
                bloques.append(actual)
            elif line.upper().startswith("CADENA:"):
                if actual is None:
                    raise ValueError("CADENA: encontrada antes de cualquier REGEX:")
                actual[1].append(normalize_cadena(line.split(":", 1)[1]))
            else:
                raise ValueError(f"Linea no reconocida en input: '{line}'")

    return bloques


# main

def process_regex(index, raw_regex, cadenas, out_dir):
    report = []
    label = chr(ord("a") + index)
    report.append("=" * 70)
    report.append(f"{label}) Expresion regular: {raw_regex}")
    report.append("=" * 70)

    norm_expr = normalize_expr(raw_regex)
    explicit = sy.insertar_concatenacion_explicita(norm_expr)
    report.append(f"Infix con concatenacion explicita: {explicit}")

    postfix_str = sy.shunting_yard_regex(norm_expr, insertar_concat=True)
    report.append(f"Postfix (Shunting Yard, Lab 2):     {postfix_str}")

    postfix = postfix_str_to_tokens(postfix_str)
    root = build_tree(postfix)   # (c) arbol sintactico -- no se despliega, solo se usa

    nfa, start, accept = build_nfa(root)   # (d) Thompson, depth-first sobre el arbol

    report.append("")
    report.append(f"AFN (Thompson) -- {nfa.num_states} estados:")
    report.extend("  " + l for l in nfa_text_report(nfa, start, accept))

    png_path = out_dir / f"afn_{label}.png"
    dibujado = draw_nfa(nfa, start, accept, f"{label}) {raw_regex}", png_path)
    report.append("")
    if dibujado:
        report.append(f"Dibujo del AFN guardado en: output/{png_path.name}")
    else:
        report.append("(Graphviz 'dot' no disponible; no se genero el dibujo del AFN)")

    report.append("")
    report.append("Simulacion de cadena(s) sobre el AFN:")
    resultados = []
    for cadena in cadenas:
        mostrar = cadena if cadena != "" else "ε (cadena vacia)"
        report.append(f"  Cadena: {mostrar}")
        acepta, pasos = simulate(nfa, start, accept, cadena)
        report.extend("  " + p for p in pasos)
        respuesta = "si" if acepta else "no"
        report.append(f"  --> ¿Se acepta la cadena? {respuesta}")
        report.append("")
        resultados.append((cadena, respuesta))

    return "\n".join(report), resultados


def main():
    here = Path(__file__).resolve().parent
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else here / "input.txt"
    out_dir = here / "output"
    out_dir.mkdir(exist_ok=True)

    bloques = parse_input(input_path)

    full_report = []
    resumen = ["Resumen (regex, cadena, ¿aceptada?):"]
    for i, (regex, cadenas) in enumerate(bloques):
        texto, resultados = process_regex(i, regex, cadenas, out_dir)
        full_report.append(texto)
        label = chr(ord("a") + i)
        for cadena, respuesta in resultados:
            mostrar = cadena if cadena != "" else "ε"
            resumen.append(f"  {label}) {regex!r:35s} cadena='{mostrar}'  -> {respuesta}")

    text = "\n\n".join(full_report) + "\n\n" + "=" * 70 + "\n" + "\n".join(resumen)
    print(text)

    report_path = out_dir / "reporte.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    main()
