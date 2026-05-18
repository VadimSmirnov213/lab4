# lab4

## Описание синтаксиса

Ниже приведена формальная грамматика языка в нотации Бэкуса-Наура (BNF) для ассемблероподобного синтаксиса (`asm`).

```bnf
<program> ::= <line> | <line> <program>

<line> ::= <empty-line>
         | <comment-line>
         | <label-line>
         | <instruction-line>
         | <data-line>

<empty-line> ::= <EOL>
<comment-line> ::= <ws-opt> ";" <text-opt> <EOL>
<label-line> ::= <label-def> <ws-opt> <comment-opt> <EOL>
<instruction-line> ::= <instruction> <ws-opt> <comment-opt> <EOL>
<data-line> ::= <number-literal> <ws-opt> <comment-opt> <EOL>
             | <string-literal> <ws-opt> <comment-opt> <EOL>

<instruction> ::= <op0>
                | <op1> <ws-plus> <arg-reg>
                | <op2> <ws-plus> <arg-reg> <sep> <arg-reg>
                | <op3> <ws-plus> <arg-reg> <sep> <arg-reg> <sep> <arg-reg>
                | <op3i> <ws-plus> <arg-reg> <sep> <arg-reg> <sep> <arg-imm>

<op0> ::= "HLT"
<op1> ::= "IN" | "OUT" | "TRAP"
<op2> ::= "LD" | "ST" | "MOV"
<op3> ::= "ADD" | "SUB" | "AND" | "OR" | "XOR" | "SHL" | "SHR"
<op3i> ::= "ADDI" | "SUBI" | "ANDI" | "ORI" | "XORI"
         | "BEQ" | "BNE" | "BLT" | "BLE" | "BGT" | "BGE"

<arg-reg> ::= "%" <register>
<arg-imm> ::= <number> | <label>
<register> ::= "R0" | "R1" | "R2" | "R3" | "R4" | "R5" | "R6" | "R7"

<label-def> ::= <label> ":"
<label> ::= <ident-start> <ident-tail>
<ident-tail> ::= "" | <ident-char> <ident-tail>
<ident-start> ::= <letter> | "_"
<ident-char> ::= <ident-start> | <digit>

<number-literal> ::= "#" <number>
<number> ::= <sign-opt> <digits>
<sign-opt> ::= "" | "-"
<digits> ::= <digit> | <digit> <digits>

<string-literal> ::= "\"" <string-chars> "\""
<string-chars> ::= "" | <string-char> <string-chars>

<comment-opt> ::= "" | ";" <text-opt>
<text-opt> ::= "" | <text-char> <text-opt>

<sep> ::= <ws-opt> "," <ws-opt>
<ws-plus> ::= <ws> | <ws> <ws-plus>
<ws-opt> ::= "" | <ws-plus>
<ws> ::= " " | "\t"
<EOL> ::= "\n" | "\r\n"

<letter> ::= "A" | ... | "Z" | "a" | ... | "z"
<digit> ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
<string-char> ::= любой символ, кроме "\"" и конца строки
<text-char> ::= любой символ, кроме конца строки
```

