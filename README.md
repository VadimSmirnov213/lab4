# Лабораторная работа №4

**Студент:** Смирнов Вадим Константинович  
**Группа:** P3219  
**Вариант:**

```text
asm | risc | neum | hw | tick | binary | trap | mem | cstr | prob1 | cache
```

---

## Язык программирования

Реализован ассемблероподобный язык (`asm`) с поддержкой:

- меток;
- секций `.text` и `.data`;
- директив `.org`, `.equ`, `.word`, `.asciiz`;
- пользовательских макроопределений (`.macro ... .endm`);
- условной компиляции (`.if/.else/.endif`);
- комментариев `; ...`.

### Синтаксис (БНФ)

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
               | ("ADD" | "SUB" | "MUL" | "DIV" | "MOD") <ws-plus> <reg> <sep> <reg> <sep> <reg>
               | ("AND" | "OR" | "XOR" | "SHL" | "SHR") <ws-plus> <reg> <sep> <reg> <sep> <reg>
               | "ADDI" <ws-plus> <reg> <sep> <reg> <sep> <imm>
               | ("LD" | "ST") <ws-plus> <reg> <sep> <reg>
               | ("BEQ" | "BNE" | "BGT" | "BLT" | "BLE" | "BGE") <ws-plus> <reg> <sep> <reg> <sep> <imm>
               | ("JMP" | "TRAP") <ws-plus> <imm>

<directive> ::= ".text"
              | ".data"
              | ".org" <ws-plus> <imm>
              | ".equ" <ws-plus> <ident> <sep> <imm>
              | ".word" <ws-plus> <imm>
              | ".asciiz" <ws-plus> <string>
              | ".macro" <ws-plus> <ident> <macro-params-opt>
              | ".endm"
              | ".if" <ws-plus> <imm-or-const>
              | ".else"
              | ".endif"

<macro-params-opt> ::= "" | <ws-plus> <ident> | <ws-plus> <ident> <sep> <ident-list>
<ident-list> ::= <ident> | <ident> <sep> <ident-list>
<imm-or-const> ::= <imm> | <ident>

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
- Тип данных: 32-битное машинное слово.
- Строки: `cstr` (`.asciiz`) — по символу на слово + завершающий `0`.

---

## Организация памяти

Архитектура памяти: `neum` (фон Нейман), код и данные в одном адресном пространстве.

- Машинное слово: 32 бита (4 байта).
- Адресация: по индексу машинного слова.
- Программа и данные размещаются транслятором в едином массиве слов с учетом `.org`.

### Memory-mapped I/O (`mem`)

- `0xFF00` — `MMIO_IN_DATA`,
- `0xFF01` — `MMIO_IN_STATUS`,
- `0xFF02` — `MMIO_OUT_DATA`.

### Регистры

- `R0..R7` — регистры общего назначения;
- `IP` — счетчик команд;
- служебные поля модели: `tick`, `halted`, признак режима прерывания.

---

## Система команд

Архитектура: `risc` (фиксированная длина инструкции, арифметика над регистрами).

### Кодирование (binary)

Каждая инструкция занимает 32 бита:

```text
[31:24] opcode
[23:20] rd
[19:16] rs1
[15:12] rs2
[11:00] imm12 (signed)
```

### Набор инструкций

| Opcode | Мнемоника | Формат | Назначение |
|---|---|---|---|
| `0x00` | `HLT`  | `-` | останов модели |
| `0x01` | `ADD`  | `rd, rs1, rs2` | сложение |
| `0x02` | `SUB`  | `rd, rs1, rs2` | вычитание |
| `0x03` | `LD`   | `rd, rs1` | чтение из памяти/MMIO |
| `0x04` | `ST`   | `rd, rs1` | запись в память/MMIO |
| `0x05` | `BEQ`  | `rs1, rs2, imm` | ветвление при равенстве |
| `0x06` | `JMP`  | `imm` | безусловный переход |
| `0x07` | `TRAP` | `imm` | программный trap-id |
| `0x08` | `IRET` | `-` | возврат из ISR |
| `0x09` | `ADDI` | `rd, rs1, imm` | сложение с immediate |
| `0x0A` | `MUL`  | `rd, rs1, rs2` | умножение |
| `0x0B` | `DIV`  | `rd, rs1, rs2` | деление |
| `0x0C` | `BNE`  | `rs1, rs2, imm` | ветвление при неравенстве |
| `0x0D` | `BGT`  | `rs1, rs2, imm` | ветвление `>` |
| `0x0E` | `MOD`  | `rd, rs1, rs2` | остаток от деления |
| `0x0F` | `AND`  | `rd, rs1, rs2` | побитовое И |
| `0x10` | `OR`   | `rd, rs1, rs2` | побитовое ИЛИ |
| `0x11` | `XOR`  | `rd, rs1, rs2` | побитовое XOR |
| `0x12` | `SHL`  | `rd, rs1, rs2` | логический сдвиг влево |
| `0x13` | `SHR`  | `rd, rs1, rs2` | логический сдвиг вправо |
| `0x14` | `BLT`  | `rs1, rs2, imm` | ветвление `<` |
| `0x15` | `BLE`  | `rs1, rs2, imm` | ветвление `<=` |
| `0x16` | `BGE`  | `rs1, rs2, imm` | ветвление `>=` |

