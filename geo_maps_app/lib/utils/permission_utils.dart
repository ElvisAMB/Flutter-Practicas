import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';

/// Utilidades para gestionar los permisos de ubicación con diálogos
/// informativos al usuario antes de solicitar el permiso del sistema.
class PermissionUtils {
  PermissionUtils._();

  /// Muestra un diálogo explicativo antes de solicitar permisos.
  /// Retorna true si el usuario acepta, false si rechaza.
  static Future<bool> showPermissionRationale(BuildContext context) async {
    final result = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        title: const Row(
          children: [
            Icon(Icons.location_on_rounded, color: Color(0xFF1A73E8)),
            SizedBox(width: 10),
            Text('Acceso a ubicación'),
          ],
        ),
        content: const Text(
          'GeoMaps necesita acceso a tu ubicación GPS para:\n\n'
          '• Mostrarte en el mapa en tiempo real\n'
          '• Calcular tu velocidad y rumbo\n'
          '• Obtener la dirección de tu posición\n\n'
          'Tu ubicación no se comparte con terceros.',
          style: TextStyle(height: 1.5),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('No, gracias'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Permitir'),
          ),
        ],
      ),
    );
    return result ?? false;
  }

  /// Muestra un diálogo cuando el permiso fue denegado permanentemente.
  static Future<void> showPermanentlyDeniedDialog(
      BuildContext context) async {
    await showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        title: const Row(
          children: [
            Icon(Icons.lock_rounded, color: Colors.red),
            SizedBox(width: 10),
            Text('Permiso bloqueado'),
          ],
        ),
        content: const Text(
          'El permiso de ubicación fue bloqueado. Para habilitarlo, '
          've a Ajustes > Aplicaciones > GeoMaps > Permisos > Ubicación '
          'y selecciona "Permitir".',
          style: TextStyle(height: 1.5),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              Geolocator.openAppSettings();
            },
            child: const Text('Ir a Ajustes'),
          ),
        ],
      ),
    );
  }

  /// Muestra un diálogo para activar el GPS del sistema.
  static Future<void> showGPSDisabledDialog(BuildContext context) async {
    await showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        title: const Row(
          children: [
            Icon(Icons.gps_off_rounded, color: Colors.orange),
            SizedBox(width: 10),
            Text('GPS desactivado'),
          ],
        ),
        content: const Text(
          'El servicio de ubicación está desactivado. '
          'Activa el GPS en los ajustes del sistema para continuar.',
          style: TextStyle(height: 1.5),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              Geolocator.openLocationSettings();
            },
            child: const Text('Activar GPS'),
          ),
        ],
      ),
    );
  }
}
