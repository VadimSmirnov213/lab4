# Лабораторная работа №4

**Выполнил**: `<ФИО>`, `<группа>`  
**Вариант**:

```text
asm | risc | neum | hw | tick | binary | trap | mem | cstr | prob1 | cache
```

## Язык программирования

Ассемблероподобный язык (`asm`) с поддержкой:

- меток;
- секций `.text` и `.data`;
- директив `.org`, `.equ`, `.word`, `.asciiz`;
- комментариев `; ...`.

### Синтаксис (BNF)

```bnf
<program> ::= <line> | <line> <program>

<line> ::= <empty-line>
         | <comment-line>
         | <label-line>
         | <instruction-line>
         | <directive-line>

<empty-line> ::= <EOL>
<comment-line> ::= <ws-opt> ";" <text-opt> <EOL>
<label-line> ::= <label-def> <ws-opt> <comment-opt> <EOL>
<instruction-line> ::= <instruction> <ws-opt> <comment-opt> <EOL>
<directive-line> ::= <directive> <ws-opt> <comment-opt> <EOL>

<instruction> ::= "HLT"
                | "IRET"
                | ("ADD" | "SUB") <ws-plus> <reg> <sep> <reg> <sep> <reg>
                | ("LD" | "ST") <ws-plus> <reg> <sep> <reg>
                | "BEQ" <ws-plus> <reg> <sep> <reg> <sep> <imm>
                | ("JMP" | "TRAP") <ws-plus> <imm>

<directive> ::= ".text"
              | ".data"
              | ".org" <ws-plus> <imm>
              | ".equ" <ws-plus> <ident> <sep> <imm>
              | ".word" <ws-plus> <imm>
              | ".asciiz" <ws-plus> <string>

<reg> ::= "%" <register>
<register> ::= "R0" | "R1" | "R2" | "R3" | "R4" | "R5" | "R6" | "R7"

<imm> ::= <number> | <label>
<label-def> ::= <label> ":"
<label> ::= <ident>
<ident> ::= <ident-start> <ident-tail>
<ident-tail> ::= "" | <ident-char> <ident-tail>
<ident-start> ::= <letter> | "_"
<ident-char> ::= <ident-start> | <digit>

<number> ::= <sign-opt> <digits>
<sign-opt> ::= "" | "-"
<digits> ::= <digit> | <digit> <digits>
<string> ::= "\"" <string-chars> "\""
<string-chars> ::= "" | <string-char> <string-chars>

<comment-opt> ::= "" | ";" <text-opt>
<text-opt> ::= "" | <text-char> <text-opt>
<sep> ::= <ws-opt> "," <ws-opt>
<ws-plus> ::= <ws> | <ws> <ws-plus>
<ws-opt> ::= "" | <ws-plus>
<ws> ::= " " | "\t"
<EOL> ::= "\n" | "\r\n"
```

### Семантика

- Стратегия вычислений: последовательное выполнение инструкций по `IP`.
- Область видимости меток и констант (`.equ`) — глобальная в рамках файла.
- Типы данных: 32-битные машинные слова (беззнаковое хранение в памяти).
- Строки: `cstr` (`.asciiz`) — по символу на машинное слово + завершающий `0`.

## Организация памяти

Архитектура памяти: `neum` (фон Нейман), код и данные в одном адресном пространстве.

- Машинное слово: 32 бита (4 байта).
- Адресация: по индексу машинного слова.
- Программа и данные размещаются транслятором в едином массиве слов с учетом `.org`.
- Поддержан memory-mapped I/O (`mem`):
  - `0xFF00` — `MMIO_IN_DATA`,
  - `0xFF01` — `MMIO_IN_STATUS`,
  - `0xFF02` — `MMIO_OUT_DATA`.

Регистры процессора:

- `R0..R7` — регистры общего назначения;
- `IP` — счетчик команд;
- служебные (в модели): флаги остановки, состояние прерывания, счётчик тактов.

## Система команд

Архитектура: `risc` (фиксированная длина инструкции, арифметика только по регистрам).

### Набор инструкций

| Opcode | Мнемоника | Формат | Описание |
|---|---|---|---|
| `0x00` | `HLT`  | `-` | Останов |
| `0x01` | `ADD`  | `rd, rs1, rs2` | `rd = rs1 + rs2` |
| `0x02` | `SUB`  | `rd, rs1, rs2` | `rd = rs1 - rs2` |
| `0x03` | `LD`   | `rd, rs1` | `rd = MEM[rs1]` |
| `0x04` | `ST`   | `rd, rs1` | `MEM[rd] = rs1` |
| `0x05` | `BEQ`  | `rs1, rs2, imm` | переход на `imm`, если `rs1 == rs2` |
| `0x06` | `JMP`  | `imm` | безусловный переход |
| `0x07` | `TRAP` | `imm` | программный trap |
| `0x08` | `IRET` | `-` | возврат из обработчика прерывания |

### Кодирование инструкций (binary)

Инструкция кодируется в 32 бита:

```text
[31:24] opcode
[23:20] rd
[19:16] rs1
[15:12] rs2
[11:00] imm12 (signed)
```

## Транслятор

Реализован в `src/assembler.py`.

### CLI

```bash
python -m src.assembler <input.asm> <output.bin> --listing <output.lst>
```

### Этапы трансляции

1. Очистка комментариев и разбор строк.
2. Первый проход: сбор меток, учет `.org`, `.equ`.
3. Второй проход: кодирование инструкций и директив в машинные слова.
4. Формирование:
   - бинарного файла (`.bin`);
   - текстового листинга (`.lst`) формата:
     `<addr> - <HEXCODE> - <mnemonic>`.

## Модель процессора

Реализована в `src/cpu.py`.

### Общая логика

- `hw` control unit (hardwired логика в коде исполнения инструкций).
- Моделирование `tick`: шаг `step()` изменяет состояние процессора и увеличивает `tick`.
- Основной цикл: `fetch -> decode -> execute`.

### Прерывания (`trap`)

- Поддержано расписание прерываний: список `(tick, byte)`.
- При наступлении события и если процессор не в ISR:
  - вход в обработчик по `interrupt_vector_addr`,
  - сохраняется `return_ip`,
  - фиксируется событие `IRQ_ENTER` в логе.
- Возврат из ISR — инструкция `IRET`.

### Ввод-вывод (`mem`)

- Ввод/вывод реализован через MMIO-адреса (`LD/ST` к специальным адресам).
- Выход накапливается в `output_buffer`.

### Журнал работы

Лог хранит:

- номер такта;
- `IP`;
- исполняемую инструкцию;
- состояние регистров;
- признак нахождения в прерывании.

## Тестирование

Тесты реализованы на `pytest`:

- `tests/test_isa.py` — кодирование/декодирование ISA;
- `tests/test_assembler.py` — транслятор, директивы, листинг;
- `tests/test_cpu.py` — исполнение инструкций, MMIO, прерывания.

Текущее состояние: `15 passed`.

Запуск:

```bash
.venv/bin/python -m pytest -q
```

## Алгоритм по варианту

`prob1` соответствует задаче Project Euler #4 (Largest Palindrome Product).

Ссылка: [https://projecteuler.net/problem=4](https://projecteuler.net/problem=4)

## Статус реализации варианта

- [x] `asm`
- [x] `risc`
- [x] `neum`
- [x] `hw`
- [x] `tick` (базовый потактовый лог)
- [x] `binary`
- [x] `trap` (базовый механизм ISR/IRET)
- [x] `mem` (MMIO)
- [x] `cstr`
- [ ] `cache` (в работе)
- [ ] Полный набор golden-тестов обязательных алгоритмов

