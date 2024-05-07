import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.preprocessing import LabelEncoder

from event_loop.activity_type import sequence_by_activities
from event_loop.event import Event
from event_loop.stack import Stack


class EventActivityAssignment:
    """
    Event-Activity Assignment component
    """

    def __init__(self, df_train, max_window_length, attributes):
        """Creates the Event-Activity Assignment component and fits it on training data"""
        self.model = None
        self.le = LabelEncoder()
        self.max_window_length = max_window_length
        self.fit_on_train_data(df_train)

        self.attributes = attributes

    def fit_on_train_data(self, train):
        """
        Fits the model on the training data
        :param train: training data
        :return:
        """
        train["joined_LE"] = self.le.fit_transform(train["event_with_roles"] + train["selective_file_data"])
        data_joined_LE = sequence_by_activities(train["joined_LE"], train["SequenceNumber"])
        unique_sequences = get_unique_sequences(data_joined_LE)
        self.model = [np.concatenate([sliding_window_view(seq, i) for seq in unique_sequences], axis=0) for i in
                      range(self.max_window_length)]

    def search_window_for_sequence(self, seq):
        """
        Check for pattern matches with the training data and return the count
        :param seq: array_like
                    sequence of events

        :return: number of occurences of seq in training data
        """
        return np.sum(np.all(self.model[len(seq)] == seq, axis=1))

    def assign_to_sequence(self, event: Event, stacks: list[Stack], n: int, exclude_indices: list[int]):
        """
        Generates candidate sequences for every event stack and assigns the event to a suiting one
        :param event: event to assign
        :param stacks: event stacks
        :param n: maximum length of candidate sequences
        :param exclude_indices: exclude indices for the stacks
        :return:
        """
        sequences = [
            self.le.transform([e.to_activity_model_string() for e in stack] + [event.to_activity_model_string()]) for
            stack in stacks]
        for i in range(n, 1, -1):
            res = [self.search_window_for_sequence(seq[-i:]) if j not in exclude_indices else -1 for j, seq in
                   enumerate(sequences)]
            max_res = max(res)
            idx = np.argmax(res)
            if max_res > 0:
                return idx
        return -1

    def exclude_stacks_by_attribute(self, stacks: list[Stack], event: Event) -> list[int]:
        """
        exclude stacks with different attributes than the event
        :param stacks:
        :param event:
        :return:
        """
        exclude_indices = []

        for key, value in event.attributes.items():
            if key in self.attributes and value:
                # exclude all stacks that have a different attribute
                exclude_indices.extend(i for i, stack in enumerate(stacks) if
                                       stack.has_attribute(key) and not stack.contains_attribute(key, value))
        return exclude_indices

    def check_stack_attributes(self, stacks: list[Stack], event: Event, exclude_indices: list[int]) -> int:
        """
        check stacks for similar attributes as the event
        :param stacks:
        :param event:
        :param exclude_indices:
        :return:
        """
        for key, value in event.attributes.items():
            if key in self.attributes and value:
                indices = [i for i, stack in enumerate(stacks) if
                           stack.contains_attribute(key, value) and i not in exclude_indices]
                if len(indices) == 1:
                    # we have a clear match -> return idx
                    return indices[0]

        return -1

    def check_stack_attributes_case_id(self, stacks: list[Stack], event: Event, exclude_indices: list[int]) -> int:
        """
        returns stack indices with a matching case id same as the events data attribtues
        :param stacks:
        :param event:
        :param exclude_indices:
        :return:
        """
        for key, value in event.attributes.items():
            if key in self.attributes and value:
                indices = [i for i, stack in enumerate(stacks) if
                           stack.case_id == Stack.case_id_from_attribute(key, value)]

                if len(indices) == 1:
                    # we have a clear match -> return idx
                    return indices[0]

        return -1

    def exclude_stacks_by_attribute_case_id(self, stacks: list[Stack], event: Event) -> list[
        int]:
        """
        generate a list of indices where the data attributes do not match the event
        :param stacks:
        :param event:
        :return:
        """
        exclude_indices = []

        for key, value in event.attributes.items():
            if key in self.attributes and value:
                # exclude all stacks that have a different attribute
                #
                for i, stack in enumerate(stacks):
                    event_case_id = Stack.case_id_from_attribute(key, value)
                    if event_case_id and stack.case_id and event_case_id != stack.case_id:
                        exclude_indices.append(i)
                # exclude_indices.extend(i for i, stack in enumerate(stacks) if Stack.case_id_from_attribute(key,
                # value) != stack.case_id and stack.case_id)
        return exclude_indices


def get_unique_sequences(seq_data):
    """
    get unique sequences from sequence data
    :param seq_data:
    :return:
    """
    # Convert each array to a tuple and create a set of tuples
    array_set = set(tuple(arr) for arr in seq_data)

    # Convert the set of tuples back to a list of NumPy arrays
    return [np.array(arr) for arr in array_set]


def search_stack_for_request_frame(frame_number, stacks):
    """
    returns the index of the stack which contains the request frame number
    :param frame_number:
    :param stacks:
    :return:
    """
    for index, stack in enumerate(stacks):
        if stack.contains_request_frame(frame_number):
            return index
    return -1


def search_stream_index(stacks: list[Stack], event: Event, exclude_indices: list[int]) -> int:
    """
    Search Stacks for the specified stream index
    :param stacks:
    :param event:
    :param exclude_indices:
    :return:
    """
    indices = [i for i, stack in enumerate(stacks) if
               stack.contains_stream_index(event.stream_index) and i not in exclude_indices]

    if len(indices) == 1:
        return indices[0]
    else:
        return -1
