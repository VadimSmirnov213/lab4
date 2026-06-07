.org 0
irq_handler:
    LD %R1, %R6
    ST %R7, %R1
    IRET

.org 20
_start:
    ADDI %R1, %R0, 72
    ST %R7, %R1
    ADDI %R1, %R0, 105
    ST %R7, %R1
    ADDI %R1, %R0, 44
    ST %R7, %R1
    ADDI %R1, %R0, 32
    ST %R7, %R1

    ADDI %R5, %R0, 5
LOOP:
    BEQ %R4, %R5, DONE
    ADDI %R4, %R4, 1
    JMP LOOP

DONE:
    ADDI %R1, %R0, 33
    ST %R7, %R1
    HLT
