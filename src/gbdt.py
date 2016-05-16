#!/usr/bin/env python
# coding=utf-8

import time
import numpy as np
import matplotlib.pyplot as plt
import logging
from sklearn.ensemble import GradientBoostingRegressor
import logging.config
from sklearn.externals import joblib
from utils import feature_reduction, evaluate
from multiprocessing import Process
import sys
import getopt
import solver
from solver import HandlePredict

sys.path.insert(0, '..')
from configure import *

logging.config.fileConfig('logging.conf')
logging.addLevelName(logging.WARNING, "\033[1;34m[%s]\033[1;0m" % logging.getLevelName(logging.WARNING))
logging.addLevelName(logging.ERROR, "\033[1;41m[%s]\033[1;0m" % logging.getLevelName(logging.ERROR))

def usage() :
    """
    """
    print 'gbdt.py usage:'
    print '-h, --help: print help message'
    print '-t, --type: the type of data need to handler, default = unit'

def loss_function(label, predict) :
    """
    """
    return sum((abs(label - predict) / label) ** 2) / len(label)

def gbdt_solver(train_x, train_y, validation_x, test_x, now_time , validation_y = np.array([]), feature_names = [], validation_artist_id=None, validation_month=None, validation_label_day=None) :
    """
    """
    logging.info('start training the gbdt model')
    params = {
        'n_estimators': 0,
        'learning_rate': 0.03,
        'random_state': 1000000007,
        'max_depth': 3,
        'verbose' : 2,
        'warm_start': True
    }

    with open(ROOT + '/result/' + now_time + '/parameters.param', 'w') as out :
        for key, val in params.items():
            out.write(str(key) + ': ' + str(val) + '\n')

    max_num_round = 700 
    batch = 10
    best_val = -1e60
    history_validation_val = []
    best_num_round = -1
    curr_round = 0

    assert max_num_round % batch == 0
    gb = GradientBoostingRegressor(**params)
    for step in xrange(max_num_round / batch) :
        train_x = train_x.copy(order='C')
        train_y = train_y.copy(order='C')
        gb.n_estimators += batch
        logging.info('current round is: %d' % curr_round)
        #gb.set_params(**params)
        gb.fit(train_x, train_y)
        curr_round += batch
        predict = gb.predict(validation_x)
        predict = HandlePredict(predict.tolist())
        curr_val = evaluate.evaluate(predict, validation_y.tolist(), validation_artist_id, validation_month, validation_label_day)
        history_validation_val.append(curr_val)
        logging.info('the current score is %.10f' % curr_val)
        if curr_round >= 150 and curr_val > best_val:
            best_num_round = curr_round
            best_val = curr_val
            joblib.dump(gb, ROOT + '/result/' + now_time + '/model/gbdt.pkl')

    logging.info('the best round is %d, the score is %.10f' % (best_num_round, best_val))
    gb = joblib.load(ROOT + '/result/' + now_time + '/model/gbdt.pkl')
    predict = gb.predict(validation_x)

    # unable to use matplotlib if used multiprocessing
    if validation_y.shape[0] and False :
        logging.info('the loss in Training set is %.4f' % loss_function(train_y, gb.predict(train_x)))
        logging.info('the loss in Validation set is %.4f' % loss_function(validation_y, gb.predict(validation_x)))

        plt.figure(figsize=(12, 6))
        # Plot feature importance
        plt.subplot(1, 2, 1)
        if (feature_names) == 0:
            feature_names = [str(i + 1) for i in xrange(validation_x.shape[0])]
        feature_names = np.array(feature_names)
        feature_importance = gb.feature_importances_
        feature_importance = 100.0 * (feature_importance / feature_importance.max())
        sorted_idx = np.argsort(feature_importance)
        pos = np.arange(sorted_idx.shape[0]) + .5
        plt.barh(pos, feature_importance[sorted_idx], align='center')
        plt.yticks(pos, feature_names[sorted_idx])
        plt.xlabel('Relative Importance')
        plt.title('Variable Importance')


        # Plot training deviance
        plt.subplot(1, 2, 2)
        test_score = np.zeros((params['n_estimators'],), dtype=np.float64)
        for i, y_pred in enumerate(gb.staged_predict(validation_x)):
            test_score[i] = loss_function(validation_y, y_pred)
        plt.title('Deviance')
        plt.plot(np.arange(params['n_estimators']) + 1, gb.train_score_, 'b-',
                          label='Training Set Deviance')
        plt.plot(np.arange(params['n_estimators']) + 1, test_score, 'r-',
                          label='Test Set Deviance')
        plt.legend(loc='upper right')
        plt.xlabel('Boosting Iterations')
        plt.ylabel('Deviance')

        plt.savefig(ROOT + '/result/' + now_time + '/statistics.jpg')

    return predict, gb.predict(test_x)

def main (type) :
    """
    """
    solver.main(gbdt_solver, 1, type, feature_reduction.undo)
    solver.main(gbdt_solver, 2, type, feature_reduction.undo)
    return 
    processes = []
    process1 = Process(target = solver.main, args = (gbdt_solver, 1, type, feature_reduction.undo))
    process1.start()
    processes.append(process1)
    process2 = Process(target = solver.main, args = (gbdt_solver, 2, type, feature_reduction.undo))
    process2.start()
    processes.append(process2)
    for process in processes:
        process.join()
    evaluate.mergeoutput()

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hj:t:', ['type=', 'jobs=', 'help'])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)

    n_jobs = 1
    type = 'unit'
    for o, a in opts:
        if o in ('-h', '--help') :
            usage()
            sys.exit(1)
        elif o in ('-t', '--type') :
            type = a
        else:
            print 'invalid parameter:', o
            usage()
            sys.exit(1)

    main(type)
