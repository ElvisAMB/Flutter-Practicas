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
          Text("Opción 1"),
          Text(
            "Texto desde Design Sistem",
            style: Theme.of(context).textTheme.titleLarge,
          ),
          Text("Opción 3", 
          style: TextStyle(
            color: Colors.red, 
            fontSize: 30,
            backgroundColor: Color.from(alpha: 125, red: 42, green: 86, blue: 2),
            fontWeight: FontWeight.w600,
            )),
        ],
      ),
    );
  }
}
