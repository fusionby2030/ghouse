#include <stdio.h>
// gcc readfile.c && ./a.out $(wc -l <  /home/pi/dev/ghouse/datacollection/tempdata.csv)

typedef struct {
  char datetime[30];
  float temperatures[6]; 
} GHOUSE_STATE; 

//wc -l <  /home/pi/dev/ghouse/datacollection/tempdata.csv
// ./a.out $(wc -l <  /home/pi/dev/ghouse/datacollection/tempdata.csv)
int main (int argc, char *argv[])
{
 
  int param = 0;
  int numlines; 
  while (param < argc)
    {
      printf ("Parameter %d is %s\n", param, argv[param]);
      param++;
    }
  sscanf(argv[1], "%d", &numlines);
  numlines = numlines - 1;
  printf ("Number of lines is %d\n", numlines);
  GHOUSE_STATE states[numlines]; 
   
  FILE *fp;
  int value;
  fp = fopen("/home/pi/dev/ghouse/datacollection/tempdata.csv", "r");
  char line[256];
  int readlines=0;
  char *lineptr;
  char *tmppointr; 
  float linetemps[6];
  char temps[6];
  char meastime[27] = "TO BE FILLED";  
  int tempsread=0;
  int i;
  
  if (fp)
  {
    while(fgets(line, sizeof(line), fp))
    {
      if (readlines > 0) {
        printf ( "%d/%d %s", readlines, numlines, line);
        // first character is like this: 2025-04-19 12:51:14.641604
        // then comma separated values, between each comma is 6 characters
        lineptr = line;
        // TODO: Date time parsing 
        lineptr = lineptr + 27;
        tempsread = 0; 
        while (tempsread < 6)
        {
           tmppointr = temps;
           for (i = 0; i < 6; i++) {
             *tmppointr = *lineptr; 
             lineptr ++ ;
             tmppointr ++; 
           }
           lineptr ++; 
           printf ( "%s\n", temps);
           sscanf (temps, "%f", linetemps[tempsread]); 
          tempsread ++;
          // TODO: check for the NONE value          
        }
      }
      for (i=0; i < 6; i++) {        
        states[readlines].temperatures[i] = linetemps[i];
      }
      tmppointr = meastime;
      lineptr   = states[readlines].datetime;
      while (*tmppointr != 0 && lineptr != 0) {
        lineptr = tmppointr;
        lineptr ++;
        tmppointr ++;
        
      }      
        // states[readlines].datetime[i]     = meastime[i];
      readlines ++;
      
      if (readlines > 5) {
        break; 
      }
    }

    fclose(fp);
  }
  return 0;
}
