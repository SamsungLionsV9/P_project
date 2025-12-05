import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:responsive_framework/responsive_framework.dart';

/// 반응형 디자인 유틸리티 (flutter_screenutil + responsive_framework 기반)
/// 화면 크기에 따라 레이아웃을 자동 조정
class Responsive {
  static const double mobileBreakpoint = 450;
  static const double tabletBreakpoint = 800;
  static const double desktopBreakpoint = 1200;

  /// 화면 너비 가져오기
  static double screenWidth(BuildContext context) =>
      MediaQuery.of(context).size.width;

  /// 화면 높이 가져오기
  static double screenHeight(BuildContext context) =>
      MediaQuery.of(context).size.height;

  /// 모바일 여부 (responsive_framework 사용)
  static bool isMobile(BuildContext context) =>
      ResponsiveBreakpoints.of(context).isMobile;

  /// 태블릿 여부
  static bool isTablet(BuildContext context) =>
      ResponsiveBreakpoints.of(context).isTablet;

  /// 데스크탑 여부
  static bool isDesktop(BuildContext context) =>
      ResponsiveBreakpoints.of(context).isDesktop;

  /// 현재 브레이크포인트 이름
  static String breakpointName(BuildContext context) =>
      ResponsiveBreakpoints.of(context).breakpoint.name;

  /// 화면 크기에 따른 값 반환
  static T value<T>(
    BuildContext context, {
    required T mobile,
    T? tablet,
    T? desktop,
  }) {
    if (isDesktop(context)) return desktop ?? tablet ?? mobile;
    if (isTablet(context)) return tablet ?? mobile;
    return mobile;
  }

  /// 화면 비율 기반 너비
  static double widthPercent(BuildContext context, double percent) =>
      screenWidth(context) * percent / 100;

  /// 화면 비율 기반 높이
  static double heightPercent(BuildContext context, double percent) =>
      screenHeight(context) * percent / 100;

  /// 반응형 폰트 크기
  static double fontSize(BuildContext context, double baseSize) {
    final width = screenWidth(context);
    if (width >= desktopBreakpoint) return baseSize * 1.2;
    if (width >= tabletBreakpoint) return baseSize * 1.1;
    if (width >= mobileBreakpoint) return baseSize;
    return baseSize * 0.9;
  }

  /// 반응형 패딩
  static EdgeInsets padding(BuildContext context) {
    return value(
      context,
      mobile: const EdgeInsets.all(16),
      tablet: const EdgeInsets.all(24),
      desktop: const EdgeInsets.all(32),
    );
  }

  /// 반응형 수평 패딩
  static EdgeInsets horizontalPadding(BuildContext context) {
    return value(
      context,
      mobile: const EdgeInsets.symmetric(horizontal: 16),
      tablet: const EdgeInsets.symmetric(horizontal: 32),
      desktop: const EdgeInsets.symmetric(horizontal: 48),
    );
  }

  /// 그리드 컬럼 수
  static int gridColumns(BuildContext context) {
    return value(context, mobile: 1, tablet: 2, desktop: 3);
  }

  /// 카드 최대 너비
  static double cardMaxWidth(BuildContext context) {
    return value(
      context,
      mobile: double.infinity,
      tablet: 600,
      desktop: 800,
    );
  }

  /// 컨텐츠 최대 너비 (센터 정렬용)
  static double contentMaxWidth(BuildContext context) {
    return value(
      context,
      mobile: double.infinity,
      tablet: 720,
      desktop: 1200,
    );
  }
}

/// 반응형 빌더 위젯
class ResponsiveBuilder extends StatelessWidget {
  final Widget mobile;
  final Widget? tablet;
  final Widget? desktop;

  const ResponsiveBuilder({
    super.key,
    required this.mobile,
    this.tablet,
    this.desktop,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth >= Responsive.tabletBreakpoint) {
          return desktop ?? tablet ?? mobile;
        }
        if (constraints.maxWidth >= Responsive.mobileBreakpoint) {
          return tablet ?? mobile;
        }
        return mobile;
      },
    );
  }
}

