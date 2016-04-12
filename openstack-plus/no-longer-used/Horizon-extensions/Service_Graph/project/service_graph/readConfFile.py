#!/usr/bin/env python

import ConfigParser

def readConfFile(filename):
	with open(filename) as f:
		prop = dict([line.strip().split('=', 1)for line in f])
	return prop
