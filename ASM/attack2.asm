START: MOV A, SP ; current position
MOV B, END ; program area
INC B
MOV C, 0x9999 ; marker value
LOOP: CMP A, B ; while A != B
JE END
MOV [B], C
INC B
JMP LOOP 
END: HLT

