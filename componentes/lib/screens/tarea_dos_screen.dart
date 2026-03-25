import 'package:flutter/material.dart';

class PresentacionScreen extends StatelessWidget {
  const PresentacionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Tarea"),
        centerTitle: true,
        backgroundColor: Colors.lightBlue,
      ),
      body: Container(
        decoration: BoxDecoration(
          border: Border(
            left: BorderSide(width: 2, color: Colors.black),
            bottom: BorderSide(width: 2, color: Colors.black),
          ),
        ),
        margin: EdgeInsets.all(4), //Separación externa
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
                    fontSize: 20,
                    height: 2,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),

            /** Imagen */
            Column(
              children: [
                Image.asset(
                  "images/oeschinen_lake_campground.jpg", //"assets/image.png",
                  fit: BoxFit.scaleDown,
                  width: 450,

                  //height: 500,
                ),
                //Text("Imagen a mostrar"),
              ],
            ),
            Padding(padding: EdgeInsetsGeometry.all(5)),
            /**Titulo y Subtitulo */
            Column(
              mainAxisAlignment: MainAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
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
                //Padding(padding: EdgeInsetsGeometry.all(2)),
                /**Estrella con valor */
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                                        Text(
                      "Kandersteg, Switzerland",
                      style: TextStyle(
                        color: Colors.grey,
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Padding(padding: EdgeInsetsGeometry.all(4)),
                    Icon(Icons.star_rate, color: Colors.orange, size: 35),
                    Text("41"),
                  ],
                ),
              ],
            ),
            /**Separador */
            Padding(padding: EdgeInsetsGeometry.all(4)),
            /** Íconos */
            Row(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.center,
              spacing: 60,
              children: [
                /**Icono 1 */
                Column(
                  children: [
                    Icon(Icons.call, color: Colors.deepPurple, size: 25),
                    Text(
                      "CALL",
                      style: TextStyle(
                        fontSize: 10,

                        //fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
                /**Icono 2 */
                Column(
                  children: [
                    Icon(
                      Icons.fmd_good_outlined,
                      color: Colors.deepPurple,
                      size: 25,
                    ),
                    Text(
                      "ROUTE",
                      style: TextStyle(
                        fontSize: 10,

                        //fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
                /**Icono 3 */
                Column(
                  children: [
                    Icon(Icons.share, color: Colors.deepPurple, size: 25),
                    Text(
                      "SHARE",
                      style: TextStyle(
                        fontSize: 10,

                        //fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            Padding(padding: EdgeInsetsGeometry.all(6)),
            /** Texto descriptivo */
            Expanded(
              child: Text(
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus vitae mattis urna. Ut vitae enim fermentum, vulputate turpis eu, finibus turpis. Vestibulum dui mi, sollicitudin ac mi non, finibus cursus nulla. Quisque vel commodo sapien, a iaculis nisi.",
                style: TextStyle(
                  fontSize: 11,

                  //fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
