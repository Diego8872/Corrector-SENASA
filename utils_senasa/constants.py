"""
Reglas esperadas por aduana para el Corrector SENASA.

Cada entrada define, para una aduana dada, los valores que la Declaración
Jurada de SENASA (DJ) debe tener en los campos "Punto de ingreso",
"Medio de transporte" y "Lugar de destino de la mercadería".

- Si el valor es un string fijo -> se compara la DJ contra esa constante.
- Si "lugar_destino" es None -> se compara la DJ contra el campo "Depósito"
  informado en la DI (no hay valor fijo, depende de cada despacho).

Para agregar una aduana nueva, sumar una entrada al diccionario ADUANA_RULES.
La clave debe ser un texto que aparezca dentro del campo "Aduana" de la DI
(comparación por substring, insensible a mayúsculas/acentos).
"""

ADUANA_RULES = {
    "EZEIZA": {
        "aliases": ["EZEIZA"],
        "puerto_ingreso": "Aeropuerto Internacional De Ezeiza - Inspeccion",
        "medio_transporte": "Aereo",
        "lugar_destino": "Terminal de Cargas Areas (TCA)",
    },
    "BUENOS AIRES": {
        # La DI suele traer la aduana como "BS.AS.(CAPITAL)" en vez de
        # "BUENOS AIRES" tal cual, por eso hace falta la lista de alias.
        "aliases": ["BUENOS AIRES", "BS AS", "BSAS", "BS.AS"],
        "puerto_ingreso": "Puerto De Buenos Aires",
        "medio_transporte": "Maritimo",
        "lugar_destino": None,  # se compara contra el Depósito de la DI
    },
}


def get_rules_for_aduana(aduana_texto: str):
    """
    Busca en ADUANA_RULES la primera clave cuyos alias aparezcan como
    substring (normalizado) dentro de aduana_texto. Devuelve (clave, reglas)
    o (None, None) si no hay match.
    """
    from .validator import normalize

    if not aduana_texto:
        return None, None

    aduana_norm = normalize(aduana_texto)
    for key, rules in ADUANA_RULES.items():
        for alias in rules["aliases"]:
            if normalize(alias) in aduana_norm:
                return key, rules
    return None, None
