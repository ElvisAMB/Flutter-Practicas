import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:tienda/firebase_options.dart';
import 'package:tienda/notifier/cart_notifier.dart';
import 'package:tienda/screens/home_screen.dart';
import 'package:tienda/screens/login_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [ChangeNotifierProvider(create: (context) => CartNotifier())],
      child: MaterialApp(
        title: 'My Store',
        //locale: const Locale('es', 'ES'),
        //supportedLocales: const [Locale('en'), Locale('es')],
        // localizationsDelegates: const [
        //   GlobalMaterialLocalizations.delegate,
        //   GlobalWidgetsLocalizations.delegate,
        //   GlobalCupertinoLocalizations.delegate,
        // ],
        debugShowCheckedModeBanner: false,
        home: (FirebaseAuth.instance.currentUser == null
            ? LoginScreen()
            : HomeScreen()),
      ),
    );
  }
}
