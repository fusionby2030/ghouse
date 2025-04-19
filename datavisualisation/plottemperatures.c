// plottemperatures.c
#define _XOPEN_SOURCE 700     // for strptime()
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <plplot.h>

#define N_TEMPS 6

typedef struct {
    time_t    tsec;              // seconds since epoch
    double    tfraction;         // fractional seconds
    float     temp[N_TEMPS];
    char      timestr[32];       // original timestamp
} GHOUSE_STATE;

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s data.csv\n", argv[0]);
        return 1;
    }

    // --- 1) Read & parse CSV into states[] ---
    FILE *fp = fopen(argv[1], "r");
    if (!fp) { perror("fopen"); return 1; }
    char line[256];
    // skip header
    fgets(line, sizeof(line), fp);

    size_t cap = 128, n = 0;
    GHOUSE_STATE *states = malloc(cap * sizeof *states);

    while (fgets(line, sizeof(line), fp)) {
        // remove newline
        line[strcspn(line, "\r\n")] = '\0';

        // timestamp token
        char *tok = strtok(line, ",");
        if (!tok) continue;

        // store original text
        strncpy(states[n].timestr, tok, sizeof(states[n].timestr)-1);
        states[n].timestr[sizeof(states[n].timestr)-1] = '\0';

        // split off fractional
        char buf[32];
        double frac = 0.0;
        strncpy(buf, tok, sizeof(buf)-1);
        buf[sizeof(buf)-1] = '\0';
        char *dot = strchr(buf, '.');
        if (dot) {
            frac = atof(dot+1) / 1e6;
            *dot = '\0';
        }
        states[n].tfraction = frac;

        // parse to struct tm
        struct tm tm0 = {0};
        if (!strptime(buf, "%Y-%m-%d %H:%M:%S", &tm0)) {
            fprintf(stderr, "Bad timestamp: %s\n", buf);
            continue;
        }
        tm0.tm_isdst = -1;
        states[n].tsec = mktime(&tm0);

        // read temperatures
        for (int i = 0; i < N_TEMPS; i++) {
            tok = strtok(NULL, ",");
            states[n].temp[i] = tok ? atof(tok) : 0.0f;
        }

        if (++n >= cap) {
            cap *= 2;
            states = realloc(states, cap * sizeof *states);
            if (!states) { perror("realloc"); break; }
        }
    }
    fclose(fp);

    if (n == 0) {
        fprintf(stderr, "No data read.\n");
        free(states);
        return 1;
    }

    // --- 2) Filter to last hour ---
    time_t now    = time(NULL) - 3600;
    time_t cutoff = 0;
    double *x = malloc(n * sizeof *x);
    double  (*y)[n] = malloc(N_TEMPS * sizeof *y);

    size_t m = 0;
    for (size_t i = 0; i < n; i++) {
        double tt = states[i].tsec + states[i].tfraction;
        if (states[i].tsec >= cutoff) {
            x[m] = tt / 60.0 / 60.0;
            for (int j = 0; j < N_TEMPS; j++)
                y[j][m] = states[i].temp[j];
            m++;
        }
    }
    if (m == 0) {
        fprintf(stderr, "No data in the last hour.\n");
        free(states); free(x); free(y);
        return 1;
    }

    // find Y range
    float ymin = y[0][0], ymax = y[0][0];
    for (int j = 0; j < N_TEMPS; j++)
        for (size_t i = 0; i < m; i++) {
            if (y[j][i] < ymin) ymin = y[j][i];
            if (y[j][i] > ymax) ymax = y[j][i];
        }

    // --- 3) Plot with PLplot ---
    plinit();
    // set date/time label format
    pltimefmt("%H:%M:%S");     // use H:M:S on ticks :contentReference[oaicite:1]{index=1}

    // world coordinates: x from first to last, y from ymin..ymax
    plenv(x[0], x[m-1], ymin, ymax, 0, 0);

    // draw axes; 'd' on X‑axis turns on date/time ticks per pltimefmt() :contentReference[oaicite:2]{index=2}
    plbox("bcd", 0.0, 0,   "lbc", 0.0, 0);

    pllab("Time", "Temperature (°C)", "Temperatures: 19.04");

    // plot each series in a different color (1..6)
    for (int j = 0; j < N_TEMPS; j++) {
        plcol0(j+1);
        plline(m, x, y[j]);
        printf ("x=%f, y=%f\n", *x, *y[j]);
    }

    plend();

    free(states);
    free(x);
    free(y);
    return 0;
}

