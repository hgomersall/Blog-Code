
#ifndef _HELLO_STRING_H
#define _HELLO_STRING_H

#ifdef _WIN32

  #ifdef HELLO_EXPORTS
    #define HELLOAPI __declspec(dllexport)
  #else
    #define HELLOAPI __declspec(dllimport)
  #endif

  #define HELLOCALL __cdecl
#else
  #define HELLOAPI
  #define HELLOCALL
#endif

/* Declare our Add function using the above definitions. */
HELLOAPI char* HELLOCALL hello_string(void);

#endif
