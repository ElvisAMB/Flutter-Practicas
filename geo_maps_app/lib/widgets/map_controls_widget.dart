import 'package:flutter/material.dart';

import '../providers/location_provider.dart';
import '../theme/app_theme.dart';

/// Columna de botones de acción flotantes sobre el mapa:
/// centrar en usuario, limpiar marcadores, zoom in/out.
class MapControlsWidget extends StatelessWidget {
  final LocationProvider provider;

  const MapControlsWidget({super.key, required this.provider});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Centrar en usuario
        _MapFab(
          icon: provider.followUser
              ? Icons.my_location_rounded
              : Icons.location_searching_rounded,
          tooltip: 'Centrar en mi ubicación',
          color: provider.followUser ? AppTheme.primaryColor : null,
          onPressed: provider.centerOnUser,
        ),
        const SizedBox(height: 8),

        // Limpiar marcadores personalizados
        _MapFab(
          icon: Icons.layers_clear_rounded,
          tooltip: 'Limpiar marcadores',
          onPressed: provider.clearCustomMarkers,
        ),
        const SizedBox(height: 8),

        // Mapa normal vs satélite
        _MapFab(
          icon: Icons.layers_rounded,
          tooltip: 'Cambiar tipo de mapa',
          onPressed: provider.toggleMapType,
        ),
      ],
    );
  }
}

class _MapFab extends StatelessWidget {
  final IconData icon;
  final String tooltip;
  final VoidCallback onPressed;
  final Color? color;

  const _MapFab({
    required this.icon,
    required this.tooltip,
    required this.onPressed,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Material(
      color: isDark ? const Color(0xFF2C2C2C) : Colors.white,
      elevation: 3,
      // ignore: deprecated_member_use
      shadowColor: Colors.black.withOpacity(0.15),
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onPressed,
        child: Tooltip(
          message: tooltip,
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Icon(
              icon,
              size: 22,
              color: color ?? Theme.of(context).iconTheme.color,
            ),
          ),
        ),
      ),
    );
  }
}
