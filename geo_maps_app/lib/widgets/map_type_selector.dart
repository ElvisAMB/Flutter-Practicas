import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:provider/provider.dart';

import '../providers/location_provider.dart';
//import '../theme/app_theme.dart';

/// Bottom sheet para seleccionar el tipo de mapa con vista previa visual.
class MapTypeSelectorSheet extends StatelessWidget {
  const MapTypeSelectorSheet({super.key});

  static Future<void> show(BuildContext context) {
    return showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (_) => const MapTypeSelectorSheet(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<LocationProvider>();

    final types = [
      _MapTypeOption(
        type: MapType.normal,
        label: 'Normal',
        icon: Icons.map_rounded,
        description: 'Calles y etiquetas',
        color: const Color(0xFF4CAF50),
      ),
      _MapTypeOption(
        type: MapType.satellite,
        label: 'Satélite',
        icon: Icons.satellite_alt_rounded,
        description: 'Imágenes aéreas reales',
        color: const Color(0xFF2196F3),
      ),
      _MapTypeOption(
        type: MapType.terrain,
        label: 'Terreno',
        icon: Icons.terrain_rounded,
        description: 'Relieve y topografía',
        color: const Color(0xFFFF9800),
      ),
      _MapTypeOption(
        type: MapType.hybrid,
        label: 'Híbrido',
        icon: Icons.layers_rounded,
        description: 'Satélite con etiquetas',
        color: const Color(0xFF9C27B0),
      ),
    ];

    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 32),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Handle
          Center(
            child: Container(
              width: 36,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 20),

          const Text(
            'Tipo de mapa',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w700,
              letterSpacing: -0.3,
            ),
          ),
          const SizedBox(height: 16),

          // Grid de opciones
          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 2.2,
            children: types.map((option) {
              final isSelected = provider.mapType == option.type;
              return GestureDetector(
                onTap: () {
                  provider.changeMapType(option.type);
                  Navigator.of(context).pop();
                },
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  decoration: BoxDecoration(
                    color: isSelected
                        ? option.color.withOpacity(0.12)
                        : Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(
                      color: isSelected ? option.color : Colors.transparent,
                      width: 2,
                    ),
                  ),
                  padding: const EdgeInsets.all(14),
                  child: Row(
                    children: [
                      Icon(
                        option.icon,
                        color: isSelected ? option.color : Colors.grey,
                        size: 22,
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              option.label,
                              style: TextStyle(
                                fontWeight: FontWeight.w600,
                                fontSize: 14,
                                color: isSelected ? option.color : null,
                              ),
                            ),
                            Text(
                              option.description,
                              style: TextStyle(
                                fontSize: 10,
                                color: Colors.grey.shade500,
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        ),
                      ),
                      if (isSelected)
                        Icon(Icons.check_circle_rounded,
                            color: option.color, size: 16),
                    ],
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}

class _MapTypeOption {
  final MapType type;
  final String label;
  final IconData icon;
  final String description;
  final Color color;

  const _MapTypeOption({
    required this.type,
    required this.label,
    required this.icon,
    required this.description,
    required this.color,
  });
}
