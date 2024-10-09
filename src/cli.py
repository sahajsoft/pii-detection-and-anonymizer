import argparse
import io
import json

from presidio_analyzer import RecognizerResult
from presidio_analyzer.analyzer_engine import AnalyzerEngine
from presidio_anonymizer.entities.engine.result.operator_result import OperatorResult
from presidio_image_redactor import ImageAnalyzerEngine
from analyzer_engine.csv_analyzer_engine import CSVAnalyzerEngine
from presidio_anonymizer import AnonymizerEngine, BatchAnonymizerEngine
from config.nlp_engine_config import FlairNLPEngine
from utils.formatter import Formatter
from operators.vault import Vault
from PIL import Image
from presidio_image_redactor import ImageRedactorEngine


import sys
import logging

NLP_ENGINE = "flair/ner-english-large"

logging.getLogger("presidio-analyzer").setLevel(logging.ERROR)
logging.getLogger("flair").setLevel(logging.ERROR)


def analyze(args):
    analyzer_results = None
    input_buffer = sys.stdin.buffer.read()
    text = None
    image = None
    if args.img:
        image = Image.open(io.BytesIO(input_buffer))
        analyzer_results = ImageAnalyzerEngine().analyze(image=image, language=args.language)
    else:
        nlp_engine = FlairNLPEngine(NLP_ENGINE)
        nlp_engine, registry = nlp_engine.create_nlp_engine()
        engine = AnalyzerEngine(registry=registry, nlp_engine=nlp_engine)
        text = input_buffer.decode("utf-8")
        if args.csv:
            engine = CSVAnalyzerEngine(engine)
        analyzer_results = engine.analyze(text=text, language=args.language)

    output = Formatter().format_output(analyzer_results, text, image)
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
    analyzer_parser.add_argument("--img", action="store_true")
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
