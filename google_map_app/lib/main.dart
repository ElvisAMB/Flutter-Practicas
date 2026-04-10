import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: MapScreen(),
    );
  }
}

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  GoogleMapController? _controller;

  LatLng _position = const LatLng(-0.1807, -78.4678); // Quito por defecto
  Set<Marker> _markers = {};

  String _status = "Obteniendo ubicación...";

  @override
  void initState() {
    super.initState();
    _getLocation();
  }

  Future<void> _getLocation() async {
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();

      if (!serviceEnabled) {
        setState(() {
          _status = "Ubicación desactivada";
        });
        return;
      }

      LocationPermission permission = await Geolocator.checkPermission();

      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }

      if (permission == LocationPermission.denied ||
          permission == LocationPermission.deniedForever) {
        setState(() {
          _status = "Permiso de ubicación denegado";
        });
        return;
      }

      final pos = await Geolocator.getCurrentPosition();

      final newPosition = LatLng(pos.latitude, pos.longitude);

      setState(() {
        _position = newPosition;
        _status = "Ubicación obtenida";
        _markers = {
          Marker(
            markerId: const MarkerId("current"),
            position: newPosition,
            infoWindow: InfoWindow(
              title: "Mi ubicación",
              snippet: "Lat: ${pos.latitude}, Lng: ${pos.longitude}",
            ),
          ),
        };
      });

      _controller?.animateCamera(CameraUpdate.newLatLngZoom(newPosition, 15));
    } catch (e) {
      setState(() {
        _status = "Error obteniendo ubicación";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Google Maps Web"), centerTitle: true),
      body: Column(
        children: [
          Expanded(
            child: GoogleMap(
              initialCameraPosition: CameraPosition(
                target: _position,
                zoom: 12,
              ),
              onMapCreated: (controller) {
                _controller = controller;
              },
              markers: _markers,
              mapType: MapType.normal,
              zoomControlsEnabled: true,
              onTap: (LatLng pos) {
                setState(() {
                  _markers = {
                    Marker(
                      markerId: const MarkerId("selected"),
                      position: pos,
                      infoWindow: InfoWindow(
                        title: "Ubicación seleccionada",
                        snippet: "Lat: ${pos.latitude}, Lng: ${pos.longitude}",
                      ),
                    ),
                  };
                });
              },
            ),
          ),
          Container(
            padding: const EdgeInsets.all(12),
            color: Colors.grey[200],
            child: Column(
              children: [
                Text(_status),
                Text("Latitud: ${_position.latitude}"),
                Text("Longitud: ${_position.longitude}"),
                const SizedBox(height: 8),
                ElevatedButton(
                  onPressed: _getLocation,
                  child: const Text("Actualizar ubicación"),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
