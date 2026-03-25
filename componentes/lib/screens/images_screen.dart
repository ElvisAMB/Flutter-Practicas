import 'package:flutter/material.dart';

class ImagesScreen extends StatelessWidget {
  const ImagesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Configuración de imagenes"),
        centerTitle: true,
        backgroundColor: Colors.lightBlue,
      ),
      body: Column(
        children: [
          // Text 1
          Text("Imagenes"),
          //subtitle: Text("Mostrar como se construyen las imagenes"),
          //leading: Icon(Icons.account_tree_outlined),
          //trailing: Icon(Icons.chevron_right),

          //Imagen
          Image.network(
            "data:image/png;base64,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",
            width: 200,
          ),

          // Image.network(
          //   "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTS2kEKs1gOGlWdACzOm_yphJm-sf2KVeiWsQ&s",
          //   width: 500,),
          Image.network(
            "https://firebasestorage.googleapis.com/v0/b/election-radar-35ba7.firebasestorage.app/o/public%2Fpexels-pixabay-459301.jpg?alt=media&token=dc9f5302-015b-4608-ad7e-bf3b4c3338ce",
            width: 500,
          ),

          //Image.network("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTS2kEKs1gOGlWdACzOm_yphJm-sf2KVeiWsQ&s"),

          //Text 2
          Text("Assets"),

          Image.asset("assets/image.png", height: 80),

          FadeInImage(
            height: 250,
            placeholder: AssetImage("assets/loading.gif"),
            image: NetworkImage(
              "https://firebasestorage.googleapis.com/v0/b/election-radar-35ba7.firebasestorage.app/o/public%2Fpexels-pixabay-459301.jpg?alt=media&token=dc9f5302-015b-4608-ad7e-bf3b4c3338ce",
              scale: 20,
            ),
          ),

          Image.asset("images/programador.jpg", height: 90),
          //Imagen

          //    ),
        ],
      ),
    );
  }
}
