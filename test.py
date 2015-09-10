#!/usr/bin/env python
# coding: utf-8
# vim: set et sw=4 ts=4 sts=4 fenc=utf-8
# Author: qfscu-bitsoal
# Created: 2015-09-10 10:39 CST

def test(c, x, y):
    a = 2
    print "c=%d, x=%d, y=%d" % (c, x,y)
    while True:
        if a<100:
            a = pow(a,a)
        else:
            return a
class C(object):

    def met1(self):
        print "I am met1"

    def met2(self):
        print "I am met2"

def test1(a):
    try:
        if a >1e10:
            print a
        else:
            return test1(a+1)
    except:
        print a


if __name__ == "__main__":
    c = C()
    mets = [c.met1, c.met2]
    print type(mets[0])
    mets[0]()
    mets[1]()
    print test(0, *[1,2])
    test1(1)

