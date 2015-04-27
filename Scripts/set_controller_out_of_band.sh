#!/bin/bash
ovs-vsctl set controller br-int connection-mode=out-of-band
ovs-vsctl set bridge br-int other-config:disable-in-band=true
