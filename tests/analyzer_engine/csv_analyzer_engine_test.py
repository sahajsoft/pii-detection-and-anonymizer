import unittest

from analyzer_engine.csv_analyzer_engine import CSVAnalyzerEngine
from config.nlp_engine_config import FlairNLPEngine


class CSVAnalayzerEngineTest(unittest.TestCase):
    def setUp(self) -> None:
        nlp_engine = FlairNLPEngine("flair/ner-english-large")
        self.csv_analyser = CSVAnalyzerEngine(nlp_engine)

    def test_csv_analyzer_engine_anonymizer(self):
        import pprint
        from presidio_anonymizer import BatchAnonymizerEngine
        analyzer_results = self.csv_analyser.analyze_csv('./sample_data.csv', language="en")

        pprint.pprint(analyzer_results)

        anonymizer = BatchAnonymizerEngine()
        anonymized_results = anonymizer.anonymize_dict(analyzer_results)
        pprint.pprint(anonymized_results)
        self.assertIsNotNone(anonymized_results)