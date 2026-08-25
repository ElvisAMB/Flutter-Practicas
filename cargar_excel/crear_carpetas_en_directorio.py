import os

def crear_carpetas(directorio_base, nombres_carpetas):
    """
    Crea una lista de carpetas dentro de un directorio dado.
    
    :param directorio_base: Ruta del directorio donde se crearán las carpetas.
    :param nombres_carpetas: Lista con los nombres de las carpetas a crear.
    """
    # Crear el directorio base si no existe
    if not os.path.exists(directorio_base):
        os.makedirs(directorio_base)
        print(f"Directorio base creado: {directorio_base}")

    for nombre in nombres_carpetas:
        ruta_carpeta = os.path.join(directorio_base, nombre)
        try:
            os.makedirs(ruta_carpeta, exist_ok=True)
            print(f"Carpeta creada: {ruta_carpeta}")
        except Exception as e:
            print(f"Error al crear {ruta_carpeta}: {e}")


if __name__ == "__main__":
    # Ejemplo de uso
    directorio = r"G:\Mi unidad\Seguridad de la Información\CISO Externo\Propuestas\(02) GMS\2026-07-03 Requisitos"
    carpetas = [
        '(01) Caso documentado en sector asegurador/financiero',
        '(02) Plantilla de matriz de riesgo de muestra',
        '(03) N° de implementaciones para posibles certificaciones del cliente',
        '(04) Reportes de pruebas anteriores',
        '(05) CVs + plan de continuidad de personal',
        '(06) Mínimo 2-3 referencias verificables',
    ]

    crear_carpetas(directorio, carpetas)