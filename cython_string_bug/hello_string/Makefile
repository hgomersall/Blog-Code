
all: hello_string

hello_string: hello_string.dll
	gcc -o string_test.exe string_test.c -L. -lhello_string

hello_string.dll: hello_string.o
	gcc -o hello_string.dll hello_string.o -s -shared -Wl,--subsystem,windows
	cp hello_string.dll ../

hello_string.o:
	gcc -c -o hello_string.o hello_string.c -D HELLO_EXPORTS

clean:
	rm -rf hello_string.o libhello_string.so hello_string.dll string_test string_test.exe
