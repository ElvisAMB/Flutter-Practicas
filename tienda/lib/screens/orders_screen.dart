import 'package:flutter/material.dart';
import 'package:tienda/services/firestore_service.dart';

class OrdersScreen extends StatelessWidget {
  const OrdersScreen({super.key});

  @override
  Widget build(BuildContext context) {
    //FirestoreService().getInvoices();
    return Scaffold(
      //Permite crear una pantalla
      appBar: AppBar(title: Text("Orders List"), centerTitle: true),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: .start,
          crossAxisAlignment: .start,
          children: [
            Text("My Orders", style: TextStyle(fontSize: 34)),
            Text("Check and admin your orders"),
            FutureBuilder(
              future: FirestoreService().getOrders(),
              builder: (context, snapshot) {
                //Controlar el error
                 if (snapshot.hasError) {
                   return Text("Ha ocurrido un error ${snapshot.data}");
                 }
                // //validar si existen datos
                 if (!snapshot.hasData) {return Text("No existen datos");}

                // //Mostrar datos
                 final data = snapshot.data ?? [];
                 return Text("Existen datos $data");
                //if(snapshot.hasError){
                //print(snapshot);
                //}

                //return SizedBox();






              },
            ),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(14.0),
                child: Column(
                  crossAxisAlignment: .start,
                  children: [
                    Text("Id: juwoijKJKJlkjp4647we65f4s56df"),
                    Text("Completed on April 26, 2026"),
                    Divider(),
                    Row(
                      children: [
                        Expanded(child: Text("Total")),
                        Text("\$245.00"),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
