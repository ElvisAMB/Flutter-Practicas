import 'package:flutter/material.dart';

class ColumnsScreen extends StatelessWidget {
  const ColumnsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Configuración de columnas"),
        centerTitle: true,
        backgroundColor: Colors.lightBlue,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: .spaceAround, //Para manejar las alineaciones
          crossAxisAlignment: .center, //Para los elementos internos
          mainAxisSize: MainAxisSize.min, //Para que la columna ocupe todo el espacio
          spacing: 40.5,
          children: [
            SizedBox(height: 20,),   //Caja vacía
            //Elemento 1
            Text("Elemento 1 que pueden contener en la columna"),
            SizedBox(height: 20,),
            //Elemento 2
            Text("Elemento 2"),
            SizedBox(height: 10,),
            //Elemento 3
            Text("Elemento 3"),
            SizedBox(height: 0,),
            //Elemento 4
            Text("Elemento 4"),
          ],
        ),
      ),
    );
  }
}
