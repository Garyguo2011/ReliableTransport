#!/bin/bash

#=`ls -1 | sed 's/^/"/g' | sed 's/$/"/g' | tr '\n' ","`
tmp=`ls -1 | sed 's/^/"/g' | sed 's/$/"/g'`
echo $tmp | tr " " "," | sed 's/^/[/' | sed 's/$/]/'
