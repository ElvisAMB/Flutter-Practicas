import 'dart:math' as math;
import 'package:google_maps_flutter/google_maps_flutter.dart';

/// Colección de funciones utilitarias para cálculos geográficos y de mapa.
class MapUtils {
  MapUtils._();

  // ── Coordenadas ────────────────────────────────────────────

  /// Formatea coordenadas en notación DMS (grados, minutos, segundos).
  /// Ejemplo: 0°13'12.59"S, 78°30'44.38"W
  static String toDMS(double latitude, double longitude) {
    return '${_coordToDMS(latitude, isLatitude: true)}, '
        '${_coordToDMS(longitude, isLatitude: false)}';
  }

  static String _coordToDMS(double decimal, {required bool isLatitude}) {
    final direction = isLatitude
        ? (decimal >= 0 ? 'N' : 'S')
        : (decimal >= 0 ? 'E' : 'W');
    final abs = decimal.abs();
    final degrees = abs.floor();
    final minutesDecimal = (abs - degrees) * 60;
    final minutes = minutesDecimal.floor();
    final seconds = (minutesDecimal - minutes) * 60;
    return "$degrees°${minutes.toString().padLeft(2, '0')}'${seconds.toStringAsFixed(2)}\"$direction";
  }

  /// Calcula el bounding box que contiene todos los puntos dados.
  /// Útil para ajustar la cámara a una colección de marcadores.
  static LatLngBounds boundsFromLatLngList(List<LatLng> points) {
    assert(points.isNotEmpty, 'La lista de puntos no puede estar vacía');

    double minLat = points.first.latitude;
    double maxLat = points.first.latitude;
    double minLng = points.first.longitude;
    double maxLng = points.first.longitude;

    for (final p in points) {
      if (p.latitude < minLat) minLat = p.latitude;
      if (p.latitude > maxLat) maxLat = p.latitude;
      if (p.longitude < minLng) minLng = p.longitude;
      if (p.longitude > maxLng) maxLng = p.longitude;
    }

    return LatLngBounds(
      southwest: LatLng(minLat, minLng),
      northeast: LatLng(maxLat, maxLng),
    );
  }

  /// Calcula el centro geográfico de una lista de puntos.
  static LatLng centerOfPoints(List<LatLng> points) {
    assert(points.isNotEmpty, 'La lista de puntos no puede estar vacía');

    double x = 0, y = 0, z = 0;

    for (final p in points) {
      final lat = p.latitude * math.pi / 180;
      final lng = p.longitude * math.pi / 180;
      x += math.cos(lat) * math.cos(lng);
      y += math.cos(lat) * math.sin(lng);
      z += math.sin(lat);
    }

    final n = points.length;
    x /= n;
    y /= n;
    z /= n;

    final centerLng = math.atan2(y, x) * 180 / math.pi;
    final hyp = math.sqrt(x * x + y * y);
    final centerLat = math.atan2(z, hyp) * 180 / math.pi;

    return LatLng(centerLat, centerLng);
  }

  // ── Distancias ─────────────────────────────────────────────

  /// Distancia haversine entre dos puntos (metros).
  static double haversineDistance(LatLng a, LatLng b) {
    const r = 6371000.0; // Radio de la Tierra en metros
    final dLat = _toRadians(b.latitude - a.latitude);
    final dLng = _toRadians(b.longitude - a.longitude);
    final sinDLat = math.sin(dLat / 2);
    final sinDLng = math.sin(dLng / 2);

    final h = sinDLat * sinDLat +
        math.cos(_toRadians(a.latitude)) *
            math.cos(_toRadians(b.latitude)) *
            sinDLng *
            sinDLng;

    return 2 * r * math.asin(math.sqrt(h));
  }

  static double _toRadians(double degrees) => degrees * math.pi / 180;

  /// Formatea una distancia en metros de forma legible.
  static String formatDistance(double meters) {
    if (meters < 1000) {
      return '${meters.toStringAsFixed(0)} m';
    } else {
      return '${(meters / 1000).toStringAsFixed(2)} km';
    }
  }

  // ── Zoom ───────────────────────────────────────────────────

  /// Calcula el nivel de zoom apropiado dado un radio en metros.
  static double zoomLevelForRadius(double radiusMeters) {
    // Aproximación logarítmica
    final zoom = 16 - math.log(radiusMeters / 500) / math.log(2);
    return zoom.clamp(1.0, 20.0);
  }

  /// Convierte el nivel de zoom a una descripción textual.
  static String zoomDescription(double zoom) {
    if (zoom < 4) return 'Mundo';
    if (zoom < 7) return 'Continente';
    if (zoom < 10) return 'País';
    if (zoom < 13) return 'Ciudad';
    if (zoom < 16) return 'Barrio';
    return 'Calle';
  }
}
