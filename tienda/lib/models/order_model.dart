import 'package:tienda/models/delivery_info_model.dart';
import 'package:tienda/models/product_model.dart';

class OrderModel {
  final String id;
  final String userId;
  final double total;
  final double delivery;
  final DateTime createdDate;
  final DeliveryInfo deliveryInfo;
  final List<ProductModel> products;

  OrderModel({
    required this.id,
    required this.userId,
    required this.total,
    required this.delivery,
    required this.createdDate,
    required this.deliveryInfo,
    required this.products,
  });

  factory OrderModel.fromMap(Map<String, dynamic> map, {String? docId}) {
    return OrderModel(
      id: docId ?? map['id'] ?? '',
      userId: map['user_id'] ?? '',
      total: (map['total'] as num).toDouble(),
      delivery: (map['delivery'] as num).toDouble(),
      createdDate: DateTime.parse(map['created_date']),
      deliveryInfo: DeliveryInfo.fromMap(
        Map<String, dynamic>.from(map['delivery_info']),
      ),
      products: (map['products'] as List<dynamic>)
          .map((p) => ProductModel.fromMap(Map<String, dynamic>.from(p)))
          .toList(),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'user_id': userId,
      'total': total,
      'delivery': delivery,
      'created_date': createdDate.toIso8601String(),
      'delivery_info': deliveryInfo.toMap(),
      'products': products.map((p) => p.toMap()).toList(),
    };
  }

  @override
  String toString() => 'OrderModel(id: $id, total: $total, userId: $userId)';
}