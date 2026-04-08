import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:provider/provider.dart';

import '../config/app_config.dart';
import '../providers/location_provider.dart';

/// Widget principal del mapa de Google Maps.
/// Gestiona la cámara, los marcadores y la interacción del usuario.
class MapWidget extends StatelessWidget {
  const MapWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<LocationProvider>(
      builder: (context, provider, _) {
        return GoogleMap(
          // ── Posición inicial de la cámara ──────────────────
          initialCameraPosition: CameraPosition(
            target: provider.cameraPosition,
            zoom: AppConfig.defaultZoom,
          ),

          // ── Configuración del mapa ─────────────────────────
          mapType: provider.mapType,
          myLocationEnabled: false, // Usamos marcador personalizado
          myLocationButtonEnabled: false,
          zoomControlsEnabled: false,
          compassEnabled: true,
          rotateGesturesEnabled: true,
          scrollGesturesEnabled: true,
          tiltGesturesEnabled: true,
          zoomGesturesEnabled: true,
          trafficEnabled: false,
          buildingsEnabled: true,
          indoorViewEnabled: false,

          // ── Marcadores ─────────────────────────────────────
          markers: provider.markers,

          // ── Callbacks ──────────────────────────────────────
          onMapCreated: provider.onMapCreated,
          onCameraMove: provider.onCameraMove,

          // Al tocar el mapa, agregar marcador personalizado
          onLongPress: (LatLng position) {
            provider.addCustomMarker(position: position);
            _showMarkerSnackBar(context, position);
          },

          // ── Padding para que la UI no tape el mapa ─────────
          padding: const EdgeInsets.only(
            top: 100,   // Deja espacio para el AppBar flotante
            bottom: 220, // Deja espacio para la tarjeta inferior
          ),
        );
      },
    );
  }

  void _showMarkerSnackBar(BuildContext context, LatLng position) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'Marcador añadido: ${position.latitude.toStringAsFixed(5)}, '
          '${position.longitude.toStringAsFixed(5)}',
        ),
        action: SnackBarAction(
          label: 'OK',
          onPressed: () =>
              ScaffoldMessenger.of(context).hideCurrentSnackBar(),
        ),
        duration: AppConfig.snackBarDuration,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }
}
