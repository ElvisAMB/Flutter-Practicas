import 'package:flutter/material.dart';
import 'package:firebase_ui_auth/firebase_ui_auth.dart' as ui;
import 'package:tienda/screens/login_screen.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ui.ProfileScreen(
      //providers: [ui.EmailAuthProvider()],
      actions: [
        ui.SignedOutAction((context) {
          final route = MaterialPageRoute(
            builder: (context) {
              return LoginScreen();
            },
          );
          Navigator.pushReplacement(context, route, result: (_) => false);
        }),
      ],
    );
  }
}

