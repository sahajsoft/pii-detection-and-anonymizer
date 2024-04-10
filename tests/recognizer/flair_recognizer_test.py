import unittest

from recognizer.flair_recognizer import FlairRecognizer


class TestFlairRecognizer(unittest.TestCase):
    def setUp(self) -> None:
        self.recognizer = FlairRecognizer(model_path="flair/ner-english-large")

    def test_flair_recognizer_analyse(self):
        test_data = "Sowmya is working in Berkley bank as an accountant since 2021"
        result = self.recognizer.analyze(test_data)
        self.assertGreater(len(result), 0)

    def test_flair_recognizes_persons_correctly(self):
        test_data = "Sowmya is a person name"
        self.assertGreater(len(self.recognizer.analyze(test_data)), 0)
        test_data = "XXXXXX is a valid name?"
        self.assertEquals(len(self.recognizer.analyze(test_data)), 0)

