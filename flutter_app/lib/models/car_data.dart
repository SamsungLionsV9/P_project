import 'package:flutter/material.dart';

// 차량 데이터 모델
class CarData {
  final String id;
  final String name;
  final String price; // 예상 시세
  final String info; // 연식/주행거리
  final String date; // 조회 날짜
  final Color color;
  bool isLiked;
  bool isNotificationOn;

  CarData({
    required this.id,
    required this.name,
    required this.price,
    required this.info,
    required this.date,
    required this.color,
    this.isLiked = false,
    this.isNotificationOn = false,
  });
}
