            ; Writes "Lorem ipsum" for ever to the output
            
            JMP start
            hello: DB "Lorem ipsum dolor sit amet, consectetur."
                   DB 0		; String terminator
            
            start:
                MOV D, 0    		; Point to output
	   loop: 
                MOV C, hello    	; Point to var
                CALL 0x08           ; Call ROM print 
	       JMP loop

