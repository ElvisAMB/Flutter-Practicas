import 'package:dio/dio.dart';
import 'package:tienda/models/product_model.dart';

class ProductService {
  final dio = Dio();

  Future<List<ProductModel>> getProducts() async {
    final response = await dio.get(
      "https://my-json-server.typicode.com/RicharC293/fake_doctors/products",
    );

    final List<ProductModel> products = (response.data as List)
        .map((e) => ProductModel.fromJson(e as Map<String, dynamic>))
        .toList();

    return products;
  } // final de getProducts
}
