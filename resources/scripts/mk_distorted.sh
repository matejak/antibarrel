#!/bin/bash

TFORM='0,-0.002,-0.01,1.05,300,300'

for idx in 00 01
do
	python ../../mk_transform.py ../patterns/lines-${idx#0}.png $TFORM ../../distorted-$idx.png
done
