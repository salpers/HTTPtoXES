from event_loop.event import Event

PTP_ATTRIBUTES = ["sale_order_id", "sale_order_line_id", "purchase_requisition_id", "purchase_requisition_line_id", ]
HR_ATTRIBUTES = ["applicant_id"]


class Stack:
    case_ids = []

    def __init__(self, setting, event: Event = None, ):
        """
        Initializes an event stack with a first event
        :param setting: HR or PTP setting
        :param event: initial event
        """
        self.label = None
        self.events: list[Event] = []
        self.attribute_list = PTP_ATTRIBUTES if setting == "PTP" else HR_ATTRIBUTES
        self.activity_type = None

        if setting == "HR":
            self.attributes = {
                "applicant_id": set(),
                "activity_id": set(),
                "mail_id": set(),
            }
        else:
            self.attributes = {
                "sale_order_id": set(),
                "sale_order_line_id": set(),
                "purchase_requisition_id": set(),
                "purchase_requisition_line_id": set(),
                "purchase_order_id": set(),
                "purchase_order_line_id": set()
            }

        self.stream_indices = set()
        self.case_id = None
        if event:
            self.append_event(event)

    def append_event(self, event: Event):
        """
        Append an event to the stack
        :param event:
        :return:
        """
        self.events.append(event)
        self.update_attributes(event)
        self.update_stream_indices(event)
        self.update_case_id(event)

    def update_attributes(self, event: Event):
        """
        Uppdate the stack attributes based on the new event
        :param event: new event
        :return:
        """
        for key, value in event.attributes.items():
            if value:
                self.attributes[key].add(value)

    def update_case_id(self, event: Event):
        """
        Updates the case id and data attributes of the stack based on the new event
        :param event:
        :return:
        """
        for key, value in event.attributes.items():
            if value and key in self.attribute_list:
                if not self.case_id:
                    # check existing case ids for key value pair
                    res = next((d for d in Stack.case_ids if key in d and d[key] == value), None)
                    # There is already an open Case with the observed attribute
                    if res:
                        # Assign it to this stack
                        self.case_id = res
                    else:
                        # Create new case with the attribute
                        case_id = {
                            "id": len(Stack.case_ids) + 1,
                            key: value}
                        Stack.case_ids.append(case_id)
                        # assign case id to this stack
                        self.case_id = case_id
                else:
                    # This stack already has a case id, add the new value to it
                    if key not in self.case_id:
                        self.case_id.update({key: value})

    def __getitem__(self, index) -> Event:
        return self.events[index]

    def __len__(self):
        return len(self.events)

    def update_stream_indices(self, event: Event):
        """
        Update the list of stream indices based on the new event
        :param event:
        :return:
        """
        self.stream_indices.add(event.stream_index)

    def contains_request_frame(self, request_frame: int) -> bool:
        """
        Checks whether the stack contains the specified request frame
        :param request_frame:
        :return: stack contains one event with the specified request frame as frame.number
        """
        return any(event.frame_number == request_frame for event in self.events)

    def contains_stream_index(self, stream_index: int) -> bool:
        """
        If the stack contains the specified stream index
        :param stream_index:
        :return:
        """
        return stream_index in self.stream_indices

    def contains_attribute(self, attribute_key, value) -> bool:
        """
        If the stack contains the specified attribute value
        :param attribute_key:
        :param value:
        :return:
        """
        res = value in self.attributes[attribute_key]
        return res

    def contains_attribute_case_id(self, attribute_key, value) -> bool:
        """
        If the stack contains the specified attribute value in its case id values
        :param attribute_key:
        :param value:
        :return:
        """
        res = self.has_attribute_case_id(attribute_key) and value in self.case_id.get(attribute_key)
        return res

    def case_id_matches_attribute(self, attribute_key, value) -> bool:
        """
        Whether the stack case id attribute matches with the value
        :param attribute_key:
        :param value:
        :return:
        """
        # get matching case ids from history
        res = next((d for d in Stack.case_ids if attribute_key in d and d[attribute_key] == value), None)

    @staticmethod
    def case_id_from_attribute(attribute_key, value):
        """
        Get the case id from an attribute value
        :param attribute_key:
        :param value:
        :return:
        """
        return next((d for d in Stack.case_ids if attribute_key in d and d[attribute_key] == value), None)

    def has_attribute(self, attribute_key) -> bool:
        """
        Whether the stack contains the specified attribute
        :param attribute_key:
        :return:
        """
        return len(self.attributes[attribute_key]) > 0

    def has_attribute_case_id(self, attribute_key) -> bool:
        """
        Whether the stack contains the specified case id attribute
        :param attribute_key:
        :return:
        """
        return self.case_id and attribute_key in self.case_id

    def __str__(self):
        return f"""Stack case_id:{self.case_id['id']} - len: {len(self.events)}"""

    def __repr__(self):
        return str(self)

    def confidence(self) -> bool:
        return self[-1].confidence

