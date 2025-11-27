import 'package:flutter/material.dart';
import '../models/car_data.dart';

class ComparisonProvider extends ChangeNotifier {
  final List<CarData> _comparingCars = [];

  List<CarData> get comparingCars => _comparingCars;

  void addCar(CarData car) {
    if (_comparingCars.length >= 3) {
      // 최대 3대까지만 비교 가능
      return;
    }
    if (!_comparingCars.contains(car)) {
      _comparingCars.add(car);
      notifyListeners();
    }
  }

  void removeCar(CarData car) {
    _comparingCars.remove(car);
    notifyListeners();
  }

  bool isComparing(CarData car) {
    return _comparingCars.contains(car);
  }

  void clear() {
    _comparingCars.clear();
    notifyListeners();
  }
}
