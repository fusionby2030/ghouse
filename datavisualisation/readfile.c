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
  if (fp)
  {
    while(fgets(line, sizeof(line), fp))
    {
      if (readlines > 0) {
        printf ( "%d/%d %s", readlines, numlines, line);
        // first character is like this: 2025-04-19 12:51:14.641604
        // then comma separated values, between each comma is 6 characters 
      }
      //printf("%s", line);
      readlines ++;

      if (readlines > 5) {
        break; 
      }
      //break;        
    }

    fclose(fp);
  }
  return 0;
}
