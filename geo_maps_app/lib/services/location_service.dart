import 'dart:async';
import 'package:geolocator/geolocator.dart';

import '../config/app_config.dart';
import '../models/location_model.dart';

/// Resultado de la solicitud de permisos de ubicación
enum PermissionResult {
  granted,
  denied,
  permanentlyDenied,
  serviceDisabled,
}

/// Servicio que encapsula toda la lógica de geolocalización.
/// Utiliza el paquete [geolocator] para acceder al GPS del dispositivo.
class LocationService {
  LocationService._();
  static final LocationService instance = LocationService._();

  StreamSubscription<Position>? _positionSubscription;
  final StreamController<Position> _positionController =
      StreamController<Position>.broadcast();

  Stream<Position> get positionStream => _positionController.stream;

  // ── Permisos ───────────────────────────────────────────────

  /// Verifica y solicita todos los permisos necesarios.
  /// Retorna el resultado del proceso de permisos.
  Future<PermissionResult> requestPermissions() async {
    // 1. Verificar si el servicio de ubicación está activo
    final serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      return PermissionResult.serviceDisabled;
    }

    // 2. Verificar permisos actuales
    LocationPermission permission = await Geolocator.checkPermission();

    // 3. Solicitar si están denegados
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        return PermissionResult.denied;
      }
    }

    // 4. Si están denegados permanentemente, redirigir a ajustes
    if (permission == LocationPermission.deniedForever) {
      return PermissionResult.permanentlyDenied;
    }

    return PermissionResult.granted;
  }

  /// Abre la configuración del sistema para que el usuario
  /// pueda habilitar los permisos manualmente.
  Future<void> openAppSettings() => Geolocator.openAppSettings();

  /// Abre la configuración de ubicación del sistema.
  Future<void> openLocationSettings() =>
      Geolocator.openLocationSettings();

  // ── Obtener posición ───────────────────────────────────────

  /// Obtiene la posición actual del dispositivo (una sola vez).
  Future<Position?> getCurrentPosition() async {
    try {
      return await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
        timeLimit: AppConfig.locationTimeout,
      );
    } on TimeoutException {
      // Intentar con la última posición conocida como fallback
      return Geolocator.getLastKnownPosition();
    } catch (_) {
      return null;
    }
  }

  // ── Tracking en tiempo real ────────────────────────────────

  /// Inicia el tracking continuo de ubicación.
  /// Los cambios se emiten a través de [positionStream].
  void startTracking() {
    _positionSubscription?.cancel();

    const locationSettings = LocationSettings(
      accuracy: LocationAccuracy.high,
      distanceFilter: 10, // metros mínimos para actualizar
    );

    _positionSubscription =
        Geolocator.getPositionStream(locationSettings: locationSettings)
            .listen(
      (position) => _positionController.add(position),
      onError: (error) => _positionController.addError(error),
    );
  }

  /// Detiene el tracking continuo.
  void stopTracking() {
    _positionSubscription?.cancel();
    _positionSubscription = null;
  }

  // ── Utilidades ─────────────────────────────────────────────

  /// Calcula la distancia en metros entre dos posiciones.
  double distanceBetween({
    required double startLat,
    required double startLng,
    required double endLat,
    required double endLng,
  }) {
    return Geolocator.distanceBetween(startLat, startLng, endLat, endLng);
  }

  /// Convierte un [Position] al modelo interno [LocationModel].
  LocationModel positionToModel(Position position) {
    return LocationModel(
      latitude: position.latitude,
      longitude: position.longitude,
      altitude: position.altitude,
      accuracy: position.accuracy,
      speed: position.speed,
      heading: position.heading,
      timestamp: position.timestamp,
    );
  }

  void dispose() {
    stopTracking();
    _positionController.close();
  }
}
