//import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:tienda/firebase_options.dart';
import 'package:tienda/notifier/cart_notifier.dart';
import 'package:tienda/screens/home_screen.dart';

void main() async {
   WidgetsFlutterBinding.ensureInitialized();
   await Firebase.initializeApp(
     options: DefaultFirebaseOptions.currentPlatform
   );

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [ChangeNotifierProvider(create: (context) => CartNotifier())],
      child: MaterialApp(
        //title: 'Mi tienda',
        debugShowCheckedModeBanner: false,
        home: /*FirebaseAuth.instance.currentUser == null ? 
        LoginScreen():*/ 
        HomeScreen(), //home: HomeScreen(),
      ),
    );
  }
}
