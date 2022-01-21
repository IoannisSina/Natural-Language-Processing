import os
import errno
import pathlib
import json
import matplotlib.pyplot as plt
from nltk import word_tokenize
from nltk.stem import SnowballStemmer
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    pairwise_distances, 
    confusion_matrix, 
    ConfusionMatrixDisplay,
    recall_score,
    precision_score,
    f1_score,
    )


def create_folder(path):

    """
    Create a folder if it doesn't exist.
    """

    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

def read_dataset():

    """
    Read the 20 newsgroups dataset and return train and test subsets.
    """

    print("Reading dataset...")
    dataset_path = os.path.join(os.path.dirname(pathlib.Path(__file__).parent.resolve()), "dataB")  # Path to the dataset
    create_folder(dataset_path)  # Create the dataset folder if it doesn't exist
    train_set = fetch_20newsgroups(data_home=dataset_path, subset='train', categories=None)  # Get the train subset and save it to the dataB folder
    test_set = fetch_20newsgroups(data_home=dataset_path, subset='test', categories=None)  # Get the test subset and save it to the dataB folder

    return train_set, test_set

def dataset_preprocessing(train_set, test_set):

    """
    PREPROCESSING SYSTEM.
    Convert each document into a list of stemmed words. (train and test subsets)
    For the test subset, return a list of strings containing all stemmed words.
    For the train subset, return a list of lists of strings containing all stemmed words.
    Save these lists to two json files -> stemmed_train_set, stemmed_test_set.
    """

    print("Preprocessing dataset...")
    stemmer = SnowballStemmer('english', ignore_stopwords=True)  # Create a stemmer object
    stemmed_train_set = [' '.join([stemmer.stem(word) for word in word_tokenize(text)]) for text in train_set.data]  # List of lists of strings containing all stemmed words
    stemmed_test_set = [' '.join([stemmer.stem(word) for word in word_tokenize(text)]) for text in test_set.data]  # List of strings containing all stemmed words

    stemmed_train_set_path = os.path.join(os.path.dirname(pathlib.Path(__file__).parent.resolve()), "dataB", "stemmed_train_set.json")  # Path to the stemmed train set
    stemmed_test_set_path = os.path.join(os.path.dirname(pathlib.Path(__file__).parent.resolve()), "dataB", "stemmed_test_set.json")  # Path to the stemmed test set
    create_folder(stemmed_train_set_path)  # Create the stemmed train set folder if it doesn't exist
    create_folder(stemmed_test_set_path)  # Create the stemmed test set folder if it doesn't exist

    with open(stemmed_train_set_path, "w") as f:  # Save the stemmed train set to a json file
        json.dump(stemmed_train_set, f)

    with open(stemmed_test_set_path, "w") as f:  # Save the stemmed test set to a json file
        json.dump(stemmed_test_set, f)

def vectorize_stemmed_sets(stemmed_train_set, stemmed_test_set):

    """
    VECTORIZE STEMMED SETS.
    Use TfidfVectorizer to convert the stemmed sets to vectors containing the tf-idf weight for each stem.
    This functions will return a matrix. Each column will represent A document of the set. We will set features equal to 8000. (dimension of vectors equals 8000)
    The idfs will be the same in both sets as we use fit_transform and tranform. The vectorizer learns the idfs from the train set.
    The matrix returned is by default sparse.
    """

    print("Vectorizing stemmed sets...")
    vectorizer = TfidfVectorizer(stop_words='english', max_features=8000)  # Create a vectorizer object ignoring stop words and using 8000 features
    stemmed_vectors_train = vectorizer.fit_transform(stemmed_train_set)  # Vectorize the train set. Learn the idfs from the train set
    stemmed_vectors_test = vectorizer.transform(stemmed_test_set)  # Vectorize the test set

    return stemmed_vectors_train, stemmed_vectors_test

def compute_distances(stemmed_vectors_train, stemmed_vectors_test):

    """
    COMPUTE DISTANCES SYSTEM.
    Compute the pairwise distances between the train and test sets.
    Use metrics = ['cosine', 'euclidean', 'l1', 'l2'] which support sparse matrices.
    For each vector in the test set, get the index of the closest vector in the train set.
    Get the predicted categories by the targer list of the train set.
    Plot confusion matrix and f1, precision and recall scores.
    """

    print("Computing distances...")
    metrics = ['cosine', 'euclidean', 'l1', 'l2']  # List of metrics to use. These metrics support sparse matrices

    for metric in metrics:
        print("\n\nComputing distances with metric: {}\n\n".format(metric))

        matr = pairwise_distances(X=stemmed_vectors_train, Y=stemmed_vectors_test, metric=metric, n_jobs=-1)  # Compute the pairwise distances between the train and test sets
        min_indices = matr.argmin(axis=0)  # Get the index of the closest vector in the train set for each vector in the test set
        assert len(min_indices) == stemmed_vectors_test.shape[0], "Calculate vectors error!"  # Check that the number of indices is the same as the number of test vectors
        predicted_categories = [train_set.target[i] for i in min_indices]  # Get the predicted categories by the targer list of the train set

        print("Recall: {}".format(recall_score(test_set.target, predicted_categories, average='micro')))
        print("Precision: {}".format(precision_score(test_set.target, predicted_categories, average='micro')))
        print("F1: {}".format(f1_score(test_set.target, predicted_categories, average='micro')))

        cm = confusion_matrix(test_set.target, predicted_categories)  # Compute the confusion matrix
        display = ConfusionMatrixDisplay(confusion_matrix=cm)  # Create a confusion matrix display object
        display.plot()  # Plot the confusion matrix
        plt.title(metric + " distance")  # Set the title of the plot
        plt.show()  # Show the confusion matrix plot

if __name__ == "__main__":

    """
    Run dataset_preprocessing() once to create the stemmed_test_set and stemmed_train_set json files.
    """

    # Preprocessing system
    train_set, test_set = read_dataset()  # Read the dataset
    # dataset_preprocessing(train_set, test_set)  # Save stemmed test and train sets to json files
    stemmed_train_set = json.load(open(os.path.join(os.path.dirname(pathlib.Path(__file__).parent.resolve()), "dataB", "stemmed_train_set.json")))  # Load the stemmed train set from a json file
    stemmed_test_set = json.load(open(os.path.join(os.path.dirname(pathlib.Path(__file__).parent.resolve()), "dataB", "stemmed_test_set.json")))  # Load the stemmed test set from a json file

    # Vectorize system
    stemmed_vectors_train, stemmed_vectors_test = vectorize_stemmed_sets(stemmed_train_set, stemmed_test_set)  # Get the stemmed vectors

    # Compute distances system
    compute_distances(stemmed_vectors_train, stemmed_vectors_test)  # Compute the distances and prin confusion matrix, f1, precision and recall scores