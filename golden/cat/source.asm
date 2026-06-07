_start:
    ADDI %R1, %R0, 0
    ADDI %R2, %R0, 10
LOOP:
    LD %R3, %R6
    ST %R7, %R3
    BEQ %R3, %R2, END
    JMP LOOP
END:
    HLT
