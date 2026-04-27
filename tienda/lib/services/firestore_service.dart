import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:tienda/models/product_model.dart';

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
    //GlobalKey<FormState> form
  ) async {
    //printToConsole(form.toString());

    final data = {
      'user_id': FirebaseAuth.instance.currentUser!.uid,
      'products': product
          .map(
            (product) => {
              'id': product.id,
              'name': product.name,
              'description': product.description,
              'price': product.price,
              'image': product.image,
            },
          )
          .toList(),
      'delivery_info': {
        'name': name,
        'delivery': delivery,
        'total': total,
        "email": email,
        "direccion": direccion,
        "ciudad": ciudad,
        "metodoPago": metodoPago,
      },
    }; //fin data
    db.collection("orders").add(data);
  }

  //Crear la operación lectura que lee las órdenes
}
