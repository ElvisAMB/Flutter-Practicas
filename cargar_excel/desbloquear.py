from openpyxl import load_workbook
import zipfile
import os
import shutil
import re

def desbloquear_todas_hojas(archivo_entrada, archivo_salida):
    """Desbloquea todas las hojas de un archivo Excel"""
    
    try:
        wb = load_workbook(archivo_entrada)
        hojas_desbloqueadas = 0
        
        for hoja in wb.worksheets:
            try:
                # Verificar si la hoja tiene protección
                if hasattr(hoja.protection, 'sheet') and hoja.protection.sheet:
                    hoja.protection.sheet = False
                    hoja.protection.password = ''
                    hoja.protection.enable()
                    print(f"✓ Hoja '{hoja.title}' desbloqueada")
                    hojas_desbloqueadas += 1
                else:
                    # Intentar desbloquear de todas formas
                    hoja.protection.sheet = False
                    hoja.protection.password = ''
                    print(f"○ Hoja '{hoja.title}' procesada (no tenía protección visible)")
                    hojas_desbloqueadas += 1
                    
            except Exception as e:
                print(f"✗ Error en hoja '{hoja.title}': {e}")
        
        wb.save(archivo_salida)
        print(f"\n✓ Archivo guardado como: {archivo_salida}")
        print(f"Total de hojas procesadas: {hojas_desbloqueadas}")
        
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
        
def desbloquear_excel_zip(archivo_entrada, archivo_salida):
    """Desbloquea Excel manipulando el archivo ZIP"""
    
    temp_dir = "temp_excel_extract"
    
    try:
        # Limpiar directorio temporal si existe
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        # Extraer el xlsx (que es un ZIP)
        print("Extrayendo archivo...")
        with zipfile.ZipFile(archivo_entrada, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Procesar hojas de cálculo
        worksheets_dir = os.path.join(temp_dir, 'xl', 'worksheets')
        hojas_procesadas = 0
        
        if os.path.exists(worksheets_dir):
            for filename in os.listdir(worksheets_dir):
                if filename.endswith('.xml'):
                    filepath = os.path.join(worksheets_dir, filename)
                    
                    # Leer el contenido
                    with open(filepath, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                    
                    # Remover todas las etiquetas de protección
                    contenido_original = contenido
                    contenido = re.sub(r'<sheetProtection[^>]*?/>', '', contenido)
                    contenido = re.sub(r'<sheetProtection[^>]*?>.*?</sheetProtection>', '', contenido, flags=re.DOTALL)
                    
                    if contenido != contenido_original:
                        # Guardar cambios
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(contenido)
                        print(f"✓ Protección removida de {filename}")
                        hojas_procesadas += 1
                    else:
                        print(f"○ {filename} no tenía protección")
        
        # Recomprimir como xlsx
        print("\nRecomprimiendo archivo...")
        with zipfile.ZipFile(archivo_salida, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root_dir, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root_dir, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
        
        print(f"\n✓ Archivo desbloqueado guardado como: {archivo_salida}")
        print(f"Total de hojas procesadas: {hojas_procesadas}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Limpiar archivos temporales
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print("Archivos temporales eliminados")