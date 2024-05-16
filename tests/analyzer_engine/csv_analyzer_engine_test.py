import unittest

from analyzer_engine.csv_analyzer_engine import CSVAnalyzerEngine
from config.nlp_engine_config import FlairNLPEngine


class CSVAnalayzerEngineTest(unittest.TestCase):
    def setUp(self) -> None:
        nlp_engine = FlairNLPEngine("flair/ner-english-large")
        self.csv_analyser = CSVAnalyzerEngine(nlp_engine)

    def test_csv_analyzer_engine_anonymizer(self):

        from presidio_anonymizer import BatchAnonymizerEngine
        analyzer_results = self.csv_analyser.analyze_csv('./data/sample_data.csv', language="en")

        anonymizer = BatchAnonymizerEngine()
        anonymized_results = anonymizer.anonymize_dict(analyzer_results)
        self.assertIsNotNone(anonymized_results)