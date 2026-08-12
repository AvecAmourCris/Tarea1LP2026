import re

# --- 1. bloques léxicos base ---
minuscula = r"[a-záéíóúñ]"
mayuscula = r"[A-ZÁÉÍÓÚÑ]"
digito = r"[0-9]"
caracteres_extra = r"[a-záéíóúñA-ZÁÉÍÓÚÑ\-]"

# --- 2. entidades del juego ---
jugador = rf"{mayuscula}{caracteres_extra}+"
equipo = rf"{mayuscula}{caracteres_extra}+"

# --- 3. patrones de extracción ---
patron_de_alineacion = rf"^\[ALINEACION\].*?({equipo})[^A-ZÁÉÍÓÚÑ]*?:\s*(.*)$"
patron_de_gol = rf"^\[({digito}+)'\].*?[Gg]o+l(?:azo)?.*?de\s+({jugador}).*?para\s+({equipo}).*?!"
patron_de_pase = rf"^\[({digito}+)'\]\s+({jugador}).*?(?:pase|toca).*?({jugador})"


def procesar_partido():
    '''
    ***
    parametros : ninguno (las siguientes son variables internas detalladas):
    - marcador : tipo diccionario, almacena el nombre del equipo como llave y la cantidad de goles como valor entero.
    - archivo : tipo objeto de texto, representa el archivo 'relator.txt' en lectura.
    - linea : tipo string, representa la línea específica actual sometida a evaluación en el ciclo iterativo.
    - linea_reconocida : tipo booleano (bandera), indica si la línea generó coincidencia con algún patrón (true) o si corresponde a ruido/error (false).
    - match_alin : tipo objeto match o none, almacena el resultado de la búsqueda del patrón de alineación en la línea actual.
    - match_gol : tipo objeto match o none, almacena el resultado de la búsqueda del patrón de gol en la línea actual.
    - match_pase : tipo objeto match o none, almacena el resultado de la búsqueda del patrón de pase en la línea actual.
    - nombre_equipo : tipo string, almacena el nombre del equipo extraído del primer grupo de captura del patrón de alineación.
    - equipo_anota : tipo string, almacena el nombre del equipo autor del gol, extraído del tercer grupo de captura del patrón de gol.
    - equipos_lista : tipo lista de strings, contiene los nombres de los equipos almacenados en las llaves del diccionario marcador.
    - equipo : tipo string, iterador utilizado para recorrer las llaves del diccionario marcador.
    - equipo1 : tipo string, representa el nombre del primer equipo extraído de la lista de equipos.
    - equipo2 : tipo string, representa el nombre del segundo equipo extraído de la lista de equipos.
    - goles1 : tipo int, representa la cantidad de goles anotados por el primer equipo.
    - goles2 : tipo int, representa la cantidad de goles anotados por el segundo equipo.
    ***
    tipo de retorno o none : none
    ***
    breve descripción de la función y el retorno : 
    inicialización de un diccionario vacío para el marcador y apertura del archivo 'relator.txt' en modo lectura. 
    posteriormente, mediante un ciclo iterativo directo sobre el archivo, se analiza cada línea eliminando los saltos 
    de línea y se evalúa la coincidencia con expresiones regulares predefinidas de forma independiente.
    se utiliza un sistema de bandera (linea_reconocida) para determinar el procesamiento efectivo de la línea.
    en caso de detección de una alineación, se registra al equipo. ante la detección de un gol, se incrementa en un punto al equipo correspondiente.
    tras finalizar la lectura, se cierra el flujo del archivo y se procesa el diccionario mediante una iteración para 
    la impresión por terminal del marcador final del partido.
    '''
    # 1. inicialización de estructuras de estado
    marcador = {}
    
    # 2. apertura de flujo de datos
    archivo = open("relator.txt", "r", encoding="utf-8")
        
    # 3. iteración directa y limpieza
    for linea in archivo:
        linea = linea.strip() 
        linea_reconocida = False
        
        # 4. evaluación léxica: registro de equipos
        match_alin = re.search(patron_de_alineacion, linea)
        if match_alin:
            nombre_equipo = match_alin.group(1)
            marcador[nombre_equipo] = 0
            linea_reconocida = True
            
        # 5. evaluación léxica: anotaciones
        match_gol = re.search(patron_de_gol, linea)
        if match_gol:
            equipo_anota = match_gol.group(3)
            if equipo_anota in marcador:
                marcador[equipo_anota] += 1
            linea_reconocida = True
            
        # 6. evaluación léxica: transiciones de balón
        match_pase = re.search(patron_de_pase, linea)
        if match_pase:
            linea_reconocida = True

        # 7. manejo de ruido y evasión de líneas inválidas
        if linea_reconocida == False:
            pass

    # 8. cierre de flujo de datos
    archivo.close()

    # 9. procesamiento de resultados para salida
    equipos_lista = []
    for equipo in marcador:
        equipos_lista.append(equipo)
    
    # 10. construcción e impresión del reporte
    if len(equipos_lista) >= 2:
        equipo1 = equipos_lista[0]
        equipo2 = equipos_lista[1]
        goles1 = marcador[equipo1]
        goles2 = marcador[equipo2]
        
        print("=== REPORTE DEL PARTIDO ===")
        print("MARCADOR FINAL: " + equipo1 + " " + str(goles1) + " - " + str(goles2) + " " + equipo2)


'''
***
parametros : ninguno
***
tipo de retorno o none : none
***
breve descripción de la función y el retorno :
sección principal del código. punto de entrada del programa que invoca
a la función procesar_partido() para el inicio de la evaluación secuencial.
'''
if __name__ == "__main__":
    procesar_partido()