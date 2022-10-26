from sklearn import preprocessing
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import recall_score, precision_score, f1_score, accuracy_score
from sklearn import svm
import json

def load_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def preprocess(raw_data):
    data = [elem.get('question')for elem in raw_data if elem.get('question') != None]
    labels = [elem.get('category') for elem in raw_data if elem.get('question') != None]
    le = preprocessing.LabelEncoder()
    labels = le.fit_transform(labels).tolist()

    return data, labels

def extract_features(data):
    vectorizer = TfidfVectorizer(max_features=1000)
    vector = vectorizer.fit_transform(data)
    features = vector.toarray()

    return features

def train(X, y):
    clf = svm.LinearSVC(C=0.01).fit(X, y)
    clf.fit(X, y)
    return clf

def evaluate(y, y_pred):
    recall = recall_score(y, y_pred, average='macro')
    precision = precision_score(y, y_pred, average='macro')
    f1 = f1_score(y, y_pred, average='macro')
    accuracy = accuracy_score(y, y_pred)

    return recall, precision, f1, accuracy

train_raw_data = load_data('data\smarttask_dbpedia_train.json')
test_raw_data = load_data('data\smarttask_dbpedia_test.json')
train_data, train_labels = preprocess(train_raw_data)
test_data, test_labels = preprocess(test_raw_data)
train_features = extract_features(train_data)
test_features = extract_features(test_data)
classifier = train(train_features, train_labels)
predicted_labels = classifier.predict(test_features)
recall, precision, f1, accuracy = evaluate(test_labels, predicted_labels)
print('recall: ' + str(recall))
print('precision: ' + str(precision))
print('accuracy: ' + str(accuracy))
print('f1: ' + str(f1))