import argparse
from presidio_analyzer.analyzer_engine import AnalyzerEngine
from presidio_anonymizer.anonymizer_engine import AnonymizerEngine
from analyzer_engine.csv_analyzer_engine import CSVAnalyzerEngine
from presidio_anonymizer import BatchAnonymizerEngine
from config.nlp_engine_config import FlairNLPEngine

NLP_ENGINE = "flair/ner-english-large"


def analyze(args):
    nlp_engine = FlairNLPEngine(NLP_ENGINE)
    analyzer_results = None

    if args.text:
        nlp_engine, registry = nlp_engine.create_nlp_engine()
        engine = AnalyzerEngine(registry=registry, nlp_engine=nlp_engine)

        analyzer_results = engine.analyze(
            text=args.text,
            language=args.language
        )
    else:
        engine = CSVAnalyzerEngine(nlp_engine)

        analyzer_results = engine.analyze_csv(
            csv_full_path=args.filepath,
            language=args.language
        )

    print(analyzer_results)
    return analyzer_results


def anonymize(args):
    analyzer_results = analyze(args)
    anonymized_results = None

    if args.text:
        anonymizer = AnonymizerEngine()
        anonymized_results = anonymizer.anonymize(args.text, analyzer_results)
    else:
        anonymizer = BatchAnonymizerEngine()
        anonymized_results = anonymizer.anonymize_dict(analyzer_results)

    print(anonymized_results)
    return anonymized_results


def main():
    parser = argparse.ArgumentParser(description="A CLI for detecting and Anonymizing PII.")
    subparsers = parser.add_subparsers(required=True)

    analyzer_parser = subparsers.add_parser("analyze", description="Analyze inputs and return PII detection results")
    analyzer_parser.add_argument("--filepath", required=False, type=str, metavar="FILE")
    analyzer_parser.add_argument("--text", required=False, type=str)
    analyzer_parser.add_argument("--language", required=False, type=str, default="en")
    analyzer_parser.set_defaults(func=analyze)

    anonymizer_parser = subparsers.add_parser("anonymize", description="Anonymize inputs")
    anonymizer_parser.add_argument("--filepath", required=False, type=str, metavar="FILE")
    anonymizer_parser.add_argument("--text", required=False, type=str)
    anonymizer_parser.add_argument("--language", required=False, type=str, default="en")
    anonymizer_parser.set_defaults(func=anonymize)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
