#include <stdlib.h>
#include <stdio.h>
#include "hello_string.h"

int main(int argc, char** argv)
{
    char* string = hello_string();

    printf("return: %s\n", string);
    free(string);

    return EXIT_SUCCESS;
}

