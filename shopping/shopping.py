import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():
    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """

    with open(filename) as f:
        reader = csv.reader(f)
        next(reader)
        data = [row for row in reader]

    evidence = []
    labels = []

    for row in data:
        # Append each row to evidence list and append the label to labels list
        evidence.append([
            # Administrative, Administrative_Duration, Informational, Informational_Duration, ProductRelated
            int(row[0]), float(row[1]), int(row[2]), float(row[3]), int(row[4]),
            # ProductRelated_Duration, BounceRates, ExitRates, PageValues, SpecialDay
            float(row[5]), float(row[6]), float(row[7]), float(row[8]), float(row[9]),
            # Month
            int(0 if row[10] == "Jan" else 1 if row[10] == "Feb" else 2 if row[10] == "Mar" \
                else 3 if row[10] == "Apr" else 4 if row[10] == "May" else 5 if row[10] == "June" \
                else 6 if row[10] == "Jul" else 7 if row[10] == "Aug" else 8 if row[10] == "Sep" \
                else 9 if row[10] == "Oct" else 10 if row[10] == "Nov" else 11),
            # OperatingSystems, Browser, Region, TrafficType, VisitorType
            int(row[11]), int(row[12]), int(row[13]), int(row[14]), int(row[15] == "Returning_Visitor"),
            # Weekend
            int(row[16] == "TRUE")
        ])
        labels.append(int(row[17] == "TRUE"))

    return (evidence, labels)


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """

    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """

    true_positive_rate = 0
    true_negative_rate = 0
    total_positive_rate = 0
    total_negative_rate = 0

    for i in range(len(labels)):
        # If the label is positive, increment total positive rate and true positive rate if the prediction is correct
        if labels[i] == 1:
            total_positive_rate += 1
            if predictions[i] == 1:
                true_positive_rate += 1
        # Otherwise, increment total negative rate and true negative rate if the prediction is correct
        else:
            total_negative_rate += 1
            if predictions[i] == 0:
                true_negative_rate += 1

    # Divide true positive rate and true negative rate by total positive rate and total negative rate respectively
    # to get sensitivity and specificity which are the proportion of actual positive labels and actual negative labels
    sensitivity = true_positive_rate / total_positive_rate
    specificity = true_negative_rate / total_negative_rate

    return (sensitivity, specificity)


if __name__ == "__main__":
    main()
