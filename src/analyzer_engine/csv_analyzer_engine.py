from presidio_analyzer import AnalyzerEngine, RecognizerResult
from typing import List
from csv import reader


class CSVAnalyzerEngine:
    def __init__(self, analyzer_engine: AnalyzerEngine):
        self.analyzer_engine = analyzer_engine

    def analyze(
        self,
        text: str,
        language: str,
    ) -> List[RecognizerResult]:
        csv_lines = text.splitlines()
        csv_reader = reader(csv_lines)
        headers = next(csv_reader)
        results = []
        current_index = 0
        for row in csv_reader:
            line_start_index = current_index
            line_text = ", ".join(row) + "\n"
            for idx, value in enumerate(row):
                header = headers[idx]
                analysis_result = self.analyzer_engine.analyze(
                    value, language, context=header
                )
                for result in analysis_result:
                    line_offset = text.index(value, line_start_index) - current_index
                    adjusted_start = current_index + line_offset + result.start
                    adjusted_end = adjusted_start + (result.end - result.start)
                    results.append(
                        RecognizerResult(
                            result.entity_type,
                            adjusted_start,
                            adjusted_end,
                            result.score,
                            result.analysis_explanation,
                            result.recognition_metadata,
                        )
                    )
            current_index += len(line_text)

        return results
