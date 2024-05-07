# Dataframe Preprocessing Methods

import re
import pandas as pd
from lxml import etree


def extract_pgsql_target(command: str):
    """
    Extract the target table of a sql INSERT / UPDATE string
    :param command: sql command
    :return: matched target table
    """
    if command is not None:
        match = re.search(r'(?:INSERT INTO|UPDATE)\s+"?([^"\s]+)', command)
        return match.group(1) if match else None
    return None


def set_event_with_roles(row):
    """
    generates the event with roles feature
    :param row: dataframe row representing a network package
    :return: event with role feature representation
    """
    sep = ": "
    res = [row["MessageType_WithRole"]]
    if row["pgsql.query_0"]:
        res.append(row["pgsql.query_0"])
    if row["pgsql.target"]:
        res.append(row["pgsql.target"])
    return ": ".join(res)


def extract_http_file_data(data):
    """
    generates features from http_file_data
    :param data: message attribute data
    :return: method_call, file_data and selective_file_data feature
    """
    if data is not None:
        # print(content)
        file_data = []
        selective_file_data = None
        method_call = None

        content = data.replace("\\xa", "")
        root = etree.fromstring(content)

        method_type = root.find(".").tag

        # extract method call
        if method_type == "methodCall":
            method_name = root.find(".//methodName")
            if method_name is not None:
                method_call = method_name.text

        elif method_type == "methodResponse":
            method_call = "response"

            # Extract parameters
        params = root.find(".//params")
        if params is not None:
            file_data = root.find(".//params").xpath('.//text()')
            # process data
            if method_call == "execute_kw" or method_call == "id":
                if 'salary_proposed' in file_data:
                    selective_file_data = "_".join([*file_data[3:5], file_data[-2]])
                elif 'search_read' in file_data:
                    # TODO Check
                    # if setting == "HR":
                    #     selective_file_data = "_".join([*file_data[3:5], file_data[-1]])
                    # else:
                    selective_file_data = "_".join([*file_data[3:5]])
                elif 'salary_expected' in file_data:
                    selective_file_data = "_".join([*file_data[3:5], file_data[6]])
                elif 'mail.activity' in file_data:
                    selective_file_data = "_".join(file_data[3:5]) if 'action_done' in file_data else "_".join(
                        [*file_data[3:5], file_data[-1]])
                elif 'stage_id' in file_data:
                    selective_file_data = "_".join([*file_data[3:5], *file_data[-2:]])
                else:
                    selective_file_data = "_".join(file_data[3:5])
            elif method_call == "response":
                method_call = file_data[0]
                if method_call == "id":
                    if 'name' in file_data:
                        pass
                    if 'salary_expected' in file_data:
                        selective_file_data = "salary_expected"

                    else:
                        selective_file_data = file_data[2]
                    # if 'picking_ids' in file_data:
                    #     selective_file_data = "picking_ids"
                    # if 'move_line_ids' in file_data:
                    #     selective_file_data = "move_line_ids"
                    # if ''
                elif method_call.isdigit():
                    method_call = "IsNumber"
                    selective_file_data = "IsNumber"
                elif method_call == "server_version":
                    selective_file_data = "server_version"
                else:
                    selective_file_data = "_".join(file_data[-2:])


            elif method_call == "version":
                selective_file_data = "version"

        elif method_call == "response":
            method_call = "faultCode"
            selective_file_data = "faultCode"

        return method_call, file_data, selective_file_data

    return "", "", ""


def merge_origin_request(row, df):
    """
    generates origin features for request / reponse packages
    :param row: dataframe row representing a network package
    :param df: dataframe with network events
    :return: method_call and selective_file_data from the request package
    """
    if pd.notna(row["http_request_in"]):
        instance_number = row["InstanceNumber"]
        request_frame = row["http_request_in"]
        business_activity = row["BusinessActivity"]
        try:
            row = df[(df["InstanceNumber"] == instance_number) & (df["frame.number"] == request_frame) & (
                    df["BusinessActivity"] == business_activity)].iloc[0]
            selective_file_data = row["selective_file_data"]
            method_call = row["request_method_call"]
            return method_call, selective_file_data
        except IndexError:
            pass
    return None, None


