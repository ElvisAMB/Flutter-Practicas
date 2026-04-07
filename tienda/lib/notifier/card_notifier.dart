import 'package:flutter/foundation.dart';
import 'package:tienda/models/product_model.dart';

class CartNotifier extends ChangeNotifier {
  List<ProductModel> _cartProducts = [];

  // ignore: unnecessary_getters_setters
  List<ProductModel> get cartProducts => _cartProducts;

  set cartProducts(List<ProductModel> products) {
    _cartProducts = products;
  }

  //Funciones
  void addProductToCart(ProductModel item) {
    _cartProducts.add(item);
    notifyListeners();
  }

  void removeProductToCard(ProductModel item) {
    _cartProducts.remove(item);
    notifyListeners();
  }

  void clearCart() {
    _cartProducts.clear();
    notifyListeners();
  }

  // Subtotal
    double get subtotal {
        final prices =  cartProducts.map((e) {
          return e.price;
        }).toList();
        return prices.isNotEmpty ? prices.reduce((a, b) => a + b) : 0.0;
    }

    // Envio 
    double get envio => 10.0;

    //Total
    double get total => subtotal + envio;
}
