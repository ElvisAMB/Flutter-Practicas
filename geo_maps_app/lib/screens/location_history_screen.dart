import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/location_model.dart';
import '../theme/app_theme.dart';
import '../utils/map_utils.dart';

/// Pantalla de historial de ubicaciones registradas durante la sesión.
class LocationHistoryScreen extends StatelessWidget {
  final List<LocationModel> history;

  const LocationHistoryScreen({super.key, required this.history});

  static Future<void> show(
      BuildContext context, List<LocationModel> history) {
    return Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => LocationHistoryScreen(history: history),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Historial de ubicaciones'),
        leading: const BackButton(),
        actions: [
          if (history.isNotEmpty)
            Center(
              child: Padding(
                padding: const EdgeInsets.only(right: 16),
                child: Text(
                  '${history.length} registros',
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.grey.shade500,
                  ),
                ),
              ),
            ),
        ],
      ),
      body: history.isEmpty
          ? _buildEmptyState()
          : ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: history.length,
              separatorBuilder: (_, __) => const SizedBox(height: 8),
              itemBuilder: (context, index) {
                // Mostrar el más reciente primero
                final item = history[history.length - 1 - index];
                final isFirst = index == 0;
                return _HistoryCard(
                  location: item,
                  isLatest: isFirst,
                  previousLocation:
                      index < history.length - 1 ? history[index + 1] : null,
                );
              },
            ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.history_rounded, size: 64, color: Colors.grey.shade300),
          const SizedBox(height: 16),
          Text(
            'Sin historial',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: Colors.grey.shade400,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Las ubicaciones registradas\naparecerán aquí',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey.shade400),
          ),
        ],
      ),
    );
  }
}

class _HistoryCard extends StatelessWidget {
  final LocationModel location;
  final bool isLatest;
  final LocationModel? previousLocation;

  const _HistoryCard({
    required this.location,
    required this.isLatest,
    this.previousLocation,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    double? distanceFromPrev;

    if (previousLocation != null) {
      distanceFromPrev = MapUtils.haversineDistance(
        previousLocation!.latLng,
        location.latLng,
      );
    }

    return Container(
      decoration: BoxDecoration(
        color: isDark ? AppTheme.cardDark : Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: isLatest
            ? Border.all(color: AppTheme.primaryColor, width: 1.5)
            : null,
        boxShadow: [
          BoxShadow(
            // ignore: deprecated_member_use
            color: Colors.black.withOpacity(0.05),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      padding: const EdgeInsets.all(14),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Ícono
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: isLatest
                  // ignore: deprecated_member_use
                  ? AppTheme.primaryColor.withOpacity(0.12)
                  : Colors.grey.shade100,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(
              isLatest ? Icons.my_location_rounded : Icons.location_on_outlined,
              size: 18,
              color: isLatest ? AppTheme.primaryColor : Colors.grey,
            ),
          ),
          const SizedBox(width: 12),

          // Datos
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    if (isLatest)
                      Container(
                        margin: const EdgeInsets.only(right: 8),
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: AppTheme.primaryColor,
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: const Text(
                          'ACTUAL',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 9,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 0.5,
                          ),
                        ),
                      ),
                    Text(
                      DateFormat('HH:mm:ss · dd/MM/yyyy')
                          .format(location.timestamp),
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey.shade500,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  location.shortAddress,
                  style: const TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Text(
                  location.formattedCoordinates,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey.shade500,
                    fontFeatures: const [FontFeature.tabularFigures()],
                  ),
                ),
                if (distanceFromPrev != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 6),
                    child: Row(
                      children: [
                        Icon(Icons.straighten_rounded,
                            size: 12, color: Colors.grey.shade400),
                        const SizedBox(width: 4),
                        Text(
                          '+${MapUtils.formatDistance(distanceFromPrev)}',
                          style: TextStyle(
                            fontSize: 11,
                            color: Colors.grey.shade400,
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
