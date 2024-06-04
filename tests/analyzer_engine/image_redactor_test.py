import pytest
import os
import shutil
from analyzer_engine.image_redactor import ImageRedactor

OUTPUT_DIR = "output"


@pytest.fixture(scope="module")
def img_red():
    return ImageRedactor()


@pytest.fixture(autouse=True, scope="module")
def setup_and_teardown():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    yield
    shutil.rmtree(OUTPUT_DIR)


def test_detects_pii_in_image_successfully(img_red):
    image = img_red.detect_pii("./data/ocr_text.png")
    image.save("./output/modified.png")
    assert os.path.isfile("./output/modified.png")
