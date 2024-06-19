"""This is a python utility file."""

# pylint: disable=R0801
# pylint: disable=R0914

from os import environ

import functions_framework
from utils.bq_query_handler import BigQueryHandler
from utils.gemini import Gemini

project_id = environ.get("PROJECT_ID")


@functions_framework.http
def get_debt_fund_recommendation(request):
    """
    Recommends debt funds to a customer.

    Args:
        request (flask.Request): The request object.
            <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>

    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """

    request_json = request.get_json(silent=True)

    customer_id = request_json["sessionInfo"]["parameters"]["cust_id"]

    query_handler = BigQueryHandler(customer_id=customer_id)

    cust_id_exists, res = query_handler.validate_customer_id()
    if not cust_id_exists:
        return res

    public_bucket = environ.get("PUBLIC_BUCKET")
    market_summ_doc = environ.get("MARKET_SUMM_DOC")
    url = "https://storage.cloud.google.com/" + public_bucket + "/" + market_summ_doc

    model = Gemini()

    debt_fund_recommendation = model.generate_response(
        """
        You have to recommend debt fund instead of equity funds as the
        account health of the user is below average in no more than 50 words.
        For example -  Given your below average account health my recommendation is to
        start with a low risk debt fund to build a stable corpus.
        Investment in equity can be started once you reach Rs.1,50,000 in a low risk debt fund.
        Also equity markets are very high at the moment and
        our research team is predicting a correction in the next 6-8 months.
        """
    )

    res = {
        "fulfillment_response": {
            "messages": [
                {"text": {"text": [debt_fund_recommendation]}},
                {
                    "text": {
                        "text": [
                            "For your information: A consolidated 1-page"
                            " outlook on Indian markets from various brokers."
                        ]
                    }
                },
                {
                    "payload": {
                        "richContent": [
                            [
                                {
                                    "type": "chips",
                                    "options": [
                                        {
                                            "text": "Market Summary",
                                            "image": {
                                                "rawUrl": "https://upload.wikimedia.org/wikipedia/"
                                                "commons/thumb/8/87/PDF_file_icon.svg/"
                                                "391px-PDF_file_icon.svg.png"
                                            },
                                            "anchor": {"href": url},
                                        },
                                    ],
                                }
                            ]
                        ]
                    }
                },
            ]
        }
    }
    return res
