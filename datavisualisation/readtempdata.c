#define _XOPEN_SOURCE 700  // for strptime()
#include "readtempdata.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define N_TEMPS 6

// typedef struct {
//     time_t    tsec;              // seconds since epoch
//     double    tfraction;         // fractional seconds
//     double    temp[N_TEMPS];     // temperature readings
//     char      timestr[32];       // original timestamp string
// } GHOUSE_STATE;

/**
 * readtemps: read CSV file and return an array of GHOUSE_STATE
 * @filename: path to CSV file (first line is header)
 * @out_count: pointer to size_t to receive number of records read
 * Returns: pointer to malloc'd GHOUSE_STATE[], or NULL on error
 * Caller must free() the returned pointer.
 */
GHOUSE_STATE* readtemps(const char *filename, size_t *out_count) {
    FILE *fp = fopen(filename, "r");
    if (!fp) {
        perror("fopen");
        return NULL;
    }
    char line[256];
    // skip header line
    if (!fgets(line, sizeof(line), fp)) {
        fprintf(stderr, "Empty file: %s\n", filename);
        fclose(fp);
        return NULL;
    }

    size_t cap = 128, n = 0;
    GHOUSE_STATE *states = malloc(cap * sizeof *states);
    if (!states) {
        perror("malloc");
        fclose(fp);
        return NULL;
    }

    while (fgets(line, sizeof(line), fp)) {
        // strip newline
        line[strcspn(line, "\r\n")] = '\0';

        // tokenize timestamp
        char *tok = strtok(line, ",");
        if (!tok) continue;
        // copy raw timestamp
        strncpy(states[n].timestr, tok, sizeof(states[n].timestr)-1);
        states[n].timestr[sizeof(states[n].timestr)-1] = '\0';

        // split off fractional seconds
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

        // parse main timestamp
        struct tm tm0 = {0};
        if (!strptime(buf, "%Y-%m-%d %H:%M:%S", &tm0)) {
            fprintf(stderr, "Bad timestamp: %s\n", buf);
            continue;
        }
        tm0.tm_isdst = -1;  // let mktime determine DST
        states[n].tsec = mktime(&tm0);

        // read N_TEMPS temperature fields
        for (int i = 0; i < N_TEMPS; i++) {
            tok = strtok(NULL, ",");
            states[n].temp[i] = tok ? atof(tok) : 0.0;
        }

        // grow array if needed
        if (++n >= cap) {
            cap *= 2;
            GHOUSE_STATE *tmp = realloc(states, cap * sizeof *states);
            if (!tmp) {
                perror("realloc");
                break;
            }
            states = tmp;
        }
    }

    fclose(fp);
    *out_count = n;
    return states;
}

