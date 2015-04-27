#!/bin/bash

ovs-vsctl add-br br-usr
ovs-vsctl del-port to-br-int
ovs-vsctl \
	-- add-port br-int to-br-usr \
	-- set interface to-br-usr type=patch options:peer=to-br-int \
	-- add-port br-usr to-br-int \
	-- set interface to-br-int type=patch options:peer=to-br-usr 


echo 'The virtual switch for users has been created'
