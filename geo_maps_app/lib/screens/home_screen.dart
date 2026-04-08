import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/location_model.dart';
import '../providers/location_provider.dart';
import '../widgets/map_widget.dart';
import '../widgets/location_info_card.dart';
import '../widgets/map_controls_widget.dart';
import '../widgets/permission_error_widget.dart';

/// Pantalla principal de la aplicación.
/// Contiene el mapa, la tarjeta de información y los controles.
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Consumer<LocationProvider>(
        builder: (context, provider, _) {
          // ── Manejo de errores de permisos ──────────────────
          if (provider.status == LocationStatus.permissionDenied ||
              provider.status == LocationStatus.permissionPermanentlyDenied ||
              provider.status == LocationStatus.serviceDisabled) {
            return PermissionErrorWidget(
              status: provider.status,
              message: provider.errorMessage ?? '',
              onOpenSettings: provider.status ==
                      LocationStatus.permissionPermanentlyDenied
                  ? provider.openAppSettings
                  : provider.status == LocationStatus.serviceDisabled
                      ? provider.openLocationSettings
                      : provider.retryInitialization,
              onRetry: provider.retryInitialization,
            );
          }

          // ── Pantalla principal con mapa ─────────────────────
          return Stack(
            children: [
              // Mapa de Google (fondo completo)
              const MapWidget(),

              // AppBar transparente flotante
              _buildTransparentAppBar(context, provider),

              // Tarjeta de información en la parte inferior
              Positioned(
                left: 0,
                right: 0,
                bottom: 0,
                child: LocationInfoCard(provider: provider),
              ),

              // Controles del mapa (derecha)
              Positioned(
                right: 16,
                bottom: 220,
                child: MapControlsWidget(provider: provider),
              ),

              // Indicador de carga inicial
              if (provider.status == LocationStatus.loading)
                const _LoadingOverlay(),
            ],
          );
        },
      ),
    );
  }

  Widget _buildTransparentAppBar(
      BuildContext context, LocationProvider provider) {
    return Positioned(
      top: 0,
      left: 0,
      right: 0,
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Row(
            children: [
              // Logo / título
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(14),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.12),
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.location_on_rounded,
                      color: Theme.of(context).colorScheme.primary,
                      size: 20,
                    ),
                    const SizedBox(width: 6),
                    const Text(
                      'GeoMaps',
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        fontSize: 16,
                        letterSpacing: -0.3,
                      ),
                    ),
                  ],
                ),
              ),

              const Spacer(),

              // Botón de tipo de mapa
              _AppBarButton(
                icon: provider.mapType.name == 'satellite'
                    ? Icons.map_rounded
                    : Icons.satellite_alt_rounded,
                tooltip: 'Cambiar tipo de mapa',
                onTap: provider.toggleMapType,
              ),

              const SizedBox(width: 8),

              // Botón tracking activo/inactivo
              _AppBarButton(
                icon: provider.isTracking
                    ? Icons.gps_fixed_rounded
                    : Icons.gps_not_fixed_rounded,
                tooltip: provider.isTracking
                    ? 'Detener seguimiento'
                    : 'Activar seguimiento',
                color: provider.isTracking ? Colors.green : null,
                onTap: provider.isTracking
                    ? provider.stopTracking
                    : provider.resumeTracking,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _AppBarButton extends StatelessWidget {
  final IconData icon;
  final String tooltip;
  final VoidCallback onTap;
  final Color? color;

  const _AppBarButton({
    required this.icon,
    required this.tooltip,
    required this.onTap,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(14),
      elevation: 2,
      shadowColor: Colors.black.withOpacity(0.12),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: onTap,
        child: Tooltip(
          message: tooltip,
          child: Padding(
            padding: const EdgeInsets.all(10),
            child: Icon(icon, size: 22, color: color),
          ),
        ),
      ),
    );
  }
}

class _LoadingOverlay extends StatelessWidget {
  const _LoadingOverlay();

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.black.withOpacity(0.3),
      child: const Center(
        child: Card(
          child: Padding(
            padding: EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                CircularProgressIndicator(),
                SizedBox(height: 16),
                Text('Obteniendo ubicación...'),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
