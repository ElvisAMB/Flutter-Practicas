import pandas as pd
import os
from datetime import datetime
import re
from pathlib import Path

def crear_carpetas_desde_excel(archivo_excel, columna, directorio_base="./carpetas"):
    """
    Crea carpetas desde un archivo Excel
    
    Args:
        archivo_excel: Ruta al archivo Excel
        columna: Nombre de la columna con los nombres de carpetas
        directorio_base: Directorio donde crear las carpetas
    """
    
    # Log de errores
    errores = []
    exitosos = []
    
    try:
        # Leer Excel
        df = pd.read_excel(archivo_excel)
        
        # Verificar que existe la columna
        if columna not in df.columns:
            print(f"Error: La columna '{columna}' no existe")
            print(f"Columnas disponibles: {list(df.columns)}")
            return
        
        # Crear directorio base
        os.makedirs(directorio_base, exist_ok=True)
        
        # Crear carpetas
        for index, nombre in enumerate(df[columna], start=1):
            nombre_limpio = str(nombre).strip()
            
            # Saltar valores vacíos
            if pd.isna(nombre) or nombre_limpio == "":
                continue
            
            ruta = os.path.join(directorio_base, nombre_limpio)
            
            try:
                os.makedirs(ruta, exist_ok=True)
                exitosos.append(nombre_limpio)
                print(f"{index}. ✓ {nombre_limpio}")
            except Exception as e:
                errores.append(f"Fila {index}: {nombre_limpio} - {str(e)}")
                print(f"{index}. ✗ {nombre_limpio} - Error: {e}")
        
        # Resumen
        print(f"\n{'='*50}")
        print(f"Carpetas creadas: {len(exitosos)}")
        print(f"Errores: {len(errores)}")
        
        # Guardar log de errores si hay
        if errores:
            with open("errores_carpetas.txt", "w", encoding="utf-8") as f:
                f.write(f"Errores - {datetime.now()}\n")
                f.write("\n".join(errores))
            print("Log de errores guardado en: errores_carpetas.txt")
            
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{archivo_excel}'")
    except Exception as e:
        print(f"Error general: {e}")


def limpiar_nombre_windows(nombre, max_length=100):
    """
    Limpia un nombre de carpeta para que sea válido en Windows
    
    Args:
        nombre: Nombre original de la carpeta
        max_length: Longitud máxima del nombre (default: 100)
    
    Returns:
        Nombre limpio y válido para Windows
    """
    # Convertir a string y eliminar espacios al inicio/final
    nombre = str(nombre).strip()
    
    # Caracteres no permitidos en Windows: < > : " / \ | ? *
    caracteres_invalidos = r'[<>:"/\\|?*]'
    nombre = re.sub(caracteres_invalidos, '_', nombre)
    
    # Eliminar caracteres de control (ASCII 0-31)
    nombre = ''.join(char for char in nombre if ord(char) >= 32)
    
    # Nombres reservados en Windows
    nombres_reservados = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    
    if nombre.upper() in nombres_reservados:
        nombre = f"_{nombre}"
    
    # Eliminar puntos y espacios al final (no permitidos en Windows)
    nombre = nombre.rstrip('. ')
    
    # Si el nombre quedó vacío, asignar uno por defecto
    if not nombre:
        nombre = "carpeta_sin_nombre"
    
    # Limitar longitud (Windows tiene límite de 260 caracteres para ruta completa)
    if len(nombre) > max_length:
        nombre = nombre[:max_length].rstrip('. ')
    
    return nombre


