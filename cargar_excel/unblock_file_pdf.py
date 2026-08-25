import pikepdf

# def desbloquear_archivo_pdf(ruta):
#     files = [f for f in os.listdir(ruta) if os.path.isfile(f)]
#     for f in files:
#         print(f)
#         if f.endswith(".pdf"):
#             pdf = pikepdf.open(f,allow_overwriting_input=True)
#             pdf.save(f)
#             continue

# Especifica el nombre del archivo que quieres modificar

def desbloquear_archivo_pdf(archivo_pdf):
    try:
        # Abre el PDF
        pdf = pikepdf.open(archivo_pdf, allow_overwriting_input=True)
        
        # Guarda el PDF (esto lo optimiza/limpia)
        pdf.save(archivo_pdf)
        
        print(f"Archivo '{archivo_pdf}' procesado exitosamente")
        
    except FileNotFoundError:
        print(f"Error: El archivo '{archivo_pdf}' no existe")
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")

def quitar_contrasena_pdf(archivo_entrada,archivo_salida):
    try:
        # Muchas veces las restricciones se pueden quitar sin contraseña
        pdf = pikepdf.open(archivo_entrada)
        pdf.save(archivo_salida, encryption=False)
        print("Restricciones removidas exitosamente")
    except Exception as e:
        print(f"Error: {e}")

# desbloquear_archivo_pdf(r'C:\Users\elvis.mora\Downloads\Registro Oficial 353 5-junio-2008.pdf')        
#funcionó con respecto a remover la constraseña
quitar_contrasena_pdf(r'C:\Users\elvis.mora\Downloads\Registro Oficial 353 5-junio-2008.pdf',r'C:\Users\elvis.mora\Downloads\Registro Oficial 353 5-junio-2008-modificado.pdf')