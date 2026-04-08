import 'package:geocoding/geocoding.dart';

/// Servicio de geocodificación inversa.
/// Convierte coordenadas GPS en direcciones legibles.
class GeocodingService {
  GeocodingService._();
  static final GeocodingService instance = GeocodingService._();

  /// Obtiene la dirección completa a partir de coordenadas.
  /// Retorna null si no se puede resolver la dirección.
  Future<Placemark?> getAddressFromCoordinates({
    required double latitude,
    required double longitude,
  }) async {
    try {
      final placemarks = await placemarkFromCoordinates(
        latitude,
        longitude,
        //localeIdentifier: 'es_EC', // Español Ecuador
      );

      if (placemarks.isNotEmpty) {
        return placemarks.first;
      }
      return null;
    } catch (e) {
      // Silenciar errores de red o de API
      return null;
    }
  }

  /// Construye una dirección formateada a partir de un [Placemark].
  String buildFormattedAddress(Placemark placemark) {
    final parts = <String>[];

    if (placemark.street?.isNotEmpty == true) {
      parts.add(placemark.street!);
    }
    if (placemark.subLocality?.isNotEmpty == true) {
      parts.add(placemark.subLocality!);
    }
    if (placemark.locality?.isNotEmpty == true) {
      parts.add(placemark.locality!);
    }
    if (placemark.administrativeArea?.isNotEmpty == true) {
      parts.add(placemark.administrativeArea!);
    }
    if (placemark.country?.isNotEmpty == true) {
      parts.add(placemark.country!);
    }

    return parts.isEmpty ? 'Dirección no disponible' : parts.join(', ');
  }

  /// Geocodificación directa: convierte un texto en coordenadas.
  Future<List<Location>> getCoordinatesFromAddress(String address) async {
    try {
      return await locationFromAddress(address);
    } catch (_) {
      return [];
    }
  }
}
