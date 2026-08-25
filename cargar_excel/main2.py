from desbloquear import desbloquear_excel_zip, desbloquear_todas_hojas
from util import limpiar_consola
from merge_excel_files import unir_hojas_excel
from copy_sheet import copiar_hoja_a_archivo_existente
from util_excel import cerrar_excel_abierto


if __name__ == '__main__':
    #  # Datos del primer archivo
    # archivo1_ruta = r'C:\Users\elvis.mora\Downloads\Mailboxes Management (2025-10-23T16_24_41.255615-05_00).xlsx'
    # hoja1_nombre = 'Licencias'
    # clave_archivo1 = 'Email'
    
    # # Datos del segundo archivo
    # archivo2_ruta = r'C:\Users\elvis.mora\Catalogo\Registro_Usuarios.xlsx'
    # hoja2_nombre = 'AllAccounts'
    # clave_archivo2 = 'EmailAddress'
        
    # limpiar_consola()
    
    # cerrar_excel_abierto(archivo1_ruta)
    
    # copiar_hoja_a_archivo_existente(
    #     archivo_origen=archivo2_ruta,
    #     hoja_origen=hoja2_nombre,
    #     archivo_destino_existente=archivo1_ruta,
    #     hoja_destino_nueva='CatalogoUsuarios'
    # )
    
    # unir_hojas_excel(
    #     ruta_archivo=archivo1_ruta,
    #     hoja_1='Licencias',
    #     hoja_2='CatalogoUsuarios',
    #     campo_hoja_1='Email',
    #     campo_hoja_2='EmailAddress',
    #     hoja_destino = "Unificación",
    #     tipo_union = "outer"
    # )
    
    limpiar_consola()
    # desbloquear_todas_hojas(r"G:\Otros ordenadores\Mi PC\CONFIANZA\Protección de Datos Personales\Formulario proveedores\2025-06-09 TechnoFilm\R-CO-09 CHECK LIST AUTOEVALUACIÓN DE CUMPLIMIENTO LOPDP PARA PROVEEDORES V003 - copia.xlsx", 
    #                         r"G:\Otros ordenadores\Mi PC\CONFIANZA\Protección de Datos Personales\Formulario proveedores\2025-06-09 TechnoFilm\R-CO-09 CHECK LIST_archivo_desbloqueado.xlsx")
    
    desbloquear_excel_zip(r"G:\Otros ordenadores\Mi PC\CONFIANZA\Protección de Datos Personales\Formulario proveedores\2025-06-09 TechnoFilm\R-CO-09 CHECK LIST AUTOEVALUACIÓN DE CUMPLIMIENTO LOPDP PARA PROVEEDORES V003 - copia.xlsx", 
                            r"G:\Otros ordenadores\Mi PC\CONFIANZA\Protección de Datos Personales\Formulario proveedores\2025-06-09 TechnoFilm\R-CO-09 CHECK LIST_archivo_desbloqueado.xlsx")