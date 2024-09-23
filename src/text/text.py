from typing import Optional
from presidio_analyzer.analyzer_engine import AnalyzerEngine
from presidio_anonymizer.anonymizer_engine import AnonymizerEngine
from config.nlp_engine_config import FlairNLPEngine

NLP_ENGINE = "flair/ner-english-large"

def text_analyzer(text, language):
    nlp_engine = FlairNLPEngine(NLP_ENGINE)
    nlp_engine, registry = nlp_engine.create_nlp_engine()
    engine = AnalyzerEngine(registry=registry, nlp_engine=nlp_engine)

    return engine.analyze(
        text=text,
        language=language
    )


def text_anonymizer(text: str, analyzer_results, operators: Optional[dict] = None):
    anonymizer = AnonymizerEngine()
    return anonymizer.anonymize(text, analyzer_results, operators)
