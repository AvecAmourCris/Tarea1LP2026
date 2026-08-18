import re

# 1. Bloque léxico EBNF
digito = r"[0-9]"
letra_min = r"[a-záéíóúñ]"
letra_may = r"[A-ZÁÉÍÓÚÑ]"
letra = rf"(?:{letra_min}|{letra_may})"
palabra = rf"(?:{letra}(?:{letra}|{digito})*)"
puntuacion = r"[.,!¡?¿'\"\-]"

# Comodín que representa <frase_variable> según EBNF:
# (palabra | " ")*  => cualquier cosa excepto corchetes y saltos de línea
frase_variable = r"[^\[\]\n]*?"

# 2. Entidades
jugador = rf"{letra_may}{letra}+"
equipo = rf"{letra_may}{letra}+"
minuto = rf"\[({digito}+)'\]"
tiempo_extra = rf"\[MINUTOS EXTRA\][ ]\+({digito}+)"
espacios = r"[ ]*"
accion_pase = rf"{espacios}(?:pase|toca){espacios}"
accion_tiro = rf"{espacios}(?:dispara|remata|patea){espacios}"
accion_robo = rf"{espacios}(?:roba|recupera|domina){espacios}"
accion_falta = rf"{espacios}(?:entrada|falta|derriba){espacios}"
grito_gol = r"(?:[Gg]o+l(?:azo)?)"

# 4. Patrones según EBNF
patron_alineacion = rf"^\[ALINEACION\][ ]El[ ]equipo[ ]({equipo})[ ]sale[ ]a[ ]la[ ]cancha[ ]con:[ ]({frase_variable})$"
patron_inicio = rf"^\[0'\]{frase_variable}({jugador})$"

patron_pase = rf"^{minuto}{espacios}({jugador}){accion_pase}({jugador})$"
patron_tiro = rf"^{minuto}{espacios}({jugador}){accion_tiro}{frase_variable}$"
patron_robo = rf"^{minuto}{espacios}({jugador}){accion_robo}{frase_variable}$"
patron_falta = rf"^{minuto}{espacios}({jugador}){accion_falta}({jugador})$"

# GOL: respetamos la estructura EBNF: <minuto> <grito_gol> "de " <jugador> " para " <equipo> "!"
patron_gol = rf"^{minuto}{frase_variable}{grito_gol}{frase_variable}de[ ]({jugador})[ ]para[ ]({equipo})!$"

# TARJETA y CAMBIO: exactamente como en EBNF
patron_tarjeta = rf"^\[(TARJETA AMARILLA|TARJETA ROJA)\]{frase_variable}({jugador}){frase_variable}$"
patron_cambio = rf"^\[CAMBIO\]{frase_variable}({jugador}){frase_variable}({jugador}){frase_variable}$"
patron_tiempo_extra = rf"^{tiempo_extra}$"


