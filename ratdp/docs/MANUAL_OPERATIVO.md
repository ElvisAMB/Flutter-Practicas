# Manual de gestión operativa — Sistema RAT

**Sistema de Registro de Actividades de Tratamiento de Datos Personales**
Soporte informático del procedimiento **PR-PDP-001 v1.0**
Compañía de seguros de fianzas y crédito — República del Ecuador

| | |
|---|---|
| Documento | MAN-RAT-001 |
| Versión | 1.0 |
| Dirigido a | Delegado de Protección de Datos, dueños de proceso, Auditoría Interna, Administrador del sistema |
| Prerrequisito | Haber leído el procedimiento PR-PDP-001 |

> Este manual explica **cómo operar la herramienta**. No sustituye al procedimiento ni constituye asesoría legal. Ante duda sobre una base de licitud, un plazo de conservación o una transferencia internacional, la fila permanece en estado *En validación* hasta el pronunciamiento del DPD y de Gerencia Legal.

---

## 1. Qué hace y qué no hace este sistema

**Hace:**

- Mantiene la matriz RAT con los 20 campos del §8 del procedimiento, una fila por finalidad.
- Impide guardar combinaciones jurídicamente inconsistentes (p. ej. scoring con efectos jurídicos declarando que no requiere EIPD).
- Registra en bitácora inmutable quién consultó, creó, modificó, eliminó o exportó cada dato, y quién cambió permisos.
- Calcula los indicadores del §10 del procedimiento (Art. 36 RLOPDP, prueba de medidas).
- Gestiona el ciclo de vida de cada fila (Borrador → … → Histórico) con transiciones controladas.
- Guarda plantillas reutilizables (cuestionarios, EIPD, test de ponderación, actas) editables sin programar.

**No hace:**

- No decide por usted la base de licitud ni el plazo de conservación. Las alertas señalan inconsistencias; el criterio jurídico es del DPD.
- No reporta automáticamente al Registro Nacional de la SPDP. Marca la fila como pendiente y recuerda el término de 10 días (Art. 86 RLOPDP); el envío es manual.
- No es el repositorio de los datos personales de clientes. Es el inventario **de los tratamientos**, no de los titulares.

Esa última distinción es la más importante y la que más se confunde en la práctica: una fila del RAT dice *«Suscripción evalúa capacidad de pago de garantes con base en el Art. 7 núm. 5»*. No contiene el nombre de ningún garante.

---

## 2. Perfiles y qué puede hacer cada uno

| Perfil | Naturaleza | Puede | No puede |
|---|---|---|---|
| **Administrador** | Fijo, permisos no editables | Todo, incluida la gestión de usuarios, perfiles y permisos | — |
| **Auditor** | Fijo, solo lectura | Consultar toda la información y la bitácora; verificar integridad; exportar | Crear, modificar o eliminar **nada**, aunque se le asignen permisos por error |
| **Usuario común** | Base editable | Lo que el administrador le conceda; por defecto consultar y registrar actividades | Gestionar accesos |
| **Personalizados** | Creados por el administrador | Combinación libre de permisos | Gestionar accesos (reservado al administrador) |

El bloqueo del perfil Auditor tiene **doble candado**: el método `has_perm()` niega todo permiso que no comience en `view_`/`ver_`, y además un control en las vistas rechaza cualquier petición que no sea de lectura. Es deliberadamente redundante: una vista mal declarada no debe abrir un hueco.

**Regla operativa:** el perfil Auditor se asigna a Auditoría Interna y al revisor externo. No se usa para «usuarios que solo consultan» — para eso se crea un perfil personalizado con permisos de vista, porque el Auditor tiene acceso a la bitácora completa.

---

## 3. Puesta en marcha (primeras dos semanas)

### Semana 1 — Parametrizar antes de cargar

No cargue actividades antes de tener los catálogos afinados. Cargar primero obliga a reeditar cada fila después.

