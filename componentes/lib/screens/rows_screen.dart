import 'package:flutter/material.dart';

class RowsScreen extends StatelessWidget {
  const RowsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Filas"),
        centerTitle: true,
        //backgroundColor: Colors.lightBlue,
      ),
      body: Center(
        child: 
        Column(
          children: [
            ListTile(
              title: Text("Opciones"),
              subtitle: Text("Debe seleccionar una opción mostrada:"),
              //leading: Icon(Icons.account_tree_outlined),
              trailing: Icon(Icons.chevron_right),
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              crossAxisAlignment: CrossAxisAlignment.start,
              //mainAxisSize: MainAxisSize.max,
              children: [
                Text("Item 1"),
                Icon(Icons.energy_savings_leaf),
                Text("Item 2"),
                Icon(Icons.access_alarm_outlined),
                Text("Item 3"),
                Icon(Icons.zoom_out),
                Text("Item4"),
                Icon(Icons.star),
              ],
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              crossAxisAlignment: CrossAxisAlignment.start,
              //mainAxisSize: MainAxisSize.max,
              children: [
                Text("Item 5"),
                Icon(Icons.energy_savings_leaf),
                Text("Item 6"),
                Icon(Icons.access_alarm_outlined),
                Text("Item 7"),
                Icon(Icons.zoom_out),
                Text("Item 8"),
                Icon(Icons.star),
              ],
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              crossAxisAlignment: CrossAxisAlignment.start,
              //mainAxisSize: MainAxisSize.max,
              children: [
                Text("Item 9"),
                Icon(Icons.energy_savings_leaf),
                Text("Item 10"),
                Icon(Icons.access_alarm_outlined),
                Text("Item 11"),
                Icon(Icons.zoom_out),
                Text("Item 12"),
                Icon(Icons.star),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
