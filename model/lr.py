from sklearn.linear_model import LogisticRegression

class LRModel:
    def __init__(self):
        self.model = LogisticRegression(solver='lbfgs')

    def fit(self, x_train, y_train):
        self.model.fit(x_train, y_train)

    def predict(self, x_test):
        return self.model.predict(x_test)