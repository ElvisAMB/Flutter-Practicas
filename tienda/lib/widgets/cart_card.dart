import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:tienda/models/product_model.dart';
import 'package:tienda/notifier/cart_notifier.dart';

class CartCard extends StatelessWidget {
  const CartCard({super.key, required this.product});

  final ProductModel product;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Row(
        spacing: 12,
        children: [
          ClipRRect(
            borderRadius: BorderRadiusGeometry.circular(16),
            child: Image.network(product.image, width: 80),
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: .start,
              children: [
                Text(
                  product.name, // "Reloj Minimalista Argento",
                  style: TextStyle(fontWeight: .w600),
                ),
                Text(product.description, style: TextStyle(fontSize: 11)),
                Row(
                  children: [
                    // Producto agregado
                    Expanded(
                      child: Text(
                        "${product.currencySymbol} ${product.price.toStringAsFixed(2)}",
                        style: TextStyle(
                          color: Colors.deepPurpleAccent,
                          fontWeight: .bold,
                        ),
                      ),
                    ),
                    Container(
                      decoration: BoxDecoration(
                        color: Color(0xFFE8DEF8),
                        borderRadius: BorderRadius.circular(100),
                      ),
                      child: Row(
                        crossAxisAlignment: .center,
                        children: [
                          SizedBox(width: 8),
                          GestureDetector(
                            onTap: () {
                              context
                                  .read<CartNotifier>()
                                  .removeProductToCard(product);
                            },
                            child: SizedBox(
                              height: 25,
                              width: 25,
                              child: Icon(Icons.remove_outlined),
                            ),
                          ),
                          SizedBox(width: 4),
                          Text("1"),
                          SizedBox(width: 4),
                          GestureDetector(
                            onTap: () {
                              context.read<CartNotifier>().addProductToCart(
                                product,
                              );
                            },
                            child: SizedBox(
                              height: 25,
                              width: 25,
                              child: Icon(Icons.add_outlined),
                            ),
                          ),
                          SizedBox(width: 8),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
