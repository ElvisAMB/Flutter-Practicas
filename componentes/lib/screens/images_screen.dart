import 'package:flutter/material.dart';

class ImagesScreen extends StatelessWidget {
  const ImagesScreen({super.key});

  @override
  Widget build(BuildContext context) {
   return Scaffold(
      appBar: AppBar(
        title: const Text("Configuración de imagenes"),
        centerTitle: true,
        backgroundColor: Colors.lightBlue,
      ),
      body: Column(
        children: [
          ListTile(
            title: Text("Columnas"),
            subtitle: Text("Mostrar como se construyen las imagenes"),
            //leading: Icon(Icons.account_tree_outlined),
            trailing: Icon(Icons.chevron_right),
            
          ),
        ],
      ),
    );
  }
}