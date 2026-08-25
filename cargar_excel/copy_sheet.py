import pandas as pd
import os

def copiar_primer_hoja_a_nuevo_archivo(
    archivo_origen: str, 
    hoja_origen: str, 
    archivo_destino: str, 
    hoja_destino: str
):
    """
    Copia una hoja específica de un archivo Excel a un archivo Excel nuevo, 
    dándole un nombre a la nueva hoja.

    Args:
        archivo_origen (str): Ruta y nombre del archivo Excel del que se va a leer.
        hoja_origen (str): Nombre de la hoja que se desea copiar.
        archivo_destino (str): Ruta y nombre del nuevo archivo Excel a crear.
        hoja_destino (str): Nombre que tendrá la hoja en el archivo de destino.
    """
    
    try:
        # 1. Cargar la hoja específica del archivo de origen
        print(f"⚙️  Cargando hoja '{hoja_origen}' de '{archivo_origen}'...")
        df = pd.read_excel(archivo_origen, sheet_name=hoja_origen)
        print(f"✅ Hoja cargada. Filas: {len(df)}")
        
    except FileNotFoundError:
        print(f"❌ Error: Archivo de origen no encontrado en la ruta: {archivo_origen}")
        return
    except KeyError:
        print(f"❌ Error: La hoja '{hoja_origen}' no se encontró en el archivo '{archivo_origen}'.")
        return
    except Exception as e:
        print(f"❌ Error al cargar la hoja: {e}")
        return

    # 2. Guardar el DataFrame en un nuevo archivo Excel con la hoja nueva
    try:
        # Usamos df.to_excel para guardar el DataFrame. 
        # Si el archivo de destino no existe, pandas lo crea automáticamente.
        df.to_excel(archivo_destino, sheet_name=hoja_destino, index=False)
        
        print(f"   Hoja '{hoja_origen}' copiada a '{hoja_destino}'.")
    except Exception as e:
        print(f"❌ Error al escribir el archivo de destino: {e}")

def copiar_hoja_a_archivo_existente(
    archivo_origen: str, 
    hoja_origen: str, 
    archivo_destino_existente: str, 
    hoja_destino_nueva: str
):
    """
    Copia una hoja específica de un archivo Excel a una nueva hoja nombrada
    dentro de un archivo Excel ya existente, sin borrar el contenido previo.

    Args:
        archivo_origen (str): Ruta y nombre del archivo Excel de donde se va a leer.
        hoja_origen (str): Nombre de la hoja que se desea copiar.
        archivo_destino_existente (str): Ruta y nombre del archivo Excel al que se va a añadir la hoja.
        hoja_destino_nueva (str): Nombre que tendrá la nueva hoja en el archivo de destino.
    """
    
    # 1. Verificar si el archivo destino existe
    if not os.path.exists(archivo_destino_existente):
        print(f"❌ Error: El archivo destino '{archivo_destino_existente}' no existe.")
        print("   Este script requiere que el archivo destino ya esté creado.")
        return

    # 2. Cargar la hoja específica del archivo de origen
    try:
        print(f"⚙️  Cargando hoja '{hoja_origen}' de '{archivo_origen}'...")
        df = pd.read_excel(archivo_origen, sheet_name=hoja_origen)
        print(f"✅ Hoja cargada. Filas: {len(df)}")
        
    except FileNotFoundError:
        print(f"❌ Error: Archivo de origen no encontrado en la ruta: {archivo_origen}")
        return
    except KeyError:
        print(f"❌ Error: La hoja '{hoja_origen}' no se encontró en el archivo '{archivo_origen}'.")
        return
    except Exception as e:
        print(f"❌ Error al cargar la hoja: {e}")
        return

    # 3. Guardar el DataFrame en una nueva hoja del archivo existente
    try:
        # Usamos pd.ExcelWriter con mode='a' (append) y engine='openpyxl' 
        # para añadir la nueva hoja sin borrar las existentes.
        with pd.ExcelWriter(archivo_destino_existente, engine='openpyxl', mode='a') as writer:
            # Escribe el DataFrame en la nueva hoja con el nombre especificado
            df.to_excel(writer, sheet_name=hoja_destino_nueva, index=False)
        
        print(f"   Hoja '{hoja_origen}' copiada y añadida como '{hoja_destino_nueva}'.")
    except Exception as e:
        print(f"❌ Error al escribir en el archivo Excel: {e}")
        print("   Asegúrese de que el archivo destino no esté abierto por otra aplicación.")

def copiar_hojas_a_destino_lote(archivo_destino: str, mapeo_copias: list):
    """
    Optimiza recursos abriendo el archivo de destino UNA SOLA VEZ.
    Copia múltiples hojas de distintos archivos de origen hacia un único archivo Excel existente,
    sin borrar el contenido previo.

    Parámetros:
        archivo_destino (str): Ruta y nombre del archivo Excel al que se añadirán las hojas.
        mapeo_copias (list): Lista de diccionarios, donde cada uno contiene:
                             - 'archivo_origen': Ruta del Excel fuente.
                             - 'hoja_origen': Nombre de la pestaña a leer.
                             - 'hoja_destino_nueva': Nombre que tendrá en el archivo final.
    """
    # 1. Verificar si el archivo destino existe y tiene contenido
    if not os.path.exists(archivo_destino) or os.path.getsize(archivo_destino) == 0:
        print(f"❌ Error: El archivo destino '{archivo_destino}' no existe o está vacío.")
        return

    try:
        print(f"📂 Abriendo archivo de destino de forma segura: {archivo_destino}")
        
        # 2. Abrimos el escritor en modo append ('a') e indicamos que reemplace si la hoja ya existe
        # openpyxl gestionará todas las inserciones en memoria antes de escribir el archivo final
        with pd.ExcelWriter(archivo_destino, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            
            # 3. Iterar por cada una de las copias solicitadas
            for tarea in mapeo_copias:
                origen = tarea['archivo_origen']
                hoja_origen = tarea['hoja_origen']
                hoja_destino = tarea['hoja_destino_nueva']
                
                # Validar existencia del archivo de origen
                if not os.path.exists(origen):
                    print(f"  ⚠️ Saltando: El archivo de origen '{origen}' no existe.")
                    continue
                
                try:
                    # Cargar hoja de origen en memoria (DataFrame)
                    df = pd.read_excel(origen, sheet_name=hoja_origen)
                    
                    # Escribir la hoja en el archivo de destino (todavía en memoria del Writer)
                    df.to_excel(writer, sheet_name=hoja_destino, index=False)
                    print(f"  ✅ Hoja '{hoja_origen}' de [{os.path.basename(origen)}] preparada como '{hoja_destino}'.")
                    
                except KeyError:
                    print(f"  ❌ Error: La hoja '{hoja_origen}' no existe dentro de '{origen}'.")
                except Exception as e:
                    print(f"  ❌ Error al procesar la hoja '{hoja_origen}': {e}")
                    
        print(f"🎉 ¡Todas las hojas fueron copiadas y guardadas correctamente en '{archivo_destino}'!")

    except PermissionError:
        print(f"❌ Error de permisos: El archivo destino '{archivo_destino}' está bloqueado (probablemente abierto en Excel).")
    except Exception as error:
        print(f"❌ Ocurrió un error inesperado al escribir el lote: {error}")


