import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from voice_assistant import Assistant, parse_intent


class ParseIntentTests(unittest.TestCase):
    def test_greeting_accepts_free_form_phrase(self):
        self.assertEqual(parse_intent("Hey there, hello!").name, "greeting")

    def test_search_extracts_user_query(self):
        intent = parse_intent("Could you search the web for Python speech recognition?")
        self.assertEqual(intent.name, "search")
        self.assertEqual(intent.args["query"], "Python speech recognition")

    def test_reminder_parses_duration_and_message(self):
        intent = parse_intent("Please remind me in 2 minutes to drink water")
        self.assertEqual(intent.name, "reminder")
        self.assertEqual(intent.args, {"seconds": 120, "task": "drink water"})

    def test_weather_parses_city(self):
        intent = parse_intent("What's the weather like in New York?")
        self.assertEqual(intent.name, "weather")
        self.assertEqual(intent.args["city"], "new york")

    def test_email_parses_address_subject_and_body(self):
        intent = parse_intent("email to a@example.test subject Hello message The report is ready")
        self.assertEqual(intent.name, "email")
        self.assertEqual(intent.args["to"], "a@example.test")
        self.assertEqual(intent.args["subject"], "Hello")
        self.assertEqual(intent.args["body"], "The report is ready")

    def test_custom_phrase_must_match_exactly(self):
        custom = {"docs": {"phrases": ["open docs"], "url": "https://example.test"}}
        self.assertEqual(parse_intent("open docs", custom).name, "custom")
        self.assertEqual(parse_intent("please open docs", custom).name, "knowledge")


class AssistantTests(unittest.TestCase):
    def setUp(self):
        self.messages = []
        self.opened_urls = []
        self.temp_dir = tempfile.TemporaryDirectory()
        self.commands_path = Path(self.temp_dir.name) / "commands.json"
        self.commands_path.write_text(
            json.dumps({"docs": {"phrases": ["open docs"], "url": "https://example.test"}}),
            encoding="utf-8",
        )
        self.assistant = Assistant(
            self.messages.append,
            opener=lambda url: self.opened_urls.append(url) or True,
            input_fn=lambda _: "NO",
            commands_path=self.commands_path,
            environ={},
        )

    def tearDown(self):
        self.assistant.close()
        self.temp_dir.cleanup()

    def test_time_command_speaks_a_response(self):
        self.assertTrue(self.assistant.handle("What time is it?"))
        self.assertRegex(self.messages[-1], r"The time is \d{2}:\d{2} [AP]M\.")

    def test_search_encodes_query_and_opens_browser(self):
        self.assistant.handle("search for cats & dogs")
        self.assertEqual(self.opened_urls, ["https://www.google.com/search?q=cats+%26+dogs"])
        self.assertIn("cats & dogs", self.messages[-1])

    def test_unconfigured_email_does_not_prompt_or_send(self):
        self.assistant.handle("email to a@example.test subject Test message Hi")
        self.assertIn("Email is not configured", self.messages[-1])

    def test_email_requires_typed_confirmation(self):
        self.assistant.environ.update(
            SMTP_HOST="smtp.example.test",
            SMTP_PORT="465",
            SMTP_USERNAME="sender@example.test",
            SMTP_PASSWORD="test-only-password",
            SMTP_FROM="sender@example.test",
        )
        self.assistant.input_fn = lambda _: "NO"
        smtp_mock = Mock()
        with unittest.mock.patch("voice_assistant.smtplib.SMTP_SSL", return_value=smtp_mock):
            self.assistant.handle("email to a@example.test subject Test message Hi")
        smtp_mock.send_message.assert_not_called()
        self.assertEqual(self.messages[-1], "Email cancelled.")

    def test_custom_command_opens_configured_https_page(self):
        self.assistant.handle("open docs")
        self.assertEqual(self.opened_urls, ["https://example.test"])

    def test_reminder_schedules_daemon_timer(self):
        with unittest.mock.patch("voice_assistant.threading.Timer") as timer_factory:
            self.assistant._set_reminder(30, "stretch")
        timer_factory.assert_called_once_with(30, self.messages.append, args=("Reminder: stretch.",))
        timer_factory.return_value.start.assert_called_once()
        self.assertTrue(timer_factory.return_value.daemon)

    def test_weather_uses_geocoding_then_forecast(self):
        geocoding_response = Mock()
        geocoding_response.json.return_value = {
            "results": [{"name": "London", "latitude": 51.5, "longitude": -0.1}]
        }
        forecast_response = Mock()
        forecast_response.json.return_value = {
            "current": {
                "temperature_2m": 14,
                "apparent_temperature": 12,
                "relative_humidity_2m": 70,
                "weather_code": 3,
            }
        }
        self.assistant.http.get = Mock(side_effect=[geocoding_response, forecast_response])

        self.assistant._weather("London")

        self.assertIn("14 degrees Celsius and partly cloudy", self.messages[-1])
        self.assertEqual(self.assistant.http.get.call_count, 2)

    def test_knowledge_reads_wikipedia_summary(self):
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"extract": "Ada Lovelace was a mathematician."}
        self.assistant.http.get = Mock(return_value=response)

        self.assistant._knowledge("Ada Lovelace")

        self.assertEqual(self.messages[-1], "Ada Lovelace was a mathematician.")
        self.assertIn("Ada_Lovelace", self.assistant.http.get.call_args.args[0])

    def test_email_is_sent_only_after_explicit_confirmation(self):
        self.assistant.environ.update(
            SMTP_HOST="smtp.example.test",
            SMTP_PORT="465",
            SMTP_USERNAME="sender@example.test",
            SMTP_PASSWORD="test-only-password",
            SMTP_FROM="sender@example.test",
        )
        self.assistant.input_fn = lambda _: "SEND"
        smtp_mock = MagicMock()
        with unittest.mock.patch("voice_assistant.smtplib.SMTP_SSL", return_value=smtp_mock):
            self.assistant.handle("email to a@example.test subject Test message Hello")
        smtp_mock.__enter__().login.assert_called_once_with("sender@example.test", "test-only-password")
        smtp_mock.__enter__().send_message.assert_called_once()
        self.assertIn("Email sent to a@example.test", self.messages[-1])

    def test_exit_returns_false(self):
        self.assertFalse(self.assistant.handle("goodbye"))


if __name__ == "__main__":
    unittest.main()
