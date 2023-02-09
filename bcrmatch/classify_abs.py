#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.preprocessing import StandardScaler

from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
sc = StandardScaler()

def preprocess_ml_dataset(dataset):
	training_dataset = pd.read_csv(dataset)
	subset_training_dataset = training_dataset.iloc[:,11:17]
	X = subset_training_dataset.iloc[:, :].values #matrix of features for all rows, and all columns except the last column. iloc stands for 'locate indexes'
	y = training_dataset.iloc[:, -1].values
	
	X[:, :] = sc.fit_transform(X[:, :])
	return(X, y)

def preprocess_input_data(myList):
	input_data = sc.transform(([myList]))
	return(input_data)

def RF(X_train,y_train):
	rf_classifier = RandomForestClassifier(n_estimators = 100, criterion ='entropy', random_state=0, max_depth = 10)
	rf_classifier.fit(X_train, y_train)
	return(rf_classifier)

def GNB(X_train,y_train):
	gb_classifier = GaussianNB()
	gb_classifier.fit(X_train, y_train)
	return(gb_classifier)

