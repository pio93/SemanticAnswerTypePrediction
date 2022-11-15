import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer

class LogRegCategorizer:
    def __init__(self, train_filename : str = './smart_dataset/datasets/dbpedia/smarttask_dbpedia_train.json'):
        self.df = pd.read_json(train_filename).dropna(subset=['question', 'category'])
        self.categories = self.df['category'].unique().tolist()
        self.count_vectorizer = CountVectorizer()
        self.x_train = self.count_vectorizer.fit_transform(self.df['question'].tolist())
        self.clf = LogisticRegression(random_state=0, solver='saga', max_iter=1000).fit(self.x_train, self.df['category'].to_list())
        # logistic regression model for predicting literal type
        x_lit_df = self.df[self.df['category']=='literal'].dropna(subset=['type'])
        x_lit_df = x_lit_df.explode('type')
        self.clf_literals = LogisticRegression(random_state=0, solver='saga', max_iter=1000).fit(
            self.count_vectorizer.transform(x_lit_df['question']), 
            x_lit_df['type'].tolist()
        )
    def predict(self, q_list: list[str]):
        # predict the category of a question
        x_test = self.count_vectorizer.transform(q_list)
        return self.clf.predict(x_test)

    def predict_literal_type(self, q_list: list[str]):
        # predict the type of questions categorized as literal
        x_lit_test = self.count_vectorizer.transform(q_list)
        return self.clf_literals.predict(x_lit_test)

