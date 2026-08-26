"""
apps/indicadores/services.py
============================
Cálculo de los indicadores del §10 del procedimiento (Art. 36 RLOPDP, prueba
de medidas).

Todos los cálculos se resuelven con agregaciones SQL sobre columnas **no
cifradas** e indexadas. Esa es la razón de fondo por la que la clasificación de
datos importa: si ``estado`` o ``datos_especiales`` estuvieran cifrados,
cada indicador exigiría traer la tabla entera a memoria.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta

from django.core.cache import cache
from django.db.models import Count, Q
from django.utils import timezone

from apps.catalogos.models import Tercero
from apps.rat.models import ActividadTratamiento, Brecha, EstadoRegistro, SiNo

CACHE_TTL = 300  # 5 minutos: los indicadores no requieren tiempo real


@dataclass
class Indicador:
    codigo: str
    nombre: str
    valor: float
    unidad: str = "%"
    meta: float | None = None
    detalle: str = ""
    tendencia: str = ""

    @property
    def cumple(self) -> bool | None:
        if self.meta is None:
            return None
        return self.valor >= self.meta

    @property
    def semaforo(self) -> str:
        if self.meta is None:
            return "neutro"
        if self.valor >= self.meta:
            return "verde"
        if self.valor >= self.meta * 0.75:
            return "amarillo"
        return "rojo"


@dataclass
class TableroIndicadores:
    total_actividades: int = 0
    indicadores: list[Indicador] = field(default_factory=list)
    por_estado: dict = field(default_factory=dict)
    por_area: list = field(default_factory=list)
    por_riesgo: dict = field(default_factory=dict)
    brechas_abiertas: int = 0
    brechas_vencidas: int = 0


def _pct(parte: int, total: int) -> float:
    return round(parte * 100.0 / total, 1) if total else 0.0


def calcular(usar_cache: bool = True) -> TableroIndicadores:
    if usar_cache:
        cacheado = cache.get("tablero_indicadores")
        if cacheado:
            return cacheado

    qs = ActividadTratamiento.objects.all()
    total = qs.count()

    agregados = qs.aggregate(
        validadas=Count("id", filter=Q(estado__in=[
            EstadoRegistro.VALIDADO, EstadoRegistro.VIGENTE])),
        con_base=Count("id", filter=~Q(justificacion_base_licitud="")),
        especiales=Count("id", filter=Q(datos_especiales=SiNo.SI)),
        sin_evaluar_especiales=Count("id", filter=Q(datos_especiales=SiNo.NO_EVALUADO)),
        transferencias=Count("id", filter=Q(transferencia_internacional=SiNo.SI)),
        # Las claves NO deben coincidir con nombres de campo del modelo: Django
        # resolvería el filtro contra la anotación previa en lugar de la columna.
        n_eipd_requerida=Count("id", filter=Q(eipd_requerida=SiNo.SI)),
        n_eipd_pendiente=Count("id", filter=Q(eipd_requerida=SiNo.SI, eipd_codigo="")),
        automatizadas=Count("id", filter=Q(decision_automatizada=True)),
        reportadas=Count("id", filter=Q(reportada_registro_nacional=True)),
        vigentes=Count("id", filter=Q(estado=EstadoRegistro.VIGENTE)),
    )

    limite_anual = timezone.localdate() - timedelta(days=365)
    desactualizadas = qs.filter(
        Q(fecha_ultima_revision__lt=limite_anual) | Q(fecha_ultima_revision__isnull=True)
    ).count()

    encargados = Tercero.objects.filter(actividades_encargado__isnull=False).distinct()
    total_encargados = encargados.count()
    conformes = encargados.filter(
        tiene_contrato=True, clausula_confidencialidad=True, clausulas_art41_completas=True,
    ).count()

    indicadores = [
        Indicador("IND-01", "Tratamientos validados", _pct(agregados["validadas"], total),
                  meta=90, detalle=f"{agregados['validadas']} de {total}"),
        Indicador("IND-02", "Con base de licitud documentada", _pct(agregados["con_base"], total),
                  meta=100, detalle=f"{agregados['con_base']} de {total}"),
        Indicador("IND-03", "Encargados con contrato conforme (Art. 41 RLOPDP)",
                  _pct(conformes, total_encargados), meta=100,
                  detalle=f"{conformes} de {total_encargados} encargados"),
        Indicador("IND-04", "EIPD pendientes", agregados["n_eipd_pendiente"], unidad="reg.",
                  detalle=f"de {agregados['n_eipd_requerida']} que la requieren"),
        Indicador("IND-05", "Actualización dentro del año", _pct(total - desactualizadas, total),
                  meta=100, detalle=f"{desactualizadas} sin revisar hace más de 365 días"),
        Indicador("IND-06", "Campo 3.9 sin evaluar", agregados["sin_evaluar_especiales"],
                  unidad="reg.", detalle="El blanco no distingue «no aplica» de «no evaluado»"),
        Indicador("IND-07", "Vigentes reportadas al Registro Nacional",
                  _pct(agregados["reportadas"], agregados["vigentes"]), meta=100,
                  detalle="Término de 10 días desde el inicio (Art. 86 RLOPDP)"),
        Indicador("IND-08", "Actividades con categorías especiales",
                  _pct(agregados["especiales"], total), unidad="%",
                  detalle=f"{agregados['especiales']} actividades"),
        Indicador("IND-09", "Actividades con transferencia internacional",
                  _pct(agregados["transferencias"], total), unidad="%",
                  detalle=f"{agregados['transferencias']} actividades"),
        Indicador("IND-10", "Actividades con decisión automatizada",
                  agregados["automatizadas"], unidad="reg.",
                  detalle="Requieren EIPD previa (Art. 42 lit. a LOPDP)"),
    ]

    por_estado = dict(
        qs.values_list("estado").annotate(n=Count("id")).values_list("estado", "n")
    )
    por_area = list(
        qs.values("area__nombre").annotate(
            n=Count("id"),
            especiales=Count("id", filter=Q(datos_especiales=SiNo.SI)),
        ).order_by("-n")[:15]
    )

    por_riesgo = {"ALTO": 0, "MEDIO": 0, "BAJO": 0}
    for a in qs.only(
        "datos_especiales", "decision_automatizada", "transferencia_internacional",
        "menores", "gran_escala",
    ):
        por_riesgo[a.nivel_riesgo] += 1

    tablero = TableroIndicadores(
        total_actividades=total,
        indicadores=indicadores,
        por_estado=por_estado,
        por_area=por_area,
        por_riesgo=por_riesgo,
        brechas_abiertas=Brecha.objects.filter(
            estado__in=[Brecha.Estado.ABIERTA, Brecha.Estado.EN_PROCESO]).count(),
        brechas_vencidas=Brecha.objects.filter(
            estado__in=[Brecha.Estado.ABIERTA, Brecha.Estado.EN_PROCESO],
            fecha_compromiso__lt=timezone.localdate()).count(),
    )
    cache.set("tablero_indicadores", tablero, CACHE_TTL)
    return tablero


def invalidar_cache() -> None:
    cache.delete("tablero_indicadores")
