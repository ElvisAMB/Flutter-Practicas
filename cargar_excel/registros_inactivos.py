import pandas as pd
import os

def filtrar_y_guardar_en_hoja_existente(
    archivo_existente: str,
    hoja_origen: str,
    columna_a_filtrar: str,
    hoja_destino_nombre: str
):
    """
    Carga una hoja de un archivo Excel, filtra las filas donde la columna 
    especificada es False, y guarda el resultado en una nueva hoja 
    dentro del mismo archivo existente.

    Args:
        archivo_existente (str): Ruta del archivo Excel existente.
        hoja_origen (str): Nombre de la hoja a leer del archivo.
        columna_a_filtrar (str): Nombre de la columna cuyo estado debe ser False.
        hoja_destino_nombre (str): Nombre de la nueva hoja donde se guardarán los resultados.
    """
    
    # 1. Cargar el DataFrame desde la hoja de origen
    try:
        print(f"⚙️  Cargando hoja '{hoja_origen}' del archivo '{archivo_existente}'...")
        df = pd.read_excel(archivo_existente, sheet_name=hoja_origen)
        print(f"✅ Hoja cargada. Total de filas: {len(df)}")
        
    except FileNotFoundError:
        print(f"❌ Error: Archivo no encontrado en la ruta: {archivo_existente}")
        return
    except KeyError:
        print(f"❌ Error: La hoja '{hoja_origen}' no se encontró en el archivo.")
        return
    except Exception as e:
        print(f"❌ Error al cargar el archivo/hoja: {e}")
        return

    # 2. Realizar el filtrado de las filas con estado False
    try:
        # Nota: El operador '==' compara el valor exacto 'False'
        df_filtrado = df[df[columna_a_filtrar] == False]
        
        print(f"✅ Filtrado completado. Filas con '{columna_a_filtrar}'=False: {len(df_filtrado)}")
        
        if len(df_filtrado) == 0:
            print("⚠️ Advertencia: No se encontraron registros con el estado False. Proceso terminado.")
            return

    except KeyError:
        print(f"❌ Error: La columna '{columna_a_filtrar}' no se encontró en la hoja '{hoja_origen}'.")
        return

    # 3. Guardar el DataFrame filtrado en una nueva hoja del archivo existente
    try:
        # Usa pd.ExcelWriter con mode='a' (append) para añadir la nueva hoja sin 
        # borrar las existentes. El motor 'openpyxl' es recomendado para este modo.
        with pd.ExcelWriter(archivo_existente, engine='openpyxl', mode='a') as writer:
            # Escribe el DataFrame filtrado en la nueva hoja
            df_filtrado.to_excel(writer, sheet_name=hoja_destino_nombre, index=False)
        
        print("\n" + "-" * 60)
        print("🎉 Éxito en el procesamiento:")
        print(f"   Los registros filtrados se han guardado en la nueva hoja:")
        print(f"   Archivo: {os.path.abspath(archivo_existente)}")
        print(f"   Hoja Destino: '{hoja_destino_nombre}'")
        print("-" * 60)

    except Exception as e:
        print(f"❌ Error al escribir en el archivo Excel: {e}")
        print("   Asegúrese de que el archivo no esté abierto por otra aplicación.")

