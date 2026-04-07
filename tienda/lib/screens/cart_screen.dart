import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:tienda/models/product_model.dart';
import 'package:tienda/notifier/card_notifier.dart';

class CartScreen extends StatelessWidget {
  const CartScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final cartProducts = context.watch<CartNotifier>().cartProducts;

    return Scaffold(
      appBar: AppBar(title: Text("Mi carrito"), centerTitle: true),
      body: ListView.builder(
        itemBuilder: (context, index) {
          final product = cartProducts[index];
          return CartCard(producto: product);
        },
        itemCount: cartProducts.length,
      ),
      bottomNavigationBar: Column(
        mainAxisSize: .min,
        children: [
          Container(
            decoration: BoxDecoration(
              color: const Color.fromARGB(135, 245, 243, 243),
              borderRadius: BorderRadius.circular(10),
              border: BoxBorder.all(style: BorderStyle.solid),
            ),
            child: Column(
              children: [
                SizedBox(height: 10),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    Text("Subtotal"),
                    //SizedBox(width: 1),
                    Text("\$454.50"),
                  ],
                ),
                SizedBox(height: 10),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    Text("Envío"),
                    //SizedBox(width: 50),
                    Text("Gratis"),
                  ],
                ),
                SizedBox(height: 10),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    Text(
                      "Total",
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    //SizedBox(width: 50),
                    Text(
                      "\$454.50",
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 10),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// class PricesCard extends StatelessWidget {
//   const PricesCard({super.key});

//   @override
//   Widget build(BuildContext context) {
//     return CartCard();
//   }
// }

class CartCard extends StatelessWidget {
  const CartCard({super.key, required this.producto});

  final ProductModel producto;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Row(
        spacing: 12,
        children: [
          ClipRRect(
            borderRadius: BorderRadiusGeometry.circular(16),
            child: Image.network(
              producto
                  .image, // "https://raw.githubusercontent.com/RicharC293/fake_doctors/refs/heads/master/images/producto-1.jpg",
              width: 80,
            ),
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: .start,
              children: [
                Text(
                  producto.name, // "Reloj Minimalista Argento",
                  style: TextStyle(fontWeight: .w600),
                ),
                Text(producto.description, style: TextStyle(fontSize: 11)),
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        producto.price.toStringAsFixed(2), //"\$120.00",
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
                              context.read()<CartNotifier>().removeProductToCard(
                                producto,
                              );
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
                              context.read()<CartNotifier>().addProductToCart(
                                producto,
                              );
                            },
                            child: SizedBox(
                              height: 25,
                              width: 25,
                              child: Icon(Icons.add_outlined),
                            ),
                          ),
                          SizedBox(width: 8),

                          /**
 * 
 * 
 * 
 */
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
