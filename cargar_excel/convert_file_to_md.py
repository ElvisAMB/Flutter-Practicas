import os
from openai import OpenAI
from markitdown import MarkItDown

def convertir_a_markdown(ruta_archivo, api_key_openai=None):
    """
    Convierte cualquier archivo (PDF, PPTX, DOCX, XLSX, JPG, PNG) a .md
    Si se detectan gráficos o imágenes, utiliza un LLM multimodal para describirlos.
    """
    # 1. Validar que el archivo exista
    if not os.path.exists(ruta_archivo):
        print(f"❌ Error: El archivo {ruta_archivo} no existe.")
        return None

    print(f"🔄 Procesando archivo: {ruta_archivo}...")

    # 2. Configurar el motor de conversión
    # Si hay API Key de OpenAI, habilitamos la descripción inteligente de gráficos
    if api_key_openai:
        client = OpenAI(api_key=api_key_openai)
        # Inicializamos MarkItDown pasando el cliente y un modelo con visión
        md_engine = MarkItDown(
            llm_client=client,
            llm_model="gpt-4o-mini"  # Excelente, rápido y muy económico en tokens
        )
        print("👁️  Modo de visión activado (los gráficos serán analizados por IA).")
    else:
        # Conversión básica basada en texto y estructuras estándar (tablas, listas)
        md_engine = MarkItDown()
        print("⚠️  Sin API Key: Los gráficos complejos podrían omitirse. Solo se extraerá texto/tablas.")

    try:
        # 3. Realizar la conversión automática según la extensión del archivo
        resultado = md_engine.convert(ruta_archivo)
        contenido_md = resultado.text_content

        # 4. Generar el nombre y ruta del archivo .md de salida
        nombre_base, _ = os.path.splitext(ruta_archivo)
        ruta_salida = f"{nombre_base}.md"

        # 5. Guardar el archivo convertido
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(contenido_md)

        print(f"✅ ¡Conversión exitosa! Archivo guardado en: {ruta_salida}")
        return ruta_salida

    except Exception as e:
        print(f"💥 Ocurrió un error durante la conversión: {e}")
        return None

# --- EJEMPLO DE USO ---
if __name__ == "__main__":
    # Cambia esto por la ruta de tu archivo (ej: "reporte.pdf", "presentacion.pptx", "datos.xlsx")
    archivo_a_convertir = "tu_presentacion_o_pdf.pptx" 
    
    # Coloca tu API key de OpenAI para habilitar la lectura de gráficos/imágenes.
    # Si solo quieres texto/tablas estructurales, déjala como None.
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "tu-api-key-aqui")

    # Ejecutar la función
    convertir_a_markdown(archivo_a_convertir, api_key_openai=OPENAI_API_KEY)
