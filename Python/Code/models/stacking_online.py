#! /usr/bin/env python

import sys, math, numpy

from lib import util, config
from lib.online_svm import OnlineSVM
from lib.online_text_svm import OnlineTextSVM

class OnlineStacking(object):

    def __init__(self, n_models):
        self.n_models = n_models
        self.models = list()
        self.clf = None

    def get_classifier(self, level):
        if level == 1:
            return OnlineTextSVM(randomize = False)
        elif level == 2:
            return OnlineSVM(randomize = False)

    def predict(self, story):
        '''return the prediction from the current set of models'''
        # calculate the input for the second level classifier
        x = None
        for i in xrange(0, self.n_models):
            if x is None:
                x = self.models[i].predict(story)
            else:
                x = numpy.vstack((x, self.models[i].predict(story)))
        x = x.transpose()
        return self.clf.predict(x)

    def fit(self, stories, labels):
        '''fit all the models to the first few samples'''
        # train the first level models
        for i in xrange(0, self.n_models):
            self.models.append(self.get_classifier(level = 1))
            self.models[i].fit(stories, labels)
        # convert the data to second level training data
        x = None
        for i in xrange(0, self.n_models):
            if x is None:
                x = self.models[i].predict(stories)
            else:
                x = numpy.vstack((x, self.models[i].predict(stories)))
        x = x.transpose()
        # train the second level model
        self.clf = self.get_classifier(level = 2)
        self.clf.fit(x, labels)

    def add(self, story, label):
        '''update all the models with the current sample'''
        for i in xrange(0, self.n_models):
            self.models[i].add(story, label)
        x = None
        for i in xrange(0, self.n_models):
            if x is None:
                x = self.models[i].predict(story)
            else:
                x = numpy.vstack((x, self.models[i].predict(story)))
        x = x.transpose()
        self.clf.add(x, label)

def main():
    # initial setup
    labels, stories = util.get_distress_data(config.CONNECTION)
    clf = OnlineStacking(n_models = 5)
    total, correct = 0.0, 0.0

    # input first two samples (having different labels), and then continue with the online mode
    positive, negative = labels.index(1), labels.index(-1)
    clf.fit( [stories[positive], stories[negative]], [labels[positive], labels[negative]] )
    indices = [i for i in xrange(0, len(labels)) if i not in [positive, negative]]
    for i in indices:
        prediction = clf.predict(stories[i])
        clf.add(stories[i], labels[i])
        if prediction == labels[i]:
            correct = correct + 1
        total = total + 1
        print "#%d => Cumulative accuracy = %.3f" % (i, correct / total)

if __name__ == "__main__":
    main()

