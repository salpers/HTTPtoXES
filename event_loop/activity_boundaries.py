import pandas as pd
import sklearn_crfsuite
from scipy.stats import entropy

from sklearn.metrics import multilabel_confusion_matrix
from sklearn_crfsuite import metrics

from event_loop.event import Event

cols = ["event_with_roles", "request_method_call", "selective_file_data",
        "origin_method", "origin_file_data"]

ENTROPY_THRESHOLD = 0.4


class ActivityBoundariesClassifier:
    """
    Classifier for identifying activity boundaries (start-event, between-event, end-event)
    """

    def __init__(self, df_train, df_test):
        """
        initialize and fit the classifier
        :param df_train: training data
        :param df_test: optional evlauation data
        """
        self.model = sklearn_crfsuite.CRF(
            max_iterations=200,
            c1=0.1,
            c2=0.01,
            all_possible_transitions=True
        )

        self.fit_on_train_data(df_train)

        if df_test is not None:
            self.evaluate(df_test)

    def fit_on_train_data(self, train):
        """
        fits the CRF model on the training data
        :param train: training data
        :return:
        """
        train_features = dict_to_features(train[cols].to_dict("records"))
        train_labels = extract_labels(train["ActivityAction"])
        self.model.fit(train_features, train_labels)

    def classify_event(self, event: Event):
        """
        Applies the CRF model to classify an event
        Sets event.activity_action
        :param event:
        :return:
        """
        marginals = self.model.predict_marginals_single([event.to_features()])[0]
        pred = get_max_from_dict(marginals)
        e = entropy([p for p in marginals.values()])

        if e > ENTROPY_THRESHOLD:
            event.confidence = False
            event.activity_action = pred
        else:
            event.confidence = True
            event.activity_action = pred

    def evaluate(self, test):
        """
        Evaluates the model on the test data
        :param test: test data
        :return:
        """
        test_features = dict_to_features(test[cols].to_dict("records"))
        test_labels = extract_labels(test["ActivityAction"])

        classes = self.model.classes_
        y_pred = self.model.predict(test_features)
        print(metrics.flat_f1_score(test_labels, y_pred, average='macro', labels=classes))
        print(metrics.flat_classification_report(test_labels, y_pred, classes))
        [print(label, "\n", matrix) for matrix, label in
         zip(multilabel_confusion_matrix(flatten(test_labels), flatten(y_pred), labels=classes), classes)]


def get_max_from_dict(d: dict):
    """
    Returns the key with the maximum value in the dictionary
    :param d: dictionary
    :return: max value
    """
    return max(d, key=lambda k: d[k])


def flatten(xss):
    """
    Flattens a list
    :param xss: list
    :return:
    """
    return [x for xs in xss for x in xs]


def dict_to_features(event_dict):
    """
    Generates a feature representation for the CRF model from a dictionary representing a single event
    :param event_dict:
    :return:
    """
    return [[{**d, "bias": 1.0}] for d in event_dict]


def extract_labels(labels):
    """
     Extracts labels for the CRF model from a dataframe column
    :param labels: labels
    :return:
    """

    return [[y] for y in labels]
