import 'package:flutter_test/flutter_test.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

import 'package:geo_maps_app/models/location_model.dart';
import 'package:geo_maps_app/utils/map_utils.dart';

void main() {
  // ── LocationModel Tests ──────────────────────────────────
  group('LocationModel', () {
    late LocationModel model;

    setUp(() {
      model = LocationModel(
        latitude: -0.2201641,
        longitude: -78.5123274,
        altitude: 2850.0,
        accuracy: 5.0,
        speed: 1.389, // ~5 km/h
        heading: 90.0,
        timestamp: DateTime(2024, 6, 1, 12, 0, 0),
        street: 'Av. Amazonas',
        city: 'Quito',
        country: 'Ecuador',
        postalCode: '170150',
      );
    });

    test('latLng retorna LatLng correcto', () {
      expect(model.latLng, equals(const LatLng(-0.2201641, -78.5123274)));
    });

    test('speedKmh convierte m/s a km/h correctamente', () {
      expect(model.speedKmh, closeTo(5.0, 0.1));
    });

    test('shortAddress devuelve calle y ciudad', () {
      expect(model.shortAddress, 'Av. Amazonas, Quito');
    });

    test('shortAddress usa ciudad si no hay calle', () {
      final m = model.copyWith(street: '');
      expect(m.shortAddress, 'Quito');
    });

    test('formattedCoordinates tiene 6 decimales', () {
      expect(model.formattedCoordinates, '-0.220164, -78.512327');
    });

    test('copyWith preserva campos no modificados', () {
      final copy = model.copyWith(speed: 2.778);
      expect(copy.latitude, model.latitude);
      expect(copy.city, model.city);
      expect(copy.speedKmh, closeTo(10.0, 0.1));
    });

    test('modelo sin ciudad usa dirección como fallback', () {
      final m = LocationModel(
        latitude: 0,
        longitude: 0,
        timestamp: DateTime.now(),
        address: 'Calle desconocida',
      );
      expect(m.shortAddress, 'Calle desconocida');
    });

    test('modelo sin ninguna dirección retorna mensaje por defecto', () {
      final m = LocationModel(
        latitude: 0,
        longitude: 0,
        timestamp: DateTime.now(),
      );
      expect(m.shortAddress, 'Dirección desconocida');
    });
  });

  // ── MapUtils Tests ───────────────────────────────────────
  group('MapUtils', () {
    test('haversineDistance entre puntos idénticos es 0', () {
      const p = LatLng(-0.22, -78.51);
      expect(MapUtils.haversineDistance(p, p), closeTo(0.0, 0.001));
    });

    test('haversineDistance entre Quito y Guayaquil ~270 km', () {
      const quito = LatLng(-0.2295, -78.5243);
      const guayaquil = LatLng(-2.1710, -79.9224);
      final dist = MapUtils.haversineDistance(quito, guayaquil);
      // Distancia aérea real ≈ 262 km
      expect(dist / 1000, inInclusiveRange(250.0, 280.0));
    });

    test('formatDistance muestra metros cuando < 1000', () {
      expect(MapUtils.formatDistance(500), '500 m');
    });

    test('formatDistance muestra km cuando >= 1000', () {
      expect(MapUtils.formatDistance(1500), '1.50 km');
    });

    test('centerOfPoints calcula el centro correcto para dos puntos', () {
      final points = [
        const LatLng(0.0, 0.0),
        const LatLng(2.0, 2.0),
      ];
      final center = MapUtils.centerOfPoints(points);
      expect(center.latitude, closeTo(1.0, 0.01));
      expect(center.longitude, closeTo(1.0, 0.01));
    });

    test('boundsFromLatLngList retorna el bounding box correcto', () {
      final points = [
        const LatLng(-1.0, -79.0),
        const LatLng(1.0, -77.0),
        const LatLng(0.0, -78.0),
      ];
      final bounds = MapUtils.boundsFromLatLngList(points);
      expect(bounds.southwest.latitude, -1.0);
      expect(bounds.northeast.latitude, 1.0);
      expect(bounds.southwest.longitude, -79.0);
      expect(bounds.northeast.longitude, -77.0);
    });

    test('zoomDescription retorna nivel correcto', () {
      expect(MapUtils.zoomDescription(5), 'Continente');
      expect(MapUtils.zoomDescription(11), 'Ciudad');
      expect(MapUtils.zoomDescription(17), 'Calle');
    });

    test('toDMS convierte coordenadas a formato grados-minutos-segundos', () {
      final dms = MapUtils.toDMS(-0.2201641, -78.5123274);
      expect(dms, contains('S'));
      expect(dms, contains('W'));
      expect(dms, contains('°'));
    });

    test('zoomLevelForRadius está dentro del rango válido', () {
      for (final radius in [100.0, 500.0, 1000.0, 10000.0, 100000.0]) {
        final zoom = MapUtils.zoomLevelForRadius(radius);
        expect(zoom, inInclusiveRange(1.0, 20.0));
      }
    });
  });

  // ── LocationStatus Tests ─────────────────────────────────
  group('LocationStatus', () {
    test('todos los estados están definidos', () {
      expect(LocationStatus.values.length, 7);
      expect(LocationStatus.values, contains(LocationStatus.initial));
      expect(LocationStatus.values, contains(LocationStatus.loading));
      expect(LocationStatus.values, contains(LocationStatus.success));
      expect(LocationStatus.values, contains(LocationStatus.error));
    });
  });
}
