import 'package:chat_real_time/core/services/firebase_service.dart';
import 'package:dartz/dartz.dart';
import 'package:flutter/material.dart';

class UserProvider extends ChangeNotifier {
  UserProvider(this._service); //Inyeccion de dependencia
  final FirebaseService _service;
  String _email = '';
  String _pass = '';

  String get email => _email;
  String get password => _pass;

  set email(String value) {
    _email = value;
    notifyListeners();
  }

  set password(String value) {
    _pass = value;
    notifyListeners();
  }

  Future<Either<String, Unit>> login() async {
    final response = await _service.loginFirebase(
      email: _email,
      password: _pass,
    );
    return response;
  }

  Future<Either<String, Unit>> register() async {
    final response = await _service.registerFirebase(
      email: _email,
      password: _pass,
    );
    return response;
  }
}
