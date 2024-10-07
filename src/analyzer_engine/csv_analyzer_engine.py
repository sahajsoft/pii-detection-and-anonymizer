from presidio_analyzer import AnalyzerEngine
from typing import List, Iterable, Optional

from presidio_analyzer import BatchAnalyzerEngine, DictAnalyzerResult
import csv


class CSVAnalyzerEngine(BatchAnalyzerEngine):

    def __init__(self, nlp_engine):
        self.nlp_engine = nlp_engine
        analyzer_engine = self.create_analyser_engine()
        super().__init__(analyzer_engine)

    def create_analyser_engine(self):
        nlp_engine, registry = self.nlp_engine.create_nlp_engine()
        analyzer = AnalyzerEngine(nlp_engine=nlp_engine, registry=registry)
        return analyzer

    def analyze_csv(
        self,
        csv_full_path: str,
        language: str,
        keys_to_skip: Optional[List[str]] = None,
        **kwargs,
    ) -> Iterable[DictAnalyzerResult]:
        with open(csv_full_path, "r") as csv_file:
            csv_list = list(csv.reader(csv_file))
            csv_dict = {
                header: list(map(str, values)) for header, *values in zip(*csv_list)
            }
            analyzer_results = self.analyze_dict(csv_dict, language, keys_to_skip)
            return list(analyzer_results)