1. **Menú Administración → Usuarios.** Cree las cuentas del DPD, dueños de proceso, TI, Legal, Cumplimiento y Auditoría. Asigne perfiles.
2. **Catálogos → Macroprocesos y Áreas.** El comando de inicialización creó los 12 macroprocesos del §6.2 del procedimiento. Ajústelos al organigrama vigente y registre en cada área el **cargo** del responsable (nunca el nombre propio: el procedimiento lo exige en el campo 3.3 para que la matriz no caduque con la rotación).
3. **Catálogos → Categorías de datos.** Vienen las 14 categorías del §3.8. Revise que el catálogo siga siendo **cerrado**: el valor de la matriz depende de que sea agregable y comparable. Si un área pide una categoría nueva, evalúe si no encaja en una existente antes de crearla.
4. **Catálogos → Terceros.** Cargue encargados y destinatarios con su estado de contrato. Este catálogo alimenta el indicador IND-03 (% de encargados con contrato conforme al Art. 41 RLOPDP), que es el que más brechas revela al inicio.
5. **Catálogos → Sistemas de información.** Con TI. Marque el país de alojamiento de cada sistema: es el insumo del campo 3.14 y la omisión más frecuente del RAT.

### Semana 2 — Levantar

6. **Plantillas.** Adapte los cuestionarios base (`CUEST-GEN`, `CUEST-SUS`, `CUEST-TH`, `CUEST-TI`) al lenguaje de la compañía. Use **Clonar** en lugar de editar la plantilla base: así conserva el original para futuras áreas.
7. **Entrevistas.** Registre cada sesión (60–90 min, dueño de proceso + persona operativa). El campo de respuestas está cifrado porque suele contener nombres de personas mencionadas.
8. **Actividades.** Una finalidad = una fila. Codifique `RAT-<ÁREA>-<NN>`.

---

## 4. Registrar una actividad, campo por campo

Los campos del formulario llevan la referencia al numeral del procedimiento y al artículo aplicable en su texto de ayuda. Notas donde la herramienta añade algo:

**3.1 Código y nombre.** El nombre debe combinar acción + finalidad. `RAT-SUS-01 — Evaluación de riesgo y capacidad de pago para suscripción` es correcto; `Base de clientes` no lo es (describe un soporte, no una actividad).

**3.5 Encargados.** Al seleccionarlos, el detalle de la actividad muestra un distintivo verde o rojo según si el contrato cumple el Art. 41 RLOPDP. Rojo genera alerta y afecta el IND-03.

**3.6 Base de licitud.** Puede seleccionar varias, pero si necesita tres bases distintas para una misma fila, **probablemente son tres actividades**. Al invocar interés legítimo (numeral 8), registre el código del test de ponderación: sin él, la fila queda con brecha.

**3.9 Datos especiales.** Tiene cuatro valores, no dos: Sí / No / No aplica / **No evaluado**. Este último es el valor por defecto y es intencional — el procedimiento advierte que «el blanco no distingue no aplica de no evaluado». El indicador IND-06 cuenta los pendientes.

Si marca *Sí*, debe indicar el tipo (crediticios, salud, biométricos, judicial, menores, discapacidad, sensible). El sistema rechaza el guardado si marca *Sí* sin tipo, porque `SÍ – crediticios` y `SÍ – salud` no tienen las mismas consecuencias.

**3.14 Transferencia internacional.** Pregunte siempre a TI la región de alojamiento antes de responder. La nube extranjera cuenta como transferencia aunque «solo almacene». Si marca *Sí*, el sistema exige país y mecanismo habilitante ecuatoriano — no acepta la fila con solo «SCC» o «BCR», que son figuras del RGPD.

**3.16 Plazo.** El sistema genera alerta si el texto contiene «indefinido». Complete además el plazo en meses cuando sea determinable: habilita las alertas de depuración.

**3.19 EIPD.** Si marca «decisión automatizada» con efectos jurídicos, el sistema **impide** poner *No* en EIPD requerida (Art. 42 lit. a). Y no permite publicar como *Vigente* una fila con EIPD requerida sin código de informe, porque la evaluación es **previa** al tratamiento.

