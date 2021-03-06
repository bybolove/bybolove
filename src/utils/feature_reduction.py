#!/usr/bin/env python
# coding=utf-8

import copy
import sys
import logging
import pandas as pd
import numpy as np
import utils.pkl as pkl
from sklearn.decomposition import PCA 
from sklearn.ensemble import GradientBoostingRegressor
import xgboost as xgb

sys.path.insert(0, '..')
sys.path.insert(0, '../..')
from configure import *

def pca_solver (data, K = PCACOMPONENT) :
    """
    Linear dimensionality reduction by pricipal component analysis
    @parameters:
        data: original data (dataFrame)
    @return:
        $1: the data after handlering (ndarray)
    """
    logging.info ('begin to run pca')
    logging.info ('the number of components in pca is %d' % K)
    pca = PCA (n_components = K , whiten = True)
    if type (data) is pd.DataFrame :
        data_values = data.values
    else :
        data_values = data
    pca.fit (data_values)
    pca_data = pca.transform (data_values)
    logging.info ('finished pca')
    return pca_data

def pca (train_x,  train_y, validation_x, validation_y, test_x, feature_name, gap_month = 1, type = 'unit') :
    """
    """
    if train_x.shape[1] != validation_x.shape[1] :
        logging.error('the number of feature in different data set is mismatch')
        exit(-1)
    
    pca_data = np.vstack ([train_x, validation_x, test_x])
    pca_data = pca_solver (pca_data)
    new_feature_name = [str(i + 1) for i in xrange(pca_data.shape[1])]
    logging.info('finished feature reduction, the original feature is :')
    print feature_name
    logging.info('the new feature is :')
    print new_feature_name
    return pca_data[:train_x.shape[0],:], pca_data[train_x.shape[0]:-test_x.shape[0]], pca_data[-test_x.shape[0]:], new_feature_name

def gbdt_feature_importance (train_x, train_y, validation_x, validation_y, feature_name, gap_month = 1, type = 'unit') :
    filepath = ROOT + '/data/feature_importance_gbdt_%d_%s' % (gap_month, type)
    if os.path.exists (filepath) :
        logging.info (filepath + ' exists!')
        feature_importance = pkl.grab (filepath)
    else :
        logging.info ('feature_importance start!')
        logging.info ('the size of data used to cal feature importance is (%d %d)' % train_x.shape)
         
        remaining_feature = copy.deepcopy(feature_name)
        each_step_removed = 20
        max_round = 1
        feature_rank = {}
        rank = 0 
        while len(remaining_feature) > 20 and max_round > 0 :
            max_round -= 1
            logging.info('the number of remaining feature is %d' % len(remaining_feature))
            gb = GradientBoostingRegressor(n_estimators = 300 , learning_rate = 0.03 , max_depth = 5, min_samples_leaf = 1000 , random_state = 1000000007, verbose = 1).fit (train_x, train_y)
            feature_importance = gb.feature_importances_
            feature_importance = 100.0 * (feature_importance / feature_importance.max ())

            sorted_index = np.argsort (feature_importance)[::-1]

            for feature_index in sorted_index[::-1]:
                rank += 1
                feature_rank[remaining_feature[feature_index]] = rank 

            with open (filepath + '_' + str(len(remaining_feature)), 'w') as out :
                for key, val, in sorted(feature_rank.items(), key = lambda v : v[1], reverse = True) :
                    out.write('%s %d\n' % (key, val))
            train_x = train_x[:,sorted_index[:-each_step_removed]] 
            remaining_feature = [remaining_feature[p] for p in sorted_index[:-each_step_removed]]

        feature_importance = []
        for feature in feature_name :
            feature_importance.append(feature_rank[feature])
        pkl.store (feature_importance, filepath)
    return feature_importance

def gbdt_dimreduce_threshold (train_x, train_y, validation_x, validation_y, test_x,  feature_name, feature_threshold = GBDTFEATURETHRESHOLD, gap_month = 1, type = 'unit') :
    """
    """
    if train_x.shape[0] != train_y.shape[0] or validation_x.shape[0] != validation_y.shape[0] :
        logging.error('the size of data set is mismatch')
        exit(-1)
    if train_x.shape[1] != validation_x.shape[1] :
        logging.error('the number of feature in different data set is mismatch')
        exit(-1)
    logging.info ('begin gbdt_dimreduce_threshold')
    logging.info ('before gbdt dim-reducing : (%d %d)' % (train_x.shape))
    data = np.vstack([train_x, validation_x])
    label = np.hstack([train_y, validation_y])
    feature_importance = gbdt_feature_importance (data, label, gap_month = gap_month, type = type)
    important_index = np.where (feature_importance > feature_threshold)[0]
    sorted_index = np.argsort (feature_importance[important_index])[::-1]

    new_train = train_x[:,important_index][:,sorted_index]
    new_validation = validation_x[:,important_index][:,sorted_index]
    new_test = test_x[:,important_index][:,sorted_index]
    new_feature_name = [feature_name[i] for i in important_index]
    new_feature_name = [new_feature_name[i] for i in sorted_index]
    logging.info ('after gbdt dim-reducing : (%d %d)' % (new_train.shape))
    logging.info('finished feature reduction, the original feature is :')
    print feature_name
    logging.info('the new feature is :')
    print new_feature_name
    return new_train, new_validation, new_test, new_feature_name