def crear_carpetas_desde_txt(archivo_origen_txt, directorio_destino="./carpetas_creadas", max_nombre=100, separador=None, columna=0):
    """
    Crea carpetas desde un archivo TXT con validaciones completas para Windows
    
    Args:
        archivo_txt: Ruta al archivo TXT con los nombres
        directorio_destino: Directorio donde crear las carpetas
        max_nombre: Longitud máxima del nombre de carpeta (default: 100)
        separador: Separador si el archivo tiene columnas (None, ',', ';', '\t', etc.)
        columna: Índice de columna a usar si hay separador (default: 0)
    
    Returns:
        dict: Estadísticas del proceso
    """
    
    estadisticas = {
        'exitosas': [],
        'errores': [],
        'duplicadas': [],
        'vacias': 0
    }
    
    try:
        # Verificar que existe el archivo
        if not os.path.exists(archivo_origen_txt):
            print(f"❌ Error: El archivo '{archivo_origen_txt}' no existe")
            return estadisticas
        
        # Crear directorio destino si no existe
        Path(directorio_destino).mkdir(parents=True, exist_ok=True)
        print(f"📁 Directorio de destino: {os.path.abspath(directorio_destino)}")
        print(f"{'='*70}\n")
        
        # Leer archivo TXT
        with open(archivo_origen_txt, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
        
        print(f"📄 Leyendo archivo: {archivo_origen_txt}")
        print(f"📊 Total de líneas: {len(lineas)}\n")
        
        carpetas_procesadas = set()  # Para detectar duplicados
        
        for num_linea, linea in enumerate(lineas, start=1):
            linea = linea.strip()
            
            # Saltar líneas vacías
            if not linea:
                estadisticas['vacias'] += 1
                continue
            
            # Si hay separador, extraer la columna especificada
            if separador:
                partes = linea.split(separador)
                if columna < len(partes):
                    nombre_original = partes[columna].strip()
                else:
                    estadisticas['errores'].append({
                        'linea': num_linea,
                        'nombre': linea,
                        'error': 'Columna no encontrada'
                    })
                    continue
            else:
                nombre_original = linea
            
            # Saltar si está vacío después de procesar
            if not nombre_original:
                estadisticas['vacias'] += 1
                continue
            
            # Limpiar nombre
            nombre_limpio = limpiar_nombre_windows(nombre_original, max_nombre)
            
            # Verificar longitud de ruta completa (límite Windows: 260 caracteres)
            ruta_completa = os.path.join(directorio_destino, nombre_limpio)
            if len(ruta_completa) > 250:  # Dejar margen de seguridad
                print(f"⚠️  Línea {num_linea}: Ruta demasiado larga, acortando nombre...")
                # Recalcular con límite más restrictivo
                max_permitido = 250 - len(directorio_destino) - 1
                nombre_limpio = limpiar_nombre_windows(nombre_original, max_permitido)
                ruta_completa = os.path.join(directorio_destino, nombre_limpio)
            
            # Detectar duplicados
            if nombre_limpio.lower() in carpetas_procesadas:
                # Agregar sufijo numérico para duplicados
                contador = 1
                nombre_base = nombre_limpio
                while nombre_limpio.lower() in carpetas_procesadas:
                    nombre_limpio = f"{nombre_base}_{contador}"
                    contador += 1
                estadisticas['duplicadas'].append(nombre_original)
                print(f"⚠️  Línea {num_linea}: Duplicado detectado, renombrado a '{nombre_limpio}'")
            
            # Crear carpeta
            try:
                os.makedirs(ruta_completa, exist_ok=True)
                carpetas_procesadas.add(nombre_limpio.lower())
                estadisticas['exitosas'].append({
                    'linea': num_linea,
                    'original': nombre_original,
                    'limpio': nombre_limpio
                })
                
                # Mostrar progreso
                if nombre_original != nombre_limpio:
                    print(f"✓ Línea {num_linea}: '{nombre_original}' → '{nombre_limpio}'")
                else:
                    print(f"✓ Línea {num_linea}: '{nombre_limpio}'")
                    
            except Exception as e:
                estadisticas['errores'].append({
                    'linea': num_linea,
                    'nombre': nombre_original,
                    'error': str(e)
                })
                print(f"✗ Línea {num_linea}: ERROR - {nombre_original} ({e})")
        
        # Mostrar resumen
        print(f"\n{'='*70}")
        print(f"📊 RESUMEN")
        print(f"{'='*70}")
        print(f"✓ Carpetas creadas exitosamente: {len(estadisticas['exitosas'])}")
        print(f"⚠️  Duplicadas (renombradas): {len(estadisticas['duplicadas'])}")
        print(f"∅ Líneas vacías omitidas: {estadisticas['vacias']}")
        print(f"✗ Errores: {len(estadisticas['errores'])}")
        
        # Mostrar errores detallados si los hay
        if estadisticas['errores']:
            print(f"\n{'='*70}")
            print(f"DETALLE DE ERRORES:")
            print(f"{'='*70}")
            for err in estadisticas['errores']:
                print(f"  Línea {err['linea']}: {err['nombre']}")
                print(f"  └─ Error: {err['error']}\n")
        
        # Guardar log
        log_file = "log_creacion_carpetas.txt"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Log de creación de carpetas\n")
            f.write(f"{'='*70}\n\n")
            f.write(f"Archivo origen: {archivo_origen_txt}\n")
            f.write(f"Directorio destino: {directorio_destino}\n")
            f.write(f"Total exitosas: {len(estadisticas['exitosas'])}\n")
            f.write(f"Total errores: {len(estadisticas['errores'])}\n\n")
            
            if estadisticas['errores']:
                f.write(f"Errores:\n")
                for err in estadisticas['errores']:
                    f.write(f"  Línea {err['linea']}: {err['nombre']} - {err['error']}\n")
        
        print(f"\n📝 Log guardado en: {log_file}")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
    
    return estadisticas


# ============================================================================
# EJEMPLOS DE USO
# ============================================================================

if __name__ == "__main__":
    
    # EJEMPLO 1: Archivo simple (una carpeta por línea)
    if input(f"¿Crear carpetas'? (s/n): ").lower() == 's':
        # print("EJEMPLO 1: Archivo TXT simple\n")
        crear_carpetas_desde_txt(
            archivo_origen_txt="G:\Otros ordenadores\Mi PC\CONFIANZA\Auditoria\RequerimientosTTHH.txt",
            directorio_destino=r"G:\Mi unidad\AVL Abogados Grabaciones\(16) Marketing Comunicaciones Atención a Clientes\Requerimientos",
            max_nombre=80
        )
    else:
        print("Opción no reconocida")
    
    # print("\n" + "="*70 + "\n")
    
    # # EJEMPLO 2: Archivo CSV (separado por comas, usar columna 0)
    # print("EJEMPLO 2: Archivo CSV (columna 0)\n")
    # crear_carpetas_desde_txt(
    #     archivo_txt="datos.csv",
    #     directorio_destino="./carpetas_ejemplo2",
    #     separador=",",
    #     columna=0
    # )
    
    # print("\n" + "="*70 + "\n")
    
    # # EJEMPLO 3: Archivo TSV (separado por tabulaciones, columna 2)
    # print("EJEMPLO 3: Archivo TSV (columna 2)\n")
    # crear_carpetas_desde_txt(
    #     archivo_origen_txt="registros.tsv",
    #     directorio_destino="./carpetas_ejemplo3",
    #     separador="\t",
    #     columna=2,
    #     max_nombre=50  # Limitar nombres a 50 caracteres
    # )