---

## 5. Ciclo de vida de una fila

```
Borrador ──► En validación ──► Validado ──► Vigente ──► Histórico
   │              │   ▲            │  ▲          │
   │              ▼   │            ▼  │          │
   └──────► Con brechas ◄──── En revisión ◄──────┘
```

Las transiciones no listadas se rechazan. En particular **no se puede saltar de Borrador a Vigente**: una fila publicada sin pasar por validación no es evidencia defendible ante la SPDP.

- **Validado** registra automáticamente quién valida y cuándo.
- **Vigente** actualiza la fecha de última revisión y activa el control del reporte al Registro Nacional.
- **Histórico** exige fecha de cese y es terminal: la fila se conserva para trazabilidad, nunca se borra.

### Sobre el borrado

El botón *Dar de baja* realiza **borrado lógico**. El registro deja de aparecer en los listados pero permanece en la base con marca de quién y cuándo. Esto responde al principio de responsabilidad proactiva y demostrada (Art. 10 lit. k LOPDP): borrar físicamente la evidencia de un tratamiento pasado destruiría precisamente lo que hay que demostrar.

---

## 6. Alertas y brechas

El detalle de cada actividad muestra las **señales de alerta** detectadas automáticamente:

| Alerta | Origen |
|---|---|
| Campo 3.9 sin evaluar | Valor por defecto no revisado |
| Campo 3.14 sin evaluar | Falta consulta a TI sobre región de alojamiento |
| EIPD requerida sin informe | Art. 42 LOPDP: la evaluación es previa |
| Decisión totalmente automatizada | Derecho del Art. 20 LOPDP |
| Datos crediticios | Recordatorio del límite imperativo de 5 años (Art. 28) |
| Encargados sin contrato conforme | Art. 41 RLOPDP |
| Plazo indefinido | Art. 10 lit. i LOPDP |
| Sin revisión hace más de 365 días | Revisión mínima anual (§10) |
| Vigente y no reportada al Registro Nacional | Término de 10 días (Art. 86 RLOPDP) |

Una alerta es un aviso automático. Una **brecha** es el reconocimiento formal de un incumplimiento con plan de acción, responsable y fecha de compromiso. Convierta la alerta en brecha cuando la corrección no sea inmediata: es lo que permite demostrar gestión, no solo detección.

El **nivel de riesgo** (Alto / Medio / Bajo) se calcula por puntos: datos especiales (+2), decisión automatizada (+2), gran escala (+2), transferencia internacional (+1), menores (+1). Es un ordenador de prioridades para el DPD, **no** un sustituto de la EIPD.

---

## 7. Indicadores de gestión

Menú **Indicadores**. Los diez indicadores incluyen los cinco sugeridos en el §10 del procedimiento:

| Código | Indicador | Meta |
|---|---|---|
| IND-01 | Tratamientos validados | 90 % |
| IND-02 | Con base de licitud documentada | 100 % |
| IND-03 | Encargados con contrato conforme | 100 % |
| IND-04 | EIPD pendientes | 0 |
| IND-05 | Actualización dentro del año | 100 % |
| IND-06 | Campo 3.9 sin evaluar | 0 |
| IND-07 | Vigentes reportadas al Registro Nacional | 100 % |
| IND-08 a IND-10 | Perfil de riesgo (especiales, transferencias, automatizadas) | informativos |

Los valores se cachean 5 minutos. Use *Refrescar* para recalcular.

**Advertencia de lectura.** Estos indicadores miden **completitud documental**, no cumplimiento sustantivo. Un IND-02 del 100 % significa que toda fila tiene algo escrito en el campo de base de licitud, no que esa base sea correcta. La validación jurídica la hace el DPD fila por fila; el indicador solo detecta lo que falta, no lo que está mal.

---

## 8. Bitácora de auditoría

