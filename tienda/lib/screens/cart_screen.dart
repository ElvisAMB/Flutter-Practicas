import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:tienda/models/product_model.dart';
import 'package:tienda/notifier/cart_notifier.dart';
import 'package:tienda/screens/checkout_screen.dart';
import 'package:tienda/widgets/cart_card.dart';

class CartScreen extends StatelessWidget {
  const CartScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final List<ProductModel> cartProducts = context
        .watch<CartNotifier>()
        .cartProducts;

    return Scaffold(
      appBar: AppBar(title: Text("Mi carrito"), centerTitle: true),
      body: ListView.builder(
        itemBuilder: (context, index) {
          final product = cartProducts[index];
          return CartCard(product: product);
        },
        itemCount: cartProducts.length,
      ),
      bottomNavigationBar: Column(
        mainAxisSize: .min,
        children: [
          Container(
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey.withAlpha(200)),
              color: Color(0xfff7f2fa),
              borderRadius: BorderRadius.circular(12),
            ),
            margin: EdgeInsets.all(16),
            padding: EdgeInsets.all(16),
            child: Column(
              children: [
                SizedBox(height: 10),
                Row(
                  mainAxisAlignment: .spaceBetween,
                  children: [
                    Text(
                      "Subtotal",
                      style: TextStyle(
                        fontWeight: .w600,
                        color: Color(0xff79767B),
                      ),
                    ),
                    //SizedBox(width: 1),
                    Text(
                      "\$${context.watch<CartNotifier>().subtotal.toStringAsFixed(2)}",
                      style: TextStyle(fontWeight: .bold),
                    ), //Text("\$454.50"),
                  ],
                ),
                SizedBox(height: 10),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      "Envío",
                      style: TextStyle(
                        fontWeight: .w600,
                        color: Color(0xff79767B),
                      ),
                    ),
                    //SizedBox(width: 50),
                    Text(
                      "\$${context.watch<CartNotifier>().envio}",
                      style: TextStyle(
                        fontWeight: .bold,
                        color: Colors.blueGrey,
                      ),
                    ),
                  ],
                ),
                Divider(), //SizedBox(height: 10),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      "Total",
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    //SizedBox(width: 50),
                    Text(
                      "\$${context.watch<CartNotifier>().total.toStringAsFixed(2)}",
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                Container(
                  width: double.infinity,
                  margin: EdgeInsets.all(16),
                  child: FilledButton(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => CheckoutScreen(),
                        ),
                      );
                    },
                    child: Text("Ir a Pagar"),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
