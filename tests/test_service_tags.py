"""Unit tests for service categorization and tag filtering."""

import unittest

from lib.service_tags import (
    SERVICE_TAGS_MAP,
    get_available_tags,
    get_services_by_tags,
)


class TestServiceTags(unittest.TestCase):
    """Test suite for service categories and tag lookup logic."""

    def test_available_tags_contains_expected_categories(self) -> None:
        """Verify that known categories are registered in available tags."""
        tags = get_available_tags()
        self.assertIn("transport", tags)
        self.assertIn("marketplace", tags)
        self.assertIn("food", tags)
        self.assertIn("entertainment", tags)
        self.assertIn("medical", tags)
        self.assertIn("fintech", tags)
        self.assertIn("education", tags)
        self.assertIn("ecommerce", tags)
        self.assertEqual(tags, sorted(tags))

    def test_get_services_by_single_tag(self) -> None:
        """Verify retrieving services by a single tag."""
        transport_services = get_services_by_tags("transport")
        self.assertIn("tapsi_passenger", transport_services)
        self.assertIn("snapp_trip", transport_services)
        self.assertIn("itoll", transport_services)

    def test_get_services_by_comma_separated_string(self) -> None:
        """Verify parsing comma-separated tag string."""
        services = get_services_by_tags("food, entertainment")
        self.assertIn("snapp_food", services)
        self.assertIn("filimo", services)
        self.assertIn("FilmNet", services)

    def test_get_services_by_list(self) -> None:
        """Verify retrieving services by list of tags."""
        services = get_services_by_tags(["fintech", "education"])
        self.assertIn("lendo", services)
        self.assertIn("azki", services)
        self.assertIn("classino", services)

    def test_get_services_by_unknown_tag(self) -> None:
        """Unknown tag returns empty list."""
        services = get_services_by_tags("non_existent_category")
        self.assertEqual(services, [])

    def test_mixed_valid_and_unknown_tags(self) -> None:
        """Unknown tags are ignored while valid ones are matched."""
        services = get_services_by_tags("food, unknown_tag_xyz")
        self.assertIn("snapp_food", services)
        self.assertIn("snapp_market", services)


if __name__ == "__main__":
    unittest.main()
