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
                prefix = "the " + header + " is: "
                suffix = ""
                analysis_result = self.analyzer_engine.analyze(
                    prefix + value + suffix,
                    language,
                    context="this is the value in the "
                    + header
                    + " column in a csv file with the following columns: "
                    + ",".join(headers),
                )
                for result in analysis_result:
                    if result.end <= len(prefix):
                        continue
                    line_offset = text.index(value, line_start_index) - current_index
                    adjusted_start = (
                        current_index + line_offset + result.start - len(prefix)
                    )
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
