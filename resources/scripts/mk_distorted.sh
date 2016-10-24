#!/bin/bash

TFORM='0,-0.05,0.1,0.9,300,300'

for idx in 00 01
do
	python ../../mk_transform.py lines-${idx#0}.png $TFORM distorted-$idx.png
done
