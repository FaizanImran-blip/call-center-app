import 'package:flutter/material.dart';
import '../services/location_api.dart';

class LocationController extends ChangeNotifier {
  final LocationApi api = LocationApi();

  // POST inputs
  String location = '';
  String name = '';

  // GET JSON response
  Map<String, dynamic> companies = {};

  bool isLoading = false;
  String? error;

  // POST input setters
  void setLocation(String value) {
    location = value;
    notifyListeners();
  }

  void setName(String value) {
    name = value;
    notifyListeners();
  }

  // GET companies JSON
  Future<void> getCompanies() async {
    isLoading = true;
    error = null;
    notifyListeners();

    try {
      companies = await api.getCompanies();
    } catch (e) {
      error = e.toString();
    }

    isLoading = false;
    notifyListeners();
  }

  // POST location and name
  Future<void> postLocation() async {
    if (location.trim().isEmpty || name.trim().isEmpty) {
      error = 'Location and name are required';
      notifyListeners();
      return;
    }

    isLoading = true;
    error = null;
    notifyListeners();

    try {
      await api.postLocation(location.trim(), name.trim());

      await getCompanies();
    } catch (e) {
      error = e.toString();
      isLoading = false;
      notifyListeners();
    }
  }
}
