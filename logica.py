def diagnosticar(sintomas):
    """
    Evalúa los síntomas de diabetes usando un sistema de puntuación ponderada.
    'sintomas' es un diccionario que viene del frontend.
    """
    # Definimos pesos para cada síntoma (algunos son más críticos que otros)
    pesos = {
        'sed': 2,
        'orina': 2,
        'cansancio': 1,
        'vision_borrosa': 2,
        'perdida_peso': 3,  # La pérdida de peso inexplicable es un signo fuerte
        'antecedentes': 2
    }

    puntos = 0

    for clave, valor in sintomas.items():
        # Validamos que el síntoma esté en nuestro diccionario de pesos
        # y que el usuario haya respondido "si"
        if clave in pesos and valor == "si":
            puntos += pesos[clave]

    # Determinamos el nivel de riesgo basado en el puntaje total
    if puntos >= 7:
        return {
            "nivel": "Riesgo Alto",
            "clase_css": "danger",
            "mensaje": "Se recomienda consultar a un médico a la brevedad para realizar exámenes de glucosa.",
            "puntos": puntos
        }
    elif puntos >= 3:
        return {
            "nivel": "Riesgo Moderado",
            "clase_css": "warning",
            "mensaje": "Existen señales de alerta. Sería prudente realizar un chequeo preventivo.",
            "puntos": puntos
        }
    else:
        return {
            "nivel": "Riesgo Bajo",
            "clase_css": "success",
            "mensaje": "No se detectan indicadores críticos, pero mantenga un estilo de vida saludable.",
            "puntos": puntos
        }