/// Todas las cadenas de texto de la app centralizadas.
/// Facilita la futura internacionalización (i18n).
class AppStrings {
  AppStrings._();

  // ── App ────────────────────────────────────────────────────
  static const String appName = 'GeoMaps';
  static const String appTagline = 'Tu ubicación en tiempo real';

  // ── Splash ─────────────────────────────────────────────────
  static const String splashLoading = 'Inicializando...';

  // ── Permisos ───────────────────────────────────────────────
  static const String permissionRequired = 'Permiso de ubicación requerido';
  static const String permissionDenied =
      'Permiso de ubicación denegado. Por favor, habilítalo para usar la app.';
  static const String permissionPermanentlyDenied =
      'Permiso de ubicación denegado permanentemente. '
      'Ve a Ajustes > Permisos para habilitarlo.';
  static const String serviceDisabled =
      'El servicio de ubicación está desactivado. '
      'Actívalo en los ajustes del sistema.';
  static const String openSettings = 'Abrir ajustes';
  static const String allowPermission = 'Permitir';
  static const String retry = 'Reintentar';

  // ── Mapa ───────────────────────────────────────────────────
  static const String myLocation = 'Mi ubicación';
  static const String customMarker = 'Marcador';
  static const String markerAdded = 'Marcador añadido';
  static const String markersCleared = 'Marcadores eliminados';
  static const String centerOnMe = 'Centrar en mi ubicación';
  static const String changeMapType = 'Cambiar tipo de mapa';
  static const String clearMarkers = 'Limpiar marcadores';

  // ── Tipos de mapa ──────────────────────────────────────────
  static const String mapNormal = 'Normal';
  static const String mapSatellite = 'Satélite';
  static const String mapTerrain = 'Terreno';
  static const String mapHybrid = 'Híbrido';

  // ── Info card ──────────────────────────────────────────────
  static const String latitude = 'LATITUD';
  static const String longitude = 'LONGITUD';
  static const String altitude = 'ALTITUD';
  static const String accuracy = 'PRECISIÓN';
  static const String speed = 'VELOCIDAD';
  static const String heading = 'RUMBO';
  static const String address = 'Dirección';
  static const String unknownAddress = 'Dirección desconocida';
  static const String fetchingLocation = 'Obteniendo ubicación...';

  // ── Estado ─────────────────────────────────────────────────
  static const String trackingLive = 'En vivo';
  static const String trackingPaused = 'Pausado';
  static const String copiedToClipboard = 'Copiado';

  // ── Errores ────────────────────────────────────────────────
  static const String errorLocation = 'No se pudo obtener la ubicación.';
  static const String errorTracking =
      'Error al recibir actualizaciones de ubicación.';
  static const String errorGeneric = 'Ocurrió un error inesperado.';

  // ── Unidades ───────────────────────────────────────────────
  static const String unitMeters = 'm';
  static const String unitKilometers = 'km';
  static const String unitKmh = 'km/h';
  static const String unitDegrees = '°';
  static const String unitNotAvailable = 'N/A';
}
