import sys

HORAS_TRABAJO = 8

def main():
    assertParametrosEsperados()

    archivoHorariosEntrada = sys.argv[1]
    archivoFranjasHorarias = sys.argv[2]

    horariosEntrada = leerHorariosEntrada(archivoHorariosEntrada)
    franjasHorarias = leerFranjasHorarias(archivoFranjasHorarias)

    variablesDecision = generarVariablesDecision(horariosEntrada)
    restricciones = generarRestricciones(horariosEntrada, franjasHorarias)

    imprimirProblemaProgramacionLineal(variablesDecision, restricciones)

# ======================= LECTURA ARCHIVOS =======================

def assertParametrosEsperados():
    if len(sys.argv) < 3:
        print("Uso: python script.py <horarios_entrada.csv> <franjas_horarias.csv>")
        sys.exit(1)

def leerFranjasHorarias(nombreArchivo):
    franjas = []
    with open(nombreArchivo, "r") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if linea:
                partes = list(map(int, linea.split(";")))  # Divide y convierte a enteros
                franjas.append(partes)
    return franjas

def leerHorariosEntrada(nombreArchivo):
    horarios = []
    with open(nombreArchivo, "r") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if linea:
                horarios.append(int(linea))  # Convierte a entero
    return horarios

# ======================= VARIABLES DE DECISIÓN =======================

def generarVariablesDecision(horariosEntrada):
    variablesDecision = {}
    
    for i, to_i in enumerate(horariosEntrada):
        variablesDecision[f"x_{i+1}"] = to_i

    return variablesDecision

# ======================= RESTRICCIONES =======================

def generarRestricciones(horariosEntrada, franjasHorarias):
    restricciones = {}

    for j, (to_j, tf_j, bj) in enumerate(franjasHorarias):
        restriccion = []
        for i, to_i in enumerate(horariosEntrada):
            if empleadoCubreFranjaHoraria(to_i, to_j, tf_j):
                restriccion.append(f"x_{i+1}")
        
        restricciones[f"r_{j+1}"] = {
            "b_j": bj,
            "x_i": restriccion
        }
    
    return restricciones

def empleadoCubreFranjaHoraria(to_i, to_j, tf_j):
    tf_i = to_i + HORAS_TRABAJO  # Hora de salida del empleado

    if tf_i < 24:
        # El empleado no cruza medianoche, trabaja en un solo día
        return to_i <= to_j and tf_i >= tf_j
    else:
        # El empleado cruza medianoche, divide su trabajo en dos partes
        to1_i = to_i
        tf1_i = 24

        to2_i = 0
        tf2_i = tf_i % 24

        return (to1_i <= to_j and tf1_i >= tf_j) or (to2_i <= to_j and tf2_i >= tf_j)

# ======================= IMPRESIÓN DEL PROBLEMA =======================

def imprimirProblemaProgramacionLineal(variablesDecision, restricciones):
    print("\n** Variables de decisión **")
    for x_i, to_i in variablesDecision.items():
        print(f"{x_i}: cantidad de empleados que entran a las {to_i:02}:00")

    print("\n** Restricciones **")
    for r_j, restriccion in restricciones.items():
        bj = restriccion["b_j"]
        x_i = restriccion["x_i"]
        restriccion_str = " + ".join(x_i) if x_i else "0"
        print(f"{restriccion_str} >= {bj}  # {r_j}")

    print("\n** Función Objetivo **")
    print("Minimizar Z =", " + ".join(variablesDecision.keys()))

if __name__ == "__main__":
    main()
