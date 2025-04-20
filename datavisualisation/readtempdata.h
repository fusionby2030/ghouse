// readtempdata.h
#ifndef READTEMPDATA_H
#define READTEMPDATA_H

#include <time.h>
#include <stddef.h>

#define N_TEMPS 6

typedef struct {
    time_t    tsec;              /* seconds since epoch */
    double    tfraction;         /* fractional seconds */
    double    temp[N_TEMPS];     /* temperature readings */
    char      timestr[32];       /* original timestamp */
} GHOUSE_STATE;

/**
 * Read a CSV file of timestamps + N_TEMPS columns.
 * @filename: path to CSV (header on first line)
 * @out_count: receives number of records read
 * @return: malloc’d array of GHOUSE_STATE, or NULL on error.
 * Caller must free() the result.
 */
GHOUSE_STATE *readtemps(const char *filename, size_t *out_count);

#endif /* READTEMPDATA_H */

