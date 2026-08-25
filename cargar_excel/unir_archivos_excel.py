import pandas as pd

def unificar_y_comparar_excel(
    archivo1_ruta: str,
    archivo2_ruta: str,
    hoja1_nombre: str,
    hoja2_nombre: str,
    nombre_nuevo_archivo: str
):

    # # --- Configuración ---

    # # Ruta del archivo Excel de entrada
    # archivo_entrada = 'datos_base.xlsx' 

    # # Nombres de las hojas que quieres unir
    # nombre_hoja_1 = 'Ventas_Enero'
    # nombre_hoja_2 = 'Ventas_Febrero'

    # # Ruta y nombre del nuevo archivo Excel de salida
    # archivo_salida = 'Ventas_Consolidadas.xlsx'

    # --- 1. Leer las hojas específicas ---

    # Lee la primera hoja en un DataFrame
    try:
        df1 = pd.read_excel(
            archivo1_ruta, 
            sheet_name=hoja1_nombre
        )
        print(f"Hoja '{hoja1_nombre}' leída con éxito.")
    except Exception as e:
        print(f"Error al leer la Hoja 1: {e}")
        exit() # Termina el script si no puede leer la hoja

    # Lee la segunda hoja en otro DataFrame
    try:
        df2 = pd.read_excel(
            archivo2_ruta, 
            sheet_name=hoja2_nombre
        )
        print(f"Hoja '{hoja2_nombre}' leída con éxito.")
    except Exception as e:
        print(f"Error al leer la Hoja 2: {e}")
        exit()

    # --- 2. Unir (Concatenar) las hojas ---

    # pd.concat() une los DataFrames. axis=0 indica que se unan por filas 
    # (una debajo de la otra), que es lo más común al unir hojas de datos.
    # ignore_index=True resetea los índices para que sean secuenciales en el DataFrame unido.
    df_unido = pd.concat([df1, df2], axis=0, ignore_index=True)

    print("\nSe han unido las hojas en un solo DataFrame.")
    # Muestra las primeras filas del resultado para verificar
    print("\nPrimeras 5 filas del DataFrame unido:")
    print(df_unido.head())

    # --- 3. Guardar el resultado en un nuevo archivo Excel ---

    try:
        # df_unido.to_excel() guarda el DataFrame como un nuevo archivo Excel.
        # index=False evita que se escriba el índice de Pandas como una columna en el Excel.
        df_unido.to_excel(
            nombre_nuevo_archivo, 
            index=False, 
            sheet_name='Consolidado' # Nombre de la hoja en el nuevo archivo
        )
        print(f"\n¡Éxito! La unión se ha guardado en '{nombre_nuevo_archivo}'")
    except Exception as e:
        print(f"Error al guardar el archivo de salida: {e}")