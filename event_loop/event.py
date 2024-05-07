from event_loop.preprocessing.dataframe import extract_http_file_data
from event_loop.preprocessing.event import *
from event_loop.preprocessing.event_attributes import *


class Event:
    """ Network event"""
    def __init__(self, data, i, event_buffer, setting):
        """
        Create a network event
        :param data: package data
        :param i: event_loop_index
        :param event_buffer: event buffer for mapping request/response events
        :param setting: HR or PTP setting
        """

        pgsql_query = extract_pgsql_query(data)
        pgsql_query_0 = pgsql_query.split(" ")[0] if pgsql_query else None
        pgsql_target = extract_target_from_pgsql_query(pgsql_query)

        self.frame_number = data["frame.number"]
        self.sniff_time = data["synthetic_sniff_time"]
        self.event_with_roles = parse_event_with_roles(data, pgsql_query, pgsql_target)
        self.stream_index = parse_stream_index(data)
        self.method_call, parsed_file_data, self.selective_file_data = extract_http_file_data(
            data["MessageAttributes"].get("http.file_data"))
        self.origin_request_frame, self.origin_method_call, self.origin_file_data = parse_origin_file_data(data,
                                                                                                           event_buffer)
        args = {'pgsql_query': pgsql_query, 'pgsql_query_0': pgsql_query_0, 'pgsql_target': pgsql_target,
            'file_data': parsed_file_data, 'selective_file_data': self.selective_file_data,
            'origin_file_data': self.origin_file_data}

        if setting == "HR":
            self.attributes = {"applicant_id": extract_applicant_id(**args), "activity_id": extract_activity_id(**args),
                "mail_id": extract_mail_id(**args)}
        else:
            self.attributes = {"sale_order_id": extract_sale_order_id(**args),
                "sale_order_line_id": extract_sale_order_line_id(**args),
                "purchase_requisition_id": extract_purchase_requisition_id(**args),
                "purchase_requisition_line_id": extract_purchase_requisition_line_id(**args),
                "purchase_order_id": extract_purchase_order_id(**args),
                "purchase_order_line_id": extract_purchase_order_line_id(**args), }

        self.event_loop_index = i
        self.confidence = None

    def to_features(self):
        """
        Generate a feature dictionary from the event
        :return: dict of features
        """
        return {"event_with_roles": self.str_if_none(self.event_with_roles),
                "request_method_call": self.str_if_none(self.method_call),
                "selective_file_data": self.str_if_none(self.selective_file_data),
                "origin_method": self.str_if_none(self.origin_method_call),
                "origin_file_data": self.str_if_none(self.origin_file_data), "bias": 1.0}

    def to_feature_list(self):
        """
        Generate a list of features from the event
        :return: list of features
        """
        return [self.str_if_none(self.event_with_roles),
                self.str_if_none(self.method_call),
                self.str_if_none(self.selective_file_data),
                self.str_if_none(self.origin_method_call),
                self.str_if_none(self.origin_file_data)]

    @staticmethod
    def str_if_none(x):
        """Replace none values with an empty string"""
        return x if x else ""

    def to_activity_model_string(self):
        """
        Transforms an event to string representation based on its attributes *event_with_roles* and *selective_filter_data*
        :return: Concatenated string of *event_with_roles* and *selective_filter_data* attributes
        """
        return (self.event_with_roles if self.event_with_roles else "") + (
            self.selective_file_data if self.selective_file_data else "")

    def __str__(self):
        return f"{self.frame_number} {self.event_with_roles} {self.origin_file_data}"
