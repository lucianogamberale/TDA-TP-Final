import sys
from pulp import LpProblem, LpMinimize, LpVariable, lpSum

HORAS_TRABAJO = 8

def main():
    assertParametrosEsperados()

    archivoHorariosEntrada = sys.argv[1]
    archivoFranjasHorarias = sys.argv[2]

    horariosEntrada = leerHorariosEntrada(archivoHorariosEntrada)
    franjasHorarias = leerFranjasHorarias(archivoFranjasHorarias)

    # Generar y resolver el problema con Simplex usando PuLP
    modelo = resolverSimplex(horariosEntrada, franjasHorarias)

    # Imprimir resultados
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

# ======================= FORMULACIÓN Y RESOLUCIÓN CON SIMPLEX =======================

def resolverSimplex(horariosEntrada, franjasHorarias):
    # Definir el problema de minimización
    modelo = LpProblem("Minimizacion_Empleados", LpMinimize)

    # Definir variables de decisión (cantidad de empleados por horario de entrada)
    variablesDecision = {
        f"x_{i+1}": LpVariable(f"x_{i+1}", lowBound=0, cat="Integer")  # Variables enteras no negativas
        for i in range(len(horariosEntrada))
    }

    # Definir la función objetivo: Minimizar la cantidad total de empleados
    modelo += lpSum(variablesDecision.values()), "Funcion_Objetivo"

    # Definir restricciones (cada franja debe ser cubierta)
    for j, (to_j, tf_j, bj) in enumerate(franjasHorarias):
        modelo += (
            lpSum(variablesDecision[f"x_{i+1}"] for i, to_i in enumerate(horariosEntrada) if empleadoCubreFranjaHoraria(to_i, to_j, tf_j))
            >= bj, 
            f"Restriccion_{j+1}"
        )

    # Resolver el problema usando el método Simplex
    modelo.solve()

    return modelo

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

# ======================= IMPRESIÓN DE RESULTADOS =======================

def imprimirResultados(modelo):
    print("\n** Resultado del problema **")

    # Verificar el estado de la solución
    estado = modelo.status
    if estado == 1:
        print("Solución encontrada:")
        for var in modelo.variables():
            print(f"{var.name}: {var.varValue}")

        print("\n** Función Objetivo **")
        print(f"Valor mínimo de empleados necesarios: {modelo.objective.value()}")
    else:
        print("No se encontró solución factible.")

if __name__ == "__main__":
    main()
