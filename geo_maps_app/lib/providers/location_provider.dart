import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:geolocator/geolocator.dart';
//import 'package:geocoding/geocoding.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

import '../config/app_config.dart';
import '../models/location_model.dart';
import '../services/location_service.dart';
import '../services/geocoding_service.dart';

/// Provider principal que gestiona todo el estado de ubicación y mapa.
/// Notifica a los widgets cuando cambia la ubicación o la configuración.
class LocationProvider extends ChangeNotifier {
  // ── Servicios ──────────────────────────────────────────────
  final _locationService = LocationService.instance;
  final _geocodingService = GeocodingService.instance;

  // ── Estado ─────────────────────────────────────────────────
  LocationStatus _status = LocationStatus.initial;
  LocationModel? _currentLocation;
  String? _errorMessage;
  bool _isTracking = false;
  bool _followUser = true;
  MapType _mapType = MapType.normal;
  double _currentZoom = AppConfig.defaultZoom;

  // Controlador del mapa de Google
  GoogleMapController? _mapController;

  // Marcadores en el mapa
  final Set<Marker> _markers = {};

  // Suscripción al stream de posición
  StreamSubscription<Position>? _positionSub;

  // ── Getters ────────────────────────────────────────────────
  LocationStatus get status => _status;
  LocationModel? get currentLocation => _currentLocation;
  String? get errorMessage => _errorMessage;
  bool get isTracking => _isTracking;
  bool get followUser => _followUser;
  MapType get mapType => _mapType;
  double get currentZoom => _currentZoom;
  Set<Marker> get markers => _markers;
  bool get hasLocation => _currentLocation != null;

  LatLng get cameraPosition =>
      _currentLocation?.latLng ?? AppConfig.defaultLocation;

  // ── Inicialización ─────────────────────────────────────────

  /// Inicializa el provider: pide permisos y obtiene la primera ubicación.
  Future<void> initialize() async {
    _setStatus(LocationStatus.loading);

    final result = await _locationService.requestPermissions();

    switch (result) {
      case PermissionResult.granted:
        await _fetchCurrentLocation();
        _startPositionStream();
        break;
      case PermissionResult.denied:
        _setStatus(LocationStatus.permissionDenied);
        _errorMessage = 'Permiso de ubicación denegado. '
            'Por favor, habilítalo para usar la app.';
        break;
      case PermissionResult.permanentlyDenied:
        _setStatus(LocationStatus.permissionPermanentlyDenied);
        _errorMessage = 'Permiso de ubicación denegado permanentemente. '
            'Ve a Ajustes > Permisos para habilitarlo.';
        break;
      case PermissionResult.serviceDisabled:
        _setStatus(LocationStatus.serviceDisabled);
        _errorMessage = 'El servicio de ubicación está desactivado. '
            'Actívalo en los ajustes del sistema.';
        break;
    }

    notifyListeners();
  }

  // ── Ubicación ──────────────────────────────────────────────

  Future<void> _fetchCurrentLocation() async {
    final position = await _locationService.getCurrentPosition();
    if (position != null) {
      await _updateLocationFromPosition(position);
    } else {
      _setStatus(LocationStatus.error);
      _errorMessage = 'No se pudo obtener la ubicación.';
    }
  }

  Future<void> _updateLocationFromPosition(Position position) async {
    LocationModel location = _locationService.positionToModel(position);

    // Geocodificación inversa para obtener la dirección
    final placemark = await _geocodingService.getAddressFromCoordinates(
      latitude: position.latitude,
      longitude: position.longitude,
    );

    if (placemark != null) {
      location = location.copyWith(
        address: _geocodingService.buildFormattedAddress(placemark),
        street: placemark.street,
        city: placemark.locality,
        country: placemark.country,
        postalCode: placemark.postalCode,
      );
    }

    _currentLocation = location;
    _setStatus(LocationStatus.success);
    _updateUserMarker(location);

    // Animar la cámara si está en modo seguimiento
    if (_followUser && _mapController != null) {
      await _animateCameraToLocation(location.latLng);
    }

    notifyListeners();
  }

