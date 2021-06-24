 /*
  * wrapio - Redirect stdio to Python-level operations
  * Copyright (C) 2021  Patmanidis Stefanos
  *
  * This program is free software: you can redistribute it and/or modify
  * it under the terms of the GNU General Public License as published by
  * the Free Software Foundation, either version 3 of the License, or
  * (at your option) any later version.
  *
  * This program is distributed in the hope that it will be useful,
  * but WITHOUT ANY WARRANTY; without even the implied warranty of
  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  * GNU General Public License for more details.
  *
  * You should have received a copy of the GNU General Public License
  * along with this program.  If not, see <https://www.gnu.org/licenses/>.
  */

 /*
  * wrapio.h:
  * Include this after stdio.h. Defines macros for common ops.
  */

int wrapio_init ( PyObject *m );

int _vfprintf ( FILE *stream, const char *format, va_list args );
int _fprintf ( FILE *stream, const char *format, ... );
int _printf ( const char *format, ... );

int _fputc ( int character, FILE * stream );
int _putc ( int character, FILE * stream );
int _putchar ( int character );
int _fputs ( const char * str, FILE * stream );
int _puts ( const char * str );

int _fflush ( FILE * stream );

// size_t fwrite ( const void * ptr, size_t size, size_t count, FILE * stream );
// int feof ( FILE * stream );

#define vfprintf _vfprintf
#define fprintf _fprintf
#define printf _printf

#define fputc _fputc
#define putc _putc
#define putchat _putchar
#define fputs _fputs
#define puts _puts

#define fflush _fflush

// FOR READ ONLY
// void rewind ( FILE * stream );

// NOT USED

// long int ftell ( FILE * stream );
// int fsetpos ( FILE * stream, const fpos_t * pos );
// int fseek ( FILE * stream, long int offset, int origin );
// int fgetpos ( FILE * stream, fpos_t * pos );

// void perror ( const char * str ); (( SEE STRING.H/STRERR ))
// void clearerr ( FILE * stream );
// int ferror ( FILE * stream );

// FILE * freopen ( const char * filename, const char * mode, FILE * stream );
