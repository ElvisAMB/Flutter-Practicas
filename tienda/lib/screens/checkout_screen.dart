import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:tienda/notifier/cart_notifier.dart';
import 'package:tienda/services/firestore_service.dart';

class CheckoutScreen extends StatefulWidget {
  const CheckoutScreen({super.key});

  @override
  State<CheckoutScreen> createState() => _CheckoutScreenState();
}

class _CheckoutScreenState extends State<CheckoutScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nombreController = TextEditingController();
  final _emailController = TextEditingController();
  final _direccionController = TextEditingController();
  final _ciudadController = TextEditingController();

  int _metodoPago = 0; // 0: Tarjeta, 1: Transferencia, 2: Efectivo

  @override
  void dispose() {
    _nombreController.dispose();
    _emailController.dispose();
    _direccionController.dispose();
    _ciudadController.dispose();
    super.dispose();
  }

  Future<void> _confirmarPedido() async {
    // ignore: avoid_print
    print(_formKey.toString());
    if (!_formKey.currentState!.validate()) return;
    // Servicio
    final cart = context.read<CartNotifier>();
    //Guardar en la base de datos
    await FirestoreService().createOrder(
      cart.cartProducts,
      cart.envio,
      cart.total,
      _nombreController.text,
      _emailController.text,
      _direccionController.text,
      _ciudadController.text,
      (_metodoPago == 0 ? "Tarjeta de Crédito" : (_metodoPago == 1 ? "Transferencia Bancaria" : "Efectivo")),
    );

    if (!mounted) return;

    context.read<CartNotifier>().clearCart();

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              decoration: BoxDecoration(
                color: Color(0xFFE8DEF8),
                shape: BoxShape.circle,
              ),
              padding: EdgeInsets.all(16),
              child: Icon(
                Icons.check_rounded,
                color: Colors.deepPurpleAccent,
                size: 40,
              ),
            ),
            SizedBox(height: 16),
            Text(
              "¡Pedido confirmado!",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 8),
            Text(
              "Tu pedido ha sido recibido. Te enviaremos una confirmación pronto.",
              textAlign: TextAlign.center,
              style: TextStyle(color: Color(0xff79767B)),
            ),
          ],
        ),
        actions: [
          SizedBox(
            width: double.infinity,
            child: FilledButton(
              onPressed: () {
                Navigator.of(ctx).pop();
                Navigator.of(context).popUntil((route) => route.isFirst);
              },
              child: Text("Go to Start"),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final cart = context.watch<CartNotifier>();

    return Scaffold(
      appBar: AppBar(title: Text("Checkout"), centerTitle: true),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: EdgeInsets.all(16),
          children: [
            // Sección datos de envío
            _SectionTitle(title: "Delivery Information"),
            SizedBox(height: 12),
            _CampoTexto(
              controller: _nombreController,
              label: "Nombres completos",
              hint: "Nombres completos",
              icon: Icons.person_outline,
              validator: (v) =>
                  (v == null || v.trim().isEmpty) ? "Ingresa tu nombre" : null,
            ),
            SizedBox(height: 12),
            _CampoTexto(
              controller: _emailController,
              label: "correo@ejemplo.com",
              hint: "Correo electrónico",
              icon: Icons.email_outlined,
              keyboardType: TextInputType.emailAddress,
              validator: (v) {
                if (v == null || v.trim().isEmpty) return "Ingresa tu correo";
                if (!v.contains('@')) return "Correo inválido";
                return null;
              },
            ),
            SizedBox(height: 12),
            _CampoTexto(
              controller: _direccionController,
              label: "Dirección",
              hint: "Dirección",
              icon: Icons.location_on_outlined,
              validator: (v) => (v == null || v.trim().isEmpty)
                  ? "Ingresa tu dirección"
                  : null,
            ),
            SizedBox(height: 12),
            _CampoTexto(
              controller: _ciudadController,
              label: "Ciudad / Estado",
              hint: "Ciudad / Estado",
              icon: Icons.location_city_outlined,
              validator: (v) =>
                  (v == null || v.trim().isEmpty) ? "Ingresa tu ciudad" : null,
            ),

            SizedBox(height: 24),

            // Sección método de pago
            _SectionTitle(title: "Método de pago"),
            SizedBox(height: 12),
            Container(
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey.withAlpha(200)),
                color: Color(0xfff7f2fa),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                children: [
                  _MetodoPagoItem(
                    value: 0,
                    groupValue: _metodoPago,
                    label: "Tarjeta de crédito / débito",
                    icon: Icons.credit_card_outlined,
                    onChanged: (v) => setState(() => _metodoPago = v!),
                  ),
                  Divider(height: 1, indent: 16, endIndent: 16),
                  _MetodoPagoItem(
                    value: 1,
                    groupValue: _metodoPago,
                    label: "Transferencia bancaria",
                    icon: Icons.account_balance_outlined,
                    onChanged: (v) => setState(() => _metodoPago = v!),
                  ),
                  Divider(height: 1, indent: 16, endIndent: 16),
                  _MetodoPagoItem(
                    value: 2,
                    groupValue: _metodoPago,
                    label: "Efectivo al recibir",
                    icon: Icons.payments_outlined,
                    onChanged: (v) => setState(() => _metodoPago = v!),
                  ),
                ],
              ),
            ),

            SizedBox(height: 24),

            // Resumen del pedido
            _SectionTitle(title: "Resumen del pedido"),
            SizedBox(height: 12),
            Container(
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey.withAlpha(200)),
                color: Color(0xfff7f2fa),
                borderRadius: BorderRadius.circular(12),
              ),
              padding: EdgeInsets.all(16),
              child: Column(
                children: [
                  ...cart.cartProducts.map(
                    (p) => Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(
                            child: Text(
                              p.name,
                              style: TextStyle(color: Color(0xff79767B)),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          Text(
                            "\$${p.price.toStringAsFixed(2)}",
                            style: TextStyle(fontWeight: FontWeight.w600),
                          ),
                        ],
                      ),
                    ),
                  ),
                  Divider(),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        "Subtotal",
                        style: TextStyle(
                          fontWeight: FontWeight.w600,
                          color: Color(0xff79767B),
                        ),
                      ),
                      Text(
                        "\$${cart.subtotal.toStringAsFixed(2)}",
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  SizedBox(height: 4),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        "Send",
                        style: TextStyle(
                          fontWeight: FontWeight.w600,
                          color: Color(0xff79767B),
                        ),
                      ),
                      Text(
                        "\$${cart.envio}",
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.blueGrey,
                        ),
                      ),
                    ],
                  ),
                  Divider(),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        "Total",
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        "\$${cart.total.toStringAsFixed(2)}",
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            SizedBox(height: 24),

            // Botón confirmar
            FilledButton(
              onPressed: _confirmarPedido,
              child: Padding(
                padding: EdgeInsets.symmetric(vertical: 4),
                child: Text("Confirmar pedido", style: TextStyle(fontSize: 16)),
              ),
            ),
            SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle({required this.title});

  final String title;

  @override
  Widget build(BuildContext context) {
    return Text(
      title,
      style: TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.bold,
        letterSpacing: 0.5,
      ),
    );
  }
}

