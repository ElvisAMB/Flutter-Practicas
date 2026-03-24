import 'package:flutter/material.dart';

void main() => runApp(const MyFirstApp());

class MyFirstApp extends StatelessWidget {
  const MyFirstApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Primera aplicación básica con FLutter',
      debugShowCheckedModeBanner: false,
      //theme: ThemeData.dark(),
      home: MyHomeScreen(),
    );
  }
}

//Configuración de una pantalla de StatelessWidget a StatefulWidget
class MyHomeScreen extends StatefulWidget {
  const MyHomeScreen({super.key});

  @override
  State<MyHomeScreen> createState() => _MyHomeScreenState();
}

class _MyHomeScreenState extends State<MyHomeScreen> {
  //Variable
  int _contador = 0;
  //Métodos
  // int _incrementarContador(int contador) {
  //   return contador + 1;
  // }

  void _ejecutarSuma() {
    _contador++;
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'Inicio',
          style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        backgroundColor: Colors.blue,
      ),
      body: Center(
        child: Text(
          (_contador > 0 ? "Se ha presionado el boton $_contador veces" : ""),
          style: TextStyle(fontSize: 15, fontWeight: FontWeight.normal),
        ),
      ),
      extendBody: true,
      floatingActionButton: FloatingActionButton(
        // onPressed: () {
        //   // _contador = _incrementarContador(_contador);
        //   // setState(() { });
        //   _ejecutarSuma();
        //   //print(_contador);
        // },
        onPressed: _ejecutarSuma,
        child: Icon(Icons.add), //child: Text("Agregar"),
      ),
    ); //Inicio de toda pantalla
  }
} //_MyHomeScreenState

//
class AddValue extends StatefulWidget {
  const AddValue({super.key});

  @override
  State<AddValue> createState() => _AddValueState();
}

class _AddValueState extends State<AddValue> {
  @override
  Widget build(BuildContext context) {
    return const Placeholder();
  }
}
