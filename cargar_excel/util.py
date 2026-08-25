import os

def limpiar_consola():
    """
    Limpia la pantalla de la consola (terminal) ejecutando el comando
    apropiado para el sistema operativo detectado (Windows, Linux, o macOS).
    """
    # Verifica el sistema operativo
    if os.name == 'nt':
        # 'nt' es el identificador de Windows
        os.system('cls')
    else:
        # 'posix' es el identificador para Linux, macOS y otros sistemas basados en Unix
        os.system('clear')
    
    print("Consola limpiada.")
    
# # --- Ejemplo de Uso ---
# if __name__ == '__main__':
#     # Agrega algunas líneas para simular contenido previo
#     print("Primer mensaje...")
#     print("Segundo mensaje...")
    
#     # Pausa para que puedas ver el contenido antes de limpiar
#     input("Presiona ENTER para limpiar la consola...")
    
#     # Llama a la función de limpieza
#     limpiar_consola()
    
#     print("Este mensaje aparece después de la limpieza.")

