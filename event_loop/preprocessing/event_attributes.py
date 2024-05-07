import re


def extract_id_from_update_query(text, verbose=False):
    """
    Extract object id from update query
    :param text: update query
    :param verbose:
    :return: object id
    """
    match = re.search(r'UPDATE "?(.*?)"? SET .* WHERE (.*?) IN \((.*?)\)$', text)
    if match:
        if verbose: print(match.groups()[-1])
        return match.groups()[-1]


def extract_value_from_insert_query(text, key, verbose=False):
    """
    Extract value from insert query
    :param text: insert query
    :param key: object key
    :param verbose:
    :return: object value
    """
    match = re.search(r'INSERT INTO \S+ (.*?) VALUES (.*?)(RETURNING|ON CONFLICT DO NOTHING|$)', text)

    if match:
        groups = [g.replace("(", "").replace(")", "").replace('"', "").replace("'", "").replace("\\xa", "") for g in
                  match.groups()]

        groups = [[g.strip() for g in group.split(",")] for group in groups]

        res = dict(zip(groups[0], groups[1]))
        if verbose:
            print(res, res.get(key))
        return res.get(key)


def capture_href(text, extract_key):
    """
    Extract key value from html text containing href
    :param text: text
    :param extract_key: object key
    :return: value from extracted key
    """
    # Regex pattern to capture the desired text
    pattern = r'<a.*? data-oe-model=(.*?) data-oe.*>\s(.*?)</a>'

    # Apply the regex pattern to extract the desired text
    match = re.search(pattern, text)

    if match:
        c1 = match.group(1)
        c2 = match.group(2)

        if c1 == "purchase.requisition" and extract_key == "sale.order_id":
            return c2.split("_")[1]
        if c1 == "purchase.order" and extract_key == "purchase.order_id":
            return extract_num_from_purchase_order_string(c2)


def extract_num_from_purchase_order_string(text):
    """
    extract number from purchase order
    :param text: purchase order
    :return: number
    """
    numeric = re.search(r'\d+', text).group()
    return int(numeric)


def extract_sale_order_id(pgsql_query: str, pgsql_query_0: str, pgsql_target: str, file_data: list[str],
                          selective_file_data: list[str], origin_file_data: list[str]):
    """
    Extracts sale order from network package
    :param pgsql_query: pgsql query
    :param pgsql_query_0: first command of pgsql query
    :param pgsql_target: pgsql target
    :param file_data: http_file_data of the network package
    :param selective_file_data: file data of the network package
    :param origin_file_data: filtered file data of the network package
    :return: sale_order_id
    """
    if origin_file_data == "sale.order_create":
        return file_data[0]

    if origin_file_data == "purchase.order_search_read" and selective_file_data == "name":
        return file_data[63].split("_")[1]

    if selective_file_data == "sale.order.line_create":
        return file_data[6]
    if selective_file_data == "purchase.requisition_create":
        return file_data[6].split("_")[1]

    if selective_file_data == "sale.order_write":
        return file_data[5]

    if pgsql_target == "sale_order" and pgsql_query_0 == "UPDATE":
        return extract_id_from_update_query(pgsql_query)

    if pgsql_target == "sale_order" and pgsql_query_0 == "INSERT":
        res = extract_value_from_insert_query(pgsql_query, "name")
        return str(extract_num_from_purchase_order_string(res) - 1)

    if pgsql_target == "mail_message" and pgsql_query_0 == "INSERT":
        res_model = extract_value_from_insert_query(pgsql_query, "model")
        if res_model == "sale.order":
            return extract_value_from_insert_query(pgsql_query, "res_id")

        body = extract_value_from_insert_query(pgsql_query, "body")
        return capture_href(body, "sale.order_id")

    if pgsql_target == "mail_compose_message" and pgsql_query_0 == "INSERT":
        body = extract_value_from_insert_query(pgsql_query, "body")
        return capture_href(body, "sale.order_id")

    if pgsql_target == "mail_followers" and pgsql_query_0 == "INSERT":
        res_model = extract_value_from_insert_query(pgsql_query, "res_model")
        if res_model == "sale.order":
            return extract_value_from_insert_query(pgsql_query, "res_id")

    if pgsql_target == "sale_order_line" and pgsql_query_0 == "INSERT":
        return extract_value_from_insert_query(pgsql_query, "order_id")

    if pgsql_target == "purchase_requisition" and pgsql_query_0 == "INSERT":
        res = extract_value_from_insert_query(pgsql_query, "name")
        return res.split("_")[1]


def extract_sale_order_line_id(pgsql_query: str, pgsql_query_0: str, pgsql_target: str, file_data: list[str],
                               selective_file_data: list[str], origin_file_data: list[str]):
    """
    Extracts sale order line id from network package
    :param pgsql_query: pgsql query
    :param pgsql_query_0: first command of pgsql query
    :param pgsql_target: pgsql target
    :param file_data: http_file_data of the network package
    :param selective_file_data: file data of the network package
    :param origin_file_data: filtered file data of the network package
    :return: sale_order_id
    """
    if origin_file_data == "sale.order.line_create":
        return file_data[0]

    if pgsql_target == "sale_order_line":
        return extract_id_from_update_query(pgsql_query)


