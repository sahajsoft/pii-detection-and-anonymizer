import argparse

from presidio_anonymizer.entities.engine.result.operator_result import OperatorResult
from analyzer_engine.csv_analyzer_engine import CSVAnalyzerEngine
from presidio_anonymizer import BatchAnonymizerEngine
from config.nlp_engine_config import FlairNLPEngine
from operators.vault import Vault
from text.text import text_analyzer, text_anonymizer

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
        if args.vaulturl:
            vault = Vault(args.vaulturl, args.vaultkey, args.vaulttoken)
            anonymized_results = vault.anonymize(args.text, analyzer_results)
        else:
            anonymized_results = text_anonymizer(args.text, analyzer_results)
    else:
        anonymizer = BatchAnonymizerEngine()
        anonymized_results = anonymizer.anonymize_dict(analyzer_results)

    print(anonymized_results)
    return anonymized_results


def deanonymize(args):
    vault = Vault(args.vaulturl, args.vaultkey, args.vaulttoken)
    anonymized_results = []
    import json
    for r in json.loads(args.anonymized_results_list):
        anonymized_results.append(OperatorResult(r['start'], r['end'], r['entity_type'], r['text'], r['operator']))

    deanonymized_result = vault.deanonymize(args.text, anonymized_results)

    print(deanonymized_result)
    return deanonymized_result


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
    anonymizer_parser.add_argument("--vaulturl", required=False, type=str)
    anonymizer_parser.add_argument("--vaulttoken", required=False, type=str)
    anonymizer_parser.add_argument("--vaultkey", required=False, type=str)
    anonymizer_parser.set_defaults(func=anonymize)

    deanonymizer_parser = subparsers.add_parser("deanonymize", description="Deanonymize inputs")
    deanonymizer_parser.add_argument("--text", required=True, type=str)
    deanonymizer_parser.add_argument("--vaulturl", required=True, type=str)
    deanonymizer_parser.add_argument("--vaulttoken", required=False, type=str)
    deanonymizer_parser.add_argument("--vaultkey", required=True, type=str)
    deanonymizer_parser.add_argument("--anonymized_results_list", required=True, type=str)
    deanonymizer_parser.set_defaults(func=deanonymize)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()


# vault test:

# from text.text import text_analyzer
# from operators.vault import Vault

# vault_config = {"url": "http://127.0.0.1:8200", "token": "", "key": "orders"}
# vault = Vault(vault_config['url'], vault_config['key'], vault_config['token'])

# print("Analyze:")
# t = "Hi my name is Qwerty and I live in London. My number is 07440 123456."
# res = text_analyzer(t, "en")
# print(res)

# print("Anonymize:")
# anon_res = vault.anonymize(t, res)
# print(anon_res.text)
# print(anon_res.items)

# print("Deanonymize:")
# deanon_res = vault.deanonymize(anon_res.text, anon_res.items)
# print(deanon_res.text)
