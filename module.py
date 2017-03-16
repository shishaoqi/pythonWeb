# -*- coding: utf-8 -*-
# @Author: shishao
# @Date:   2017-03-16 20:18:13
# @Last Modified by:   shishao
# @Last Modified time: 2017-03-16 20:25:27
import sys

def test():
    args = sys.argv
    if len(args)==1:
        print 'Hello, world!'
    elif len(args)==2:
        print 'Hello, %s!' % args[1]
    else:
        print 'Too many arguments!'

if __name__=='__main__':
    test()