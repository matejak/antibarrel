#!/bin/bash

TFORM='0,0.000,-0.10,1.10,300,300'

for idx in 00 01
do
	python ../../mk_transform.py ../patterns/lines-${idx#0}.png $TFORM ../../distorted-$idx.png
done
