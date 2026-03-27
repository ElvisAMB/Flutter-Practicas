import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Nuestra Tienda"),
        centerTitle: true,
        backgroundColor: Colors.blue,
        actions: [
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Icon(Icons.person),
          )
        ],
      ),
      body: Column(
        children: [
          Text("Colección 2026"),
          Text("Diseño Atemporal"),
          Image.network(""),
          Text("Jarrón de cerámica"),
          Text("45"),
          //Tipos de botones que existen en flutter
          
        ],
      ),
    );
  }
}
