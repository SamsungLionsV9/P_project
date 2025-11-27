import 'package:flutter/material.dart';
import '../models/car_data.dart';

/// 차량 비교 상태 관리 Provider
class ComparisonProvider extends ChangeNotifier {
  final List<CarData> _comparingCars = [];
  static const int maxCompareCount = 3;

  List<CarData> get comparingCars => List.unmodifiable(_comparingCars);
  int get compareCount => _comparingCars.length;
  bool get canAddMore => _comparingCars.length < maxCompareCount;
  bool get hasEnoughToCompare => _comparingCars.length >= 2;

  /// 비교 목록에 차량 추가 (인덱스 기반 고유 색상 할당)
  bool addCar(CarData car) {
    if (_comparingCars.length >= maxCompareCount) {
      return false;
    }
    if (_comparingCars.any((c) => c.id == car.id)) {
      return false; // 이미 추가됨
    }
    // 인덱스 기반 고유 색상 할당 (감가율 차트에서 구분 가능하도록)
    final coloredCar = car.copyWith(
      color: CarData.getColorByIndex(_comparingCars.length),
    );
    _comparingCars.add(coloredCar);
    notifyListeners();
    return true;
  }

  /// 비교 목록에서 차량 제거
  void removeCar(CarData car) {
    _comparingCars.removeWhere((c) => c.id == car.id);
    notifyListeners();
  }

  /// 비교 목록에 있는지 확인
  bool isComparing(CarData car) {
    return _comparingCars.any((c) => c.id == car.id);
  }

  /// ID로 비교 목록 확인
  bool isComparingById(String id) {
    return _comparingCars.any((c) => c.id == id);
  }

  /// 비교 목록 토글
  bool toggleCompare(CarData car) {
    if (isComparing(car)) {
      removeCar(car);
      return false;
    } else {
      return addCar(car);
    }
  }

  /// 비교 목록 초기화
  void clear() {
    _comparingCars.clear();
    notifyListeners();
  }

  /// 가격 비교 결과 계산
  Map<String, dynamic> getPriceComparison() {
    if (_comparingCars.isEmpty) {
      return {'error': '비교할 차량이 없습니다'};
    }

    final prices = _comparingCars.map((c) => c.priceValue).toList();
    final minPrice = prices.reduce((a, b) => a < b ? a : b);
    final maxPrice = prices.reduce((a, b) => a > b ? a : b);
    final avgPrice = prices.reduce((a, b) => a + b) / prices.length;

    final cheapest = _comparingCars.firstWhere((c) => c.priceValue == minPrice);
    final mostExpensive = _comparingCars.firstWhere((c) => c.priceValue == maxPrice);

    return {
      'cheapest': cheapest,
      'mostExpensive': mostExpensive,
      'priceDifference': maxPrice - minPrice,
      'averagePrice': avgPrice,
      'cars': _comparingCars.map((c) => {
        'car': c,
        'price': c.priceValue,
        'diffFromCheapest': c.priceValue - minPrice,
        'percentFromAvg': ((c.priceValue - avgPrice) / avgPrice * 100).toStringAsFixed(1),
      }).toList(),
    };
  }
}
