extension StringHelpers on String {
  /// "john doe" → "John Doe"
  String toTitleCase() => split(' ')
      .map((w) => w.isEmpty ? w : '${w[0].toUpperCase()}${w.substring(1).toLowerCase()}')
      .join(' ');

  /// Returns true if this is a valid email address.
  bool get isValidEmail => RegExp(r'^[\w.+\-]+@[\w\-]+\.[a-zA-Z]{2,}$').hasMatch(this);

  /// Returns true if the string is null-safe non-empty.
  bool get isNotBlank => trim().isNotEmpty;
}
