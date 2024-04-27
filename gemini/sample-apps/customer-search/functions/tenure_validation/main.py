import re

import functions_framework


def get_number_of_days(fd_tenure: str) -> int:
    """Calculates the number of days in a fixed deposit tenure.

    Args:
      fd_tenure (str): The fixed deposit tenure in the format "X year Y month
      Z day".

    Returns:
      int: The number of days in the fixed deposit tenure.
    """

    years = 0
    months = 0
    days = 0

    year_re = re.search(r"(\d+) year", fd_tenure)
    month_re = re.search(r"(\d+) month", fd_tenure)
    day_re = re.search(r"(\d+) day", fd_tenure)

    if year_re is not None:
        years = int(year_re.group(1))
    if month_re is not None:
        months = int(month_re.group(1))
    if day_re is not None:
        days = int(day_re.group(1))

    # Convert the years, months, and days to integers.
    years = int(years)
    months = int(months)
    days = int(days)

    # Calculate the total number of days in the tenure.
    total_days = 365 * years + 30 * months + days

    print(total_days)
    return total_days


@functions_framework.http
def validate_fd_tenure(
    request: functions_framework.HttpRequest,
) -> functions_framework.HttpResponse:
    """HTTP Cloud Function.

    Args:
      request (flask.Request): The request object.
      <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>

    Returns:
      The response text, or any set of values that can be turned into a
      Response object using `make_response`
      <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)

    print(request_json["sessionInfo"]["parameters"])

    fd_tenure = request_json["sessionInfo"]["parameters"]["fd_tenure"]
    number_of_days = get_number_of_days(fd_tenure)

    res = {
        "fulfillment_response": {"messages": [{"text": {"text": []}}]},
        "sessionInfo": {"parameters": {"number_of_days": number_of_days}},
    }
    print(res)
    return res