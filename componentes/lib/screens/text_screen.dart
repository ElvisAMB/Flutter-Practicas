import 'package:flutter/material.dart';

class TextScreen extends StatelessWidget {
  const TextScreen({super.key});

  @override
  Widget build(BuildContext context) {
 return Scaffold(
      appBar: AppBar(
        title: const Text("Configuración de texto"),
        centerTitle: true,
        //leading: Icon(Icons.arrow_back_rounded),
      ),
      body: Column(
        children: [
          ListTile(
            title: Text("Columnas"),
            subtitle: Text("Mostrar como se construyen los textos"),
            //leading: Icon(Icons.account_tree_outlined),
            trailing: Icon(Icons.chevron_right),
            
          ),
        ],
      ),
    );
  }
}