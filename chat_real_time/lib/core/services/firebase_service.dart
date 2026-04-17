import 'package:dartz/dartz.dart';
import 'package:firebase_auth/firebase_auth.dart';

class FirebaseService {
  const FirebaseService(this.firebaseAuth);

  final FirebaseAuth firebaseAuth;

  Future<Either<String, Unit>> loginFirebase({
    required String email,
    required String password,
  }) async {
    try {
      await FirebaseAuth.instance.signInWithEmailAndPassword(
        email: email,
        password: password,
      );
      return right(unit);
    } catch (error) {
      return left(error.toString());
    }
  }

  Future<Either<String, Unit>> registerFirebase({
    required String email,
    required String password,
  }) async {
    try {
      await FirebaseAuth.instance.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );
      return right(unit);
    } catch (error) {
      return left(error.toString());
    }
  }
}
