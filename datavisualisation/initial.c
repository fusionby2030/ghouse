#include <stdio.h>

int main (int argc, char *argv[])
{
  int param = 0;
  while (param < argc)
    {
      printf ("Parameter %d is %s\n", param, argv[param]);
      param++;
    }
  return 0;
}
