import 'package:flutter/material.dart';

/// 호버 시 튀어나오는 카드 효과
/// 마우스를 올리면 살짝 올라오고 그림자가 짙어짐
class HoverCard extends StatefulWidget {
  final Widget child;
  final double hoverScale;
  final double hoverElevation;
  final Duration duration;
  final BorderRadius? borderRadius;
  final Color? backgroundColor;
  final VoidCallback? onTap;

  const HoverCard({
    super.key,
    required this.child,
    this.hoverScale = 1.02,
    this.hoverElevation = 12,
    this.duration = const Duration(milliseconds: 200),
    this.borderRadius,
    this.backgroundColor,
    this.onTap,
  });

  @override
  State<HoverCard> createState() => _HoverCardState();
}

class _HoverCardState extends State<HoverCard> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final defaultBorderRadius = BorderRadius.circular(16);
    final effectiveBorderRadius = widget.borderRadius ?? defaultBorderRadius;
    final bgColor = widget.backgroundColor ?? 
        (isDark ? const Color(0xFF1E1E1E) : Colors.white);

    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      cursor: widget.onTap != null ? SystemMouseCursors.click : MouseCursor.defer,
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: widget.duration,
          curve: Curves.easeOutCubic,
          transform: Matrix4.identity()
            ..translate(0.0, _isHovered ? -4.0 : 0.0)
            ..scale(_isHovered ? widget.hoverScale : 1.0),
          transformAlignment: Alignment.center,
          decoration: BoxDecoration(
            color: bgColor,
            borderRadius: effectiveBorderRadius,
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(_isHovered ? 0.15 : 0.05),
                blurRadius: _isHovered ? widget.hoverElevation : 4,
                offset: Offset(0, _isHovered ? 8 : 2),
                spreadRadius: _isHovered ? 2 : 0,
              ),
            ],
          ),
          child: ClipRRect(
            borderRadius: effectiveBorderRadius,
            child: widget.child,
          ),
        ),
      ),
    );
  }
}

/// 호버 시 색상이 변하는 버튼/카드
class HoverColorCard extends StatefulWidget {
  final Widget child;
  final Color? hoverColor;
  final Color? defaultColor;
  final Duration duration;
  final BorderRadius? borderRadius;
  final VoidCallback? onTap;

  const HoverColorCard({
    super.key,
    required this.child,
    this.hoverColor,
    this.defaultColor,
    this.duration = const Duration(milliseconds: 150),
    this.borderRadius,
    this.onTap,
  });

  @override
  State<HoverColorCard> createState() => _HoverColorCardState();
}

class _HoverColorCardState extends State<HoverColorCard> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final defaultBg = widget.defaultColor ?? 
        (isDark ? const Color(0xFF1E1E1E) : Colors.white);
    final hoverBg = widget.hoverColor ?? 
        (isDark ? const Color(0xFF2A2A2A) : Colors.grey[50]);
    final effectiveBorderRadius = widget.borderRadius ?? BorderRadius.circular(12);

    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      cursor: widget.onTap != null ? SystemMouseCursors.click : MouseCursor.defer,
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: widget.duration,
          curve: Curves.easeOut,
          decoration: BoxDecoration(
            color: _isHovered ? hoverBg : defaultBg,
            borderRadius: effectiveBorderRadius,
            border: Border.all(
              color: _isHovered 
                  ? const Color(0xFF0066FF).withOpacity(0.3)
                  : Colors.grey.withOpacity(0.1),
              width: _isHovered ? 1.5 : 1,
            ),
          ),
          child: widget.child,
        ),
      ),
    );
  }
}

/// 호버 시 아이콘/버튼이 커지는 효과
class HoverScaleWidget extends StatefulWidget {
  final Widget child;
  final double scale;
  final Duration duration;
  final VoidCallback? onTap;

  const HoverScaleWidget({
    super.key,
    required this.child,
    this.scale = 1.1,
    this.duration = const Duration(milliseconds: 150),
    this.onTap,
  });

  @override
  State<HoverScaleWidget> createState() => _HoverScaleWidgetState();
}

class _HoverScaleWidgetState extends State<HoverScaleWidget> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      cursor: widget.onTap != null ? SystemMouseCursors.click : MouseCursor.defer,
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedScale(
          scale: _isHovered ? widget.scale : 1.0,
          duration: widget.duration,
          curve: Curves.easeOutBack,
          child: widget.child,
        ),
      ),
    );
  }
}

/// 터치/호버 시 물결 효과 + 확대
class InteractiveCard extends StatefulWidget {
  final Widget child;
  final VoidCallback? onTap;
  final BorderRadius? borderRadius;
  final Color? backgroundColor;
  final EdgeInsetsGeometry? padding;

  const InteractiveCard({
    super.key,
    required this.child,
    this.onTap,
    this.borderRadius,
    this.backgroundColor,
    this.padding,
  });

  @override
  State<InteractiveCard> createState() => _InteractiveCardState();
}

class _InteractiveCardState extends State<InteractiveCard> {
  bool _isHovered = false;
  bool _isPressed = false;

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bgColor = widget.backgroundColor ?? 
        (isDark ? const Color(0xFF1E1E1E) : Colors.white);
    final effectiveBorderRadius = widget.borderRadius ?? BorderRadius.circular(16);

    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: GestureDetector(
        onTapDown: (_) => setState(() => _isPressed = true),
        onTapUp: (_) {
          setState(() => _isPressed = false);
          widget.onTap?.call();
        },
        onTapCancel: () => setState(() => _isPressed = false),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          curve: Curves.easeOut,
          transform: Matrix4.identity()
            ..translate(0.0, _isHovered ? -3.0 : 0.0)
            ..scale(_isPressed ? 0.98 : (_isHovered ? 1.01 : 1.0)),
          transformAlignment: Alignment.center,
          padding: widget.padding,
          decoration: BoxDecoration(
            color: bgColor,
            borderRadius: effectiveBorderRadius,
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(_isHovered ? 0.12 : 0.05),
                blurRadius: _isHovered ? 16 : 8,
                offset: Offset(0, _isHovered ? 6 : 2),
              ),
            ],
            border: Border.all(
              color: _isHovered 
                  ? const Color(0xFF0066FF).withOpacity(0.2)
                  : Colors.transparent,
            ),
          ),
          child: widget.child,
        ),
      ),
    );
  }
}
