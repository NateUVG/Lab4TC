

PRECEDENCIA = {
    '|': 1,
    '.': 2,
    '*': 3,
    '+': 3,
    '?': 3,
}

UNARIOS_POSTFIJOS = {'*', '+', '?'}
OPERADORES_BINARIOS = {'|', '.'}


def es_simbolo(c):
    """Un simbolo es cualquier caracter del alfabeto (no operador, no parentesis)."""
    return c not in PRECEDENCIA and c not in ('(', ')')


def insertar_concatenacion_explicita(regex):
    """Inserta el operador '.' de concatenacion explicita donde esta implicita."""
    resultado = []
    n = len(regex)

    for i in range(n):
        c1 = regex[i]
        resultado.append(c1)

        if i + 1 < n:
            c2 = regex[i + 1]
            c1_puede_terminar = es_simbolo(c1) or c1 in (')', '*', '+', '?')
            c2_puede_iniciar = es_simbolo(c2) or c2 == '('
            if c1_puede_terminar and c2_puede_iniciar:
                resultado.append('.')

    return ''.join(resultado)


def shunting_yard_regex(regex, insertar_concat=True):
    """Convierte una expresion regular infija a notacion postfija."""
    if insertar_concat:
        regex = insertar_concatenacion_explicita(regex)

    salida = []
    pila_ops = []

    for token in regex:

        if es_simbolo(token):
            salida.append(token)

        elif token in UNARIOS_POSTFIJOS or token in OPERADORES_BINARIOS:
            while (pila_ops and pila_ops[-1] != '(' and
                   PRECEDENCIA.get(pila_ops[-1], 0) >= PRECEDENCIA[token]):
                salida.append(pila_ops.pop())
            pila_ops.append(token)

        elif token == '(':
            pila_ops.append(token)

        elif token == ')':
            while pila_ops and pila_ops[-1] != '(':
                salida.append(pila_ops.pop())
            if not pila_ops:
                raise ValueError("Parentesis desbalanceados: falta '('")
            pila_ops.pop()

        else:
            raise ValueError(f"Token no reconocido: '{token}'")

    while pila_ops:
        op = pila_ops.pop()
        if op == '(':
            raise ValueError("Parentesis desbalanceados: sobra '('")
        salida.append(op)

    return ''.join(salida)
