import sklearn_crfsuite

from event_loop.stack import Stack

cols = ["event_with_roles", "request_method_call", "selective_file_data",
        "origin_method", "origin_file_data"]


class ActivityTypeClassifier:
    """
    Classifier for identifying activity type
    """
    def __init__(self, df_train):
        """
        initialize the classifier and fits it on training data
        :param df_train: training data
        """
        self.model = sklearn_crfsuite.CRF(
            max_iterations=200,
            c1=0.1,
            c2=0.01,
            all_possible_transitions=True
            # all_possible_transitions=True
        )

        self.fit_on_train_data(df_train)

    def fit_on_train_data(self, train):
        """
        Fits the classifier on the training data
        :param train: training data
        :return:
        """
        activity_sequences = sequence_by_activities(train, train["SequenceNumber"])
        features_seq_window = [seq2features(seq[cols].to_dict("records"), 10, 10) for seq in activity_sequences]
        labels_seq_window = [seq["BusinessActivity"] for seq in activity_sequences]
        X_train = flatten_and_encapsulate(features_seq_window)
        y_train = flatten_and_encapsulate(labels_seq_window)

        self.model.fit(X_train, y_train)

    def classify_stack(self, stack: Stack):
        """
        Classifies the activity type of an activity
        :param stack:
        :return:
        """
        seq = seq2features([event.to_features() for event in stack], 10, 10)
        pred = self.model.predict_marginals([[ele] for ele in seq])
        pred_cwmv = confidence_weighted_majority_voting(pred)
        stack.activity_type = pred_cwmv


def confidence_weighted_majority_voting(predictions):
    """
    Perform confidence-weighted majority voting on each sublist of predictions.

    :param predictions: A list of dictionaries where each dictionary contains predictions and their confidences.
    :return: A list of majority voted predictions for each sublist.
    """

    # Initialize variables to store cumulative confidences for each prediction
    cumulative_confidences = {label: 0.0 for label in predictions[0][0].keys()}

    # Calculate cumulative confidences for each prediction across all dictionaries in the sublist
    for prediction_dict in predictions:
        for label, confidence in prediction_dict[0].items():
            cumulative_confidences[label] += confidence

    # Find the prediction with the maximum cumulative confidence
    return max(cumulative_confidences, key=cumulative_confidences.get)


def sequence_by_activities(data, seq_data):
    """Returns a list of sequences indicated by seq_data value"""
    return [data[seq_data == i] for i in range(seq_data.max())]


def seq2features(seq, bw, fw):
    """
    generates events from a sequence
    :param seq:
    :param bw:
    :param fw:
    :return:
    """
    return [event2features(seq, i, bw, fw) for i in range(len(seq))]


def event2features(seq, i, bw, fw):
    """
    Generates context features from an event
    :param seq: sequence
    :param i: current index of the sequence
    :param bw: backward window
    :param fw: forward window
    :return:
    """
    features = {"bias": 1.0}

    features.update({
        f"0:{k}": v for k, v in seq[i].items()
    })

    for j in range(1, bw + 1):
        index = i - j
        if index >= 0:
            features.update({
                f"-{j}:{k}": v for k, v in seq[index].items()
            })
        else:
            features.update({
                f"-{j}:{k}": "NoMessage" for k, _ in seq[i].items()
            })

    for j in range(1, fw + 1):
        index = i + j
        if index < len(seq):
            features.update({
                f"+{j}:{k}": v for k, v in seq[index].items()
            })
        else:
            features.update({
                f"+{j}:{k}": "NoMessage" for k, _ in seq[i].items()
            })

    return features


def flatten_and_encapsulate(list_of_list):
    """Processes a list of lists for the CRF to handle"""
    return [[item] for sublist in list_of_list for item in sublist]
