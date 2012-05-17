#include <stdlib.h>
#include <string.h>
#include "hello_string.h"

char* HELLOCALL hello_string()
{
    static char* return_string;

    return_string = (char *)malloc(sizeof(char) * 30);

    strcpy(return_string, "A string in malloced memory");

    return return_string;
}
