# -*- coding: utf-8 -*-
# @Author: shishao
# @Date:   2017-03-22 00:57:29
# @Last Modified by:   shishao
# @Last Modified time: 2017-03-22 00:57:41
class MyTest:

    myname = 'peter'

    # add a instance attribute
    def __init__(self, name):
        self.name = name

    # class access class attribute
    def sayhello(self):
        print "say hello to %s" % MyTest.myname

    # instance can access class attribute
    def sayhello_1(self):
        print "say hello to %s" % self.myname

    # It's a snap! instance can access instance attribute
    def sayhello_2(self):
        print "say hello to %s" % self.name

    # class can not access instance attribute!!!
    def sayhello_3(self):
        #print "say hello to %s" % MyTest.name
        pass

if __name__ == '__main__':
    test = MyTest("abc")
    test.sayhello()
    test.sayhello_1()
    test.sayhello_2()
    test.sayhello_3()