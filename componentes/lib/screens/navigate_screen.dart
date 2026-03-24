import 'package:flutter/material.dart';

class NavigateScreen extends StatelessWidget {
  const NavigateScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Configuración de navegacion"),
        centerTitle: true,
        backgroundColor: Colors.lightBlue,
      ),
      body: Column(
        children: [
          ListTile(
            title: Text("Columnas"),
            subtitle: Text("Mostrar como se construyen la navegacion"),
            //leading: Icon(Icons.account_tree_outlined),
            trailing: Icon(Icons.chevron_right),
            
          ),
        ],
      ),
    );
  }
}