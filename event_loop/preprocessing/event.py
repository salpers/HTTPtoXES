import re


def parse_origin_file_data(data: dict, event_buffer):
    """
    get origin features for request / response packets
    :param data: event data
    :param event_buffer: buffer with events
    :return: request / response features
    """
    origin_request_frame_number = data["MessageAttributes"].get("http.request_in")

    if origin_request_frame_number:
        origin_request_frame_number = int(origin_request_frame_number)
        # find event
        res = [event for event in event_buffer if event.frame_number == origin_request_frame_number]
        if len(res) > 0:
            origin_event = res[0]
            return origin_request_frame_number, origin_event.method_call, origin_event.selective_file_data
    return None, "", ""


def extract_pgsql_query(data: dict):
    """
    extract and sanitize pgsql query from message attributes
    :param data: event data
    :return: pgsql query
    """
    query = data["MessageAttributes"].get("pgsql.query")

    return query.strip(' \\xa') if query else None


def extract_target_from_pgsql_query(query: str):
    """
    Extract the target table of a sql INSERT / UPDATE string
    :param query: sql command
    :return: matched target table
    """
    if query is not None:
        match = re.search(r'(?:INSERT INTO|UPDATE)\s+"?([^"\s]+)', query)
        return match.group(1) if match else None
    return None


def parse_event_with_roles(data: dict, pgsql_query: str, pgsql_target: str):
    """
    generates the event with roles feature
    :param data: event data
    :param pgsql_query: pgsql query
    :param pgsql_target: pgsql target
    :return: event with roles feature
    """
    res = [data["MessageType_WithRole"]]

    if pgsql_query:
        res.append(pgsql_query.split(" ")[0])
    if pgsql_target:
        res.append(pgsql_target)

    return ": ".join(res)


def parse_stream_index(data: dict):
    """
    Extract stream index from session
    :param data: event data
    :return: stream index
    """
    return data["session_generalized"].split(" ")[1]


def keep_event(event_data: dict):
    """
    filter event
    :param event_data: event data
    :return: whether to keep the event or discard it
    """
    # Allowed message types
    message_type_filter = {
        "HttpRequest:POST /xmlrpc/2/common HTTP/1.1\\r\\n",
        "HttpRequest:POST /xmlrpc/2/object HTTP/1.1\\r\\n",
        "HttpResponse:HTTP/1.0 200 OK\\r\\n",
        "SmtpReassembledMessage",
        "PgsqlRequest:Simple query",
    }

    if event_data["MessageType"] not in message_type_filter:
        return False

    pgsql_query = extract_pgsql_query(event_data)

    if pgsql_query and not pgsql_query.startswith(('UPDATE', 'INSERT')):
        return False

    return True
