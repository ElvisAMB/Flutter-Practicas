// ignore_for_file: avoid_print

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
            Text("My Orders", style: TextStyle(fontSize: 30)),
            Text("Check and admin your orders"),
            FutureBuilder(
              future: FirestoreService().getOrders(),
              builder: (context, snapshot) {
                //Controlar el error
                if (snapshot.hasError) {
                  return Text("Ha ocurrido un error ${snapshot.data}");
                }
                // //validar si existen datos
                if (!snapshot.hasData) {
                  return Text("No existen datos");
                }
                // //Mostrar datos
                final data = snapshot.data ?? [];
                
                return Expanded(
                  child: ListView.builder(
                    shrinkWrap: true,
                    itemBuilder: (context, index) {
                      final order = data[index];
                      //print(order);
                      return Card(
                        child: Padding(
                          padding: const EdgeInsets.all(14.0),
                          child: Column(
                            crossAxisAlignment: .start,
                            children: [
                              Text("ID: ${order.id}"),
                              Text(
                                "Did it at ${order.createdDate.toIso8601String()}",
                              ),
                              Divider(),
                              Row(
                                children: [
                                  Expanded(child: Text("Total")),
                                  Text("\$${order.total}"),
                                ],
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}
