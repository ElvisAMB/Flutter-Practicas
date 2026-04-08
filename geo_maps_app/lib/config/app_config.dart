import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

/// Configuración centralizada de la aplicación.
/// Todas las constantes y claves de API se gestionan aquí.
class AppConfig {
  AppConfig._(); // Clase no instanciable

  // ── Clave de API ───────────────────────────────────────────
  static String get googleMapsApiKey {
    final key = dotenv.env['GOOGLE_MAPS_API_KEY'];
    assert(key != null && key.isNotEmpty,
        'GOOGLE_MAPS_API_KEY no está definida en el archivo .env');
    return key!;
  }

  // ── Mapa: posición inicial ─────────────────────────────────
  /// Quito, Ecuador como posición por defecto
  static const LatLng defaultLocation = LatLng(-0.2201641, -78.5123274);
  static const double defaultZoom = 14.0;
  static const double streetZoom = 17.0;
  static const double countryZoom = 6.0;

  // ── Geolocalización ────────────────────────────────────────
  /// Intervalo de actualización de ubicación en ms
  static const int locationUpdateIntervalMs = 5000;

  /// Distancia mínima en metros para actualizar
  static const double locationDistanceFilter = 10.0;

  /// Tiempo de espera para obtener ubicación
  static const Duration locationTimeout = Duration(seconds: 15);

  // ── Geocoding ──────────────────────────────────────────────
  static const int geocodingResultsLimit = 1;

  // ── UI ─────────────────────────────────────────────────────
  static const Duration splashDuration = Duration(seconds: 2);
  static const Duration snackBarDuration = Duration(seconds: 3);
  static const double cardBorderRadius = 16.0;
  static const double markerInfoWindowMaxWidth = 250.0;
}
