# /usr/bin/python3
# -*- coding: UTF-8 -*-
"""assembler test suite"""
import logging
import asmbattle

class Test:
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        self.memory = asmbattle.Memory()
        self.screen = asmbattle.Screen(32, 8)
        self.cpu = asmbattle.Cpu(self.memory,  self.screen, 0)

    def main(self):
        print(self.memory)
        print(self.screen)
        asm = asmbattle.Assembler()
        try:
            print(asm.assemble(""" XXX """))
        except ValueError:
            pass
        else:
            raise AssertionError("exception not raised for XXX")

        print(asm.assemble("""
                         jmp start
             ;
             variable:   db	09
             ;
             start:      add	A, 2
                         add	b, a
                         add c, [a]
                         add d, [a+3]
                         ;add a, [sp]
                         ;add a, [variable]
                         ;add a, [variable+3]
                         """
                           ))

        print(asm.assemble("""
                         jmp start
             ;
             variable:   db	254
             ;
             start:      sub	A, 2
                         sub	b, a
                         sub c, [a]
                         sub d, [a +3]
                         sub a, [sp]
                         sub a, [variable]
                         ;sub a, [variable+3]
                         """
                           ))

        print(asm.assemble("""
                         ; inc-dec test
             start:      mov a, 0        ; first compare
                         mov b, 2        ; second compare
                         mov c, cursor   ; screen cursor
                         inc a
                         dec b
                         cmp a, b
                         je  say_ok
             say_not_ok: mov d, [NOT_OK] ; d = messsage
                         jmp display
             say_ok:     mov d, [OK]
             display:    out [c], d
                         inc c
                         hlt

             OK:         db	'O'
             NOT_OK:     db  'E'
             cursor:     db  0
                         """
                           ))

        print(asm.assemble("""
            ;
            ;
            start:      dec a
                        dec b
                        dec c
                        dec d 
                        dec sp
                        ; dec f
            variable:   db	0xFF
                        """))

        print(asm.assemble("""
            ;
            variable:   db  0xFF
            start:      cmp	A, c
                        cmp	a, sp
                        cmp sp, b
                        cmp a, [sp]
                        cmp a, [variable]
                        cmp a, [2]
                        cmp a, 2
                        """))

        print(asm.assemble("""
             variable:   db 0xFF
                         jmp	a
            ;            jmp [sp]
            ;            jmp [variable]
            ;            jmp [a]
		         jmp variable
                        """))
        print(asm.assemble("""
        start:
                         jc	a
                         jc	b
                         jc	c
                         jc	d
                         jc	sp
                         jc 253
                         jc start            

                         jb	a
                         ;jb	b
                         ;jb	c
                         ;jb	d
                         ;jb	sp
                         ;jb 253
                         ;jb start            

                         jnae	a
                         ;jnae	b
                         ;jnae	c
                         ;jnae	d
                         ;jnae	sp
                         ;jnae 253
                         ;jnae start            

                         jnc	a
                         jnc	b
                         jnc	c
                         jnc	d
                         jnc	sp
                         jnc 253
                         jnc start            

                         jnb	a
                         ;jnb	b
                         ;jnb	c
                         ;jnb	d
                         ;jnb	sp
                         ;jnb 253
                         ;jnb start            

                         jae	a
                         ;jae	b
                         ;jae	c
                         ;jae	d
                         ;jae	sp
                         ;jae 253
                         ;jae start            

                         jz	a
                         jz	b
                         jz	c
                         jz	d
                         jz	sp
                         jz 253
                         jz start            

                         je	a
                         ;je	b
                         ;je	c
                         ;je	d
                         ;je	sp
                         ;je 253
                         ;je start            
                        """))

        print(asm.assemble("""
        start:
                         jnz	a
                         jnz	b
                         jnz	c
                         jnz	d
                         jnz	sp
                         jnz 253
                         jnz start            

                          jne	a
                         ;jne	b
                         ;jne	c
                         ;jne	d
                         ;jne	sp
                         ;jne 253
                         ;jne start            

                          ja	a
                         ;ja	b
                         ;ja	c
                         ;ja	d
                         ;ja	sp
                         ;ja 253
                         ;ja start            

                         jnbe	a
                         jnbe	b
                         jnbe	c
                         jnbe	d
                         jnbe	sp
                         jnbe 253
                         jnbe start            

                          jna	a
                         ;jna	b
                         ;jna	c
                         ;jna	d
                         ;jna	sp
                         ;jna 253
                         ;jna start            

                          jnbe	a
                         ;jnbe	b
                         ;jnbe	c
                         ;jnbe	d
                         ;jnbe	sp
                         ;jnbe 253
                         ;jnbe start            

                         jna	a
                         jna	b
                         jna	c
                         jna	d
                         jna	sp
                         jna 253
                         jna start            

                          jbe	a
                         ;jbe	b
                         ;jbe	c
                         ;jbe	d
                         ;jbe	sp
                         ;jbe 253
                         ;jbe start            
                        """))

        print(asm.assemble("""
            start:
                 push	a
                 push	b
                 push	c
                 push	d
                 push	sp
                 push	[a]
                 push	[b]
                 push	[c]
                 push	[d]
                 push	[sp]
                 push   [255]
                 push   254

                 pop	a
                 pop	b
                 pop	c
                 pop	d
                 pop	sp

                 call	a
                 call	b
                 call	c
                 call	d
                 call	sp
                 ;call   [255]
                 call   254
                 
                 ret
                """))

        print(asm.assemble("""
            variable: db "ALLO"
            start:
                 mul	a
                 mul	b
                 mul	c
                 mul	d
                 mul	sp
                 mul	[a]
                 mul	[b]
                 mul	[c]
                 mul	[d]
                 mul	[sp]
                 mul   [255]
                 mul   254

                 div	a
                 div	b
                 div	c
                 div	d
                 div	sp
                 div	[a]
                 div	[b]
                 div	[c]
                 div	[d]
                 div	[sp]
                 div   [255]
                 div   254

            reStart:and	A, b
                    and	a, sp
                    and sp, b
                    and a, [sp]
                    and a, [variable]
                    and a, [2]
                    and a, 2
                    
                    or 	A, b
                    or 	a, sp
                    or  sp, b
                    or  a, [sp]
                    or  a, [variable]
                    or  a, [2]
                    or  a, 2
                """))

        print(asm.assemble("""
        start:      xor 	A, b
                    xor 	a, sp
                    xor  sp, b
                    xor  a, [sp]
                    xor  a, [start]
                    xor  a, [2]
                    xor  a, 2

             not    a
             not	b
             not	c
             not	d
             not	sp
            """))

        print(asm.assemble("""
              start:shl 	A, b
                    shl 	a, [sp]
                    shl  a, [start]
                    shl  a, 2

                    sal 	A, b
                    sal 	a, [sp]
                    sal  a, [start]
                    sal  a, 2

                    shr 	A, b
                    shr 	a, [sp]
                    shr  a, [start]
                    shr  a, 2

                    sar 	A, b
                    sar 	a, [sp]
                    sar  a, [start]
                    sar  a, 2
            """))

        self.execute("""
            hlt
            """)

        self.execute("""
            mov D, [B+2]    ; indirect to reg
            mov A, D        ; reg to reg
            mov B, [3]      ; address to reg
            mov sp, 231     ; to reflect result of: https://schweigi.github.io/assembler-simulator/
            
            hlt
            """)

        self.execute("""
            start:      mov sp, 231
                        MOV	A, 2
                        mov	a, sp
                        mov	a, [sp]
                        mov	a, [sp+5]
                        mov	a, [sp-16]
                        mov 	[a], sp
                        mov 	a, [variable]
            ;           mov	[a], [variable]
                        mov	[variable], b
                        mov	[variable], 3
                        mov	[a], 4
                        mov	[a+11], 4
                        mov 	a, [33]
            ;           mov	[a], [33]
                        mov	[34], b
                        mov	[34], 3
                        mov	[a], 4
                        hlt
            ;
            variable:   db	99 
            variable_s: db	"Attention"
            variable_c: db  'c'
            """)

        self.execute("""
                        jmp start
            ;
            variable:   db	09
            ;
            start:      add	A, 2
                        add	b, a
                        add c, [a]
                        add d, [a +3]
                        add a, [sp]
                        add a, [variable]
                        """)

        self.execute("""
                        jmp start
            ;
            variable:   db	254
            ;
            start:      sub	A, 2
                        sub	b, a
                        sub c, [a]
                        sub d, [a +3]
                        sub a, [variable]
                        """)

        self.execute("""
                         ; inc-dec test
             start:      mov a, 0        ; first compare
                         mov b, 2        ; second compare
                         mov c, cursor   ; screen cursor
                         inc a
                         dec b
                         cmp a, b
                         je  say_ok
             say_not_ok: mov d, [NOT_OK] ; d = messsage
                         jmp display
             say_ok:     mov d, [OK]
             display:    out [c], d
                         inc c
                         hlt

             OK:         db	'O'
             NOT_OK:     db  'E'
             cursor:     db  0
                        """)

        self.execute("""
                        """)

        self.execute("""
                        """)

        self.execute("""
                        """)

        self.execute("""
                        """)

    def execute (self, code: str):
        self.cpu.reset()
        self.memory.reset()
        self.screen.reset()
        asm = asmbattle.Assembler()
        program = asm.assemble(code)
        print(program)
        self.memory.mass_store(0, program["code"])
        while self.cpu.step():
            print("CPU:\n"+ str(self.cpu))
            print("Memory:\n"+str(self.memory))
            print("Screen:\n"+str(self.screen))


if __name__ == '__main__':
    Test().main()

