import 'package:dio/dio.dart';
import 'package:tienda/models/product_model.dart';

class ProductService {
  final dio = Dio();

  void getProducts() async {
    final response = await dio.get(
      "https://my-json-server.typicode.com/RicharC293/fake_doctors/products",
    );

    final List<ProductModel> products = (response.data as List)
        .map((e) => ProductModel.fromJson(e as Map<String, dynamic>))
        .toList();

    

    print(products.first);
    
  }// final de getProducts
}
