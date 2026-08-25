
import os


def eliminar_archivo(archivo):
    """Elimina un archivo dado como parámetro de entrada."""
    esEliminado = False
    
    if os.path.exists(archivo):
        try:
            os.remove(archivo)
            print(f"El archivo '{archivo}' fue eliminado con éxito.")
            esEliminado = True
        except FileNotFoundError as fe:
            print(f"Error: El archivo '{archivo}' no se puede eliminar: {fe}.")
        except PermissionError as pe:
            print(f"Error: No se puede eliminar. El archivo está abierto por otro programa: {pe}")
        except Exception as e:
            print(f"Ocurrió un error inesperado al eliminar: {e}")
    else:
         esEliminado = True
         print(f"El archivo '{archivo}' no existe. Continuando ejecución...")
                 
    return esEliminado