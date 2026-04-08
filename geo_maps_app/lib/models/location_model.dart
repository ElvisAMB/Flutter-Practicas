import 'package:google_maps_flutter/google_maps_flutter.dart';

/// Estado del servicio de ubicación
enum LocationStatus {
  initial,
  loading,
  success,
  error,
  permissionDenied,
  permissionPermanentlyDenied,
  serviceDisabled,
}

/// Modelo principal de ubicación del dispositivo
class LocationModel {
  final double latitude;
  final double longitude;
  final double? altitude;
  final double? accuracy;   // metros
  final double? speed;      // m/s
  final double? heading;    // grados
  final DateTime timestamp;
  final String? address;
  final String? street;
  final String? city;
  final String? country;
  final String? postalCode;

  const LocationModel({
    required this.latitude,
    required this.longitude,
    this.altitude,
    this.accuracy,
    this.speed,
    this.heading,
    required this.timestamp,
    this.address,
    this.street,
    this.city,
    this.country,
    this.postalCode,
  });

  /// Convierte a LatLng de Google Maps
  LatLng get latLng => LatLng(latitude, longitude);

  /// Velocidad en km/h
  double? get speedKmh => speed != null ? speed! * 3.6 : null;

  /// Dirección formateada compacta
  String get shortAddress {
    if (street != null && city != null) return '$street, $city';
    if (city != null) return city!;
    if (address != null) return address!;
    return 'Dirección desconocida';
  }

  /// Coordenadas formateadas con precisión
  String get formattedCoordinates =>
      '${latitude.toStringAsFixed(6)}, ${longitude.toStringAsFixed(6)}';

  LocationModel copyWith({
    double? latitude,
    double? longitude,
    double? altitude,
    double? accuracy,
    double? speed,
    double? heading,
    DateTime? timestamp,
    String? address,
    String? street,
    String? city,
    String? country,
    String? postalCode,
  }) {
    return LocationModel(
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      altitude: altitude ?? this.altitude,
      accuracy: accuracy ?? this.accuracy,
      speed: speed ?? this.speed,
      heading: heading ?? this.heading,
      timestamp: timestamp ?? this.timestamp,
      address: address ?? this.address,
      street: street ?? this.street,
      city: city ?? this.city,
      country: country ?? this.country,
      postalCode: postalCode ?? this.postalCode,
    );
  }

  @override
  String toString() =>
      'LocationModel(lat: $latitude, lng: $longitude, city: $city)';
}

/// Modelo para un marcador personalizado en el mapa
class MapMarkerModel {
  final String id;
  final LatLng position;
  final String title;
  final String? snippet;
  final MarkerType type;
  final DateTime createdAt;

  const MapMarkerModel({
    required this.id,
    required this.position,
    required this.title,
    this.snippet,
    this.type = MarkerType.custom,
    required this.createdAt,
  });
}

enum MarkerType { currentLocation, custom, saved }
