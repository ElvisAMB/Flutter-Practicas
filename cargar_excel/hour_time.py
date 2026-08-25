import datetime

def getDateDefault():
    # Obtener la fecha y hora actual (incluyendo milisegundos y zona horaria si se configura)
    ahora = datetime.datetime.now()

    # 1. Imprimir la fecha y hora completa por defecto
    print(f"{ahora}")
    # Ejemplo de salida: 2025-10-20 17:45:13.123456

def getDateFormat():
    # Obtener la fecha y hora actual (incluyendo milisegundos y zona horaria si se configura)
    ahora = datetime.datetime.now()
    
    # 2. Imprimir en un formato legible (DD/MM/AAAA HH:MM:SS)
    formato_legible = ahora.strftime("%d/%m/%Y %H:%M:%S")
    print(f"{formato_legible}")
    # Ejemplo de salida: 20/10/2025 17:45:13

def getDate():
    # Obtener la fecha y hora actual (incluyendo milisegundos y zona horaria si se configura)
    ahora = datetime.datetime.now()

    # 3. Imprimir solo la fecha
    solo_fecha = ahora.strftime("%Y-%m-%d")
    print(f"3. Solo Fecha (YYYY-MM-DD): {solo_fecha}")
    # Ejemplo de salida: 2025-10-20

def getTime():
    # Obtener la fecha y hora actual (incluyendo milisegundos y zona horaria si se configura)
    ahora = datetime.datetime.now()

    # 4. Imprimir solo la hora
    solo_hora = ahora.strftime("%H:%M:%S")
    print(f"{solo_hora}")
    # Ejemplo de salida: 17:45:13