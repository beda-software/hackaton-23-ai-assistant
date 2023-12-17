import logging
from ..utils import minify_json_string


def test_minify_json_string_func():
    s = """Based on your instructions, I will create a JSON string representing a FHIR QuestionnaireResponse resource. Since I do not have the actual contents of the Questionnaire at "Questionnaire/ultrasound-pregnancy-screening-second-trimester", I'm going to make assumptions about the question items in the Questionnaire that would align with the provided clinical data.

Here's an example of what the QuestionnaireResponse could look like, assuming there are questions corresponding to gestational age, fetal biparietal diameter, and head circumference:

```json
{
  "resourceType": "QuestionnaireResponse",
  "status": "completed",
  "questionnaire": "Questionnaire/ultrasound-pregnancy-screening-second-trimester",
  "item": [
    {
      "linkId": "1",
      "text": "Gestational age",
      "answer": [
        {
          "valueInteger": 20
        }
      ]
    }
  ]
}
```

Make sure to replace `"linkId"` values with the correct ones that match with the ids of the actual questionnaire items, and also adjust the `"text"` fields as per the exact wording used in the questionnaire. The "`valueInteger`" or "`valueDecimal`" types should correspond to the type of data expected by the questionnaire (age as an integer, measurements as decimals)."""

    new_s = s.replace("\n", "")
    assert minify_json_string(new_s) == {
        "resourceType": "QuestionnaireResponse",
        "status": "completed",
        "questionnaire": "Questionnaire/ultrasound-pregnancy-screening-second-trimester",
        "item": [
            {
                "linkId": "1",
                "text": "Gestational age",
                "answer": [{"valueInteger": 20}],
            },
        ],
    }
