# Tarea1LP2026

================================================================================
TAREA 1: INTÉRPRETE DE RELATO - ANALIZADOR LÉXICO
================================================================================

Nombre: Cristóbal Alonso Uteau González
Rol: 202473629-9

---

1. DESCRIPCIÓN GENERAL
Este programa es un analizador léxico desarrollado en Python que procesa la 
transcripción de un relato radial de fútbol. Utilizando exclusivamente el 
módulo de expresiones regulares (re), el script extrae entidades válidas 
(equipos y jugadores) y procesa eventos secuenciales para calcular 
estadísticas, evadiendo el "ruido" o texto basura de la transmisión.

2. INSTRUCCIONES DE EJECUCIÓN Y REQUISITOS DE ENTRADA
Para garantizar la correcta ejecución del programa, es imperativo cumplir 
con las siguientes condiciones:

    a) Ubicación del archivo de entrada: El archivo de texto que contiene 
       la transcripción del partido debe llamarse obligatoriamente 
       "relator.txt". Este archivo DEBE estar ubicado en el mismo 
       directorio de ejecución (la misma carpeta) que el archivo fuente 
       "analizador.py". El programa utiliza rutas relativas, por lo que 
       fallará si los archivos se encuentran separados.

    b) Ejecución: Abrir una terminal o línea de comandos, navegar hacia 
       el directorio donde se encuentran ambos archivos y ejecutar el 
       siguiente comando:

       python analizador.py

3. SALIDAS DEL PROGRAMA
Una vez finalizada la ejecución, el programa generará automáticamente:
    - Un reporte estadístico impreso directamente por la terminal.

================================================================================