/// 반응형 그리드 뷰
class ResponsiveGridView extends StatelessWidget {
  final List<Widget> children;
  final double spacing;
  final double runSpacing;
  final int? mobileColumns;
  final int? tabletColumns;
  final int? desktopColumns;

  const ResponsiveGridView({
    super.key,
    required this.children,
    this.spacing = 16,
    this.runSpacing = 16,
    this.mobileColumns,
    this.tabletColumns,
    this.desktopColumns,
  });

  @override
  Widget build(BuildContext context) {
    final columns = Responsive.value(
      context,
      mobile: mobileColumns ?? 1,
      tablet: tabletColumns ?? 2,
      desktop: desktopColumns ?? 3,
    );

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: columns,
        crossAxisSpacing: spacing,
        mainAxisSpacing: runSpacing,
        childAspectRatio: 1.2,
      ),
      itemCount: children.length,
      itemBuilder: (context, index) => children[index],
    );
  }
}

/// 반응형 컨테이너 (센터 정렬)
class ResponsiveContainer extends StatelessWidget {
  final Widget child;
  final double? maxWidth;
  final EdgeInsetsGeometry? padding;

  const ResponsiveContainer({
    super.key,
    required this.child,
    this.maxWidth,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    final effectiveMaxWidth = maxWidth ?? Responsive.contentMaxWidth(context);
    final effectivePadding = padding ?? Responsive.horizontalPadding(context);

    return Center(
      child: Container(
        constraints: BoxConstraints(maxWidth: effectiveMaxWidth),
        padding: effectivePadding,
        child: child,
      ),
    );
  }
}

/// 화면 크기 변경 감지 위젯
class ScreenSizeNotifier extends StatelessWidget {
  final Widget Function(BuildContext context, Size size, bool isMobile) builder;

  const ScreenSizeNotifier({
    super.key,
    required this.builder,
  });

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;
    final isMobile = ResponsiveBreakpoints.of(context).isMobile;
    return builder(context, size, isMobile);
  }
}

// ============================================================
// ScreenUtil 확장 메서드 (간편 사용)
// 사용법: 16.w, 16.h, 14.sp, 8.r
// ============================================================

/// 반응형 사이즈 확장 (num에 적용)
extension ResponsiveSize on num {
  /// 반응형 너비 (width)
  double get w => ScreenUtil().setWidth(this);
  
  /// 반응형 높이 (height)  
  double get h => ScreenUtil().setHeight(this);
  
  /// 반응형 폰트 사이즈 (scalable pixels)
  double get sp => ScreenUtil().setSp(this);
  
  /// 반응형 radius
  double get r => ScreenUtil().radius(this);
  
  /// 반응형 수평 패딩
  SizedBox get horizontalSpace => SizedBox(width: w);
  
  /// 반응형 수직 패딩
  SizedBox get verticalSpace => SizedBox(height: h);
}

/// EdgeInsets 확장
extension ResponsiveEdgeInsets on EdgeInsets {
  /// 반응형 EdgeInsets
  EdgeInsets get r => EdgeInsets.only(
    left: left.w,
    top: top.h,
    right: right.w,
    bottom: bottom.h,
  );
}

/// 반응형 위젯 확장
extension ResponsiveWidget on Widget {
  /// 최대 너비 제한 + 센터 정렬
  Widget constrained({double maxWidth = 600}) {
    return Center(
      child: ConstrainedBox(
        constraints: BoxConstraints(maxWidth: maxWidth),
        child: this,
      ),
    );
  }
  
  /// 반응형 패딩 적용
  Widget responsivePadding(BuildContext context) {
    return Padding(
      padding: Responsive.padding(context),
      child: this,
    );
  }
}
