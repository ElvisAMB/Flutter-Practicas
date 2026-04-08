import 'package:flutter/material.dart';

import '../models/location_model.dart';
import '../theme/app_theme.dart';

/// Widget que muestra errores relacionados con permisos y servicios
/// de ubicación, con opciones claras de acción para el usuario.
class PermissionErrorWidget extends StatelessWidget {
  final LocationStatus status;
  final String message;
  final VoidCallback? onOpenSettings;
  final VoidCallback? onRetry;

  const PermissionErrorWidget({
    super.key,
    required this.status,
    required this.message,
    this.onOpenSettings,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    final config = _getConfig(status);

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Ícono de error
              Container(
                width: 96,
                height: 96,
                decoration: BoxDecoration(
                  // ignore: deprecated_member_use
                  color: config.color.withOpacity(0.12),
                  shape: BoxShape.circle,
                ),
                child: Icon(config.icon, size: 48, color: config.color),
              ),
              const SizedBox(height: 32),

              // Título
              Text(
                config.title,
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.w700,
                  letterSpacing: -0.5,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 12),

              // Mensaje descriptivo
              Text(
                message,
                style: TextStyle(
                  fontSize: 15,
                  color: Colors.grey.shade600,
                  height: 1.5,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 40),

              // Botón principal de acción
              if (onOpenSettings != null)
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: onOpenSettings,
                    icon: Icon(config.actionIcon),
                    label: Text(config.actionLabel),
                  ),
                ),

              const SizedBox(height: 12),

              // Botón secundario de reintentar
              if (onRetry != null &&
                  status != LocationStatus.permissionPermanentlyDenied)
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    onPressed: onRetry,
                    icon: const Icon(Icons.refresh_rounded),
                    label: const Text('Reintentar'),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  _ErrorConfig _getConfig(LocationStatus status) {
    switch (status) {
      case LocationStatus.permissionDenied:
        return const _ErrorConfig(
          icon: Icons.location_off_rounded,
          color: AppTheme.errorColor,
          title: 'Permiso de ubicación requerido',
          actionIcon: Icons.lock_open_rounded,
          actionLabel: 'Conceder permiso',
        );
      case LocationStatus.permissionPermanentlyDenied:
        return const _ErrorConfig(
          icon: Icons.no_encryption_rounded,
          color: AppTheme.errorColor,
          title: 'Permiso bloqueado',
          actionIcon: Icons.settings_rounded,
          actionLabel: 'Abrir ajustes',
        );
      case LocationStatus.serviceDisabled:
        return const _ErrorConfig(
          icon: Icons.location_disabled_rounded,
          color: AppTheme.warningColor,
          title: 'GPS desactivado',
          actionIcon: Icons.gps_fixed_rounded,
          actionLabel: 'Activar ubicación',
        );
      default:
        return const _ErrorConfig(
          icon: Icons.error_outline_rounded,
          color: AppTheme.errorColor,
          title: 'Error de ubicación',
          actionIcon: Icons.refresh_rounded,
          actionLabel: 'Reintentar',
        );
    }
  }
}

class _ErrorConfig {
  final IconData icon;
  final Color color;
  final String title;
  final IconData actionIcon;
  final String actionLabel;

  const _ErrorConfig({
    required this.icon,
    required this.color,
    required this.title,
    required this.actionIcon,
    required this.actionLabel,
  });
}
