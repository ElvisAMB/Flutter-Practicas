import os
import zipfile

def comprimir_archivo(ruta_origen, ruta_destino):
    # Comprobamos que el archivo original exista
    if not os.path.exists(ruta_origen):
        print(f"El archivo {ruta_origen} no existe.")
        return

    # Creamos y escribimos el archivo .zip utilizando compresión estándar
    with zipfile.ZipFile(ruta_destino, 'w', zipfile.ZIP_DEFLATED) as archivo_zip:
        archivo_zip.write(ruta_origen, os.path.basename(ruta_origen))
    
    print(f"Archivo comprimido guardado en: {ruta_destino}")

# Ejecución de la función
archivo_a_comprimir = r"C:\Users\elvis.mora\Documents\(01) Campañas de Concientización[1].pdf"
archivo_zip_salida = r"C:\Users\elvis.mora\Documents\(01) Campañas de Concientización.pdf.zip"

comprimir_archivo(archivo_a_comprimir, archivo_zip_salida)
