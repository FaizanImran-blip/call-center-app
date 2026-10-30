import 'dart:convert';
import 'package:http/http.dart' as http;

class LocationApi {
  static const String baseUrl = 'http://10.0.2.2:8000';

  // POST: Location + Name
  Future<Map<String, dynamic>> postLocation(
    String location,
    String name,
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl/postlocation/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'location': location, 'name': name}),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }

    throw Exception('POST Error: ${response.statusCode} ${response.body}');
  }

  // GET: Complete Companies JSON
  Future<Map<String, dynamic>> getCompanies() async {
    final response = await http.get(Uri.parse('$baseUrl/getcompanies/'));

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }

    throw Exception('GET Error: ${response.statusCode} ${response.body}');
  }
}
