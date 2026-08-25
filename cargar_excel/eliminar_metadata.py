from docx import Document
from docx.oxml.ns import qn
import sys
import os

def limpiar_metadatos(ruta_archivo):
    doc = Document(ruta_archivo)
    props = doc.core_properties

    # Eliminar todos los metadatos
    props.author = ""
    props.last_modified_by = ""
    props.title = ""
    props.subject = ""
    props.description = ""
    props.keywords = ""
    props.category = ""
    props.comments = ""
    props.version = ""
    props.revision = 1
    
    # Guardar con sufijo _limpio
    nombre, ext = os.path.splitext(ruta_archivo)
    nueva_ruta = f"{nombre}_limpio{ext}"
    doc.save(nueva_ruta)
    print(f"✓ Guardado: {nueva_ruta}")

# Uso: python limpiar_docx.py archivo.docx
if __name__ == "__main__":
    #for archivo in sys.argv[1:]:
    archivo = r"C:\Users\elvis.mora\Documents\Eliminar metadatos de archivos.docx"
    limpiar_metadatos(archivo)