class _CampoTexto extends StatelessWidget {
  const _CampoTexto({
    required this.controller,
    required this.label,
    required this.hint,
    required this.icon,
    required this.validator,
    this.keyboardType,
  });

  final TextEditingController controller;
  final String label;
  final String hint;
  final IconData icon;
  final String? Function(String?) validator;
  final TextInputType? keyboardType;

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      validator: validator,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        prefixIcon: Icon(icon),
        filled: true,
        fillColor: Color(0xfff7f2fa),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.grey.withAlpha(200)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.grey.withAlpha(200)),
        ),
      ),
    );
  }
}

class _MetodoPagoItem extends StatelessWidget {
  const _MetodoPagoItem({
    required this.value,
    required this.groupValue,
    required this.label,
    required this.icon,
    required this.onChanged,
  });

  final int value;
  final int groupValue;
  final String label;
  final IconData icon;
  final void Function(int?) onChanged;

  @override
  Widget build(BuildContext context) {
    return RadioListTile<int>(
      value: value,
      // ignore: deprecated_member_use
      groupValue: groupValue,
      // ignore: deprecated_member_use
      onChanged: onChanged,
      activeColor: Colors.deepPurpleAccent,
      title: Row(
        spacing: 8,
        children: [
          Icon(icon, size: 20, color: Color(0xff79767B)),
          Text(label, style: TextStyle(fontSize: 14)),
        ],
      ),
    );
  }
}
