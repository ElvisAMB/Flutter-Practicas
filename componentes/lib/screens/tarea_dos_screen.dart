import 'package:flutter/material.dart';

class PresentacionScreen extends StatelessWidget {
  const PresentacionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Implementación de conocimientos"),
        centerTitle: true,
        backgroundColor: Colors.lightBlue,
      ),
      body: Container(
        decoration: BoxDecoration(
          border: BoxBorder.all(color: Colors.black),
          borderRadius: BorderRadius.all(Radius.circular(10)),
          //backgroundBlendMode: BlendMode.difference,
        ),
        margin: EdgeInsets.all(10), //Separación externa
        padding: EdgeInsets.all(20),
        child: Column(
          verticalDirection: VerticalDirection.down,
          children: [
            /**Texto de cabecera*/
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  "Flutter layout demo",
                  style: TextStyle(
                    //color: Colors.red,
                    fontSize: 20,
                    height: 3,
                    backgroundColor: Color.from(
                      alpha: 125,
                      red: 42,
                      green: 86,
                      blue: 2,
                    ),
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),

            /** Imagen */
            Column(
              children: [
                Image.asset(
                  "assets/image.png",
                  fit: BoxFit.scaleDown,
                  width: 80,
                  //height: 100,
                  //alignment: Alignment.center,
                  //fit: BoxFit.fill,
                ),
                Text("Imagen a mostrar"),
              ],
            ),

            /**Titulo y Subtitulo */
            Column(
              mainAxisAlignment: MainAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      "Oeschinen Lake Campground",
                      style: TextStyle(
                        color: Colors.black,
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
                /**Estrella con valor */
                Row(
                  children: [
                    Text(
                      "Kandersteg, Switzerland",
                      style: TextStyle(
                        color: Colors.grey,
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Icon(Icons.star_rate, color: Colors.orange, size: 35),
                    Text("41"),
                  ],
                ),
              ],
            ),
            /**Separador */

            /** Íconos */
            Row(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.center,
              spacing: 60,
              children: [
                Icon(Icons.call, color: Colors.deepPurple, size: 35),
                Icon(
                  Icons.arrow_outward_rounded,
                  color: Colors.deepPurple,
                  size: 35,
                ),
                Icon(Icons.share, color: Colors.deepPurple, size: 35),
              ],
            ),
            /** Texto descriptivo */
            Expanded(
              child: Text(
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus vitae mattis urna. Ut vitae enim fermentum, vulputate turpis eu, finibus turpis. Vestibulum dui mi, sollicitudin ac mi non, finibus cursus nulla. Quisque vel commodo sapien, a iaculis nisi. Donec a eros porta, bibendum felis elementum, congue lectus. Vestibulum vestibulum arcu pharetra facilisis iaculis. Etiam viverra nec leo sed venenatis. Ut nec erat sit amet odio sagittis commodo. Pellentesque consectetur pulvinar varius. Integer mollis blandit ante non facilisis. Duis pharetra a nulla ac semper.",
              ),
            ),
          ],
        ),
      ),
    );
  }
}
