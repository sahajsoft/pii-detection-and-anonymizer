import argparse
import json
import logging
import sys

from presidio_analyzer import RecognizerResult
from presidio_analyzer.analyzer_engine import AnalyzerEngine
from presidio_anonymizer.entities.engine.result.operator_result import OperatorResult
from presidio_anonymizer import AnonymizerEngine, BatchAnonymizerEngine
from presidio_vault.vault import Vault

from pii_detection_and_anonymizer.analyzer_engine.csv_analyzer_engine import CSVAnalyzerEngine
from pii_detection_and_anonymizer.config.nlp_engine_config import FlairNLPEngine


NLP_ENGINE = "flair/ner-english-large"

logging.getLogger("presidio-analyzer").setLevel(logging.ERROR)
logging.getLogger("flair").setLevel(logging.ERROR)


def analyze(args):
    analyzer_results = None
    nlp_engine = FlairNLPEngine(NLP_ENGINE)
    nlp_engine, registry = nlp_engine.create_nlp_engine()
    engine = AnalyzerEngine(registry=registry, nlp_engine=nlp_engine)
    text = sys.stdin.read()
    if args.csv:
        engine = CSVAnalyzerEngine(engine)
    analyzer_results = engine.analyze(text=text, language=args.language)

    output = {
        "text": text,
        "analyzer_results": [
            {
                "entity_type": result.entity_type,
                "start": result.start,
                "end": result.end,
                "score": result.score,
                "analysis_explanation": result.analysis_explanation,
                "recognition_metadata": result.recognition_metadata,
            }
            for result in analyzer_results
        ],
    }
    print(json.dumps(output, indent=2))
    return analyzer_results


def anonymize(args):
    anonymized_results = None
    anonymizer_engine = None
    input_data = sys.stdin.read()
    input_json = json.loads(input_data)
    text = input_json.get("text", "")
    analyzer_results_data = input_json.get("analyzer_results", [])
    analyzer_results = [
        RecognizerResult.from_json(analyzer_result)
        for analyzer_result in analyzer_results_data
    ]

    if args.vaulturl:
        anonymizer_engine = Vault(args.vaulturl, args.vaultkey, args.vaulttoken)
    else:
        anonymizer_engine = AnonymizerEngine()

    anonymized_results = anonymizer_engine.anonymize(text, analyzer_results)

    json_results = json.loads(anonymized_results.to_json())

    output = {
        "text": json_results.get("text", ""),
        "anonymizer_results": json_results.get("items", []),
    }

    print(json.dumps(output, indent=2))
    return anonymized_results


def deanonymize(args):
    vault = Vault(args.vaulturl, args.vaultkey, args.vaulttoken)
    input_data = sys.stdin.read()
    input_json = json.loads(input_data)
    text = input_json.get("text", "")
    anonymizer_results_data = input_json.get("anonymizer_results", [])
    anonymizer_results = [
        OperatorResult(
            anonymizer_result["start"],
            anonymizer_result["end"],
            anonymizer_result["entity_type"],
            anonymizer_result["text"],
            anonymizer_result["operator"],
        )
        for anonymizer_result in anonymizer_results_data
    ]
    deanonymized_result = vault.deanonymize(text, anonymizer_results)
    print(deanonymized_result.to_json())
    return deanonymized_result


def main():
    parser = argparse.ArgumentParser(
        description="A CLI for detecting and Anonymizing PII."
    )
    subparsers = parser.add_subparsers(required=True)

    analyzer_parser = subparsers.add_parser(
        "analyze", description="Analyze inputs and return PII detection results"
    )
    analyzer_parser.add_argument("--csv", action="store_true")
    analyzer_parser.add_argument("--language", required=False, type=str, default="en")
    analyzer_parser.set_defaults(func=analyze)

    anonymizer_parser = subparsers.add_parser(
        "anonymize", description="Anonymize inputs"
    )
    anonymizer_parser.add_argument("--language", required=False, type=str, default="en")
    anonymizer_parser.add_argument("--vaulturl", required=False, type=str)
    anonymizer_parser.add_argument("--vaulttoken", required=False, type=str)
    anonymizer_parser.add_argument("--vaultkey", required=False, type=str)
    anonymizer_parser.set_defaults(func=anonymize)

    deanonymizer_parser = subparsers.add_parser(
        "deanonymize", description="Deanonymize inputs"
    )
    deanonymizer_parser.add_argument("--vaulturl", required=True, type=str)
    deanonymizer_parser.add_argument("--vaulttoken", required=False, type=str)
    deanonymizer_parser.add_argument("--vaultkey", required=True, type=str)
    deanonymizer_parser.add_argument(
        "--anonymized_results_list", required=False, type=str
    )
    deanonymizer_parser.set_defaults(func=deanonymize)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
