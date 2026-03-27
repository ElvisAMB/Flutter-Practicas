import 'package:flutter/material.dart';

class PresentacionScreen extends StatelessWidget {
  const PresentacionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Flutter Layout Demo"),
        centerTitle: true,
        //backgroundColor: Colors.lightBlue,
      ),
      body: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(
          verticalDirection: VerticalDirection.down,
          children: [
            /** Imagen */
            Image.asset("images/oeschinen_lake_campground.jpg"),

            /**Titulo y Subtitulo */
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          "Oeschinen Lake Campground",
                          style: TextStyle(
                            // color: Colors.black,
                            // fontSize: 18,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        Text(
                          "Kandersteg, Switzerland",
                          style: TextStyle(
                            color: Colors.grey,
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Icon(Icons.star_rate, color: Colors.amber),
                  Text("41"),
                ],
              ),
            ),
            /**Fin Titulo y Subtitulo */

            /** Botones */
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,

              children: [
                /** 1 */
                Column(
                  children: [
                    Icon(Icons.call, color: Colors.indigo),
                    Text("CALL", style: TextStyle(color: Colors.indigo)),
                  ],
                ),
                /** Fin 1 */
                /**Icono 2 */
                Column(
                  children: [
                    Icon(Icons.fmd_good_outlined, color: Colors.indigo),
                    Text("ROUTE", style: TextStyle(color: Colors.indigo)),
                  ],
                ),
                /**Fin Icono 2 */
                /**Icono 3 */
                Column(
                  children: [
                    Icon(Icons.share_rounded, color: Colors.indigo),
                    Text("SHARE", style: TextStyle(color: Colors.indigo)),
                  ],
                ),
                /**Fin Icono 3 */
              ],
            ),

            /** Fin Botones */
            /**Inicio de texto final */
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Text(
                "Lake Oeschinen lies at the foot of the Blüemlisalp in the Bernese Alps. Situated 1,578 meters above sea level, it is one of the larger Alpine Lakes. A gondola ride from Kandersteg, followed by a half-hour walk through pastures and pine forest, leads you to the lake, which warms to 20 degrees Celsius in the summer. Activities enjoyed here include rowing, and riding the summer toboggan run.",
                style: TextStyle(
                  fontSize: 11,

                  //fontWeight: FontWeight.w600,
                ),
              ),
            ),
            /**Final de texto final */
          ],
        ),
      ),
    );
  }
}
