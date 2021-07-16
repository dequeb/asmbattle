	; fibonacci 0,1,1,2,3,5,8...
	; A last value
	; B current value
		JMP BEGIN
	SEP:	DB ", "
	   	DB 00
	BEGIN:	MOV A, 1		; next value
		MOV B, 0		; current value
		MOV D, 0		; print pointer
		MOV C, SEP		; separator string

		PUSH A		; save registers
		PUSH B
		PUSH C
		CALL 0x000A		; print B
		POP C
		POP B		; restore registers
		POP A
		JMP SWAP		; to ensure the sequence begins by 0, 1, 1, ...

	loop:	PUSH A		; save registers
		PUSH B
		PUSH C	
		CALL 0x0008		; print ", "
		POP C
		POP B		; restore registers
		POP A

		ADD B, A		; B + A -> B
		JC END		; stop on buffer overflow
		PUSH A		; save registers
		PUSH B
		PUSH C
		CALL 0x000A		; print B
		POP C
		POP B		; restore registers
		POP A

	SWAP:	PUSH A		; swap A, B
		PUSH B
		POP A
		POP B
		JMP loop
	END:	HLT