  // ── Tracking en tiempo real ────────────────────────────────

  void _startPositionStream() {
    _locationService.startTracking();
    _isTracking = true;

    _positionSub = _locationService.positionStream.listen(
      (position) => _updateLocationFromPosition(position),
      onError: (_) {
        _setStatus(LocationStatus.error);
        _errorMessage = 'Error al recibir actualizaciones de ubicación.';
        notifyListeners();
      },
    );
  }

  void stopTracking() {
    _locationService.stopTracking();
    _positionSub?.cancel();
    _isTracking = false;
    notifyListeners();
  }

  void resumeTracking() {
    _startPositionStream();
    notifyListeners();
  }

  // ── Mapa ───────────────────────────────────────────────────

  void onMapCreated(GoogleMapController controller) {
    _mapController = controller;
    // Si ya tenemos ubicación, animar la cámara al crearla
    if (_currentLocation != null) {
      _animateCameraToLocation(_currentLocation!.latLng);
    }
  }

  Future<void> _animateCameraToLocation(LatLng target) async {
    await _mapController?.animateCamera(
      CameraUpdate.newCameraPosition(
        CameraPosition(target: target, zoom: _currentZoom),
      ),
    );
  }

  Future<void> centerOnUser() async {
    if (_currentLocation == null) return;
    _followUser = true;
    await _animateCameraToLocation(_currentLocation!.latLng);
    notifyListeners();
  }

  void onCameraMove(CameraPosition position) {
    _currentZoom = position.zoom;
    // Si el usuario mueve el mapa manualmente, desactivar seguimiento
    if (_followUser) {
      _followUser = false;
      notifyListeners();
    }
  }

  void toggleMapType() {
    _mapType = _mapType == MapType.normal ? MapType.satellite : MapType.normal;
    notifyListeners();
  }

  void changeMapType(MapType type) {
    _mapType = type;
    notifyListeners();
  }

  // ── Marcadores ─────────────────────────────────────────────

  void _updateUserMarker(LocationModel location) {
    // Remover marcador anterior del usuario
    _markers.removeWhere((m) => m.markerId.value == 'current_location');

    _markers.add(
      Marker(
        markerId: const MarkerId('current_location'),
        position: location.latLng,
        infoWindow: InfoWindow(
          title: 'Mi ubicación',
          snippet: location.shortAddress,
        ),
        icon: BitmapDescriptor.defaultMarkerWithHue(
          BitmapDescriptor.hueAzure,
        ),
      ),
    );
  }

  /// Agrega un marcador personalizado en el punto indicado.
  void addCustomMarker({required LatLng position, String? title}) {
    final id = 'marker_${DateTime.now().millisecondsSinceEpoch}';
    _markers.add(
      Marker(
        markerId: MarkerId(id),
        position: position,
        infoWindow: InfoWindow(
          title: title ?? 'Marcador',
          snippet: '${position.latitude.toStringAsFixed(5)}, '
              '${position.longitude.toStringAsFixed(5)}',
        ),
      ),
    );
    notifyListeners();
  }

  void clearCustomMarkers() {
    _markers.removeWhere((m) => m.markerId.value != 'current_location');
    notifyListeners();
  }

  // ── Permisos y ajustes ─────────────────────────────────────

  Future<void> openAppSettings() => _locationService.openAppSettings();
  Future<void> openLocationSettings() =>
      _locationService.openLocationSettings();

  Future<void> retryInitialization() => initialize();

  // ── Helpers privados ───────────────────────────────────────

  void _setStatus(LocationStatus status) {
    _status = status;
  }

  @override
  void dispose() {
    _positionSub?.cancel();
    _locationService.dispose();
    _mapController?.dispose();
    super.dispose();
  }
}
