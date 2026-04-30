import "package:google_maps_apis/geocoding.dart";

class GoogleMapService {
  // Future<GeocodingResponse> getAddress(Location location) async {
  //   final geocoding = GoogleMapsGeocoding(
  //     apiKey: "AIzaSyCs_1hrO1OYvHyk07F21PG9hYwBY3Q7rLY",
  //   );
  //   final response = await geocoding.searchByLocation(location);
  //   return response;
  // }

  Future<GeocodingResponse> getAddress({
    required double lat,
    required double lng,
  }) async {
    final geocoding = GoogleMapsGeocoding(
      apiKey: "AIzaSyCs_1hrO1OYvHyk07F21PG9hYwBY3Q7rLY",
    );
    final response = await geocoding.searchByLocation(
      Location(lat: lat, lng: lng),
    );
    
    return response;
  }

Future<void> getAddressFromCoordinates(double lat, double lng) async {
  //List<Placemark> placemarks = await placemarkFromCoordinates(lat, lng);

  // if (placemarks.isNotEmpty) {
  //   Placemark place = placemarks.first;

  //   final ciudad      = place.locality;               // "Quito"
  //   final barrio      = place.subLocality;            // "La Mariscal"
  //   final calle       = place.street;                 // "Av. Amazonas"
  //   final provincia   = place.administrativeArea;     // "Pichincha"
  //   final pais        = place.country;                // "Ecuador"
  //   final codigoPostal= place.postalCode;             // "170143"

  //   // Dirección completa formateada
  //   final direccionCompleta = [
  //     place.street,
  //     place.subLocality,
  //     place.locality,
  //     place.administrativeArea,
  //     place.country,
  //   ].where((e) => e != null && e.isNotEmpty).join(', ');

  //   print(direccionCompleta);
    // "Av. Amazonas, La Mariscal, Quito, Pichincha, Ecuador"
  }
}

