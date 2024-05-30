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
            # Parse the request params
            try:
                req_json = request.get_json()
                if not req_json.get("text"):
                    raise Exception("No text provided")

                if not req_json.get("language"):
                    raise Exception("No language provided")

                recognizer_result_list = self.engine.analyze_text(
                    text=req_json.get("text"),
                    language=req_json.get("language")
                )

                return Response(
                    json.dumps(
                        recognizer_result_list,
                        default=lambda o: o.to_dict(),
                        sort_keys=True,
                    ),
                    content_type="application/json",
                )
            except TypeError as te:
                error_msg = (
                    f"Failed to parse /analyze request "
                    f"for AnalyzerEngine.analyze(). {te.args[0]}"
                )
                self.logger.error(error_msg)
                return jsonify(error=error_msg), 400

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