def procesar_partido():
    """
    ***
    Parametros: ninguno
    ***
    Tipo de retorno: None
    ***
    Breve descripción:
    Analiza el archivo 'relator.txt', extrae eventos de juego, calcula
    estadísticas de posesión, detecta inconsistencias (jugadores fantasma,
    saltos temporales, errores de equipo/posesión) y genera un reporte por
    terminal y un archivo 'inconsistencias.txt'.
    """
    marcador = {}
    equipo_de_jugador = {}
    estadisticas = {}
    lista_inconsistencias = []
    
    ultimo_minuto_valido = 0
    equipo_con_posesion = None
    jugador_con_balon = None
    
    regex_alin = re.compile(patron_alineacion)
    regex_inicio = re.compile(patron_inicio)
    regex_pase = re.compile(patron_pase)
    regex_tiro = re.compile(patron_tiro)
    regex_robo = re.compile(patron_robo)
    regex_falta = re.compile(patron_falta)
    regex_gol = re.compile(patron_gol)
    regex_tarjeta = re.compile(patron_tarjeta)
    regex_cambio = re.compile(patron_cambio)
    regex_extra = re.compile(patron_tiempo_extra)

    archivo = open("relator.txt", "r", encoding="utf-8-sig")
    for linea in archivo:
        linea = linea.strip()
        if not linea:
            continue

        # A. Alineación
        coincide_alin = regex_alin.match(linea)
        if coincide_alin:
            nombre_equipo = coincide_alin.group(1)
            if nombre_equipo not in marcador:
                marcador[nombre_equipo] = 0
                estadisticas[nombre_equipo] = {
                    "pases": 0, "tiros": 0, "robos": 0,
                    "faltas": 0, "amarillas": 0, "rojas": 0,
                    "minutos_posesion": 0
                }
            cadena_jugadores = coincide_alin.group(2)
            lista_nombres = re.split(rf",[ ]*|[ ]+y[ ]+", cadena_jugadores)
            for nombre in lista_nombres:
                nombre_limpio = nombre.strip()
                if nombre_limpio:
                    equipo_de_jugador[nombre_limpio] = nombre_equipo
            continue

        # B. Inicio
        coincide_inicio = regex_inicio.match(linea)
        if coincide_inicio:
            jugador_saque = coincide_inicio.group(1)
            if jugador_saque in equipo_de_jugador:
                jugador_con_balon = jugador_saque
                equipo_con_posesion = equipo_de_jugador[jugador_saque]
            else:
                texto_error = f"ERROR: Jugador Desconocido.\nLínea: \"{linea}\"\nMotivo: '{jugador_saque}' no pertenece a ninguna alineación.\n\n"
                lista_inconsistencias.append((0, texto_error))
            continue

        # C. Cambio (según EBNF)
        coincide_cambio = regex_cambio.match(linea)
        if coincide_cambio:
            sale = coincide_cambio.group(1)
            entra = coincide_cambio.group(2)
            if sale in equipo_de_jugador:
                eq = equipo_de_jugador[sale]
                del equipo_de_jugador[sale]
                equipo_de_jugador[entra] = eq
            else:
                texto_error = f"ERROR: Jugador Desconocido.\nLínea: \"{linea}\"\nMotivo: El jugador saliente '{sale}' no estaba en cancha.\n\n"
                lista_inconsistencias.append((ultimo_minuto_valido, texto_error))
            continue

        # D. Tarjeta (según EBNF)
        coincide_tarjeta = regex_tarjeta.match(linea)
        if coincide_tarjeta:
            tipo_tarjeta = coincide_tarjeta.group(1)
            jug_sancionado = coincide_tarjeta.group(2)
            if jug_sancionado in equipo_de_jugador:
                eq = equipo_de_jugador[jug_sancionado]
                if tipo_tarjeta == "TARJETA AMARILLA":
                    estadisticas[eq]["amarillas"] += 1
                else:
                    estadisticas[eq]["rojas"] += 1
                    del equipo_de_jugador[jug_sancionado]
            else:
                texto_error = f"ERROR: Jugador Desconocido.\nLínea: \"{linea}\"\nMotivo: '{jug_sancionado}' no está en la cancha.\n\n"
                lista_inconsistencias.append((ultimo_minuto_valido, texto_error))
            continue

        # E. Pase
        coincide_pase = regex_pase.match(linea)
        if coincide_pase:
            min_act = int(coincide_pase.group(1))
            origen = coincide_pase.group(2)
            destino = coincide_pase.group(3)
            
            valido = True
            if min_act < ultimo_minuto_valido:
                texto_error = f"ERROR: Salto Temporal.\nLínea: \"{linea}\"\nMotivo: Minuto {min_act}' menor al último registrado ({ultimo_minuto_valido}').\n\n"
                lista_inconsistencias.append((min_act, texto_error))
                valido = False
            elif origen not in equipo_de_jugador:
                texto_error = f"ERROR: Jugador Desconocido.\nLínea: \"{linea}\"\nMotivo: '{origen}' no está registrado en cancha.\n\n"
                lista_inconsistencias.append((min_act, texto_error))
                valido = False
            elif destino not in equipo_de_jugador:
                texto_error = f"ERROR: Jugador Desconocido.\nLínea: \"{linea}\"\nMotivo: '{destino}' no está registrado en cancha.\n\n"
                lista_inconsistencias.append((min_act, texto_error))
                valido = False
            elif equipo_de_jugador[origen] != equipo_de_jugador[destino]:
                texto_error = f"ERROR: Inconsistencia de Pase.\nLínea: \"{linea}\"\nMotivo: No se puede realizar un pase a un jugador rival.\n\n"
                lista_inconsistencias.append((min_act, texto_error))
                valido = False
            elif equipo_con_posesion != equipo_de_jugador[origen]:
                texto_error = f"ERROR: Inconsistencia de Posesión.\nLínea: \"{linea}\"\nMotivo: {equipo_de_jugador[origen]} no tiene la posesión para pasar el balón.\n\n"
                lista_inconsistencias.append((min_act, texto_error))
                valido = False
            
            if valido:
                delta = min_act - ultimo_minuto_valido
                if equipo_con_posesion:
                    estadisticas[equipo_con_posesion]["minutos_posesion"] += delta
                ultimo_minuto_valido = min_act
                equipo_con_posesion = equipo_de_jugador[destino]
                jugador_con_balon = destino
                estadisticas[equipo_con_posesion]["pases"] += 1
            continue

        # F. Tiro
        coincide_tiro = regex_tiro.match(linea)
        if coincide_tiro:
            min_act = int(coincide_tiro.group(1))
            jug_tiro = coincide_tiro.group(2)
            
            valido = True
            if min_act < ultimo_minuto_valido:
                texto_error = f"ERROR: Salto Temporal.\nLínea: \"{linea}\"\nMotivo: Minuto {min_act}' menor al último registrado.\n\n"
                lista_inconsistencias.append((min_act, texto_error))
                valido = False
            elif jug_tiro not in equipo_de_jugador:
                texto_error = f"ERROR: Jugador Desconocido.\nLínea: \"{linea}\"\nMotivo: '{jug_tiro}' no está en cancha.\n\n"
                lista_inconsistencias.append((min_act, texto_error))
                valido = False
            elif equipo_con_posesion != equipo_de_jugador[jug_tiro]:
                texto_error = f"ERROR: Inconsistencia de Posesión.\nLínea: \"{linea}\"\nMotivo: {equipo_de_jugador[jug_tiro]} no puede disparar sin posesión previa.\n\n"
                lista_inconsistencias.append((min_act, texto_error))
                valido = False
            
            if valido:
                delta = min_act - ultimo_minuto_valido
                if equipo_con_posesion:
                    estadisticas[equipo_con_posesion]["minutos_posesion"] += delta
                ultimo_minuto_valido = min_act
                estadisticas[equipo_de_jugador[jug_tiro]]["tiros"] += 1
            continue

        # G. Robo
        coincide_robo = regex_robo.match(linea)
        if coincide_robo:
            min_act = int(coincide_robo.group(1))
            jug_robo = coincide_robo.group(2)
            
            valido = True
            if min_act < ultimo_minuto_valido:
                texto_error = f"ERROR: Salto Temporal.\nLínea: \"{linea}\"\nMotivo: Minuto {min_act}' menor al último registrado.\n\n"
                lista_inconsistencias.append((min_act, texto_error))
                valido = False
            elif jug_robo not in equipo_de_jugador:
                texto_error = f"ERROR: Jugador Desconocido.\nLínea: \"{linea}\"\nMotivo: '{jug_robo}' no está en cancha.\n\n"
                lista_inconsistencias.append((min_act, texto_error))
                valido = False
            
            if valido:
                delta = min_act - ultimo_minuto_valido
                if equipo_con_posesion:
                    estadisticas[equipo_con_posesion]["minutos_posesion"] += delta
                ultimo_minuto_valido = min_act
                equipo_con_posesion = equipo_de_jugador[jug_robo]
                jugador_con_balon = jug_robo
                estadisticas[equipo_con_posesion]["robos"] += 1
            continue

        # H. Falta
        coincide_falta = regex_falta.match(linea)
        if coincide_falta:
            min_act = int(coincide_falta.group(1))
            infractor = coincide_falta.group(2)
            recibe_falta = coincide_falta.group(3)
            
            valido = True
            if min_act < ultimo_minuto_valido:
                texto_error = f"ERROR: Salto Temporal.\nLínea: \"{linea}\"\nMotivo: Minuto {min_act}' menor al último registrado.\n\n"
                lista_inconsistencias.append((min_act, texto_error))
                valido = False
            elif infractor not in equipo_de_jugador:
                texto_error = f"ERROR: Jugador Desconocido.\nLínea: \"{linea}\"\nMotivo: '{infractor}' no está registrado en cancha.\n\n"
                lista_inconsistencias.append((min_act, texto_error))
                valido = False
            elif recibe_falta not in equipo_de_jugador:
                texto_error = f"ERROR: Jugador Desconocido.\nLínea: \"{linea}\"\nMotivo: '{recibe_falta}' no está registrado en cancha.\n\n"
                lista_inconsistencias.append((min_act, texto_error))
                valido = False
            
            if valido:
                delta = min_act - ultimo_minuto_valido
                if equipo_con_posesion:
                    estadisticas[equipo_con_posesion]["minutos_posesion"] += delta
                ultimo_minuto_valido = min_act
                estadisticas[equipo_de_jugador[infractor]]["faltas"] += 1
                equipo_con_posesion = equipo_de_jugador[recibe_falta]
                jugador_con_balon = recibe_falta
            continue

        # I. Gol (según EBNF)
        coincide_gol = regex_gol.match(linea)
        if coincide_gol:
            min_act = int(coincide_gol.group(1))
            anotador = coincide_gol.group(2)
            eq_anota = coincide_gol.group(3)
            
            valido = True
            if min_act < ultimo_minuto_valido:
                texto_error = f"ERROR: Salto Temporal.\nLínea: \"{linea}\"\nMotivo: Minuto {min_act}' menor al último registrado.\n\n"
                lista_inconsistencias.append((min_act, texto_error))
                valido = False
            elif anotador not in equipo_de_jugador:
                texto_error = f"ERROR: Jugador Desconocido.\nLínea: \"{linea}\"\nMotivo: '{anotador}' no pertenece a ninguna alineación.\n\n"
                lista_inconsistencias.append((min_act, texto_error))
                valido = False
            elif equipo_de_jugador[anotador] != eq_anota:
                texto_error = f"ERROR: Inconsistencia de Equipo.\nLínea: \"{linea}\"\nMotivo: '{anotador}' no pertenece a {eq_anota}.\n\n"
                lista_inconsistencias.append((min_act, texto_error))
                valido = False
            elif equipo_con_posesion != eq_anota:
                texto_error = f"ERROR: Inconsistencia de Posesión.\nLínea: \"{linea}\"\nMotivo: {eq_anota} no poseía el balón antes de anotar.\n\n"
                lista_inconsistencias.append((min_act, texto_error))
                valido = False
            
            if valido:
                delta = min_act - ultimo_minuto_valido
                if equipo_con_posesion:
                    estadisticas[equipo_con_posesion]["minutos_posesion"] += delta
                ultimo_minuto_valido = min_act
                marcador[eq_anota] += 1
                estadisticas[eq_anota]["tiros"] += 1
            continue

        # J. Tiempo extra
        coincide_extra = regex_extra.match(linea)
        if coincide_extra:
            continue

    archivo.close()

    # Escribir inconsistencias
    f_incons = open("inconsistencias.txt", "w", encoding="utf-8")
    lista_inconsistencias.sort(key=lambda x: x[0])
    for _, texto in lista_inconsistencias:
        f_incons.write(texto)
    f_incons.close()
    
    # Reporte final
    equipos_lista = list(marcador.keys())
    if len(equipos_lista) >= 2:
        eq1, eq2 = equipos_lista[0], equipos_lista[1]
        pos_total = estadisticas[eq1]["minutos_posesion"] + estadisticas[eq2]["minutos_posesion"]
        if pos_total > 0:
            porc_eq1 = round((estadisticas[eq1]["minutos_posesion"] / pos_total) * 100, 1)
            porc_eq2 = round((estadisticas[eq2]["minutos_posesion"] / pos_total) * 100, 1)
        else:
            porc_eq1 = porc_eq2 = 50.0
        
        print("=== REPORTE DEL PARTIDO ===")
        print(f"MARCADOR FINAL: {eq1} {marcador[eq1]} - {marcador[eq2]} {eq2}")
        print(f"POSESIÓN: {eq1} {porc_eq1}% - {eq2} {porc_eq2}%")

if __name__ == "__main__":
    procesar_partido()