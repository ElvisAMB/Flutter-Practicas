// ignore_for_file: avoid_print

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:tienda/models/order_model.dart';
import 'package:tienda/models/product_model.dart';
import 'package:uuid/uuid.dart';

class FirestoreService {
  //Inicializar firestore (base de datos en Firebase)
  final db = FirebaseFirestore.instance;

  //Crear la operación de ecsritura que crea la orden
  Future<void> createOrder(
    List<ProductModel> product,
    double delivery,
    double total,
    String name,
    String email,
    String direccion,
    String ciudad,
    String metodoPago,
  ) async {
    final data = {
      'id': Uuid().v1(),
      'user_id': FirebaseAuth.instance.currentUser!.uid,
      'products': product
          .map(
            (product) => {
              'id': product.id,
              "currency": product.currency,
              "currencySymbol": product.currencySymbol,
              'description': product.description,
              'image': product.image,
              'name': product.name,
              'price': product.price,
            },
          )
          .toList(),
      'delivery_info': {
        'name': name,
        "email": email,
        "address": direccion,
        "city": ciudad,
        "payMethod": metodoPago,
      },
      'delivery': delivery,
      'total': total,
      "created_date": DateTime.now().toIso8601String(),
    }; //fin data
    db.collection("orders").add(data);
  }

  //Crear la operación lectura que lee las órdenes
  Future<List<OrderModel>> getOrders() async {
    final snapshot = await FirebaseFirestore.instance
        .collection('orders')
        .get();

    return snapshot.docs
        .map((doc) => OrderModel.fromMap(doc.data(), docId: doc.id))
        .toList();
  }

  Future<void> getInvoices() async {
    final data = await db.collection("orders").get();

    for (var item in data.docs) {
      print(item.data());
    }
  }
}
