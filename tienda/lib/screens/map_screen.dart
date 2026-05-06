// ignore_for_file: avoid_print
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'package:tienda/services/google_map_service.dart';

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => MapScreenState();
}

class MapScreenState extends State<MapScreen> {
  final Completer<GoogleMapController> _controller =
      Completer<GoogleMapController>();

  static const CameraPosition _kGooglePlex = CameraPosition(
    target: LatLng(-2.1676853297405576, -79.90471284357757),
    zoom: 10.4746,
  );

  CameraPosition? _cameraPosition;
  List<String> _locationName = [];
  final _googleApiService = GoogleMapService();

  static const CameraPosition _kLake = CameraPosition(
    bearing: 192.8334901395799,
    target: LatLng(-2.1676853297405576, -79.90471284357757),
    tilt: 59.440717697143555,
    zoom: 19.151926040649414,
  );

  @override
  void initState() {
    super.initState();
    // Consultar la geolocalización
    _getUserPosition();
  }

  Future<void> _getUserPosition() async {
    try {
      final position = await _determinePosition();
      final GoogleMapController controller = await _controller.future;
      controller.animateCamera(
        CameraUpdate.newCameraPosition(
          CameraPosition(
            target: LatLng(position.latitude, position.longitude),
            zoom: 10,
          ),
        ),
      );
      await controller.animateCamera(CameraUpdate.newCameraPosition(_kLake));
    } catch (e) {
      print("There is an error: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Address", style: TextStyle(color: Colors.white)),
        titleTextStyle: TextStyle(fontSize: 20),
        centerTitle: true,
      ),

      body: Stack(
        children: [
          GoogleMap(
            mapType: MapType.terrain,
            initialCameraPosition: _kGooglePlex,
            onMapCreated: (GoogleMapController controller) {
              _controller.complete(controller);
            },
            onCameraMove: (position) {
              // Nos da latitud y longitud
              _cameraPosition = position;
            },
            onCameraIdle: () async {
              final target = _cameraPosition?.target;
              // Retorno temprano - early return
              if (target == null) return;

              final response = await _googleApiService.getAddress(
                lat: target.latitude,
                lng: target.longitude,
              );

              // Dirección
              final address = response.results?.firstOrNull?.formattedAddress
                  ?.split(",")
                  .firstOrNull;
              // Ciudad
              final city = response.results?.firstOrNull?.addressComponents
                  ?.firstWhere((value) {
                    return value.types?.contains("administrative_area_level_2") ?? false;
                  });
              // provincia
              final state = response.results?.firstOrNull?.addressComponents
                  ?.firstWhere((value) {
                    return value.types?.contains(
                          "administrative_area_level_1",
                        ) ??
                        false;
                  });

              _locationName = [address ?? "","${city?.longName ?? ""}, ${state?.longName ?? ""}",];
                            
              setState(() {});
            },
            zoomControlsEnabled: false,
            webCameraControlEnabled: false,
          ), //Google Map
          Positioned.fill(
            child: Icon(Icons.location_on, size: 30, color: Colors.red),
          ),
        ],
      ), // Stack
      floatingActionButton: FloatingActionButton(
        onPressed: _getUserPosition,
        child: Icon(Icons.my_location),
      ),
      bottomNavigationBar: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(
          mainAxisSize: .min,
          crossAxisAlignment: .start,
          spacing: 16,
          children: [
            Text("Place: ${_locationName.join(" ")}"),
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: () {
                  Navigator.pop(context, _locationName);
                },
                child: Text("Confirm"),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Determine the current position of the device.
///
/// When the location services are not enabled or permissions
/// are denied the `Future` will return an error.
Future<Position> _determinePosition() async {
  bool serviceEnabled;
  LocationPermission permission;

  // Test if location services are enabled.
  serviceEnabled = await Geolocator.isLocationServiceEnabled();
  if (!serviceEnabled) {
    // Location services are not enabled don't continue
    // accessing the position and request users of the
    // App to enable the location services.
    return Future.error('Location services are disabled.');
  }

  permission = await Geolocator.checkPermission();
  if (permission == LocationPermission.denied) {
    permission = await Geolocator.requestPermission();
    if (permission == LocationPermission.denied) {
      // Permissions are denied, next time you could try
      // requesting permissions again (this is also where
      // Android's shouldShowRequestPermissionRationale
      // returned true. According to Android guidelines
      // your App should show an explanatory UI now.
      return Future.error('Location permissions are denied');
    }
  }

  if (permission == LocationPermission.deniedForever) {
    // Permissions are denied forever, handle appropriately.
    return Future.error(
      'Location permissions are permanently denied, we cannot request permissions.',
    );
  }

  // When we reach here, permissions are granted and we can
  // continue accessing the position of the device.
  return await Geolocator.getCurrentPosition();
}
