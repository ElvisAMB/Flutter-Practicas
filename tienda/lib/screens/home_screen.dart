import 'package:flutter/material.dart';
import 'package:tienda/screens/cart_screen.dart';
import 'package:tienda/screens/orders_screen.dart';
import 'package:tienda/screens/profile_screen.dart';
import 'package:tienda/services/product_service.dart';
import 'package:tienda/widgets/product_card.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Our Store", style: TextStyle(color: Colors.white)),
        centerTitle: true,
        backgroundColor: Colors.deepPurpleAccent,
        actions: [
          IconButton(
            onPressed: () {
              final route = MaterialPageRoute(
                builder: (context) {
                  return ProfileScreen();
                },
              );
              Navigator.push(context, route);
            },
            icon: Icon(Icons.account_circle_outlined),
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: .center,
          children: [
            Text(
              "Colección 2024",
              style: TextStyle(
                color: Colors.grey,
                fontSize: 12,
                fontWeight: FontWeight.w400,
                letterSpacing: 3,
              ),
            ),

            Text(
              "Diseño Atemporal",
              style: TextStyle(
                fontSize: 32,
                color: Colors.black,
                fontWeight: FontWeight.bold,
              ),
            ),

            FutureBuilder(
              future: ProductService().getProducts(),
              builder: (context, snapshot) {
                if (snapshot.hasError) {
                  return Text("Ha ocurrido un eror en la consulta");
                }

                if (!snapshot.hasData) {
                  return Center(child: CircularProgressIndicator());
                }

                final data = snapshot.data ?? [];

                return ListView.builder(
                  itemBuilder: (context, index) {
                    final producto = data[index];
                    return ProductCard(productModel: producto);
                  },
                  itemCount: data.length,
                  shrinkWrap: true,
                  physics: NeverScrollableScrollPhysics(),
                );
              }, // final builder
            ),
          ],
        ),
      ),

      bottomNavigationBar: BottomNavigationBar(
        items: [
          // #0
          BottomNavigationBarItem(icon: Icon(Icons.home), label: "Home"), 
          // #1
          BottomNavigationBarItem(
            icon: Icon(Icons.receipt),
            label: "Orders",
          ), 
          // #2
          BottomNavigationBarItem(
            icon: Icon(Icons.shopping_cart),
            label: "Cart",
          ), 
        ],
        onTap: (value) {
          switch (value) {
            case 1:
              final route = MaterialPageRoute(
                builder: (context) {
                  return OrdersScreen();
                },
              );
              Navigator.push(context, route);
              break;
            case 2:
              final route = MaterialPageRoute(
                builder: (context) {
                  return CartScreen();
                },
              );
              Navigator.push(context, route);
              break;
            default:
          }
        },
      ),
    );
  }
}
