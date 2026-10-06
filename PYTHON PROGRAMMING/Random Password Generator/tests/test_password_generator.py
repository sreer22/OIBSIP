import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from password_generator import (
    AMBIGUOUS_CHARACTERS,
    CHARACTER_GROUPS,
    MAX_LENGTH,
    MIN_LENGTH,
    generate_password,
    password_strength,
)


class PasswordGenerationTests(unittest.TestCase):
    def test_password_has_requested_length_and_every_selected_class(self):
        selected = ["uppercase", "lowercase", "numbers", "symbols"]
        password = generate_password(64, selected)

        self.assertEqual(len(password), 64)
        self.assertTrue(any(character in CHARACTER_GROUPS["uppercase"] for character in password))
        self.assertTrue(any(character in CHARACTER_GROUPS["lowercase"] for character in password))
        self.assertTrue(any(character in CHARACTER_GROUPS["numbers"] for character in password))
        self.assertTrue(any(character in CHARACTER_GROUPS["symbols"] for character in password))

    def test_password_only_uses_selected_character_pools(self):
        password = generate_password(32, ["uppercase", "numbers"])
        allowed = set(CHARACTER_GROUPS["uppercase"] + CHARACTER_GROUPS["numbers"])
        self.assertLessEqual(set(password), allowed)

    def test_password_excludes_ambiguous_characters(self):
        selected = ["uppercase", "lowercase", "numbers", "symbols"]
        password = generate_password(128, selected, exclude_ambiguous=True)
        self.assertTrue(set(password).isdisjoint(AMBIGUOUS_CHARACTERS))

    def test_ambiguous_exclusion_still_satisfies_required_groups(self):
        password = generate_password(32, ["uppercase", "lowercase", "numbers"], exclude_ambiguous=True)
        self.assertTrue(any(character in CHARACTER_GROUPS["uppercase"] for character in password))
        self.assertTrue(any(character in CHARACTER_GROUPS["lowercase"] for character in password))
        self.assertTrue(any(character in CHARACTER_GROUPS["numbers"] for character in password))

    def test_length_boundaries_are_supported(self):
        self.assertEqual(len(generate_password(MIN_LENGTH, ["uppercase", "lowercase"])), MIN_LENGTH)
        self.assertEqual(len(generate_password(MAX_LENGTH, ["uppercase", "lowercase"])), MAX_LENGTH)

    def test_invalid_lengths_are_rejected(self):
        for length in (MIN_LENGTH - 1, MAX_LENGTH + 1, 8.5, True):
            with self.subTest(length=length), self.assertRaises(ValueError):
                generate_password(length, ["uppercase", "lowercase"])

    def test_requires_two_character_types(self):
        with self.assertRaisesRegex(ValueError, "at least two"):
            generate_password(12, ["lowercase"])
        with self.assertRaisesRegex(ValueError, "at least two"):
            generate_password(12, [])

    def test_rejects_unknown_character_type(self):
        with self.assertRaisesRegex(ValueError, "Unknown character type"):
            generate_password(12, ["uppercase", "emoji"])

    def test_duplicate_selected_types_are_deduplicated(self):
        password = generate_password(8, ["uppercase", "lowercase", "uppercase"])
        self.assertEqual(len(password), 8)
        self.assertTrue(any(character in CHARACTER_GROUPS["uppercase"] for character in password))
        self.assertTrue(any(character in CHARACTER_GROUPS["lowercase"] for character in password))

    def test_generator_uses_secrets_choice_and_shuffle(self):
        with patch("password_generator.secrets.choice", side_effect=lambda pool: pool[0]) as choose:
            with patch("password_generator.secrets.SystemRandom.shuffle") as shuffle:
                password = generate_password(10, ["uppercase", "lowercase"])
        self.assertEqual(len(password), 10)
        self.assertGreaterEqual(choose.call_count, 10)
        shuffle.assert_called_once()


class PasswordStrengthTests(unittest.TestCase):
    def test_strength_categories(self):
        self.assertEqual(password_strength(8, 2), "Weak")
        self.assertEqual(password_strength(12, 2), "Medium")
        self.assertEqual(password_strength(16, 3), "Strong")
        self.assertEqual(password_strength(32, 1), "Weak")


if __name__ == "__main__":
    unittest.main()
