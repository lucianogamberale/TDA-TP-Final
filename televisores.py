import sys
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus

HORAS_TRABAJO = 8


def main():
    assertParametrosEsperados()

    archivoHorariosEntrada = sys.argv[1]
    archivoFranjasHorarias = sys.argv[2]

    horariosEntrada = leerHorariosEntrada(archivoHorariosEntrada)
    franjasHorarias = leerFranjasHorarias(archivoFranjasHorarias)

    # genero y resuelvo el problema con Simplex usando PuLP
    modelo = resolverSimplex(horariosEntrada, franjasHorarias)

    # imprimo resultados
    imprimirResultados(modelo)


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
                partes = linea.split(";")
                partes = [int(valor) for valor in partes]
                franjas.append(partes)
    return franjas


def leerHorariosEntrada(nombreArchivo):
    horarios = []
    with open(nombreArchivo, "r") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if linea:
                horarios.append(int(linea))
    return horarios


# ======================= FORMULACIÓN Y RESOLUCIÓN CON SIMPLEX =======================


def resolverSimplex(horariosEntrada, franjasHorarias):
    # defino el Problema de Minimización
    modelo = LpProblem("Minimizacion_Empleados", LpMinimize)

    # defino Variables de Decisión (cantidad de empleados por horario de entrada)
    variablesDecision = {}
    for i in range(len(horariosEntrada)):
        nombre_variable = f"x_{i+1}"
        variablesDecision[nombre_variable] = LpVariable(
            nombre_variable, lowBound=0, cat="Integer"
        )  # Variables enteras no negativas

    # defino la Función Objetivo: Minimizar la cantidad total de empleados
    modelo += lpSum(variablesDecision.values()), "Funcion_Objetivo"

    # defino Restricciones (cada franja debe ser cubierta)
    for j in range(len(franjasHorarias)):
        to_j, tf_j, bj = franjasHorarias[j]
        empleados_cubren_franja = []
        for i in range(len(horariosEntrada)):
            to_i = horariosEntrada[i]
            if empleadoCubreFranjaHoraria(to_i, to_j, tf_j):
                empleados_cubren_franja.append(variablesDecision[f"x_{i+1}"])

        modelo += lpSum(empleados_cubren_franja) >= bj, f"Restriccion_{j+1}"

    # guardo el problema en un archivo .lp para dejar la información del problema
    modelo.writeLP("Minimizacion_Empleados.lp")

    # resuelvo el problema usando el método Simplex
    modelo.solve()

    return modelo


def empleadoCubreFranjaHoraria(to_i, to_j, tf_j):
    tf_i = to_i + HORAS_TRABAJO  # Hora de salida del empleado

    if tf_i < 24:
        # el empleado no cruza medianoche, trabaja en un solo día
        return to_i <= to_j and tf_i >= tf_j
    else:
        # el empleado cruza medianoche, divide su trabajo en dos partes
        to1_i = to_i
        tf1_i = 24
        to2_i = 0
        tf2_i = tf_i % 24

        return (to1_i <= to_j and tf1_i >= tf_j) or (to2_i <= to_j and tf2_i >= tf_j)


# ======================= IMPRESIÓN DE RESULTADOS =======================


def imprimirResultados(modelo):
    print("\n** Resultado del problema **")

    # verifico el estado de la solución
    estado = LpStatus[modelo.status]
    print(f"Estado de la solución: {estado}")

    if estado == "Optimal":
        print("\n** Solución encontrada **")
        for var in modelo.variables():
            print(f"{var.name} = {var.varValue}")

        print("\n** Función Objetivo **")
        print("Minimizar:")
        print(f"  Z = {' + '.join([f'{coef}*{var.name}' for var, coef in zip(modelo.variables(), [1]*len(modelo.variables()))])}")

        print("\n** Restricciones **")
        for nombre, restriccion in modelo.constraints.items():
            print(f"  {nombre}: {restriccion}")

        print("\n** Valor óptimo de la función objetivo **")
        print(f"  Z* = {modelo.objective.value()}")

    else:
        print("No se encontró una solución factible.")



if __name__ == "__main__":
    main()