def gbdt_dimreduce_number (train_x, train_y, validation_x, validation_y, test_x, feature_name, feature_number = GBDTFEATURENUMBER, gap_month = 1, type = 'unit') :
    """
    """
    if train_x.shape[0] != train_y.shape[0] or validation_x.shape[0] != validation_y.shape[0] :
        logging.error('the size of data set is mismatch')
        exit(-1)
    if train_x.shape[1] != validation_x.shape[1] :
        logging.error('the number of feature in different data set is mismatch')
        exit(-1)
    logging.info ('begin gbdt_dimreduce_number')
    logging.info ('before gbdt dim-reducing : (%d %d)' % (train_x.shape))
    data = np.vstack([train_x, validation_x])
    label = np.hstack([train_y, validation_y])
    feature_importance = gbdt_feature_importance (data, label, validation_x, validation_y, feature_name, gap_month = gap_month, type = type)
    sorted_index = np.argsort (feature_importance)[::-1]
    sorted_index = sorted_index[:feature_number]
    
    new_train = train_x[:,sorted_index]
    new_validation = validation_x[:,sorted_index]
    new_test = test_x[:,sorted_index]
    new_feature_name = [feature_name[i] for i in sorted_index]
    logging.info ('after gbdt dim-reducing : (%d %d)' % (new_train.shape))
    logging.info('finished feature reduction, the original feature is :')
    print feature_name
    logging.info('the new feature is :')
    print new_feature_name
    return new_train, new_validation, new_test, new_feature_name

def mix_pca_gbdt (train_x, train_y, validation_x, validation_y, test_x, feature_name, feature_number = GBDTFEATURENUMBER, gap_month = 1, type = 'unit') :
    """
    """
    if train_x.shape[0] != train_y.shape[0] or validation_x.shape[0] != validation_y.shape[0] :
        logging.error('the size of data set is mismatch')
        exit(-1)
    if train_x.shape[1] != validation_x.shape[1] :
        logging.error('the number of feature in different data set is mismatch')
        exit(-1)
    logging.info ('before mix_pca_gbdt dim-reducing : (%d %d)' % (train_x.shape))
    data = np.vstack([train_x, validation_x])
    label = np.hstack([train_y, validation_y])
    feature_importance = gbdt_feature_importance (data, label, gap_month = gap_month, type = type)
    sorted_index = np.argsort (feature_importance)[::-1]

    new_train_gbdt = train_x[:,sorted_index[:feature_number]]
    new_validation_gbdt = validation_x[:,sorted_index[:feature_number]]
    new_test_gbdt = test_x[:,sorted_index[:feature_number]]
    new_feature_name_gbdt = [feature_name[i] for i in sorted_index[:feature_number]]

    new_train_pca, new_validation_pca, new_test_pca, new_feature_name_pca = pca(train_x[:,feature_number:feature_number + REMAININGFORPCA], None,
                                                                                validation_x[:,feature_number:feature_number + REMAININGFORPCA], None,
                                                                                test_x[:,feature_number:feature_number + REMAININGFORPCA], 
                                                                                feature_name = None, gap_month = gap_month, type = type
                                                                               )
    
    new_train = np.hstack([new_train_gbdt, new_train_pca]) 
    new_validation = np.hstack([new_validation_gbdt, new_validation_pca])
    new_test = np.hstack([new_test_gbdt, new_test_pca])
    new_feature_name = new_feature_name_gbdt; new_feature_name.extend(new_feature_name_pca)

    logging.info ('after mix_pca_gbdt dim-reducing : (%d %d)' % (new_train.shape))
    return new_train, new_validation, new_test, new_feature_name

def undo (train_x, train_y, validation_x, validation_y, test_x, feature_name, gap_month = 1, type = 'unit') :
    """
    nothing to do
    """
    logging.info('no feature reduction')
    return train_x, validation_x, test_x, feature_name

