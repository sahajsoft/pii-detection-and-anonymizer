import json
import logging
import os
import uuid
from typing import Tuple
import csv

from flask import Flask, request, jsonify, Response, send_file
from presidio_analyzer import AnalyzerEngine, DictAnalyzerResult, RecognizerResult
from presidio_anonymizer import AnonymizerEngine, BatchAnonymizerEngine
from presidio_vault.vault import Vault

from pii_detection_and_anonymizer.analyzer_engine.csv_analyzer_engine import CSVAnalyzerEngine
from pii_detection_and_anonymizer.config.nlp_engine_config import FlairNLPEngine

DEFAULT_PORT = "3000"
NLP_ENGINE = "flair/ner-english-large"
UPLOAD_DIR = "file_uploads"


class Server:
    """HTTP Server for calling Presidio Analyzer."""

    def __init__(self):
        self.logger = logging.getLogger("pii-detection-anonymizer")
        self.logger.setLevel(os.environ.get("LOG_LEVEL", self.logger.level))
        self.app = Flask(__name__)
        self.logger.info("Starting analyzer engine")
        nlp_engine = FlairNLPEngine(NLP_ENGINE)
        nlp_engine, registry = nlp_engine.create_nlp_engine()
        engine = AnalyzerEngine(registry=registry, nlp_engine=nlp_engine)
        self.engine = CSVAnalyzerEngine(engine)
        self.logger.info("Started analyzer engine")
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

        @self.app.route("/health")
        def health() -> str:
            """Return basic health probe result."""
            return "PII detection and anonymizer service is up"

        @self.app.route("/analyze", methods=["POST"])
        def analyze() -> Tuple[str, int]:
            """Execute the analyzer function."""
            try:
                file = request.files["file"]
                language = request.form["language"]
                if file.filename == "":
                    return jsonify({"error": "No selected file"}), 400

                filepath = f"{UPLOAD_DIR}/{uuid.uuid4()}"
                file.save(filepath)
                self.logger.info(f"Successfully saved file: {filepath}")
                with open(filepath, "r") as file:
                    text = file.read()

                analyzer_results = self.engine.analyze(text, language=language)
                self.logger.debug(f"Analyzed file with results: {analyzer_results}")
                os.remove(filepath)
                self.logger.info(f"Successfully removed file: {filepath}")

                return (
                    jsonify(
                        [
                            {
                                "entity_type": result.entity_type,
                                "start": result.start,
                                "end": result.end,
                                "score": result.score,
                                "analysis_explanation": result.analysis_explanation,
                                "recognition_metadata": result.recognition_metadata,
                            }
                            for result in analyzer_results
                        ]
                    ),
                    200,
                )
            except Exception as e:
                self.logger.error(
                    f"A fatal error occurred during execution of "
                    f"AnalyzerEngine.analyze(). {e}"
                )
                return jsonify(error=e.args[0]), 500

        @self.app.route("/anonymize", methods=["POST"])
        def anonymize() -> Response:
            """Execute the anonymizer function."""
            try:
                analyzer_results = json.loads(request.form["analyzer_results"])
                anonymizer_engine = None
                vault_config = request.form.get("vault_config")
                if vault_config:
                    vault_config = json.loads(vault_config)
                    anonymizer_engine = Vault(
                        vault_url=vault_config["url"],
                        vault_key=vault_config["key"],
                        vault_token=vault_config.get("token"),
                    )
                else:
                    anonymizer_engine = AnonymizerEngine()

                dict_analyzer_results = []
                for key, value in analyzer_results.items():
                    recognizer_results = []
                    for results_for_each_entry in value["recognizer_results"]:
                        each_entry_recognizer_results = []
                        for r in results_for_each_entry:
                            each_entry_recognizer_results.append(
                                RecognizerResult(
                                    r["entity_type"], r["start"], r["end"], r["score"]
                                )
                            )
                        recognizer_results.append(each_entry_recognizer_results)
                    dict_analyzer_results.append(
                        DictAnalyzerResult(
                            key=key,
                            value=value["value"],
                            recognizer_results=recognizer_results,
                        )
                    )

                anonymizer = BatchAnonymizerEngine(anonymizer_engine)
                anonymized_results = anonymizer.anonymize_dict(dict_analyzer_results)

                data = []
                keys = anonymized_results.keys()
                for i in range(len(anonymized_results[list(keys)[0]])):
                    row = {key: anonymized_results[key][i] for key in keys}
                    data.append(row)

                filename = f"{UPLOAD_DIR}/{uuid.uuid4()}.csv"
                with open(filename, "w", newline="") as output:
                    writer = csv.DictWriter(output, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(data)

                return send_file(
                    os.path.abspath(filename),
                    mimetype="text/csv",
                    as_attachment=True,
                    download_name="anonymized_data.csv",
                )
            except Exception as e:
                self.logger.error(
                    f"A fatal error occurred during execution of " f"anonymize(). {e}"
                )
                return jsonify(error=e.args[0]), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    server = Server()
    server.app.run(host="0.0.0.0", port=port)
