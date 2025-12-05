import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';

class FavoritesProvider extends ChangeNotifier {
  final ApiService _api = ApiService();
  final AuthService _authService = AuthService();

  List<Favorite> _favorites = [];
  bool _isLoading = false;
  String? _error;

  List<Favorite> get favorites => _favorites;
  bool get isLoading => _isLoading;
  String? get error => _error;

  /// 초기 데이터 로드
  Future<void> loadFavorites() async {
    if (!_authService.isLoggedIn) {
      _favorites = [];
      notifyListeners();
      return;
    }

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final results = await _api.getFavorites();
      _favorites = results;
    } catch (e) {
      _error = e.toString();
      debugPrint('FavoritesProvider Error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// 찜 여부 확인
  bool isFavorite(RecommendedCar deal) {
    return _favorites.any((f) => f.isSameDeal(deal));
  }

  /// 찜 토글 (추가/삭제)
  Future<void> toggleFavorite(RecommendedCar deal) async {
    if (!_authService.isLoggedIn) return;

    final existing = _favorites.where((f) => f.isSameDeal(deal)).toList();
    final isCurrentlyFavorite = existing.isNotEmpty;

    // 1. Optimistic Update (즉시 반영)
    if (isCurrentlyFavorite) {
      _favorites.removeWhere((f) => f.isSameDeal(deal));
    } else {
      final tempFavorite = Favorite(
        id: DateTime.now().millisecondsSinceEpoch, // 임시 ID
        carId: deal.carId,
        brand: deal.brand,
        model: deal.model,
        year: deal.year,
        mileage: deal.mileage,
        predictedPrice: deal.predictedPrice.toDouble(),
        actualPrice: deal.actualPrice,
        detailUrl: deal.detailUrl,
        createdAt: DateTime.now().toIso8601String(),
      );
      _favorites.add(tempFavorite);
    }
    notifyListeners();

    // 2. API 호출
    try {
      if (isCurrentlyFavorite) {
        await _api.removeFavorite(existing.first.id);
      } else {
        await _api.addFavorite(
          brand: deal.brand,
          model: deal.model,
          year: deal.year,
          mileage: deal.mileage,
          predictedPrice: deal.predictedPrice.toDouble(),
          actualPrice: deal.actualPrice,
          detailUrl: deal.detailUrl,
          carId: deal.carId,
        );
      }
      // 3. 최신 데이터 동기화
      await loadFavorites();
    } catch (e) {
      debugPrint('Toggle favorite failed: $e');
      // 실패 시 롤백 (간단히 다시 로드)
      await loadFavorites();
    }
  }
}
