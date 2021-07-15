
 
            ; Simple example
            ; Writes Hello World to the output
            
            JMP start
            hello: DB "Hello World!" 	; Variable
                   DB 0		; String terminator
            
            start:
                MOV C, hello    	; Point to var 
                MOV D, 0      		; Point to output
                CALL 0x08        ; Call ROM print 
                HLT             	; Stop execution
            
        ;