Menú **Auditoría**. Registra:

- Ingresos, intentos fallidos (con bloqueo tras 5 intentos) y cierres de sesión.
- Creación, modificación (con el detalle antes/después de cada campo), eliminación y restauración.
- Cambios de estado y **cambios de permisos o perfil**.
- Consultas de detalle y **exportaciones**, con el número de filas exportadas.
- Accesos denegados.

### Integridad verificable

Cada evento guarda `SHA-256(hash del evento anterior + contenido del evento actual)`. Alterar o borrar una fila directamente en la base de datos rompe la cadena. El botón **Verificar integridad** (o `manage.py verificar_bitacora`) recorre la cadena e informa el número del primer evento comprometido.

Esto es una propiedad fuerte y conviene entender su alcance real: **detecta** manipulación posterior, no la **impide**. Alguien con privilegios de administrador en el motor de base de datos puede borrar toda la tabla. Lo que no puede hacer es alterar un registro y que la verificación siga dando correcta. Para que la detección sirva, la verificación debe ejecutarse periódicamente y su resultado conservarse — el documento de instalación incluye la tarea programada.

### Sobre el volumen

No se audita cada carga de página: multiplicaría el volumen por 10–50 sin aportar evidencia útil. Se auditan las vistas de detalle, las exportaciones y toda escritura. La lectura masiva se controla en el punto donde existe riesgo real de fuga: la exportación.

### Retención

Por defecto 7 años (2555 días), alineado con la conservación contable. El comando `purgar_bitacora` exporta a CSV con hash SHA-256 antes de eliminar, y registra la purga. **La cadena hash se reinicia tras cada purga**: conserve el archivo CSV como evidencia del tramo eliminado.

---

## 9. Por qué no todo está cifrado

Esta pregunta aparece en toda auditoría, conviene tener la respuesta documentada.

**Está cifrado con AES-256-GCM:** nombres, apellidos, correo, documento y teléfono de los usuarios del sistema; contacto de terceros; entrevistados y respuestas de entrevistas; observaciones y detalle de medidas de seguridad de las actividades; contenido de documentos generados; **detalle de la bitácora**.

**No está cifrado:** código y nombre de la actividad, área, estado, fechas, tipo de acción de bitácora, nombre del usuario que actúa.

El motivo es técnico y no negociable. El cifrado seguro usa un valor aleatorio por operación, de modo que el mismo texto produce un resultado distinto en cada fila. Consecuencia: sobre un campo cifrado el motor de base de datos **no puede** filtrar por igualdad, buscar por coincidencia parcial, ordenar ni agrupar. Si se cifrara `estado`, calcular el IND-01 exigiría traer toda la tabla a memoria y descifrar cada fila.

El criterio aplicado es de **clasificación**: se cifra lo que es dato personal de una persona identificable; se deja indexado lo que es metadato de tratamiento. Una fila que dice «Suscripción evalúa capacidad de pago, base Art. 7 núm. 5, conserva 6 años» no identifica a nadie.

Para los campos cifrados donde sí se necesita búsqueda exacta (correo, documento de usuarios) existe un **índice ciego**: un valor derivado determinista almacenado en columna indexada. Permite `buscar por correo exacto` a velocidad de índice; **no** permite búsqueda parcial. Por eso la pantalla de usuarios avisa que la búsqueda por correo o documento debe ser exacta.

Si intenta un filtro imposible desde código, el sistema devuelve un error explicativo en lugar de cero resultados silenciosos.

---

## 10. Plantillas

Menú **Plantillas**. Once plantillas base cubren cuestionarios por área, EIPD, test de ponderación, acta de entrevista, cláusulas de encargo, notificación de vulneración, aviso de privacidad y ficha para el Registro Nacional.

- **Clonar** antes de modificar una plantilla base: conserva el original.
- El cuerpo admite variables `{{ actividad }}`, `{{ area }}`, `{{ usuario }}`, `{{ fecha }}`, `{{ organizacion }}`.
- **Vista previa** valida la sintaxis contra una actividad real antes de publicar.
- El campo *esquema de campos* permite declarar formularios adicionales sin programar.

