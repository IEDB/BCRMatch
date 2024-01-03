#!/usr/bin/env python

import numpy as np
import pandas as pd
import xgboost
import platform

from sklearn.preprocessing import StandardScaler

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB

import os
# Ignore tensorflow's CUDA warning messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras import regularizers

sc = StandardScaler()

def preprocess_ml_dataset(dataset):
	training_dataset = pd.read_csv(dataset)
	subset_training_dataset = training_dataset.iloc[:,1:7]
	X = subset_training_dataset.iloc[:, :].values #matrix of features for all rows, and all columns except the last column. iloc stands for 'locate indexes'
	y = training_dataset.iloc[:, -1].values

	#Splitting data into training and testing datasets
	#from sklearn.model_selection import train_test_split
	#X_train, X_test_1, y_train, y_test_1 = train_test_split(X, y, test_size = 0.25, random_state = 0, stratify = y )
	
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

def LR(X_train, y_train):
	log_reg_classifier = LogisticRegression()
	log_reg_classifier.fit(X_train, y_train)
	return(log_reg_classifier)

def XGB(X_train, y_train):
	xgb_classifier = xgboost.XGBClassifier(random_state = 0, max_depth=6, n_estimators=200,learning_rate=0.1,min_child_weight=0.1,scale_pos_weight=0.1)
	xgb_classifier.fit(X_train, y_train)
	return(xgb_classifier)

def FFNN(X_train, y_train):
	if platform.processor() == "arm":
		opt = tf.keras.optimizers.legacy.SGD(learning_rate=0.001)
	else:
		opt = tf.keras.optimizers.SGD(learning_rate=0.001)
	#Initialize the ANN
	ann = Sequential()
	#Add input layer and first hidden layer
	ann.add(Dense(units=30, activation='relu',input_shape=(6,), kernel_regularizer = regularizers.L2(0.01)))
	#Add additional hidden layer
	for i in range(4):
		ann.add(Dense(units=30, activation='relu'))
	ann.add(Dropout(0.5))
	#Add output layer
	#ann.add(Dense(units=1, activation='sigmoid'))
	ann.add(Dense(units=1, activation='sigmoid'))
	#ann.summary()
	#Compiling the ANN
	ann.compile(optimizer = opt, loss= 'binary_crossentropy' ,metrics = [tf.keras.metrics.AUC()])
	ann.fit(X_train, y_train, batch_size = 128, epochs = 70)
	return(ann)