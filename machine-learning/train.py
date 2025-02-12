import dataset as ds
import labelingFunctions as lf
from snorkel.labeling import LabelModel, PandasLFApplier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn.naive_bayes import GaussianNB
import fasttext
import random
import nltk
from nltk.corpus import wordnet as wn
from snorkel.augmentation import transformation_function
import pickle
import pandas as pd

# Define the label mappings for convenience
ABSTAIN = 0
POSITIVE = 1
NEGATIVE = 2


df_train = ds.get_davison() #out performed combined dataset

# Define the set of labeling functions (LFs)
lfs = [lf.lf_keyword_strong_swearing, lf.lf_keyword_violence,
        lf.lf_spacy_words_sexism, lf.lf_keyword_raicism, lf.lf_spacy_words_gpe,
        lf.lf_keyword_shaming,  lf.lf_spacy_threat, lf.lf_spacy_terrorism,
        lf.lf_neg_nonehumansubject]
# Unused ones :
# lf.lf_spacy_animals, lf.lf_spacy_politics,  # giving false positives

# Apply the LFs to the unlabeled training data
applier = PandasLFApplier(lfs)
L_train = applier.apply(df_train)

# Train the label model and compute the training labels
# Cardinality was 2. Got : ValueError: L_train has cardinality 3, cardinality=2 passed in.
label_model = LabelModel(cardinality=3, verbose=True)
label_model.fit(L_train, n_epochs=500, log_freq=50, seed=123)
df_train["label"] = label_model.predict(L=L_train, tie_break_policy="abstain")

#output
df_train.to_csv('labelledDataset.csv', index = None, header = True)

# Filter out useless data
df_train = df_train[df_train.label != ABSTAIN]
print("Useful data remaining: " + str(df_train.shape[0]))

# Ignoring Transformation Functions for Data Augmentation for now...
# TODO: create transformation functions for different categories of hatespeech

# Ignoring slicing, don't think we need it

# Training a Classifier
docs = df_train.iloc[:,0].tolist() # first column of data frame (first_name)
print(df_train)

train_text = []
for doc in docs:
    # print(doc.text)
    train_text.append(doc.text)
# print(train_text)

count_vec = CountVectorizer(ngram_range=(1, 2))
X_train = count_vec.fit_transform(train_text)

# Support Vector Machines
# clf = svm.SVC(kernel='linear', C = 1.0)
# clf.fit(X=X_train, y=df_train.label.values)

# Naive Bayes Classification
# gnb = GaussianNB()
# gnb.fit(X=X_train, y=df_train.label.values)

# over
clf = LogisticRegression(solver="lbfgs", max_iter=1000)
clf.fit(X=X_train, y=df_train.label.values)

# save the model to disk
pickle.dump(clf, open("./hate_speech_classifier", 'wb'))
pickle.dump(count_vec, open("./hate_speech_CountVectorizer", 'wb'))
