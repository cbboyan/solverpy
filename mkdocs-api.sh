#!/bin/bash

for i in `find src -name "*.py" | grep -v __init__ | cut -d/ -f2-`; do 
   j="${i:0:-3}"; 
   k=`echo $j | tr "/" "."`; 
   mkdir -p `dirname docs/api/$j`; 
   echo "::: $k" > docs/api/$j.md; 
   echo "done: $k"
done 
