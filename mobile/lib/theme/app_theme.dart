import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  static const Color primary = Color(0xFF1A56DB);   // Bleu CartePro
  static const Color secondary = Color(0xFF0E9F6E); // Vert succès
  static const Color danger = Color(0xFFE02424);
  static const Color warning = Color(0xFFFF8800);
  static const Color surface = Color(0xFFF9FAFB);
  static const Color textPrimary = Color(0xFF111928);
  static const Color textSecondary = Color(0xFF6B7280);

  static ThemeData get light {
    final base = GoogleFonts.interTextTheme();
    return ThemeData(
      useMaterial3: true,
      textTheme: base,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primary,
        brightness: Brightness.light,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.white,
        foregroundColor: textPrimary,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: GoogleFonts.inter(
          fontSize: 18,
          fontWeight: FontWeight.w600,
          color: textPrimary,
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primary,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
          textStyle: GoogleFonts.inter(
            fontSize: 15,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: Color(0xFFE5E7EB)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: Color(0xFFE5E7EB)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: primary, width: 2),
        ),
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      ),
      cardTheme: CardTheme(
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: const BorderSide(color: Color(0xFFE5E7EB)),
        ),
        color: Colors.white,
      ),
    );
  }

  // Étiquettes pipeline en français avec couleurs
  static const pipelineColors = {
    'new': Color(0xFF6B7280),
    'contacted': Color(0xFF1A56DB),
    'quote_sent': Color(0xFFFF8800),
    'won': Color(0xFF0E9F6E),
    'lost': Color(0xFFE02424),
  };

  static const priorityColors = {
    'low': Color(0xFF6B7280),
    'medium': Color(0xFF1A56DB),
    'high': Color(0xFFE02424),
  };
}
