import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';

import '../models/location_model.dart';
import '../providers/location_provider.dart';
import '../theme/app_theme.dart';

/// Tarjeta inferior que muestra la información de ubicación actual:
/// coordenadas, dirección, altitud, velocidad y precisión.
class LocationInfoCard extends StatelessWidget {
  final LocationProvider provider;

  const LocationInfoCard({super.key, required this.provider});

  @override
  Widget build(BuildContext context) {
    final location = provider.currentLocation;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      decoration: BoxDecoration(
        color: isDark ? AppTheme.cardDark : Colors.white,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
        boxShadow: [
          BoxShadow(
            // ignore: deprecated_member_use
            color: Colors.black.withOpacity(0.12),
            blurRadius: 20,
            offset: const Offset(0, -4),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Handle visual
          Container(
            margin: const EdgeInsets.only(top: 12),
            width: 36,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.grey.shade300,
              borderRadius: BorderRadius.circular(2),
            ),
          ),

          Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
            child: location == null
                ? _buildLoadingState()
                : _buildLocationData(context, location),
          ),
        ],
      ),
    );
  }

  Widget _buildLoadingState() {
    return const SizedBox(
      height: 80,
      child: Center(
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            SizedBox(
              width: 18,
              height: 18,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
            SizedBox(width: 12),
            Text('Obteniendo ubicación...', style: TextStyle(fontSize: 15)),
          ],
        ),
      ),
    );
  }

  Widget _buildLocationData(BuildContext context, LocationModel location) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Fila de estado y timestamp
        Row(
          children: [
            Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: provider.isTracking
                    // ignore: deprecated_member_use
                    ? AppTheme.accentColor.withOpacity(0.15)
                    // ignore: deprecated_member_use
                    : Colors.orange.withOpacity(0.15),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    provider.isTracking
                        ? Icons.radio_button_checked
                        : Icons.pause_circle_outline,
                    size: 12,
                    color: provider.isTracking
                        ? AppTheme.accentColor
                        : Colors.orange,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    provider.isTracking ? 'En vivo' : 'Pausado',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: provider.isTracking
                          ? AppTheme.accentColor
                          : Colors.orange,
                    ),
                  ),
                ],
              ),
            ),
            const Spacer(),
            Text(
              DateFormat('HH:mm:ss').format(location.timestamp),
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey.shade500,
              ),
            ),
          ],
        ),

        const SizedBox(height: 14),

        // Dirección
        Row(
          children: [
            const Icon(Icons.place_rounded, size: 18, color: AppTheme.primaryColor),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                location.shortAddress,
                style: const TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                  letterSpacing: -0.2,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),

        const SizedBox(height: 16),
        const Divider(height: 1),
        const SizedBox(height: 14),

        // Grid de datos: lat, lng, altitud, precisión, velocidad
        Row(
          children: [
            _DataTile(
              label: 'LATITUD',
              value: location.latitude.toStringAsFixed(6),
              icon: Icons.north_rounded,
              onCopy: () => _copyToClipboard(
                  context, location.latitude.toStringAsFixed(6)),
            ),
            const SizedBox(width: 12),
            _DataTile(
              label: 'LONGITUD',
              value: location.longitude.toStringAsFixed(6),
              icon: Icons.east_rounded,
              onCopy: () => _copyToClipboard(
                  context, location.longitude.toStringAsFixed(6)),
            ),
            const SizedBox(width: 12),
            _DataTile(
              label: 'ALTITUD',
              value: location.altitude != null
                  ? '${location.altitude!.toStringAsFixed(1)} m'
                  : 'N/A',
              icon: Icons.terrain_rounded,
            ),
          ],
        ),

        const SizedBox(height: 10),

        Row(
          children: [
            _DataTile(
              label: 'PRECISIÓN',
              value: location.accuracy != null
                  ? '±${location.accuracy!.toStringAsFixed(0)} m'
                  : 'N/A',
              icon: Icons.gps_fixed_rounded,
            ),
            const SizedBox(width: 12),
            _DataTile(
              label: 'VELOCIDAD',
              value: location.speedKmh != null
                  ? '${location.speedKmh!.toStringAsFixed(1)} km/h'
                  : '0.0 km/h',
              icon: Icons.speed_rounded,
            ),
            const SizedBox(width: 12),
            _DataTile(
              label: 'RUMBO',
              value: location.heading != null
                  ? '${location.heading!.toStringAsFixed(0)}°'
                  : 'N/A',
              icon: Icons.navigation_rounded,
            ),
          ],
        ),
      ],
    );
  }

  void _copyToClipboard(BuildContext context, String text) {
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Copiado: $text'),
        duration: const Duration(seconds: 2),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }
}

/// Tile individual de dato con etiqueta, valor e ícono.
class _DataTile extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final VoidCallback? onCopy;

  const _DataTile({
    required this.label,
    required this.value,
    required this.icon,
    this.onCopy,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Expanded(
      child: GestureDetector(
        onLongPress: onCopy,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
          decoration: BoxDecoration(
            color: isDark
                // ignore: deprecated_member_use
                ? Colors.white.withOpacity(0.07)
                : const Color(0xFFF1F3F4),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(icon, size: 12, color: AppTheme.primaryColor),
                  const SizedBox(width: 4),
                  Text(
                    label,
                    style: TextStyle(
                      fontSize: 9,
                      fontWeight: FontWeight.w700,
                      color: Colors.grey.shade500,
                      letterSpacing: 0.5,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Text(
                value,
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  letterSpacing: -0.2,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