def extract_purchase_requisition_id(pgsql_query: str, pgsql_query_0: str, pgsql_target: str, file_data: list[str],
                                    selective_file_data: list[str], origin_file_data: list[str]):
    """
    Extracts purchase requisition id from network package
    :param pgsql_query: pgsql query
    :param pgsql_query_0: first command of pgsql query
    :param pgsql_target: pgsql target
    :param file_data: http_file_data of the network package
    :param selective_file_data: file data of the network package
    :param origin_file_data: filtered file data of the network package
    :return: sale_order_id
    """
    if origin_file_data == "purchase.requisition_create":
        return file_data[0]
    if selective_file_data == "purchase.requisition_write":
        return file_data[5]
    if selective_file_data == "purchase.order_create":
        return file_data[8]
    if selective_file_data == "purchase.requisition.line_create":
        return file_data[6]

    if pgsql_target == "purchase_requisition" and pgsql_query_0 == "UPDATE":
        return extract_id_from_update_query(pgsql_query)

    if pgsql_target == "mail_message" and pgsql_query_0 == "INSERT":
        res_model = extract_value_from_insert_query(pgsql_query, "model")
        if res_model == "purchase.requisition":
            return extract_value_from_insert_query(pgsql_query, "res_id")

    if pgsql_target == "mail_followers" and "purchase.requisition" in pgsql_query:
        return extract_value_from_insert_query(pgsql_query, "res_id")

    if pgsql_target == "purchase_requisition_line" and pgsql_query_0 == "INSERT":
        return extract_value_from_insert_query(pgsql_query, "requisition_id")


def extract_purchase_requisition_line_id(pgsql_query: str, pgsql_query_0: str, pgsql_target: str, file_data: list[str],
                                         selective_file_data: list[str], origin_file_data: list[str]):
    """
    Extracts purchase requisition line id from network package
    :param pgsql_query: pgsql query
    :param pgsql_query_0: first command of pgsql query
    :param pgsql_target: pgsql target
    :param file_data: http_file_data of the network package
    :param selective_file_data: file data of the network package
    :param origin_file_data: filtered file data of the network package
    :return: sale_order_id
    """
    if origin_file_data == "purchase.requisition.line_create":
        return file_data[0]

    if pgsql_target == "purchase_requisition_line" and pgsql_query_0 == "UPDATE":
        return extract_id_from_update_query(pgsql_query)


def extract_purchase_order_id(pgsql_query: str, pgsql_query_0: str, pgsql_target: str, file_data: list[str],
                              selective_file_data: list[str], origin_file_data: list[str]):
    """
    Extracts purchase order id from network package
    :param pgsql_query: pgsql query
    :param pgsql_query_0: first command of pgsql query
    :param pgsql_target: pgsql target
    :param file_data: http_file_data of the network package
    :param selective_file_data: file data of the network package
    :param origin_file_data: filtered file data of the network package
    :return: sale_order_id
    """
    if origin_file_data == "purchase.order_create":
        return file_data[0]

    if selective_file_data == "account.invoice.line_create":
        return file_data[20]

    if selective_file_data == "purchase.order.line_create":
        return file_data[6]

    if selective_file_data == "purchase.order_button_confirm":
        return file_data[5]

    if selective_file_data == "purchase.order_search_read":
        return file_data[7]

    if selective_file_data == "purchase.order_write":
        return file_data[5]

    if selective_file_data == "account.invoice_create":
        return str(extract_num_from_purchase_order_string(file_data[-1]))

    if pgsql_target == "purchase_order" and pgsql_query_0 == "UPDATE":
        return extract_id_from_update_query(pgsql_query)

    if pgsql_target == "account_invoice_purchase_order_rel" and pgsql_query_0 == "INSERT":
        return extract_value_from_insert_query(pgsql_query, "purchase_order_id")

    if pgsql_target == "mail_message" and pgsql_query_0 == "INSERT":
        res_model = extract_value_from_insert_query(pgsql_query, "model")
        if res_model == "purchase.order":
            return extract_value_from_insert_query(pgsql_query, "res_id")
        body = extract_value_from_insert_query(pgsql_query, "body")
        return capture_href(body, "purchase.order_id")

    if pgsql_target == "mail_compose_message" and pgsql_query_0 == "INSERT":
        res_model = extract_value_from_insert_query(pgsql_query, "model")
        if res_model == "purchase.order":
            return extract_value_from_insert_query(pgsql_query, "res_id", )
        body = extract_value_from_insert_query(pgsql_query, "body")
        return capture_href(body, "purchase.order_id")

    if pgsql_target == "mail_followers" and "purchase.order" in pgsql_query:
        return extract_value_from_insert_query(pgsql_query, "res_id")

    if pgsql_target == "purchase_order" and pgsql_query_0 == "INSERT":
        res = extract_value_from_insert_query(pgsql_query, "name")
        return extract_num_from_purchase_order_string(res)

    if pgsql_target == "purchase_order_line" and pgsql_query_0 == "INSERT":
        return extract_value_from_insert_query(pgsql_query, "order_id")

    if pgsql_target == "purchase_order_stock_picking_rel" and pgsql_query_0 == "INSERT":
        return extract_value_from_insert_query(pgsql_query, "purchase_order_id")


