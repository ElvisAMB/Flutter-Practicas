// models/delivery_info.dart

class DeliveryInfo {
  final String name;
  final String email;
  final String city;
  final String address;
  final String payMethod;

  DeliveryInfo({
    required this.name,
    required this.email,
    required this.city,
    required this.address,
    required this.payMethod,
  });

  factory DeliveryInfo.fromMap(Map<String, dynamic> map) {
    return DeliveryInfo(
      name: map['name'] ?? '',
      email: map['email'] ?? '',
      city: map['city'] ?? '',
      address: map['address'] ?? '',
      payMethod: map['payMethod'] ?? '',
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'name': name,
      'email': email,
      'city': city,
      'address': address,
      'payMethod': payMethod,
    };
  }
}