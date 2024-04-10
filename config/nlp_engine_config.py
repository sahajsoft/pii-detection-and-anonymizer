from recognizer.flair_recognizer import FlairRecognizer
from presidio_analyzer import RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
import spacy


class NLPEngineConfig:

    def __init__(self, model_path):
        self.model_path = model_path

    def create_nlp_engine(self):
        pass


class FlairNLPEngine(NLPEngineConfig):
    def create_nlp_engine(self):
        '''
        Flair doesn't have an official NLP Engine. Hence making it as a Recognizer to presidio
        :param model_path:
        :return:
        '''
        registry = RecognizerRegistry()
        registry.load_predefined_recognizers()
        if not spacy.util.is_package("en_core_web_sm"):
            spacy.cli.download("en_core_web_sm")
        flair_recognizer = FlairRecognizer(model_path=self.model_path)
        nlp_configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
        }
        registry.add_recognizer(flair_recognizer)
        registry.remove_recognizer("SpacyRecognizer")

        nlp_engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()

        return nlp_engine, registry
