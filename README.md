# LL(1) and SLR(1) Parser Generator

Python program that reads a context-free grammar, computes its **FIRST** and **FOLLOW** sets, and builds two parsers from it: an **LL(1)** predictive parser and an **SLR(1)** shift-reduce parser. It reports whether the grammar is LL(1), SLR(1), both or neither, and then validates input strings with the parser you choose.

Final project, Universidad EAFIT (2025-1). Written in **Python 3.13 using only the standard library** (no parsing libraries).

## Features

- Reads a grammar from the console and identifies its terminals, nonterminals and start symbol.
- Computes FIRST and FOLLOW sets for every nonterminal.
- **LL(1):** builds the predictive parsing table and validates strings with a stack-based derivation.
- **SLR(1):** builds the LR(0) automaton (closure and goto over item sets) and the ACTION/GOTO tables, then validates strings with shift/reduce operations.
- Detects table conflicts to decide which parsers apply to the grammar.

## Code structure

| Component | Responsibility |
|---|---|
| `Grammar` | Parses the productions and computes FIRST and FOLLOW sets |
| `LL1Parser` | Builds the LL(1) table and runs the predictive parse |
| `SLR1Parser` | Builds the LR(0) automaton and ACTION/GOTO tables and runs the shift/reduce parse |
| `main()` / `parse_strings()` | Console interaction: grammar input, parser selection and string validation |

The full write-up is in [`Proyectofinallenguajes.pdf`](Proyectofinallenguajes.pdf).

## Authors

- **Samuel Calderón Duque**: [GitHub](https://github.com/sscalderod) · [LinkedIn](https://www.linkedin.com/in/samuel-calderon-duque-b8772b37a/)
- **Matías Monsalve Ruiz**

## System and Tools

- **Operating System:** Windows 11 / macOS Sequoia.
- **Programming Language:** Python 3.13.
- **Tools:** PyCharm 2024.3.3.

## Instruction
 Have Python installed, open the IDE of your preference, open the file "parser.py" after that run the files as follows: 

``` 
python parser.py
```

You will be asked to enter the number of productions lines, and then the productions. If a production has two or more productions you separate them with space.

The input must be in this format:

`3`

`S -> AB`

`A -> aA d`

`B -> bBc e`

Once the grammar is loaded, you will see:

`Select a parser (T: for LL(1), B: for SLR(1), Q: quit):` (it will vary depending on the grammar, check the explanation).

- Type T and press Enter to use the LL(1) parser.

- Type B and press Enter to use the SLR(1) parser.

- Type Q and press Enter to quit.

You can now enter strings made up of terminal symbols.

Each will return either  `yes` (accepted) or `no` (rejected) by the parser.

To stop entering strings and return to the main menu, just press `Enter` on an empty line.

## Explanation 
The first part of the program reads a context-free grammar from user input. The grammar is entered line by line in the form `A -> xyz`, where `A` is a nonterminal and `xyz` is a sequence of terminals and/or nonterminals. The program processes the input to extract all nonterminals, terminals, and the start symbol. Then, it calculates the FIRST and FOLLOW sets for each nonterminal. These sets are essential for building the parsing tables used later.

When the grammar is loaded, the program attempts to construct two types of parsers:

An LL(1) parser using a predictive parsing table.

An SLR(1) parser using an LR(0) automaton and FOLLOW sets.

If successful, the program reports whether the grammar is LL(1), SLR(1), both, or neither.

Output example after entering a SLR(1) and LL(1) grammar:

`Select a parser (T: for LL(1), B: for SLR(1), Q: quit):`

The second part of the program prompts the user to enter strings to test against the grammar. If the LL(1) parser is available and selected (`T`), it will use the predictive parsing table to process each string. The algorithm uses a stack to simulate derivations and matches input tokens against expected productions.

Output example when using the LL(1) parser:

`Input: aabb`

`Output: yes`

The third part of the program allows you to validate the same strings using an SLR(1) parser (`B`). The SLR(1) parser builds a full LR(0) automaton where each state represents a set of parsing items. Based on this automaton, it constructs the ACTION and GOTO tables. Using these tables, the parser performs shift/reduce operations to validate the string.

Output example when using the SLR(1) parser:

`Input: abbb`

`Output: no`