def xgb_feature_importance (train_x, train_y, validation_x, validation_y, feature_name, gap_month = 1, type = 'unit') :
    filepath = ROOT + '/data/xgb_feature_importance_xgb_%d_%s' % (gap_month, type)
    if os.path.exists (filepath) :
        logging.info (filepath + ' exists!')
        feature_importance = pkl.grab (filepath)
    else :
        logging.info ('xgb_feature_importance start!')
        logging.info ('the size of data used to cal feature importance is (%d %d)' % train_x.shape)
        
        remaining_feature=copy.deepcopy(feature_name)
        each_step_removed=20
        feature_rank={}
        max_round = 1
        rank=0
        params = {
            'eta' : 0.03,
            'silent': 1,
            'objective' : 'reg:linear',
            'max_depth' : 4,
            'seed' : 1000000007,
            'gamma': 0,  # default 0, minimum loss reduction required to partition
            'min_child_weight':1, # default 1, minimun number of instances in each node
            'alpha':0, # default 0, L1 norm
            'lambda':1, # default 1, L2 norm
        }       
        while len(remaining_feature) > 20 and max_round > 0:
            max_round -= 1
            logging.info('the number of remaining feature is %d' % len(remaining_feature))
            dtrain=xgb.DMatrix(train_x, label=train_y, feature_names=remaining_feature)
            dvalidation=xgb.DMatrix(validation_x, label=validation_y, feature_names=remaining_feature)
            watchlist=[(dtrain, 'train'), (dvalidation, 'validation')]
            evals_result={}
            bst = xgb.train(params, dtrain, num_boost_round=300, evals=watchlist, evals_result=evals_result, early_stopping_rounds=15)
            feature_importance_tmp=bst.get_fscore()
            feature_importance = np.array([ feature_importance_tmp[c] if c in feature_importance_tmp else 0 for c in remaining_feature],dtype=np.float64)
            feature_importance = 100.0 * (feature_importance / feature_importance.max())       

            sorted_index = np.argsort (feature_importance)[::-1]

            for feature_index in sorted_index[::-1]:
                rank += 1
                feature_rank[remaining_feature[feature_index]] = rank 

            with open (filepath + '_' + str(len(remaining_feature)), 'w') as out :
                for key, val, in sorted(feature_rank.items(), key = lambda v : v[1], reverse = True) :
                    out.write('%s %d\n' % (key, val))
            train_x = train_x[:,sorted_index[:-each_step_removed]] 
            validation_x = validation_x[:, sorted_index[:-each_step_removed]]
            remaining_feature = [remaining_feature[p] for p in sorted_index[:-each_step_removed]]

        feature_importance = []
        for feature in feature_name :
            feature_importance.append(feature_rank[feature])
        pkl.store (feature_importance, filepath)
    return feature_importance

def xgb_dimreduce_threshold (train_x, train_y, validation_x, validation_y, test_x,  feature_name, feature_threshold = GBDTFEATURETHRESHOLD, gap_month = 1, type = 'unit') :
    """
    """
    if train_x.shape[0] != train_y.shape[0] or validation_x.shape[0] != validation_y.shape[0] :
        logging.error('the size of data set is mismatch')
        exit(-1)
    if train_x.shape[1] != validation_x.shape[1] :
        logging.error('the number of feature in different data set is mismatch')
        exit(-1)
    logging.info ('begin xgb_dimreduce_threshold')
    logging.info ('before xgb dim-reducing : (%d %d)' % (train_x.shape))
    feature_importance = xgb_feature_importance (train_x, train_y, validation_x, validation_y, feature_name, gap_month = gap_month, type = type)
    important_index = np.where (feature_importance > feature_threshold)[0]
    sorted_index = np.argsort (feature_importance[important_index])[::-1]

    new_train = train_x[:,important_index][:,sorted_index]
    new_validation = validation_x[:,important_index][:,sorted_index]
    new_test = test_x[:,important_index][:,sorted_index]
    new_feature_name = [feature_name[i] for i in important_index]
    new_feature_name = [new_feature_name[i] for i in sorted_index]
    logging.info ('after xgb dim-reducing : (%d %d)' % (new_train.shape))
    logging.info('finished feature reduction, the original feature is :')
    print feature_name
    logging.info('the new feature is :')
    print new_feature_name
    return new_train, new_validation, new_test, new_feature_name

def xgb_dimreduce_number (train_x, train_y, validation_x, validation_y, test_x, feature_name, feature_number = GBDTFEATURENUMBER, gap_month = 1, type = 'unit') :
    """
    """
    if train_x.shape[0] != train_y.shape[0] or validation_x.shape[0] != validation_y.shape[0] :
        logging.error('the size of data set is mismatch')
        exit(-1)
    if train_x.shape[1] != validation_x.shape[1] :
        logging.error('the number of feature in different data set is mismatch')
        exit(-1)
    logging.info ('begin xgb_dimreduce_number')
    logging.info ('before xgb dim-reducing : (%d %d)' % (train_x.shape))
    data = np.vstack([train_x, validation_x])
    label = np.hstack([train_y, validation_y])
    feature_importance = xgb_feature_importance (data, label, validation_x, validation_y, feature_name, gap_month = gap_month, type = type)
    sorted_index = np.argsort (feature_importance)[::-1]
    sorted_index = sorted_index[:feature_number]
    
    new_train = train_x[:,sorted_index]
    new_validation = validation_x[:,sorted_index]
    new_test = test_x[:,sorted_index]
    new_feature_name = [feature_name[i] for i in sorted_index]
    logging.info ('after xgb dim-reducing : (%d %d)' % (new_train.shape))
    logging.info('finished feature reduction, the original feature is :')
    print feature_name
    logging.info('the new feature is :')
    print new_feature_name
    return new_train, new_validation, new_test, new_feature_name

if __name__ == '__main__' :
    pass
