import 'package:flutter/material.dart';
import 'controllers/location_controller.dart';

void main() {
  runApp(const LocationApp());
}

class LocationApp extends StatelessWidget {
  const LocationApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Company Finder',
      theme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed: const Color(0xFF087F65),
        scaffoldBackgroundColor: const Color(0xFFF5F7FA),
        fontFamily: 'Roboto',
      ),
      home: const LocationHome(),
    );
  }
}

class LocationHome extends StatefulWidget {
  const LocationHome({super.key});

  @override
  State<LocationHome> createState() => _LocationHomeState();
}

class _LocationHomeState extends State<LocationHome> {
  late final LocationController controller;

  final locationInput = TextEditingController();
  final nameInput = TextEditingController();

  @override
  void initState() {
    super.initState();

    controller = LocationController();
    controller.addListener(_updateUI);
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      print('GET STARTED: /getcompanies/');

      await controller.getCompanies();

      print('GET COMPLETED');
      print('GET DATA: ${controller.companies}');
      print('GET ERROR: ${controller.error}');
    });
  }

  void _updateUI() {
    if (mounted) setState(() {});
  }

  @override
  void dispose() {
    controller.removeListener(_updateUI);
    controller.dispose();
    locationInput.dispose();
    nameInput.dispose();
    super.dispose();
  }

  Future<void> submitLocation() async {
    controller.setLocation(locationInput.text);
    controller.setName(nameInput.text);

    print('POST STARTED: /postlocation/');
    print('POST LOCATION: ${locationInput.text}');
    print('POST NAME: ${nameInput.text}');

    await controller.postLocation();

    print('POST COMPLETED');
    print('POST ERROR: ${controller.error}');
    print('COMPANIES AFTER POST: ${controller.companies}');

    if (!mounted) return;

    if (controller.error == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Search completed successfully'),
          backgroundColor: Color(0xFF087F65),
        ),
      );
    }
  }

  List<dynamic> get businessList {
    final data = controller.companies['data'];

    if (data is Map && data['businesses'] is List) {
      return data['businesses'] as List;
    }

    return [];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: const Row(
          children: [
            Icon(Icons.travel_explore, color: Color(0xFF087F65)),
            SizedBox(width: 10),
            Text(
              'Company Finder',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Color(0xFF172B36),
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            onPressed: controller.isLoading ? null : controller.getCompanies,
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh companies',
          ),
        ],
      ),

      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: ListView(
                padding: const EdgeInsets.all(20),
                children: [
                  // Header
                  const Text(
                    'Discover Companies',
                    style: TextStyle(
                      fontSize: 27,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF172B36),
                    ),
                  ),

                  const SizedBox(height: 7),

                  Text(
                    'Find businesses by location and company name.',
                    style: TextStyle(fontSize: 14, color: Colors.grey.shade600),
                  ),

                  const SizedBox(height: 24),

                  // Search Card
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.04),
                          blurRadius: 15,
                          offset: const Offset(0, 5),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Search Filters',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),

                        const SizedBox(height: 18),

                        TextField(
                          controller: locationInput,
                          decoration: InputDecoration(
                            labelText: 'Location',
                            hintText: 'e.g. London, UK',
                            prefixIcon: const Icon(Icons.location_on_outlined),
                            filled: true,
                            fillColor: const Color(0xFFF5F7FA),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                              borderSide: BorderSide.none,
                            ),
                          ),
                        ),

                        const SizedBox(height: 14),

                        TextField(
                          controller: nameInput,
                          decoration: InputDecoration(
                            labelText: 'Company / Business Name',
                            hintText: 'e.g. Software Companies',
                            prefixIcon: const Icon(Icons.business_outlined),
                            filled: true,
                            fillColor: const Color(0xFFF5F7FA),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                              borderSide: BorderSide.none,
                            ),
                          ),
                        ),

                        const SizedBox(height: 20),

                        SizedBox(
                          width: double.infinity,
                          height: 52,
                          child: ElevatedButton.icon(
                            onPressed: controller.isLoading
                                ? null
                                : submitLocation,
                            icon: const Icon(Icons.search),
                            label: const Text(
                              'Search Companies',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF087F65),
                              foregroundColor: Colors.white,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                          ),
                        ),

                        if (controller.isLoading) ...[
                          const SizedBox(height: 18),
                          const LinearProgressIndicator(
                            color: Color(0xFF087F65),
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            'Fetching companies...',
                            style: TextStyle(fontSize: 12),
                          ),
                        ],
                      ],
                    ),
                  ),

                  const SizedBox(height: 25),

                  // Results Header
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Companies',
                        style: TextStyle(
                          fontSize: 21,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF172B36),
                        ),
                      ),

                      Text(
                        '${businessList.length} Results',
                        style: const TextStyle(
                          color: Color(0xFF087F65),
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 15),

                  // Error
                  if (controller.error != null)
                    Container(
                      padding: const EdgeInsets.all(15),
                      margin: const EdgeInsets.only(bottom: 15),
                      decoration: BoxDecoration(
                        color: Colors.red.shade50,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        controller.error!,
                        style: const TextStyle(color: Colors.red),
                      ),
                    ),

                  // Companies
                  if (businessList.isEmpty && !controller.isLoading)
                    Container(
                      padding: const EdgeInsets.all(30),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: const Column(
                        children: [
                          Icon(
                            Icons.business_center_outlined,
                            size: 45,
                            color: Colors.grey,
                          ),
                          SizedBox(height: 12),
                          Text(
                            'No companies found',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                          SizedBox(height: 5),
                          Text(
                            'Search for a location to find companies.',
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    ),

                  ...businessList.map((item) {
                    final company = Map<String, dynamic>.from(item);

                    return Container(
                      margin: const EdgeInsets.only(bottom: 13),
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: Colors.grey.shade200),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Container(
                                height: 45,
                                width: 45,
                                decoration: BoxDecoration(
                                  color: const Color(0xFFE5F4EF),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: const Icon(
                                  Icons.business,
                                  color: Color(0xFF087F65),
                                ),
                              ),

                              const SizedBox(width: 12),

                              Expanded(
                                child: Text(
                                  company['name']?.toString() ?? 'Unknown',
                                  style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 16,
                                  ),
                                ),
                              ),
                            ],
                          ),

                          const SizedBox(height: 15),

                          if (company['category'] != null)
                            _infoRow(
                              Icons.category_outlined,
                              company['category'].toString(),
                            ),

                          if (company['address'] != null)
                            _infoRow(
                              Icons.location_on_outlined,
                              company['address'].toString(),
                            ),

                          if (company['phone'] != null)
                            _infoRow(
                              Icons.phone_outlined,
                              company['phone'].toString(),
                            ),

                          if (company['website'] != null ||
                              company['maps_url'] != null)
                            _infoRow(
                              Icons.language,
                              (company['website'] ?? company['maps_url'])
                                  .toString(),
                            ),

                          const SizedBox(height: 10),

                          Row(
                            children: [
                              const Icon(
                                Icons.star,
                                color: Colors.orange,
                                size: 19,
                              ),
                              const SizedBox(width: 5),
                              Text(
                                company['rating']?.toString() ?? 'N/A',
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(width: 5),
                              Text(
                                '(${company['reviews'] ?? 0} reviews)',
                                style: TextStyle(
                                  color: Colors.grey.shade600,
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    );
                  }),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _infoRow(IconData icon, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 17, color: const Color(0xFF087F65)),
          const SizedBox(width: 9),
          Expanded(child: Text(value, style: const TextStyle(fontSize: 13))),
        ],
      ),
    );
  }
}