---

## Транслятор

Реализация: `src/assembler.py`.

### CLI

```bash
python -m src.assembler <input.asm> <output.bin> --listing <output.lst>
```

### Этапы трансляции

1. Очистка комментариев и разбор строк.
2. Препроцессинг: раскрытие `.macro`, обработка `.if/.else/.endif`.
3. Первый проход: сбор меток, учет `.org`, `.equ`.
4. Второй проход: кодирование инструкций и директив в машинные слова.
5. Формирование:
   - бинарного файла (`.bin`);
   - листинга (`.lst`) формата `<addr> - <HEXCODE> - <mnemonic>`.

---

## Модель процессора

Реализация: `src/cpu.py`.

### Общая логика

- `hw` control unit (hardwired в коде исполнения инструкций);
- цикл `fetch -> decode -> execute`;
- режим `tick`: счётчик тактов инкрементируется на каждом шаге модели;
- журнал исполнения хранится в `TickLog`.

### Прерывания (`trap`)

Поддержан входной график прерываний: список `(tick, byte)`.

При наступлении события:

1. если процессор не в ISR — выполняется вход в обработчик;
2. сохраняется адрес возврата `return_ip`;
3. `IP` переключается на `interrupt_vector_addr`;
4. в журнал пишется `IRQ_ENTER`.

Возврат из ISR выполняется инструкцией `IRET`.

### Кеш (`cache`)

Реализован простой direct-mapped кеш (`SimpleCache`):

- hit: +1 такт;
- miss: +10 тактов;
- для наблюдения в лог пишутся события `CACHE_HIT` и `CACHE_MISS`.

MMIO-доступы кеш не используют.

### Тактовая модель инструкций

В текущей реализации `tick` считается на уровне шага `CPU.step()`:

- базово любая инструкция добавляет `+1` такт;
- для `LD`/`ST` в обычную память добавляется штраф доступа через кеш:
  - `CACHE_HIT`: дополнительно `+1` такт;
  - `CACHE_MISS`: дополнительно `+10` тактов;
- для `LD`/`ST` в MMIO (`0xFF00..0xFF02`) кеш не используется, остается базовый `+1` такт;
- событие входа в прерывание (`IRQ_ENTER`) занимает отдельный шаг и тоже добавляет `+1` такт.

Итого:

- большинство инструкций (`ADD`, `SUB`, `ADDI`, `JMP`, `BEQ`, `TRAP`, `IRET`, и т.д.) — `1` такт;
- `LD`/`ST` (обычная память): `2` такта при hit и `11` тактов при miss;
- `LD`/`ST` (MMIO): `1` такт.

### Схемы DataPath и ControlUnit



## Тестирование

Тесты реализованы на `pytest`.

### Unit / integration

- `tests/test_isa.py` — кодирование/декодирование ISA.
- `tests/test_assembler.py` — трансляция, директивы, листинг.
- `tests/test_cpu.py` — исполнение инструкций, MMIO, прерывания, кеш.

### Golden (end-to-end)

`tests/test_golden.py` прогоняет цепочку:

```text
source.asm -> assembler -> binary/listing -> CPU run -> сравнение с expected
```

Используются кейсы:

- `golden/hello`
- `golden/cat`
- `golden/hello_user_name`
- `golden/sort`
- `golden/double_precision`
- `golden/prob1`

Для каждого кейса сравниваются:

- итоговый вывод (`expected_output.txt`);
- репрезентативные строки трейса (`expected_trace_lines.txt`).

### Запуск

```bash
.venv/bin/python -m pytest -q
```

Текущее локальное состояние: `29 passed`.

---

## Алгоритм по варианту

`prob1` — Project Euler #4 (Largest Palindrome Product).  
Ссылка: [https://projecteuler.net/problem=4](https://projecteuler.net/problem=4)

---

## Статус реализации варианта

- [x] `asm`
- [x] `risc`
- [x] `neum`
- [x] `hw`
- [x] `tick` (пошаговое моделирование с подсчётом тактов)
- [x] `binary`
- [x] `trap`
- [x] `mem` (MMIO)
- [x] `cstr`
- [x] `prob1`
- [x] `cache` (базовая модель кеша в CPU)

---

## Пример использования

```bash
# 1) Трансляция
python -m src.assembler golden/hello/source.asm hello.bin --listing hello.lst

# 2) Прогон тестов
.venv/bin/python -m pytest -q
```

