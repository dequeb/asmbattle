START:	MOV A, SP		; current position
	MOV B, END		; program area
	MOV C, 0x25  	   ; marker value
LOOP:	CMP A, B		; while A != B
	JE  END
	MOV [A], C
	DEC A
	JMP LOOP		
END:	HLT

