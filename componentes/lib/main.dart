import 'package:componentes/screens/home_screen.dart';
import 'package:flutter/material.dart';
//matapp
void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Componentes',
      debugShowCheckedModeBanner: false,
      home: HomeScreen(),
      //showSemanticsDebugger: false,
    );
  }
}