def apply_filter(df: pd.DataFrame):
    """
    filters a dataframe of network events
    :param df: dataframe with network events
    :return: filtered dataframe
    """
    # 1 preprocess
    df["pgsql.query"] = df["MessageAttributes"].apply(lambda x: x.get("pgsql.query")).str.strip(' \\xa')

    df["pgsql.target"] = df["pgsql.query"].apply(extract_pgsql_target)

    # 2 filter by message type
    # Message Types to keep
    message_type_filter = {
        "HttpRequest:POST /xmlrpc/2/common HTTP/1.1\\r\\n",
        "HttpRequest:POST /xmlrpc/2/object HTTP/1.1\\r\\n",
        "HttpResponse:HTTP/1.0 200 OK\\r\\n",
        "SmtpReassembledMessage",
        "PgsqlRequest:Simple query",
    }

    df = df[df["MessageType"].isin(message_type_filter)]

    # 3 keep PGSQL query that are either UPDATE or INSERT
    df = df[df['pgsql.query'].apply(lambda x: str(x).startswith(('UPDATE', 'INSERT')) if x is not None else True)]

    # Extra Step for Email PTP Filtering
    df = df[~df["pgsql.target"].isin(["fetchmail_server", "ir_cron", "ir_config_parameter"])]

    return df


def extract_features(df: pd.DataFrame):
    """
    generate features for network events
    :param df: dataframe with network events
    :return: generates features for the network events
    """
    df["pgsql.query"] = df["MessageAttributes"].apply(lambda x: x.get("pgsql.query")).str.strip(' \\xa')

    # Extract first Keyword from Query
    df["pgsql.query_0"] = df["pgsql.query"].str.split(" ").str[0]

    # Extract target from Query
    df["pgsql.target"] = df['pgsql.query'].apply(extract_pgsql_target)

    # Build Event with roles feature
    df["event_with_roles"] = df.apply(set_event_with_roles, axis=1)

    # Extract XML http file data from Message Attributes
    df["http_file_data"] = df["MessageAttributes"].apply(lambda x: x.get("http.file_data", None))

    # Only for response packets: Specifies the request packet a response is referring to
    df["http_request_in"] = df["MessageAttributes"].apply(lambda x: x.get("http.request_in", pd.NA)).astype("Int64")

    # Extract HTTP Features
    df[["request_method_call", "file_data", "selective_file_data"]] = df.apply(
        lambda x: extract_http_file_data(x["http_file_data"]), axis=1, result_type="expand")

    # Map Origin Requests
    df[["origin_method", "origin_file_data"]] = df.apply(merge_origin_request, axis=1, df=df,
                                                         result_type="expand").fillna("")

    cols = ["BusinessActivity",
            "InstanceNumber",
            "frame.number",
            "sniff_time",
            "synthetic_sniff_time",
            "event_with_roles",
            "request_method_call",
            "file_data",
            "pgsql.query",
            "pgsql.target",
            "selective_file_data",
            "origin_method",
            "origin_file_data"]

    return df[cols].fillna("")


def pre_process(df):
    """
    preprocesses the dataframe
    :param df: dataframe with network events
    :return: preprocessed dataframe
    """
    df = apply_filter(df)
    df = extract_features(df)

    return df


def extract_labels(labels):
    """
    extract labels for CRF
    :param labels:
    :return:
    """
    return [[y] for y in labels]


def mark_start_end(df):
    """
    Marks start and end of each trace
    :param df: dataframe with network events
    :return: dataframe with start and end of each trace marked
    """
    # Mark start event of each BusinessActivity Instance
    df["activityStart"] = df.groupby(["BusinessActivity", "InstanceNumber", ]).cumcount() == 0
    # Mark end event of each Business Activity Instance
    df["activityEnd"] = df.groupby(["BusinessActivity", "InstanceNumber", ]).cumcount(ascending=False) == 0
    # Merge start and end columns to form labels
    df["ActivityAction"] = df.apply(lambda row: "Activity Start" if row["activityStart"] else (
        "Activity End" if row["activityEnd"] else 'NoAction'), axis=1)

    return df.drop(["activityStart", 'activityEnd'], axis=1)


def assign_sequence_number(df):
    """
    Adds a SequenceNumber column to the input dataframe
    :param df: dataframe with network events
    :return: dataframe with sequence numbers
    """
    df_seq = df.sort_values(by=["InstanceNumber", "BusinessActivity", "frame.number"])
    df_seq["SequenceNumber"] = df_seq.groupby(["BusinessActivity", "InstanceNumber"]).ngroup()
    df_seq["SequenceNumber"] -= df_seq['SequenceNumber'].min()
    return df_seq


def create_eval_dataframe(df_gt, df_il):
    """
    Creates evaluation dataframe
    :param df_gt: ground truth dataframe
    :param df_il: dataframe with unlabeled evaluation data
    :return:
    """
    start_indices = df_gt["start"].tolist()
    end_indices = df_gt["actual_end"].tolist()
    df_test = pre_process(df_il)
    df_test["ActivityAction"] = df_test["frame.number"].apply(lambda x: "Activity Start" if x in start_indices else
    ("Activity End" if x in end_indices else "NoAction"))
    test_labels = extract_labels(df_test["ActivityAction"])
    return df_test, test_labels
