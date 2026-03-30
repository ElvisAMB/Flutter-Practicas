import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Nuestra Tienda"),
        centerTitle: true,
        backgroundColor: Colors.blue,
        actions: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Icon(Icons.person),
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20.0),
          child: Column(
            crossAxisAlignment: .center,
            children: [
              SizedBox(height: 20),
              Column(
                children: [
                  Text(
                    "Coleccion 2024",
                    style: TextStyle(
                      color: Colors.grey,
                      fontSize: 12,
                      fontWeight: FontWeight.w400,
                      letterSpacing: 2,
                    ),
                  ),
                ],
              ),
              SizedBox(height: 8),
              Text(
                "Diseno Atemporal",
                style: TextStyle(
                  fontSize: 32,
                  color: Colors.black,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 30),

              //Imagen
              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadiusGeometry.circular(50),
                  child: Image.network(
                    "https://raw.githubusercontent.com/RicharC293/fake_doctors/refs/heads/master/images/producto-1.jpg",
                    height: 400,
                    fit: BoxFit.cover,
                    width: double.infinity,
                  ),
                ),
              ),

              SizedBox(height: 16),
              Text(
                "Jarron de ceramica",
                style: TextStyle(
                  fontSize: 20,
                  color: Colors.black,
                  fontWeight: FontWeight.bold,
                ),
              ),
              //Buttons
              Text("\$45", style: TextStyle(fontSize: 16, color: Colors.grey)),

              SizedBox(height: 16),

              Container(
                decoration: BoxDecoration(
                  color: Colors.deepPurpleAccent,
                  borderRadius: BorderRadius.circular(50),
                  border: Border(
                    left: BorderSide(
                      width: 190,
                      color: Colors.deepPurpleAccent,
                      //strokeAlign: BorderSide.strokeAlignCenter,
                    ),
                    right: BorderSide(
                      width: 190,
                      color: Colors.deepPurpleAccent,
                      //strokeAlign: BorderSide.strokeAlignCenter,
                    ),
                  ),
                ),
                child: Text(
                  "Anadir",
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),

              SizedBox(height: 16),


            ],
          ),
        ),
      ),
    );
  }
}
