import os
from pypdf import PdfReader, PdfWriter


def optimizar_pdf(ruta_entrada, ruta_salida):
    # Inicializar el lector y el escritor de PDF
    reader = PdfReader(ruta_entrada)
    writer = PdfWriter()

    # Copiar las páginas al escritor
    for page in reader.pages:
        writer.add_page(page)

    # Aplicar compresión sin pérdida a las imágenes y textos internos
    for page in writer.pages:
        page.compress_content_streams()  # Comprime el contenido de la página

    # Guardar el nuevo archivo optimizado
    with open(ruta_salida, "wb") as f:
        writer.write(f)

    # Calcular y mostrar la reducción
    tamano_original = os.path.getsize(ruta_entrada) / 1024
    tamano_final = os.path.getsize(ruta_salida) / 1024
    print(f"Tamaño original: {tamano_original:.2f} KB")
    print(f"Tamaño optimizado: {tamano_final:.2f} KB")

# Uso del script
optimizar_pdf(r"C:\Users\elvis.mora\Documents\(01) Campañas de Concientización.pdf", r"C:\Users\elvis.mora\Documents\(01) Campañas de Concientización[1].pdf")
