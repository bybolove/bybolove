#!/usr/bin/env python
# coding=utf-8

import logging 
import math
import os
import datetime
import sys

sys.path.insert(0, '..')
sys.path.insert(0, '../..')
from configure import *

def evaluate(predict, label, artist, month, day) :
    """
    """
    if len(predict) != len(label):
        logging.error('the number of predict is not match with label')
        exit(1)

    artist_day_predict = {}
    artist_day_label = {}
    date_set = set()
    for row in xrange(len(predict)) :
        artist_day = artist[row] + '#' + str(month[row]) + '#' + str(day[row])
        date_set.add(str(int(month[row])) + '#' + str(int(day[row])))
        artist_day_predict.setdefault(artist_day, 0)
        artist_day_label.setdefault(artist_day, 0)

# predict and label -1
        artist_day_predict[artist_day] += predict[row]-1
        artist_day_label[artist_day] += label[row]-1

    artist_all = {}
    artist_error = {}
    
    for key in artist_day_predict.keys() :
        artist = key.split('#')[0]
        error = ((artist_day_predict[key] - artist_day_label[key] + 1) / (artist_day_label[key] + 1)) ** 2
        artist_all.setdefault(artist, 0)
        artist_error.setdefault(artist, 0)

        artist_all[artist] += artist_day_label[key]
        artist_error[artist] += error

    score = 0 
    all = 0
    for artist in artist_all.keys():
        score += (1 - math.sqrt(artist_error[artist] / len(date_set))) * math.sqrt(artist_all[artist])
        all += math.sqrt(artist_all[artist])
    logging.info('the total score is %.10f' % all)
    return score

def output(name, predict, artist, month, day) :
    """
    """
    # no 10.31
    illegal_month=201510
    illegal_day=31

    artist_day_predict = {}
    for row in xrange(len(predict)) :
        artist_day = artist[row] + '#' + str(month[row]) + '#' + str(day[row])
        artist_day_predict.setdefault(artist_day, 0)

        # predict and label -1
        artist_day_predict[artist_day] += predict[row]-1

    with open(name, 'w') as out :
        for key, value in artist_day_predict.items() :
            artist, month, day = key.split('#')
            if (int(month)==illegal_month) and (int(day)==illegal_day):
                continue
            out.write('%s,%d,%s%02d\n' % (artist, value, month, int(day)))

def mergeoutput(filepath) :
    """
    """
    os.system("cat " + ROOT + '/predict_1' + " >> " + filepath + '/mars_tianchi_artist_plays_predict.csv')
    os.system("cat " + ROOT + '/predict_2' + " >> " + filepath + '/mars_tianchi_artist_plays_predict.csv')
    os.system("rm " + ROOT + '/predict_1')
    os.system("rm " + ROOT + '/predict_2')
    
