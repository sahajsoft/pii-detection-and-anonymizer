import pytest

from analyzer_engine.csv_analyzer_engine import CSVAnalyzerEngine
from config.nlp_engine_config import FlairNLPEngine


def test_csv_analyzer_engine_anonymizer():
    nlp_engine = FlairNLPEngine("flair/ner-english-large")
    csv_analyzer = CSVAnalyzerEngine(nlp_engine)
    from presidio_anonymizer import BatchAnonymizerEngine
    analyzer_results = csv_analyzer.analyze_csv('./tests/sample_data/sample_data.csv', language="en")

    anonymizer = BatchAnonymizerEngine()
    anonymized_results = anonymizer.anonymize_dict(analyzer_results)
    assert anonymized_results
