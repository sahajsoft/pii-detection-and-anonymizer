import argparse
from analyzer_engine.csv_analyzer_engine import CSVAnalyzerEngine
from text.text import text_analyzer, text_anonymizer
from presidio_anonymizer import BatchAnonymizerEngine
from config.nlp_engine_config import FlairNLPEngine

NLP_ENGINE = "flair/ner-english-large"


def analyze(args):
    analyzer_results = None

    if args.text:
        analyzer_results = text_analyzer(args.text, args.language)
    else:
        nlp_engine = FlairNLPEngine(NLP_ENGINE)
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
        anonymized_results = text_anonymizer(args.text, analyzer_results)
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


# vault test:
from presidio_anonymizer.entities import OperatorConfig
def vault_encrypt(text):
    return text + "x"

operators = {"DEFAULT": OperatorConfig("custom", {"lambda": vault_encrypt})}

t = "Hi my name is Qwerty and I live in London. My number is 07440 123456."
res = text_analyzer(t, "en")
anon_res = text_anonymizer(t, res, operators)

print(anon_res)
