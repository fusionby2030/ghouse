gcc -std=gnu11 \ 
  -I/home/akadam/builds/build_plplot/include -I/home/akadam/builds/plplot-5.15.0/include \
  readtempdata.c plottemp.c -o plottemperatures \
  -L/home/akadam/builds/build_plplot/src \
  -lplplot -lm


./plottemperatures /home/akadam/dev/ghouse/datacollection/tempdata.csv

depends on PLplot for now..
