# ASM battle

This program is for me the old dream of creating a playing field to experiment the (legal) meeting of pseudo pirates. 

## The game
Each player submits a program in the simplified assembler supported by the program. Each program is assembled, loaded in its own memory location and is assigned a virtual processor. Each memory location and each character written to screen at the end of the game counts for one point.

A tiny BIOS provide a branch table for CPU startup and a print function (null terminated string). It's up to you to find where it is. (clue there is a "Hello World" program that uses it...)

This is an early version. Enhancements will come based on user feedback.

## Acknowledgement
This project is based on "Simple 8-bit Assembler Simulator" by Marco Schweighauser (2015). https://schweigi.github.io/assembler-simulator/ 


_Michel_, July 5th, 2021

https://www.michelrondeau.com