def extract_purchase_order_line_id(pgsql_query: str, pgsql_query_0: str, pgsql_target: str, file_data: list[str],
                                   selective_file_data: list[str], origin_file_data: list[str]):
    """
    Extracts purchase order line id from network package
    :param pgsql_query: pgsql query
    :param pgsql_query_0: first command of pgsql query
    :param pgsql_target: pgsql target
    :param file_data: http_file_data of the network package
    :param selective_file_data: file data of the network package
    :param origin_file_data: filtered file data of the network package
    :return: sale_order_id
    """
    if origin_file_data == "purchase.order.line_create":
        return file_data[0]

    if selective_file_data == "account.invoice.line_create":
        return file_data[16]
    if pgsql_target == "purchase_order_line" and pgsql_query_0 == "UPDATE":
        return extract_id_from_update_query(pgsql_query)


def extract_applicant_id(pgsql_query: str, pgsql_query_0: str, pgsql_target: str, file_data: list[str],
                         selective_file_data: list[str], origin_file_data: list[str]):
    """
    Extracts applicant id from network package
    :param pgsql_query: pgsql query
    :param pgsql_query_0: first command of pgsql query
    :param pgsql_target: pgsql target
    :param file_data: http_file_data of the network package
    :param selective_file_data: file data of the network package
    :param origin_file_data: filtered file data of the network package
    :return: sale_order_id
    """
    if origin_file_data == "hr.applicant_create":
        return file_data[0]
    if selective_file_data and "hr.applicant_write" in selective_file_data:
        return file_data[5]
    if selective_file_data == "hr.applicant_archive_applicant":
        return file_data[5]
    if selective_file_data == "hr.applicant_search_read":
        return file_data[7]
    if selective_file_data and "mail.activity_create" in selective_file_data:
        return file_data[10]
    if origin_file_data == "hr.applicant_search_read":
        return file_data[1]
    if pgsql_target == "hr_applicant" and pgsql_query_0 == "UPDATE":
        return extract_id_from_update_query(pgsql_query)

    if pgsql_target == "mail_followers" and pgsql_query_0 == "INSERT":
        res_model = extract_value_from_insert_query(pgsql_query, "res_model")
        if res_model == "hr.applicant":
            return extract_value_from_insert_query(pgsql_query, "res_id")


def extract_activity_id(pgsql_query: str, pgsql_query_0: str, pgsql_target: str, file_data: list[str],
                        selective_file_data: list[str], origin_file_data: list[str]):
    """
    Extracts activity id from network package
    :param pgsql_query: pgsql query
    :param pgsql_query_0: first command of pgsql query
    :param pgsql_target: pgsql target
    :param file_data: http_file_data of the network package
    :param selective_file_data: file data of the network package
    :param origin_file_data: filtered file data of the network package
    :return: sale_order_id
    """
    # if pgsql_query:
    #     return extract_sql_activity_id(pgsql_query)
    if origin_file_data and "mail.activity_create" in origin_file_data:
        return file_data[0]
    if selective_file_data == "mail.activity_search_read":
        return file_data[7]

    if origin_file_data == "mail.activity_search_read":
        return file_data[1]

    if selective_file_data == "mail.activity_action_done":
        return file_data[5]

    if pgsql_target == "mail_activity" and pgsql_query_0 == "UPDATE":
        return extract_id_from_update_query(pgsql_query)

    if pgsql_target == "mail_message" and pgsql_query_0 == "INSERT":
        pass
        # TODO FIX HTML Parsing
        # extract_value_from_insert_query(pgsql_query,"", verbose=True)


def extract_mail_id(pgsql_query: str, pgsql_query_0: str, pgsql_target: str, file_data: list[str],
                    selective_file_data: list[str], origin_file_data: list[str]):
    """
    Extracts mail id from network package
    :param pgsql_query: pgsql query
    :param pgsql_query_0: first command of pgsql query
    :param pgsql_target: pgsql target
    :param file_data: http_file_data of the network package
    :param selective_file_data: file data of the network package
    :param origin_file_data: filtered file data of the network package
    :return: sale_order_id
    """
    if origin_file_data == "mail.activity_action_done":
        return file_data[0]

    if pgsql_target == "mail_message" and pgsql_query_0 == "UPDATE":
        return extract_id_from_update_query(pgsql_query)
