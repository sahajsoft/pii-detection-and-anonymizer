import json
import logging
import os
import uuid
from typing import Tuple

from flask import Flask, request, jsonify, Response

from analyzer_engine.csv_analyzer_engine import CSVAnalyzerEngine
from config.nlp_engine_config import FlairNLPEngine

DEFAULT_PORT = "3000"
NLP_ENGINE = "flair/ner-english-large"
UPLOAD_DIR = "./file_uploads"

class Server:
    """HTTP Server for calling Presidio Analyzer."""

    def __init__(self):
        self.logger = logging.getLogger("pii-detection-anonymizer")
        self.logger.setLevel(os.environ.get("LOG_LEVEL", self.logger.level))
        self.app = Flask(__name__)
        self.logger.info("Starting analyzer engine")
        nlp_engine = FlairNLPEngine(NLP_ENGINE)
        self.engine = CSVAnalyzerEngine(nlp_engine)
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
                file = request.files['file']
                if file.filename == '':
                    return jsonify({'error': 'No selected file'}), 400

                filepath = f'{UPLOAD_DIR}/{uuid.uuid4()}'
                file.save(filepath)
                self.logger.info(f"Successfully saved file: {filepath}")

                analyzer_results = self.engine.analyze_csv(
                    csv_full_path=filepath,
                    language="en"
                )
                self.logger.debug(f"Analyzed file with results: {analyzer_results}")
                os.remove(filepath)
                self.logger.info(f"Successfully removed file: {filepath}")

                analyzer_results_dict = {}
                for a in analyzer_results:
                    recognizer_results = []
                    for r in a.recognizer_results:
                        recognizer_results.append([o.to_dict() for o in r])
                    analyzer_results_dict[a.key] = {
                        "value": a.value,
                        "recognizer_results": recognizer_results
                    }

                return jsonify(analyzer_results_dict), 200
            except Exception as e:
                self.logger.error(
                    f"A fatal error occurred during execution of "
                    f"AnalyzerEngine.analyze(). {e}"
                )
                return jsonify(error=e.args[0]), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    server = Server()
    server.app.run(host="0.0.0.0", port=port)
