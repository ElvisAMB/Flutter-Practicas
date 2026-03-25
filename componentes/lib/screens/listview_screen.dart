import 'package:flutter/material.dart';

class ListViewScreen extends StatelessWidget {
  const ListViewScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Manejo de listas"),
        centerTitle: true,
        backgroundColor: Colors.lightBlue,
        //leading: Icon(Icons.arrow_back_rounded),
      ),

      // body: ListView(
      //   children: [
      //     Image.asset("assets/image.png", height: 400,),
      //     Image.asset("assets/image.png"),
      //     Image.asset("images/programador.jpg"),
      //     Image.asset("assets/image.png"),
      //     Image.asset("assets/image.png"),
      //     Image.asset("assets/image.png"),
      //     Image.asset("assets/image.png"),
      //     Image.asset("assets/image.png"),
      //   ],
      // )
      body: ListView.separated(
        itemCount: 20,
        separatorBuilder: (context, index) {
          return Divider();
        },
        itemBuilder: (context, index) {
          //Para crear un mismo diseño, se crea una lista infinita
          //return Image.asset("assets/image.png");
          return Card(
            child: Padding(
              padding: const EdgeInsets.all(8.0),
              child: Text("Elemento: $index"),
            ),
          );
        },
      ),
    );
  }
}
