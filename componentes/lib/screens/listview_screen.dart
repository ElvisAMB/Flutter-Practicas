import 'package:flutter/material.dart';

class ListViewScreen extends StatelessWidget {
  const ListViewScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Configuración de listas"),
        centerTitle: true,
        backgroundColor: Colors.lightBlue,
        //leading: Icon(Icons.arrow_back_rounded),
      ),
      body: Column(
        children: [
          ListTile(
            title: Text("ListView"),
            subtitle: Text("Mostrar como se construyen las listas"),
            //leading: Icon(Icons.account_tree_outlined),
            trailing: Icon(Icons.chevron_right),
            
          ),
        ],
      ),
    );
  }
}
