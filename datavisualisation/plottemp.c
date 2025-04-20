#include <stdio.h>
#include <stdlib.h>
#include <plplot.h>
#include "readtempdata.h"

// bring in the reader
// #include "readtempdata.c"

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s data.csv\n", argv[0]);
        return 1;
    }

    // read CSV into array
    size_t count;
    GHOUSE_STATE *data = readtemps(argv[1], &count);
    if (!data) {
        return 1;
    }

    // allocate plot arrays
    double *x = malloc(count * sizeof *x);
    double (*y)[count] = malloc(N_TEMPS * sizeof *y);
    if (!x || !y) {
        perror("malloc");
        free(data);
        return 1;
    }

    // populate x (time) and y (temps)
    for (size_t i = 0; i < count; i++) {
        x[i] = data[i].tsec + data[i].tfraction;
        for (int j = 0; j < N_TEMPS; j++) {
            y[j][i] = data[i].temp[j];
        }
    }
    double t0 = x[0];
    for (size_t i=0; i< count; i++) {
        x[i] = (x[i] - t0) / 3600; 
    }
    
    // find Y range
    double ymin = y[0][0], ymax = y[0][0];
    for (int j = 0; j < N_TEMPS; j++) {
        for (size_t i = 0; i < count; i++) {
            if (y[j][i] < ymin) ymin = y[j][i];
            if (y[j][i] > ymax) ymax = y[j][i];
        }
    }

    // initialize PLplot
    plinit();
    pltimefmt("%H:%M:%S");
    plenv(x[0], x[count-1], ymin, ymax, 0, 0);
    plbox("bcd", 0.0, 0, "bcd", 0.0, 0);
    pllab("Time", "Temperature (°C)", "All Available Data");

    // plot each series in a different color
    for (int j = 0; j < N_TEMPS; j++) {
        plcol0(j + 1);
        plline(count, x, y[j]);
    }

    plend();

    free(x);
    free(y);
    free(data);
    return 0;
}

