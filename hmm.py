# -*- coding: utf-8 -*-
from utils import *
from hmmlearn import hmm


def train_model_hmm(train_dir):
    """
    :param train_dir: derivative order, default order is 2
    :return: hmm_models
    """
    hmm_models = []
    # iterate through the training directory
    for digit in os.listdir(train_dir):
        # get the directory of digit
        digit_dir = os.path.join(train_dir, digit)
        # get the digit label
        label = digit_dir[digit_dir.rfind('/') + 1:]
        # start training
        X = np.array([])
        train_files = [x for x in os.listdir(digit_dir) if x.endswith('.wav')]
        for file_name in train_files:
            file_path = os.path.join(digit_dir, file_name)
            # get mfcc feature and ignore the warning
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                features_mfcc = mfcc(file_path)
            # append mfcc to X
            if len(X) == 0:
                X = features_mfcc
            else:
                X = np.append(X, features_mfcc, axis=0)

            # get the hmm model
            model = hmm.GaussianHMM(n_components=4, covariance_type='diag', n_iter=1800)
            # fit hmm model
            np.seterr(all='ignore')
            model.fit(X)
            hmm_models.append((model, label))
    return hmm_models


def predict_hmm(hmm_models, test_files):
    """
    :param hmm_models: trained hmm models
    :param test_files: test files
    """
    count = 0
    pred_true = 0
    for test_file in test_files:
        # get mfcc feature and ignore the warning
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            features_mfcc = mfcc(test_file)
        # calculate the score and get the maximum score
        max_score = -float('inf')
        predicted_label = ""
        for item in hmm_models:
            model, label = item
            score = model.score(features_mfcc)
            if score > max_score:
                max_score = score
                predicted_label = label

        # determine if the prediction is correct
        count += 1
        if os.path.splitext(test_file)[0][-1] == predicted_label[-1]:
            pred_true += 1
    print("---------- HMM (GaussianHMM) ----------")
    print("Train num: 160, Test num: %d, Predict true num: %d"%(count, pred_true))
    print("Accuracy: %.2f"%(pred_true / count))


if __name__ == '__main__':
    # train the model
    hmm_models = train_model_hmm("./processed_train_records")

    # append all test records and start digit recognition
    test_files = []
    for root, dirs, files in os.walk("./processed_test_records"):
        for file in files:
            # Make sure the suffix is correct and avoid the influence of hidden files
            if os.path.splitext(file)[1] == '.wav':
                test_files.append(os.path.join(root, file))
    predict_hmm(hmm_models, test_files)

