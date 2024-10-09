import io


class Formatter:

    def __init__(self):
        pass

    def format_output(self ,analyzer_results, text, image):
        if image:
            output = io.BytesIO()
            image.convert('RGB').save(output, format='JPEG')
            return {
                "image": list(output.getvalue()),
                "analyzer_results": [
                    {
                        "entity_type": result.entity_type,
                        "start": result.start,
                        "end":  result.end,
                        "score": result.score,
                        "left" : result.left,
                        "top" : result.top,
                        "width" : result.width,
                        "height" : result.height
                    }
                    for result in analyzer_results
                ]
            }

        return {
            "text": text,
            "analyzer_results": [
                {
                    "entity_type": result.entity_type,
                    "start": result.start,
                    "end": result.end,
                    "score": result.score,
                    "analysis_explanation": result.analysis_explanation,
                    "recognition_metadata": result.recognition_metadata,
                }
                for result in analyzer_results
            ],
        }