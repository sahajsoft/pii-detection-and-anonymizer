import pytest

from recognizer.flair_recognizer import FlairRecognizer


def test_flair_recognizer_analyze():
    recognizer = FlairRecognizer(model_path="flair/ner-english-large")
    test_data = "Sowmya is working in Berkley bank as an accountant since 2021"
    result = recognizer.analyze(test_data)
    assert len(result) > 0

def test_flair_recognizes_persons_correctly():
    recognizer = FlairRecognizer(model_path="flair/ner-english-large")
    test_data = "Sowmya is a person name"
    assert len(recognizer.analyze(test_data)) > 0
    test_data = "XXXXXX is a valid name?"
    assert len(recognizer.analyze(test_data)) == 0
