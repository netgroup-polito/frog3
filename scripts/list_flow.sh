#!/bin/bash

ovs-ofctl --protocol=OpenFlow13 dump-flows $1
