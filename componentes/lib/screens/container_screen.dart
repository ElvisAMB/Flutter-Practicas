import 'package:flutter/material.dart';

class ContainerScreen extends StatelessWidget {
  const ContainerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Contenedores"),
        centerTitle: true,
        backgroundColor: Colors.lightBlue,
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          //Container 1
          Container(
            width: 350, //  double.infinity, //Ocupe todo lo definido  //1800,
            //height: 400,
            //color: Colors.yellowAccent, //No se puede usar en conjunto con la propiedad Decoration
            decoration: BoxDecoration(
              color: Colors.lightBlue,
              border: Border(
                left: BorderSide(
                  width: 2,
                  color: Colors.blueAccent,
                  //strokeAlign: BorderSide.strokeAlignCenter,
                ),
              ),
              //borderRadius: BorderRadius.circular(40),
              borderRadius: BorderRadius.all(Radius.circular(8)),
            ),
            margin: EdgeInsets.all(10), //Separación externa
            padding: EdgeInsets.all(10), //Separación interna
            child: Column(
              children: [
                //Titulo Nombre del estudiante
                Row(
                  children: [
                    //Expanded(child: Icon(Icons.work_outline_rounded)),
                    Expanded(child: Text("Elvis Mora", style: TextStyle(fontSize: 25),textAlign: .center,)),
                  ],
                ),
                //Descripción del estudiante
                Row(
                  //spacing: 50,
                  children: [
                    Expanded(child: Icon(Icons.access_alarm_sharp)),
                    Expanded(  //Para que ajuste el texto que es extenso
                      child: Text(
                        "Desarrollador en práctica de Flutter, ingeniero en sistemas computacionales",
                        style: TextStyle(fontSize: 20),
                      ),
                    ),
                  ],
                ),
              ],
            ),
            // Row(
            //   children: [
            //     Icon(Icons.monetization_on_outlined),
            //     Text("   "),
            //     Text("Configuración de un contenedor"),
            //   ],
            // ),
          ),
          // //Container 2
          // Container(
          //   width: 1500,
          //   height: 200,
          //   //color: Colors.yellowAccent, //No se puede usar en conjunto con la propiedad Decoration
          //   decoration: BoxDecoration(
          //     color: Colors.blue,
          //     border: Border(
          //       left: BorderSide(
          //         width: 2,
          //         color: Colors.blueAccent,
          //         //strokeAlign: BorderSide.strokeAlignCenter,
          //       ),
          //     ),
          //     //borderRadius: BorderRadius.circular(40),
          //     borderRadius: BorderRadius.all(Radius.circular(10)),
          //   ),
          //   child: Row(
          //     children: [
          //       Icon(Icons.monetization_on_outlined),
          //       Text("   "),
          //       Text("Configuración de un contenedor"),
          //     ],
          //   ),
          // ),
          // //Container 3
          // Container(
          //   width: 1200,
          //   height: 200,
          //   //color: Colors.yellowAccent, //No se puede usar en conjunto con la propiedad Decoration
          //   decoration: BoxDecoration(
          //     color: Colors.red,
          //     border: Border(
          //       left: BorderSide(
          //         width: 2,
          //         color: Colors.blueAccent,
          //         //strokeAlign: BorderSide.strokeAlignCenter,
          //       ),
          //     ),
          //     //borderRadius: BorderRadius.circular(40),
          //     borderRadius: BorderRadius.all(Radius.circular(10)),
          //   ),
          //   child: Row(
          //     children: [
          //       Icon(Icons.monetization_on_outlined),
          //       Text("   "),
          //       Text("Configuración de un contenedor"),
          //     ],
          //   ),
          // ),
        ],
      ),

      // body: Column(
      //   children: [
      //     ListTile(
      //       title: Text("Columnas"),
      //       subtitle: Text("Mostrar como se construyen las contenedores"),
      //       //leading: Icon(Icons.account_tree_outlined),
      //       trailing: Icon(Icons.chevron_right),
      //     ),

      //     Container(
      //       width: 150,
      //       height: 200,
      //       color: Colors.blue,
      //       padding: EdgeInsets.all(100),
      //       //alignment: Alignment(50, 10),
      //       decoration: BoxDecoration(
      //         color: Colors.yellow,
      //         borderRadius: BorderRadius.circular(20),
      //         border: Border.all(color: const Color.fromARGB(255, 168, 17, 17), width: 10),
      //       ),
      //       child: Text("Into de container"),
      //     ),
      //   ],
      // ),
    );
  }
}
