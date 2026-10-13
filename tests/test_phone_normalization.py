"""Tests for Iranian phone number validation and normalization."""

import unittest
from Bomber import normalize_iranian_phone_number


class TestIranianPhoneNumberNormalization(unittest.TestCase):
    """Verify normalization rules and edge cases for Iranian phone numbers."""

    def test_standard_domestic_format_returns_unchanged(self) -> None:
        raw_domestic_number: str = "09123456789"
        normalized_number: str = normalize_iranian_phone_number(raw_domestic_number)
        self.assertEqual(normalized_number, "09123456789")

    def test_international_prefix_without_plus_normalized_to_domestic(self) -> None:
        raw_international_number: str = "989123456789"
        normalized_number: str = normalize_iranian_phone_number(raw_international_number)
        self.assertEqual(normalized_number, "09123456789")

    def test_international_prefix_with_plus_normalized_to_domestic(self) -> None:
        raw_prefixed_number: str = "+989123456789"
        normalized_number: str = normalize_iranian_phone_number(raw_prefixed_number)
        self.assertEqual(normalized_number, "09123456789")

    def test_trunkless_ten_digit_number_prepends_trunk_zero(self) -> None:
        raw_trunkless_number: str = "9123456789"
        normalized_number: str = normalize_iranian_phone_number(raw_trunkless_number)
        self.assertEqual(normalized_number, "09123456789")

    def test_embedded_country_code_digits_not_truncated(self) -> None:
        """Regression test: phone numbers with '98' inside subscriber digits must not be truncated."""
        phone_number_with_embedded_ninety_eight: str = "989129845678"
        normalized_number: str = normalize_iranian_phone_number(
            phone_number_with_embedded_ninety_eight
        )
        self.assertEqual(normalized_number, "09129845678")
        self.assertEqual(len(normalized_number), 11)

    def test_whitespace_and_hyphens_stripped_cleanly(self) -> None:
        formatted_raw_number: str = "  +98 912-345-6789  "
        normalized_number: str = normalize_iranian_phone_number(formatted_raw_number)
        self.assertEqual(normalized_number, "09123456789")

    def test_empty_input_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            normalize_iranian_phone_number("")

    def test_non_numeric_input_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            normalize_iranian_phone_number("0912abcdefg")

    def test_invalid_length_domestic_raises_value_error(self) -> None:
        short_domestic_number: str = "091234567"
        with self.assertRaises(ValueError):
            normalize_iranian_phone_number(short_domestic_number)

    def test_invalid_length_international_raises_value_error(self) -> None:
        short_international_number: str = "989123456"
        with self.assertRaises(ValueError):
            normalize_iranian_phone_number(short_international_number)

    def test_non_iranian_mobile_prefix_raises_value_error(self) -> None:
        landline_or_foreign_number: str = "982188776655"
        with self.assertRaises(ValueError):
            normalize_iranian_phone_number(landline_or_foreign_number)

    def test_persian_numerals_normalized_to_ascii_domestic_format(self) -> None:
        persian_phone_number_input: str = "۰۹۱۲۳۴۵۶۷۸۹"
        normalized_number: str = normalize_iranian_phone_number(persian_phone_number_input)
        self.assertEqual(normalized_number, "09123456789")

    def test_arabic_numerals_normalized_to_ascii_domestic_format(self) -> None:
        arabic_phone_number_input: str = "٠٩١٢٣٤٥٦٧٨٩"
        normalized_number: str = normalize_iranian_phone_number(arabic_phone_number_input)
        self.assertEqual(normalized_number, "09123456789")

    def test_persian_international_with_prefix_and_whitespace(self) -> None:
        persian_international_input: str = "  +۹۸ ۹۱۲ ۳۴۵ ۶۷۸۹  "
        normalized_number: str = normalize_iranian_phone_number(persian_international_input)
        self.assertEqual(normalized_number, "09123456789")


if __name__ == "__main__":
    unittest.main()
