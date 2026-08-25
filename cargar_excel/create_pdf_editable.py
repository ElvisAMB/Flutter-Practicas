#!/usr/bin/env python3
"""
Script para crear un PDF con campos editables (formulario interactivo)
Versión simplificada y compatible
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import black, blue, lightgrey

def crear_pdf_con_campos_editables(nombre_archivo):
    """
    Crea un PDF con diferentes tipos de campos editables
    
    Args:
        nombre_archivo: Nombre del archivo PDF a crear
    """
    # Crear el canvas
    c = canvas.Canvas(nombre_archivo, pagesize=letter)
    ancho, alto = letter
    
    # Título del formulario
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, alto - 50, "Formulario de Evaluación")
    
    # Línea separadora
    c.setStrokeColor(blue)
    c.setLineWidth(2)
    c.line(50, alto - 65, ancho - 50, alto - 65)
    
    y_posicion = alto - 100
    c.setStrokeColor(black)
    c.setLineWidth(1)
    
    # ===== SECCIÓN 1: INFORMACIÓN PERSONAL =====
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(blue)
    c.drawString(50, y_posicion, "1. Información Personal")
    c.setFillColor(black)
    y_posicion -= 30
    
    # Campo de texto: Nombre
    c.setFont("Helvetica", 11)
    c.drawString(50, y_posicion, "Nombre completo:*")
    c.acroForm.textfield(
        name='nombre_completo',
        tooltip='Ingrese su nombre completo',
        x=180,
        y=y_posicion - 5,
        width=320,
        height=22,
        borderColor=black,
        fillColor=lightgrey,
        textColor=black,
        forceBorder=True,
        borderWidth=1
    )
    y_posicion -= 35
    
    # Campo de texto: Email
    c.drawString(50, y_posicion, "Correo electrónico:*")
    c.acroForm.textfield(
        name='correo_electronico',
        tooltip='ejemplo@correo.com',
        x=180,
        y=y_posicion - 5,
        width=320,
        height=22,
        borderColor=black,
        fillColor=lightgrey,
        textColor=black,
        forceBorder=True,
        borderWidth=1
    )
    y_posicion -= 35
    
    # Campo de texto: Teléfono
    c.drawString(50, y_posicion, "Teléfono:")
    c.acroForm.textfield(
        name='telefono',
        tooltip='Ingrese su número de teléfono',
        x=180,
        y=y_posicion - 5,
        width=200,
        height=22,
        borderColor=black,
        fillColor=lightgrey,
        textColor=black,
        forceBorder=True,
        borderWidth=1
    )
    y_posicion -= 35
    
    # Campo de texto: Dirección
    c.drawString(50, y_posicion, "Dirección:")
    c.acroForm.textfield(
        name='direccion',
        tooltip='Ingrese su dirección completa',
        x=180,
        y=y_posicion - 5,
        width=320,
        height=22,
        borderColor=black,
        fillColor=lightgrey,
        textColor=black,
        forceBorder=True,
        borderWidth=1
    )
    y_posicion -= 35
    
    # Campo de texto: Ciudad
    c.drawString(50, y_posicion, "Ciudad:")
    c.acroForm.textfield(
        name='ciudad',
        tooltip='Ciudad',
        x=180,
        y=y_posicion - 5,
        width=150,
        height=22,
        borderColor=black,
        fillColor=lightgrey,
        textColor=black,
        forceBorder=True,
        borderWidth=1
    )
    
    # Campo de texto: Código Postal
    c.drawString(350, y_posicion, "Código Postal:")
    c.acroForm.textfield(
        name='codigo_postal',
        tooltip='CP',
        x=450,
        y=y_posicion - 5,
        width=50,
        height=22,
        borderColor=black,
        fillColor=lightgrey,
        textColor=black,
        forceBorder=True,
        borderWidth=1
    )
    y_posicion -= 50
    
    # ===== SECCIÓN 2: FECHA DE NACIMIENTO =====
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(blue)
    c.drawString(50, y_posicion, "2. Fecha de Nacimiento")
    c.setFillColor(black)
    y_posicion -= 30
    
    c.setFont("Helvetica", 11)
    c.drawString(50, y_posicion, "Fecha:")
    c.acroForm.textfield(
        name='fecha_nacimiento',
        tooltip='DD/MM/AAAA',
        x=180,
        y=y_posicion - 5,
        width=120,
        height=22,
        borderColor=black,
        fillColor=lightgrey,
        textColor=black,
        forceBorder=True,
        borderWidth=1
    )
    c.setFont("Helvetica", 9)
    c.setFillColor(blue)
    c.drawString(310, y_posicion, "(formato: DD/MM/AAAA)")
    c.setFillColor(black)
    y_posicion -= 50
    
    # ===== SECCIÓN 3: GÉNERO (RADIO BUTTONS) =====
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(blue)
    c.drawString(50, y_posicion, "3. Género")
    c.setFillColor(black)
    y_posicion -= 30
    
    c.setFont("Helvetica", 11)
    
    # Radio button: Masculino
    c.acroForm.radio(
        name='genero',
        tooltip='Seleccione Masculino',
        value='masculino',
        x=50,
        y=y_posicion - 5,
        size=15,
        borderColor=black,
        fillColor=None,
        textColor=blue,
        forceBorder=True
    )
    c.drawString(70, y_posicion, "Masculino")
    
    # Radio button: Femenino
    c.acroForm.radio(
        name='genero',
        tooltip='Seleccione Femenino',
        value='femenino',
        x=180,
        y=y_posicion - 5,
        size=15,
        borderColor=black,
        fillColor=None,
        textColor=blue,
        forceBorder=True
    )
    c.drawString(200, y_posicion, "Femenino")
    
    # Radio button: Otro
    c.acroForm.radio(
        name='genero',
        tooltip='Seleccione Otro',
        value='otro',
        x=310,
        y=y_posicion - 5,
        size=15,
        borderColor=black,
        fillColor=None,
        textColor=blue,
        forceBorder=True
    )
    c.drawString(330, y_posicion, "Otro")
    y_posicion -= 50
    
    # ===== SECCIÓN 4: INTERESES (CHECKBOXES) =====
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(blue)
    c.drawString(50, y_posicion, "4. Intereses (seleccione todos los que apliquen)")
    c.setFillColor(black)
    y_posicion -= 30
    
    c.setFont("Helvetica", 11)
    
    # Primera fila de checkboxes
    # Checkbox: Deportes
    c.acroForm.checkbox(
        name='interes_deportes',
        tooltip='Deportes',
        x=50,
        y=y_posicion - 5,
        size=15,
        checked=False,
        borderColor=black,
        fillColor=None,
        textColor=blue,
        forceBorder=True
    )
    c.drawString(70, y_posicion, "Deportes")
    
    # Checkbox: Música
    c.acroForm.checkbox(
        name='interes_musica',
        tooltip='Música',
        x=180,
        y=y_posicion - 5,
        size=15,
        checked=False,
        borderColor=black,
        fillColor=None,
        textColor=blue,
        forceBorder=True
    )
    c.drawString(200, y_posicion, "Música")
    
    # Checkbox: Lectura
    c.acroForm.checkbox(
        name='interes_lectura',
        tooltip='Lectura',
        x=310,
        y=y_posicion - 5,
        size=15,
        checked=False,
        borderColor=black,
        fillColor=None,
        textColor=blue,
        forceBorder=True
    )
    c.drawString(330, y_posicion, "Lectura")
    y_posicion -= 25
    
    # Segunda fila de checkboxes
    # Checkbox: Tecnología
    c.acroForm.checkbox(
        name='interes_tecnologia',
        tooltip='Tecnología',
        x=50,
        y=y_posicion - 5,
        size=15,
        checked=False,
        borderColor=black,
        fillColor=None,
        textColor=blue,
        forceBorder=True
    )
    c.drawString(70, y_posicion, "Tecnología")
    
    # Checkbox: Arte
    c.acroForm.checkbox(
        name='interes_arte',
        tooltip='Arte',
        x=180,
        y=y_posicion - 5,
        size=15,
        checked=False,
        borderColor=black,
        fillColor=None,
        textColor=blue,
        forceBorder=True
    )
    c.drawString(200, y_posicion, "Arte")
    
    # Checkbox: Viajes
    c.acroForm.checkbox(
        name='interes_viajes',
        tooltip='Viajes',
        x=310,
        y=y_posicion - 5,
        size=15,
        checked=False,
        borderColor=black,
        fillColor=None,
        textColor=blue,
        forceBorder=True
    )
    c.drawString(330, y_posicion, "Viajes")
    y_posicion -= 50
    
    # ===== SECCIÓN 5: COMENTARIOS =====
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(blue)
    c.drawString(50, y_posicion, "5. Comentarios adicionales")
    c.setFillColor(black)
    y_posicion -= 30
    
    c.setFont("Helvetica", 11)
    c.drawString(50, y_posicion, "Escriba cualquier comentario o información adicional:")
    y_posicion -= 10
    
    c.acroForm.textfield(
        name='comentarios',
        tooltip='Ingrese sus comentarios aquí',
        x=50,
        y=y_posicion - 90,
        width=500,
        height=90,
        borderColor=black,
        fillColor=lightgrey,
        textColor=black,
        forceBorder=True,
        borderWidth=1
    )
    y_posicion -= 120
    
    # ===== SECCIÓN 6: ACEPTACIÓN DE TÉRMINOS =====
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(blue)
    c.drawString(50, y_posicion, "6. Aceptación de Términos")
    c.setFillColor(black)
    y_posicion -= 30
    
    c.setFont("Helvetica", 11)
    c.acroForm.checkbox(
        name='acepto_terminos',
        tooltip='Acepto los términos y condiciones',
        x=50,
        y=y_posicion - 5,
        size=15,
        checked=False,
        borderColor=black,
        fillColor=None,
        textColor=blue,
        forceBorder=True
    )
    c.drawString(70, y_posicion, "Acepto los términos y condiciones*")
    y_posicion -= 30
    
    # Firma
    c.drawString(50, y_posicion, "Firma:")
    c.acroForm.textfield(
        name='firma',
        tooltip='Escriba su nombre como firma',
        x=180,
        y=y_posicion - 5,
        width=250,
        height=22,
        borderColor=black,
        fillColor=lightgrey,
        textColor=black,
        forceBorder=True,
        borderWidth=1
    )
    
    # Nota al pie
    c.setFont("Helvetica", 8)
    c.setFillColor(black)
    c.drawString(50, 40, "* Campos obligatorios")
    c.drawString(50, 30, "Nota: Complete todos los campos y guarde el documento. Los campos son editables con Adobe Reader o cualquier lector PDF compatible.")
    
    # Guardar el PDF
    c.save()
    
    print(f"✓ PDF creado exitosamente: {nombre_archivo}")
    print(f"\nCampos editables incluidos:")
    print(f"  📝 Campos de texto: nombre, email, teléfono, dirección, ciudad, código postal, fecha, comentarios, firma")
    print(f"  ⚪ Radio buttons: género (3 opciones)")
    print(f"  ☑️  Checkboxes: 6 intereses + aceptación de términos")
    print(f"\n✅ Total: 16 campos interactivos")


if __name__ == "__main__":
    # Crear el PDF con campos editables
    crear_pdf_con_campos_editables(r"C:\Users\elvis.mora\Downloads\formulario_editable.pdf")
    print("\n🎉 ¡Listo! Puedes abrir el PDF y editar todos los campos.")
