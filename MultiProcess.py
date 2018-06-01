# -*- coding: UTF-8 -*- 
# Authorized by Vlon Jang
# Created on 2017-06-13
# Blog: www.wangqingbaidu.cn
# Email: wangqingbaidu@gmail.com
# From kwai, www.kuaishou.com
# ©2015-2017 All Rights Reserved.
#

"""
2017-06-13    First start.
2017-08-26    Add parameters and feed_backs. 
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import multiprocessing
import math, time

def _get_value(v, t):
    if t == 'i' or t == 'integer':
        return int(v.value)
    else:
        return float(v.value)

class MultiProcess():
    """MultiProcess, Give total samples to deal with, a function and kwargs and split parts.
    
    Parameters
    ---------------
    @samples: Total samples to process, in list or tuple type.
    @function: A single thread function to process samples.
    @num_process: Number of process to run.
    @feed_back: `func` return values. It can be list or tuple. Only integer and double supported.
        eg. [`i`,'d'] which mean an integer and a double while be returned from `function`.
    @kwargs: Other parameters passing to the `function`.
    
    Methods:
    ---------------
    @start: Star processing.
    @wait: wait for all the process to exit.
    @run: Useful, combine `start` and `wait`.
    
    Properties:
    ---------------
    @feed_back: `function` feed backs, in original order.
        shape: [num_process, len(`feed_back`)]
    
    How2use:
    ---------------
    samples = balabala
    function = bala
    # If `function` doesn't return values.
    MultiProcess(samples, function, numprocess=8).run()
    # Else
    mp = MultiProcess(samples, function, feed_back=['i', 'd'], num_process=8)
    mp.run()
    feed_back = mp.feed_back()
    """
    def __init__(self, samples, funcition, num_process=1, feed_back=[], **kwargs):
        self.samples = samples
        self.func = funcition
        self.kwargs = kwargs
        self.num_process = num_process
        self.thread_list = []
    
        self.share_mem = []
        for t in feed_back:
            if not (t == 'i' or t == 'd' or t == 'integer' or t == 'double'):
                raise ValueError('Type of feed backs must be i(integer) or d(double).')
        for _ in range(num_process):
            fbv = []
            for _ in range(len(feed_back)):
                fbv.append(multiprocessing.Value('d', 0))
            self.share_mem.append(fbv)
        self.feed_back_type = feed_back
        
    def start(self, sleep_time=0):
        """
        Exception
        ---------------
        VauleError: `samples`, `func`, `num_process` parameters setttings.
        """
        if self.samples and self.func and self.num_process:
            samples_per_thread = int(math.ceil(len(self.samples) / self.num_process))
            
            for i in range(self.num_process):
                kwargs = {'thread_id':i, 
                          'samples':self.samples[samples_per_thread * i: samples_per_thread * (i + 1)]}
                if self.feed_back_type:
                    kwargs.update({'feed_back':self.share_mem[i]})
                kwargs.update(self.kwargs)
                sthread = multiprocessing.Process(target=self.func, kwargs=kwargs)
                print ('Starting process %d from %d to %d ...' %(i, 
                                                                samples_per_thread * i, 
                                                                min(len(self.samples), 
                                                                    samples_per_thread * (i + 1))))
                sthread.start()
                self.thread_list.append(sthread)
                if sleep_time and sleep_time > 0:
                    time.sleep(sleep_time)
        else:
            raise ValueError ('Error while starting multi process',
                   'Please check `samples`, `func`, `num_process` parameters')
            
    def wait(self):     
        for t in self.thread_list:
            t.join()
            
    def run(self, sleep_time=0):
        self.start(sleep_time)
        self.wait()
        return self
        
    @property
    def feed_back(self):
        fb_list = []
        for fb in self.share_mem:
            fb_list += [_get_value(v, t) for v, t in zip(fb, self.feed_back_type)]
        return fb_list