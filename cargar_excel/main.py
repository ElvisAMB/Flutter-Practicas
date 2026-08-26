import datetime
from delete_file import eliminar_archivo
from validation import validar_dos_campos_excel, validar_y_formato_celda_con_color
from util_excel import (
    cerrar_excel_abierto,
    establecer_ancho_columnas_excel,
    ocultar_hoja_excel,
)
from util import limpiar_consola
from order_sheet import ordenar_contenido_hoja_excel
from merge_excel_files import unir_hojas_excel, unir_hojas_excel_cadena
from filter import (
    aplicar_filtros_e_inmovilizar_lote,
    copiar_registros_filtrados_lote,
    inmovilizar_filas_por_hoja,
)
from copy_sheet import copiar_hojas_a_destino_lote, copiar_primer_hoja_a_nuevo_archivo
from datetime import datetime

##########################################################################
# GENERACION DE ARCHIVO CONSOLIDADO PARA CERTIFIFACIÓN DE USUARIOS
##########################################################################

if __name__ == "__main__":

    ##########################################################################
    # Datos del archivo obtenido del área de TI.
    ##########################################################################

    # archivo1_ruta = r'G:\Otros ordenadores\Mi PC\CONFIANZA\Seguridad de la Información\Certificación de Usuarios SC\2025\09 2025\usuarios_dominio_20250926.xlsx'
    archivo_cuentas_active_directory = r"G:\Mi unidad\Seguridad de la Información\Certificación de Usuarios SC\2026\07 2026\usuarios_dominio_20260825.xlsx"

    hoja_cuentas_active_directory = "usuarios_dominio_20260825"
    clave_archivo1 = "EmailAddress"

    ##########################################################################
    # Datos del archivo obtenido del área de TTHH: Quitar el encabezado, formatear el archivo quitando las columnas que no son necesarias.
    ##########################################################################

    # archivo2_ruta = r'G:\Otros ordenadores\Mi PC\CONFIANZA\Seguridad de la Información\Certificación de Usuarios SC\2025\09 2025\Lista de colaboradores HcmFront 2025-09-24.xlsx'
    archivo2_ruta = r"G:\Mi unidad\Seguridad de la Información\Certificación de Usuarios SC\2026\07 2026\Lista de colaboradores.xlsx"
    hoja2_nombre = "Colaboradores"
    clave_archivo2 = "Email Corporativo"

    archivo_catalogo_ruta = r"G:\Mi unidad\Seguridad de la Información\Certificación de Usuarios SC\Catalogo\Catalogo_Usr_Ser_Prov_Pasant.xlsx"

    fecha = datetime.now().strftime("%Y-%m-%d_%H%M")

    # Nombre de archivo y carpeta de salida
    nombre_nuevo_archivo = rf"G:\Mi unidad\Seguridad de la Información\Certificación de Usuarios SC\2026\07 2026\Analisis_CU_{fecha}.xlsx"
    # print(nombre_nuevo_archivo)

    limpiar_consola()

    cerrar_excel_abierto(nombre_nuevo_archivo)

    ##########################################################################
    # Eliminar el archivo si existe.
    ##########################################################################

    if eliminar_archivo(nombre_nuevo_archivo):
        copiar_primer_hoja_a_nuevo_archivo(
            archivo_origen=archivo_catalogo_ruta,
            hoja_origen="TotalCtasSerProvPasan",
            archivo_destino=nombre_nuevo_archivo,
            hoja_destino="CatalogoSerProPas",
        )

        tareas_de_copia = [
            {
                "archivo_origen": archivo_cuentas_active_directory,
                "hoja_origen": hoja_cuentas_active_directory,
                "hoja_destino_nueva": "UsrActDirectory",
            },
            {
                "archivo_origen": archivo2_ruta,
                "hoja_origen": hoja2_nombre,
                "hoja_destino_nueva": "UsrNomina",
            },
        ]

        copiar_hojas_a_destino_lote(
            archivo_destino=nombre_nuevo_archivo, mapeo_copias=tareas_de_copia
        )

        # 1. Defines la lista secuencial de uniones (el orden importa)
        secuencia_uniones = [
            {
                "hoja_1": "UsrActDirectory",
                "hoja_2": "CatalogoSerProPas",
                "campo_hoja_1": "SID",
                "campo_hoja_2": "SID",
                "hoja_destino": "SrvProvPas",
                "tipo_union": "outer",
            },
            {
                "hoja_1": "SrvProvPas",  # Usa el resultado del paso anterior directamente desde la RAM
                "hoja_2": "UsrNomina",
                "campo_hoja_1": "EmailAddress",
                "campo_hoja_2": "Email Corporativo",
                "hoja_destino": "AllAccounts",
                "tipo_union": "outer",
            },
        ]

        # 2. Ejecutas la optimización en una sola línea
        unir_hojas_excel_cadena(
            ruta_archivo=nombre_nuevo_archivo, operaciones_union=secuencia_uniones
        )

        # 1. Configuras la lista de criterios de filtrado
        configuracion_filtros = [
            {
                "nombre_columna": "Enabled",
                "valor_columna": "0.0",
                "hoja_destino": "AccountsDisabled",
            },
            {
                "nombre_columna": "Enabled",
                "valor_columna": "1.0",
                "hoja_destino": "AccountsEnabled",
            },
        ]

        # 2. Ejecutas la extracción optimizada en una sola línea
        copiar_registros_filtrados_lote(
            ruta_archivo=nombre_nuevo_archivo,
            hoja_origen="AllAccounts",
            operaciones_filtrado=configuracion_filtros,
        )

        # cerrar_excel_abierto(nombre_nuevo_archivo)

        unir_hojas_excel(
            ruta_archivo=nombre_nuevo_archivo,
            hoja_1="UsrActDirectory",
            hoja_2="UsrNomina",
            campo_hoja_1="EmailAddress",
            campo_hoja_2="Email Corporativo",
            hoja_destino="UsrNominaEnabled",
            tipo_union="right",
        )

        # Ordenamiento por hoja y columna(s) específica(s)

        ordenar_contenido_hoja_excel(
            archivo_ruta=nombre_nuevo_archivo,
            hoja_a_ordenar="AccountsEnabled",
            campos_ordenacion=["Tipo", "Sucursal", "Primer apellido"],
            ascendente=True,  # Ordenación Ascendente
        )

        ordenar_contenido_hoja_excel(
            archivo_ruta=nombre_nuevo_archivo,
            hoja_a_ordenar="UsrNominaEnabled",
            campos_ordenacion=["Sucursal", "LastName", "FirstName"],
            ascendente=True,  # Ordenación Ascendente
        )

        ##########################################################################
        # Realizar validaciones, reglas de revisión.
        ##########################################################################

        validar_y_formato_celda_con_color(
            archivo_ruta=nombre_nuevo_archivo,
            hoja_nombre="UsrNominaEnabled",
            columna_identificador="SamAccountName",
        )
        # cerrar_excel_abierto(nombre_nuevo_archivo)

        validar_dos_campos_excel(
            archivo=nombre_nuevo_archivo,
            hoja="AllAccounts",
            campo_1="H",
            campo_2="AB",
            campo_a_pintar="A",
            fila_inicio=2,
        )

        ##########################################################################
        # Aplicación de filtros en hojas.
        ##########################################################################

        try:
            hojas_procesar = {
                "UsrActDirectory": "A2",
                "UsrNomina": "A2",
                "AllAccounts": "A2",
                "AccountsDisabled": "A2",
                "AccountsEnabled": "A2",
                "UsrNominaEnabled": "A2",
            }

            aplicar_filtros_e_inmovilizar_lote(
                ruta_archivo=nombre_nuevo_archivo,
                configuracion_hojas=hojas_procesar,
                fila_encabezado=1,
            )

        except Exception as error:
            print(f"Error al aplicar filtros Excel: {error}")

        ##########################################################################
        # Inmovilizar el número de fila dado en la hoja del archivo Excel.
        ##########################################################################

        try:
            hojas_config = {
                "UsrActDirectory": "A2",
                "UsrNomina": "A2",
                "AllAccounts": "A2",
                "AccountsDisabled": "A2",
                "AccountsEnabled": "A2",
                "UsrNominaEnabled": "A2",
            }

            inmovilizar_filas_por_hoja(
                ruta_archivo=nombre_nuevo_archivo, configuracion_hojas=hojas_config
            )
        except Exception as error:
            print(
                f"Error al inmovilizar el número de fila dado en la hoja del archivo Excel: {error}"
            )

        ##########################################################################
        # Establecer el ancho de columna personalizado por varios campos de la hoja del archivo Excel.
        ##########################################################################

        ## Diccionario: {'Nombre exacto de la columna': Ancho deseado}
        ANCHO_COLUMNAS = {
            "Name": 26,
            "FirstName": 15,
            "LastName": 18,
            "WhenCreated": 18,
            "LastLogon": 18,
            "PwdLastSet": 18,
            "WhenChanged": 18,
            "Enabled": 12,
            "EmailAddress": 31,
            "CanonicalName": 21,
            "CannotChangePassword": 27,
            "Department": 19,
            "DisplayName": 33,
            "SamAccountName": 22,
            "CN": 26,
            "ProtectedFromAccidentalDeletion": 35,
            "SID": 21,
            "BadLogonCount": 19,
            "PasswordNeverExpires": 24,
            "Nombre": 23,
            "Primer apellido": 23,
            "Segundo apellido": 23,
            "Email Corporativo": 34,
            "Descriptor de Cargo": 49,
            "Sucursal": 14,
            "Fecha de contratación": 21,
        }

        establecer_ancho_columnas_excel(
            archivo_ruta=nombre_nuevo_archivo,
            hoja_nombre="UsrNominaEnabled",
            columnas_ancho=ANCHO_COLUMNAS,
        )

        ###################################################################################
        # Ocultación simple ('hidden'): el usuario puede desocultar desde el menú de Excel.
        ###################################################################################

        ocultar_hoja_excel(
            archivo_ruta=nombre_nuevo_archivo,
            nombre_hoja_a_ocultar="CatalogoSerProPas",
            modo_oculto="hidden",
        )
        ocultar_hoja_excel(
            archivo_ruta=nombre_nuevo_archivo,
            nombre_hoja_a_ocultar="SrvProvPas",
            modo_oculto="hidden",
        )

        ###################################################################################
    else:
        print("No se puede continuar con la creación del archivo.")
