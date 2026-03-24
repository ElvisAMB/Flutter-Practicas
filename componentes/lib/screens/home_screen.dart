import 'package:componentes/screens/columns_screen.dart';
import 'package:componentes/screens/container_screen.dart';
import 'package:componentes/screens/images_screen.dart';
import 'package:componentes/screens/listview_screen.dart';
import 'package:componentes/screens/navigate_screen.dart';
import 'package:componentes/screens/rows_screen.dart';
import 'package:componentes/screens/text_screen.dart';
import 'package:flutter/material.dart';

//STL
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Inicio", style: TextStyle(color: Colors.white)),
        centerTitle: true,
        backgroundColor: Colors.lightBlue,
        forceMaterialTransparency: true,
      ),
      body: Column(
        children: [
          //ListTile 1 - Columnas
          ListTile(
            title: Text("Columnas"),
            subtitle: Text("Mostrar como se construyen las columnas"),
            leading: Icon(Icons.account_tree_outlined),
            trailing: Icon(Icons.chevron_right),
            onTap: () {
              //navigator/Configuración de navegación a través de la invocación de una clase columns_screen.dart
              final route = MaterialPageRoute(
                builder: (context) => ColumnsScreen(),
              );
              Navigator.push(
                context,
                route,
              ); //Si tiene push se crear automáticamente la navegación hacia atrás
            },
          ),
          //ListTile 1 - Filas
          ListTile(
            title: Text("Filas"),
            subtitle: Text("Mostrar como se construyen las filas"),
            leading: Icon(Icons.ac_unit_rounded),
            trailing: Icon(Icons.chevron_right),
            
            onTap: () {
              //navigator/Configuración de navegación a través de la invocación de una clase columns_screen.dart
              final route = MaterialPageRoute(
                builder: (context) => RowsScreen(),
              );
              Navigator.push(
                context,
                route,
              ); //Si tiene push se crear automáticamente la navegación hacia atrás
            },
          ),
          //ListTile 1 - Containers
          ListTile(
            title: Text("Contenedor"),
            subtitle: Text("Mostrar como se construye el Contenedor"),
            leading: Icon(Icons.confirmation_num),
            trailing: Icon(Icons.chevron_right),
            onTap: () {
              //navigator/Configuración de navegación a través de la invocación de una clase columns_screen.dart
              final route = MaterialPageRoute(
                builder: (context) => ContainerScreen(),
              );
              Navigator.push(
                context,
                route,
              ); //Si tiene push se crear automáticamente la navegación hacia atrás
            },
          ),
          //ListTile 1 - Imagenes
          ListTile(
            title: Text("Imagen"),
            subtitle: Text("Mostrar como se construyen la Imagen"),
            leading: Icon(Icons.image),
            trailing: Icon(Icons.chevron_right),
            onTap: () {
              //navigator/Configuración de navegación a través de la invocación de una clase columns_screen.dart
              final route = MaterialPageRoute(
                builder: (context) => ImagesScreen(),
              );
              Navigator.push(
                context,
                route,
              ); //Si tiene push se crear automáticamente la navegación hacia atrás
            },
          ),
          //ListTile 1 - ListView
          ListTile(
            title: Text("Lista"),
            subtitle: Text("Mostrar como se construyen las listas"),
            leading: Icon(Icons.list),
            trailing: Icon(Icons.chevron_right),
            onTap: () {
              //navigator/Configuración de navegación a través de la invocación de una clase columns_screen.dart
              final route = MaterialPageRoute(
                builder: (context) => ListViewScreen(),
              );
              Navigator.push(
                context,
                route,
              ); //Si tiene push se crear automáticamente la navegación hacia atrás
            },
          ),
          //ListTile 1 - Navegacion
          ListTile(
            title: Text("Navegacion"),
            subtitle: Text("Mostrar como se construyen las Navegacion"),
            leading: Icon(Icons.assistant_navigation),
            trailing: Icon(Icons.chevron_right),
            onTap: () {
              //navigator/Configuración de navegación a través de la invocación de una clase columns_screen.dart
              final route = MaterialPageRoute(
                builder: (context) => NavigateScreen(),
              );
              Navigator.push(
                context,
                route,
              ); //Si tiene push se crear automáticamente la navegación hacia atrás
            },
          ),
          ListTile(
            title: Text("Textos"),
            subtitle: Text("Mostrar como se construyen las Textos"),
            leading: Icon(Icons.text_fields),
            trailing: Icon(Icons.chevron_right),
            onTap: () {
              //navigator/Configuración de navegación a través de la invocación de una clase columns_screen.dart
              final route = MaterialPageRoute(
                builder: (context) => TextScreen(),
              );
              Navigator.push(
                context,
                route,
              ); //Si tiene push se crear automáticamente la navegación hacia atrás
            },
          ),
        ],
      ),
    );
  }
}
