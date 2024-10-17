from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
import pytest

from pii_detection_and_anonymizer.analyzer_engine.csv_analyzer_engine import CSVAnalyzerEngine
from pii_detection_and_anonymizer.config.nlp_engine_config import FlairNLPEngine


def test_csv_analyzer_engine_anonymizer():
    nlp_engine = FlairNLPEngine("flair/ner-english-large")
    nlp_engine, registry = nlp_engine.create_nlp_engine()
    engine = AnalyzerEngine(registry=registry, nlp_engine=nlp_engine)
    csv_analyzer = CSVAnalyzerEngine(engine)
    with open("./tests/sample_data/sample_data.csv", "r") as file:
        text = file.read()
    analyzer_results = csv_analyzer.analyze(text, language="en")
    anonymizer = AnonymizerEngine()
    anonymized_results = anonymizer.anonymize(text, analyzer_results)
    assert anonymized_results
