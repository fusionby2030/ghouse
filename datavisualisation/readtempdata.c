#define _XOPEN_SOURCE 700
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>

#define MAX_LINE_LEN 256
#define N_TEMPS      6

typedef struct {
    // store the epoch second
    time_t timestamp;
    // if you need sub‐second precision:
    double fractional;
    // raw string for labeling axes, etc.
    char timestr[32];    

    float temperatures[N_TEMPS];
} GHOUSE_STATE;

int main(void) {
    FILE *fp = fopen("/home/akadam/dev/ghouse/datacollection/tempdata.csv", "r"); 
//     FILE *fp = fopen("/home/pi/dev/ghouse/datacollection/tempdata.csv", "r");
    if (!fp) {
        perror("fopen");
        return 1;
    }

    // First line is a header
    char line[MAX_LINE_LEN];
    if (!fgets(line, sizeof(line), fp)) {
        fprintf(stderr, "empty file?\n");
        fclose(fp);
        return 1;
    }

    // allocate an initial batch of states; we'll realloc if needed
    size_t capacity = 128;
    size_t count    = 0;
    GHOUSE_STATE *states = malloc(capacity * sizeof *states);

    while (fgets(line, sizeof(line), fp)) {
        // strip newline
        line[strcspn(line, "\r\n")] = '\0';

        // 1) pull timestamp token
        char *tok = strtok(line, ",");
        if (!tok) continue;

        // copy the raw string for later (e.g. axis labels)
        strncpy(states[count].timestr, tok, sizeof(states[count].timestr)-1);
        states[count].timestr[sizeof(states[count].timestr)-1] = '\0';

        // 2) parse out sub‐seconds if present
        char buf[32];
        double frac = 0.0;
        strncpy(buf, tok, sizeof(buf)-1);
        buf[sizeof(buf)-1] = '\0';
        char *dot = strchr(buf, '.');
        if (dot) {
            // move off the dot, parse microseconds
            frac = atof(dot+1) / 1e6;
            *dot = '\0';  // truncate to just "YYYY‑MM‑DD HH:MM:SS"
        }
        states[count].fractional = frac;

        // 3) parse the main timestamp
        struct tm tm0 = {0};
        if (!strptime(buf, "%Y-%m-%d %H:%M:%S", &tm0)) {
            fprintf(stderr, "bad timestamp: %s\n", buf);
            continue;
        }
        tm0.tm_isdst = -1;   // let mktime figure out DST
        states[count].timestamp = mktime(&tm0);

        // 4) grab each of the N_TEMPS float fields
        for (int i = 0; i < N_TEMPS; i++) {
            tok = strtok(NULL, ",");
            if (!tok) {
                fprintf(stderr, "missing field %d on line %zu\n", i+1, count+2);
                states[count].temperatures[i] = 0;
            } else {
                states[count].temperatures[i] = atof(tok);
            }
        }

        count++;
        if (count >= capacity) {
            capacity *= 2;
            states = realloc(states, capacity * sizeof *states);
            if (!states) {
                perror("realloc");
                break;
            }
        }
    }

    fclose(fp);

    printf("Read %zu records.\n", count);
    // Example: print first few:
    for (size_t i = 0; i < count && i < 5; i++) {
        struct tm *lt = localtime(&states[i].timestamp);
        char timestr[64];
        strftime(timestr, sizeof(timestr), "%Y-%m-%d %H:%M:%S", lt);
        printf("%s.%06.0f →", timestr, states[i].fractional * 1e6);
        for (int j = 0; j < N_TEMPS; j++)
            printf(" %5.2f", states[i].temperatures[j]);
        putchar('\n');
    }

    // …now hand `states` & `count` off to your plotting/GUI routine…

    free(states);
    return 0;
}