El renderizado se ejecuta en un motor aislado, sin acceso a funciones del sistema: una plantilla es contenido editable, no código de confianza.

---

## 11. Rutinas periódicas

| Frecuencia | Tarea | Responsable |
|---|---|---|
| Diaria | Revisar accesos denegados e intentos fallidos en bitácora | Administrador |
| Semanal | Revisar brechas vencidas (tablero) | DPD |
| Mensual | Verificar integridad de la bitácora y archivar el resultado | Auditoría Interna |
| Mensual | Revisar actividades sin campo 3.9 o 3.14 evaluado (IND-06) | DPD |
| Trimestral | Revisar vencimientos de contratos de encargados | DPD / Legal |
| Anual | Revisión integral del RAT; cada dueño de proceso certifica sus filas | DPD + dueños de proceso |
| Anual | Revisar perfiles y permisos; retirar accesos de personal desvinculado | Administrador |
| Ante cambio | Nuevo producto, sistema, proveedor o país de alojamiento: notificar al DPD **antes** de iniciar | Dueño de proceso |

La última fila es la que sostiene todo lo demás. El procedimiento lo formula como «nada nuevo sin RAT»: la EIPD es previa (Art. 42) y el reporte al Registro Nacional vence a los 10 días del inicio del tratamiento (Art. 86 RLOPDP). Un control que se activa después del despliegue llega tarde por definición.

---

## 12. Preguntas frecuentes

**¿Dos áreas usan los mismos datos, es una fila o dos?**
Depende de la finalidad. Si emisión y marketing usan los mismos datos de cliente, son **dos** actividades: distinta base legal, distinto plazo, distintos destinatarios.

**¿El corredor de seguros es encargado o destinatario?**
Normalmente ninguno de los dos: es responsable independiente de su propio tratamiento. Encargado solo si trata por cuenta y bajo instrucciones de la compañía. El criterio es quién decide la finalidad.

**¿El reasegurador es corresponsable?**
No, salvo pacto expreso de decisión conjunta. Es destinatario, y casi siempre implica transferencia internacional.

**Busqué un usuario por correo y no aparece.**
La búsqueda por correo es exacta (campo cifrado). Verifique la dirección completa o busque por nombre de usuario, que sí admite coincidencia parcial.

**Un registro desapareció del listado.**
Fue dado de baja lógicamente. Sigue en la base; el administrador puede restaurarlo. La baja quedó en bitácora con autor y fecha.

**No puedo publicar una actividad como Vigente.**
Revise: transición no permitida desde el estado actual, EIPD requerida sin código de informe, o falta de país/mecanismo si declaró transferencia internacional. El mensaje de error indica el campo.

**¿Puedo dar a un usuario permisos de solo lectura sin hacerlo Auditor?**
Sí, y es lo recomendado: cree un perfil personalizado con permisos `view_`. El perfil Auditor incluye acceso a la bitácora completa, que no todo lector necesita.

---

## 13. Contacto y escalamiento

| Situación | A quién |
|---|---|
| Duda sobre base de licitud, plazo o transferencia | Delegado de Protección de Datos |
| Fallo de la aplicación, error de acceso | Administrador del sistema / TI |
| **Ruptura detectada en la cadena de la bitácora** | DPD **y** Seguridad de la Información, de inmediato |
| Vulneración de seguridad con datos personales | DPD — recuerde los términos: 5 días a la Autoridad (Art. 43), 3 días al titular cuando exista riesgo (Art. 46), 2 días del encargado al responsable |

---

*Documento de referencia interna. Las citas normativas corresponden a la LOPDP (2021) y su Reglamento General (Decreto 904, 2023). La SPDP emite normativa complementaria de forma continua: verifique resoluciones vigentes en spdp.gob.ec antes de cada revisión anual.*
