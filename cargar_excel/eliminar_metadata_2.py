from docx import Document
from lxml import etree
import zipfile, shutil, os, re, sys

def limpiar_todo(ruta_archivo):
    nombre, ext = os.path.splitext(ruta_archivo)
    nueva_ruta = f"{nombre}_limpio{ext}"
    shutil.copy2(ruta_archivo, nueva_ruta)

    # Abrir el DOCX como ZIP y limpiar el XML interno
    temp_dir = f"{nombre}_temp"
    os.makedirs(temp_dir, exist_ok=True)

    with zipfile.ZipFile(nueva_ruta, 'r') as z:
        z.extractall(temp_dir)

    # --- Limpiar core.xml (metadatos principales) ---
    core_path = os.path.join(temp_dir, "docProps", "core.xml")
    if os.path.exists(core_path):
        tree = etree.parse(core_path)
        root = tree.getroot()
        campos_sensibles = [
            "creator", "lastModifiedBy", "title",
            "subject", "description", "keywords",
            "category", "revision"
        ]
        for elem in root.iter():
            tag_local = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if tag_local in campos_sensibles:
                elem.text = ""
        tree.write(core_path, xml_declaration=True,
                   encoding="UTF-8", standalone=True)
        print("✓ core.xml limpiado")

    # --- Limpiar settings.xml (rsids con huella del equipo) ---
    settings_path = os.path.join(temp_dir, "word", "settings.xml")
    if os.path.exists(settings_path):
        tree = etree.parse(settings_path)
        root = tree.getroot()
        ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        # Eliminar todos los rsid (identificadores de sesión de edición)
        for rsids in root.findall(f"{{{ns}}}rsids"):
            root.remove(rsids)
        tree.write(settings_path, xml_declaration=True,
                   encoding="UTF-8", standalone=True)
        print("✓ settings.xml limpiado (rsids eliminados)")

    # --- Limpiar document.xml (revisiones con nombre de usuario/equipo) ---
    doc_path = os.path.join(temp_dir, "word", "document.xml")
    if os.path.exists(doc_path):
        with open(doc_path, "r", encoding="utf-8") as f:
            contenido = f.read()
        # Eliminar atributos w:author que guardan nombre de usuario
        contenido = re.sub(r'w:author="[^"]*"', 'w:author=""', contenido)
        # Eliminar atributos w:date de revisiones
        contenido = re.sub(r'w:date="[^"]*"', 'w:date=""', contenido)
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(contenido)
        print("✓ document.xml limpiado (autores y fechas de revisión)")

    # Reempaquetar el DOCX
    os.remove(nueva_ruta)
    with zipfile.ZipFile(nueva_ruta, 'w', zipfile.ZIP_DEFLATED) as z:
        for carpeta_raiz, _, archivos in os.walk(temp_dir):
            for archivo in archivos:
                ruta_completa = os.path.join(carpeta_raiz, archivo)
                ruta_relativa = os.path.relpath(ruta_completa, temp_dir)
                z.write(ruta_completa, ruta_relativa)

    # Limpiar carpeta temporal
    shutil.rmtree(temp_dir)
    print(f"\n✅ Archivo limpio guardado como: {nueva_ruta}")

# Uso
if __name__ == "__main__":
    #for archivo in sys.argv[1:]:
    archivo = r"C:\Users\elvis.mora\Documents\Eliminar metadatos de archivos.docx"
    limpiar_todo(archivo)