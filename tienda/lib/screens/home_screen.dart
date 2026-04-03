import 'package:flutter/material.dart';
import 'package:tienda/screens/cart_screen.dart';
import 'package:tienda/services/product_service.dart';
import 'package:tienda/widgets/product_card.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Nuestra Tienda", style: TextStyle(color: Colors.white)),
        centerTitle: true,
        backgroundColor: Colors.deepPurpleAccent,
        actions: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Icon(Icons.person),
          ),
        ],
      ),
      body: Column(
        crossAxisAlignment: .center,
        children: [
          SizedBox(height: 40),
          Column(
            children: [
              Text(
                "Colección 2024",
                style: TextStyle(
                  color: Colors.grey,
                  fontSize: 12,
                  fontWeight: FontWeight.w400,
                  letterSpacing: 2,
                ),
              ),
            ],
          ),
          SizedBox(height: 2),
          Text(
            "Diseño Atemporal",
            style: TextStyle(
              fontSize: 32,
              color: Colors.black,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: 30),

          //Imagen
          // Container(
          //   decoration: BoxDecoration(
          //     color: Colors.white,
          //     borderRadius: BorderRadius.circular(20),
          //   ),
          //   child: ClipRRect(
          //     borderRadius: BorderRadiusGeometry.circular(50),
          //     child: Image.network(
          //       "https://raw.githubusercontent.com/RicharC293/fake_doctors/refs/heads/master/images/producto-1.jpg",
          //       height: 400,
          //       fit: BoxFit.cover,
          //       width: double.infinity,
          //     ),
          //   ),
          // ),

          // SizedBox(height: 16),
          // Text(
          //   "Jarrón de cerámica",
          //   style: TextStyle(
          //     fontSize: 20,
          //     color: Colors.black,
          //     fontWeight: FontWeight.bold,
          //   ),
          // ),
          // //Buttons
          // Text("\$45", style: TextStyle(fontSize: 16, color: Colors.grey)),

          // SizedBox(height: 16),

          // SizedBox(
          //   width: 350,
          //   child: FilledButton(
          //     style: ButtonStyle(),
          //     onPressed: () {
          //       // Product Service
          //       Expanded(
          //         child: FutureBuilder(
          //           future: ProductService().getProducts(),
          //           builder: (context, snapshot) {
          //             if (snapshot.hasError) {
          //               return Text("Ha ocurrido un eror en la consulta");
          //             }

          //             if (!snapshot.hasData) {
          //               return Center(child: CircularProgressIndicator());
          //             }

          //             final productos = snapshot.data ?? [];

          //             return ListView.builder(
          //               itemBuilder: (context, index) {
          //                 final producto = productos[index];
          //                 return ProductCard(productModel: producto);
          //               },
          //               itemCount: productos.length,
          //               shrinkWrap: true,
          //               physics: NeverScrollableScrollPhysics(),
          //             );
          //           },
          //         ),
          //       );
          //     },
          //     child: Text("Añadir"),
          //   ),
          // ),
          // SizedBox(height: 16),
          ProductCard(productModel: product)
        ],
      ),

      bottomNavigationBar: BottomNavigationBar(
        items: [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: "Home"),
          BottomNavigationBarItem(
            icon: Icon(Icons.shopping_cart),
            label: "Cart",
          ),
        ],
        onTap: (value) {
          if (value == 1) {
            final route = MaterialPageRoute(
              builder: (context) {
                return CartScreen();
              },
            );
            Navigator.push(context, route);
          }
        },
      ),
    );
  }
}
