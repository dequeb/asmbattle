START:	MOV A, SP		; current position
	MOV B, END		; program area
	MOV C, 0x25  	   ; marker value (%)
LOOP:	CMP A, B		; while A != B
	JE  NEXT
	MOV [A], C
	DEC A
	JMP LOOP		
BEFORE:	MOV C, END   		; Point to var 
	MOV D, 0    		; Point to output
	CALL 0x09        ; Call ROM print CALL 0x09           ; Call ROM print 
NEXT:	MOV A, START    	; begin of program
	MOV B, 0x0040		; ROM
LOOP2:	CMP A, B		; while A != B
	JE  SCREEN
	MOV [A], C
	DEC A
	JMP LOOP2

START2:	MOV A, SP		; current position
	MOV B, END		; program area
	MOV C, 0x25  	   ; marker value
LOOP3:	CMP A, B		; while A != B
	JE  NEXT2
	MOV [A], C
	DEC A
	JMP LOOP3	
SCREEN:	
	MOV C, END     		; Point to var 
	MOV D, 0    		; Point to output
	CALL 0x09           ; Call ROM print CALL 0x09           ; Call ROM print 
NEXT2:	MOV A, START    	; begin of program
	MOV B, 0x0039		; ROM
LOOP4:	CMP A, B		; while A != B
	JE  SCREEN
	MOV [A], C
	DEC A
END:	JMP LOOP4

