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

# VAULT_URL = "http://127.0.0.1:8200"
# VAULT_KEY = "orders"
# from presidio_anonymizer.anonymizer_engine import AnonymizerEngine
# from presidio_anonymizer.deanonymize_engine import DeanonymizeEngine
# from presidio_anonymizer.entities import OperatorConfig
# from text.text import text_analyzer
# from operators.vault import VaultEncrypt, VaultDecrypt
# print("Analyze:")
# t = "Hi my name is Qwerty and I live in London. My number is 07440 123456."
# res = text_analyzer(t, "en")
# print(res)

# print("Anonymize:")
# anonymizer = AnonymizerEngine()
# anonymizer.add_anonymizer(VaultEncrypt)
# operators = {"DEFAULT": OperatorConfig("vault_encrypt", {"vault_url": VAULT_URL, "key": VAULT_KEY})}
# anon_res = anonymizer.anonymize(t, res, operators)
# print(anon_res.text)


# print("Deanonymize:")
# deanonymizer = DeanonymizeEngine()
# deanonymizer.add_deanonymizer(VaultDecrypt)
# de_ops = {"DEFAULT": OperatorConfig("vault_decrypt", {"vault_url": VAULT_URL, "key": VAULT_KEY})}
# deanon_res = deanonymizer.deanonymize(anon_res.text, anon_res.items, de_ops)
# print(deanon_res.text)
