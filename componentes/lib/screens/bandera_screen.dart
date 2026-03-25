import 'package:flutter/material.dart';

class BanderaScreen extends StatelessWidget {
  const BanderaScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Contenedores"),
        centerTitle: true,
        backgroundColor: Colors.lightBlue,
      ),
      body: Container(
        width: 1000,
        height: 400,
        decoration: BoxDecoration(
          border: Border(
            left: BorderSide(width: 2, color: Colors.blueAccent),
            right: BorderSide(width: 2, color: Colors.blueAccent),
            bottom: BorderSide(width: 2, color: Colors.blueAccent),
            top: BorderSide(width: 2, color: Colors.blueAccent),
          ),
          borderRadius: BorderRadius.all(Radius.circular(10)),
        ),
        margin: EdgeInsets.all(40), //Separación externa
        padding: EdgeInsets.all(10), //Separación interna
        /**Subelementos */
        child: Row(
          children: [
            /*Imagen*/
            // Expanded(
            //   child: Column(
            //     children: [
            Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Image.network(
                  "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTS2kEKs1gOGlWdACzOm_yphJm-sf2KVeiWsQ&s",
                  height: 350,
                  //alignment: AlignmentGeometry.directional(10, 40),
                  width: 400,
                ),
              ],
              //     ),
              //   ],
              // ),
            ),
            Column(
              children: [
                Column(children: [Text("   ")]),
              ],
            ),
            /**Bandera */
            Expanded(
              child: Column(
                spacing: 0.0,
                children: [
                  /* Contenedor de amarillo */
                  Column(
                    children: [
                      Row(
                        children: [
                          Container(
                            height: 150,
                            width: 440,
                            decoration: BoxDecoration(color: Colors.yellow),
                            margin: EdgeInsets.all(0), //Separación externa
                            padding: EdgeInsets.all(0), //Separación interna
                          ),
                        ],
                      ),
                      /* Contenedor de azul */
                      Row(
                        children: [
                          Container(
                            height: 100,
                            width: 440,
                            decoration: BoxDecoration(color: Colors.blue),
                            margin: EdgeInsets.all(0), //Separación externa
                            padding: EdgeInsets.all(0), //Separación interna
                          ),
                        ],
                      ),
                      /* Contenedor de rojo */
                      Row(
                        children: [
                          Container(
                            height: 100,
                            width: 440,
                            decoration: BoxDecoration(color: Colors.red),
                            margin: EdgeInsets.all(0), //Separación externa
                            padding: EdgeInsets.all(0), //Separación interna
                          ),
                        ],
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
