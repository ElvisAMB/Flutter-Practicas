import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:tienda/models/product_model.dart';
import 'package:tienda/notifier/cart_notifier.dart';

class ProductCard extends StatelessWidget {
  const ProductCard({super.key, required this.productModel});

  final ProductModel productModel;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 400,
      decoration: BoxDecoration(
        color: const Color.fromARGB(255, 224, 246, 255),
        borderRadius: BorderRadius.circular(36),
      ),
      margin: EdgeInsets.all(14),
      child: Column(
        children: [
          ClipRRect(
            borderRadius: BorderRadiusGeometry.only(
              topLeft: Radius.circular(32),
              topRight: Radius.circular(32),
            ),
            child: Image.network(productModel.image),
          ),
          SizedBox(height: 12),
          Text(productModel.name, style: TextStyle(fontWeight: .bold)),
          SizedBox(height: 8),
          //Text(productModel.price.toStringAsFixed(2)),
          Text(
            "${productModel.currencySymbol}${productModel.price.toStringAsFixed(2)}",
          ),
          SizedBox(height: 8),
          SizedBox(
            width: 350,
            child: FilledButton(
              onPressed: () {
                context.read<CartNotifier>().addProductToCart(productModel);
              },
              child: Text("Añadir"),
            ),
          ),
          SizedBox(height: 12),
        ],
      ),
    );
  }
}
