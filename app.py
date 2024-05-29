import json
import logging
import os
from typing import Tuple

from flask import Flask, request, jsonify, Response

from analyzer_engine.csv_analyzer_engine import CSVAnalyzerEngine
from config.nlp_engine_config import FlairNLPEngine

DEFAULT_PORT = "3000"
NLP_ENGINE = "flair/ner-english-large"

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

                filepath = f'uploads/{file.filename}'
                file.save(filepath)
                self.logger.info(f"Successfully saved file: {filepath}")

                analyzer_result_list = self.engine.analyze_csv(
                    csv_full_path=filepath,
                    language="en"
                )

                resp = {}
                for result in analyzer_result_list:
                    resp['key'] = result.key
                    resp['value'] = result.value
                    resp['recognizer_results'] = json.dumps(
                        result.recognizer_results,
                        default=lambda o: o.to_dict(),
                        sort_keys=True,
                    )

                return jsonify(resp), 200
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
