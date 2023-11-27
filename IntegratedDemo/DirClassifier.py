import joblib
import numpy as np

class DirClassifier:

    def __init__(self) -> None:
        
        self.model = joblib.load("./IntegratedDemo/model/clf_svc.joblib")
        self.le = joblib.load("./IntegratedDemo/model/le.joblib")
        self.co = 0.5
        self.label_thres = 0.1


    def get_class(self, diff_18, diff_20, diff_spec):
        pred = self.model.predict([[diff_18, diff_20, diff_spec]])
        return self.le.inverse_transform(pred)