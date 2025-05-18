import time


class Grammar:

    def __init__(self):
        self.productions = {}
        self.terminals = set()
        self.non_terminals = set()
        self.start_symbol = 'S'

    def add_production(self, non_terminal, productions):

        if non_terminal not in self.productions:
            self.productions[non_terminal] = []
            self.non_terminals.add(non_terminal)

        for prod in productions:
            self.productions[non_terminal].append(prod)

            for symbol in prod:
                if symbol.isupper():
                    self.non_terminals.add(symbol)
                elif symbol != 'e':  #'e' representa epsilon
                    self.terminals.add(symbol)

    def read_grammar(self, input_lines):
        num_non_terminals = int(input_lines[0])

        for i in range(1, num_non_terminals + 1):
            line = input_lines[i].strip()
            parts = line.split('->')

            non_terminal = parts[0].strip()
            productions_str = parts[1].strip().split()

            self.add_production(non_terminal, productions_str)

    def get_first_set(self):
        first = {symbol: set() for symbol in self.non_terminals}

        #Para cada terminal a, FIRST(a) = {a}
        for terminal in self.terminals:
            first[terminal] = {terminal}

        #Para epsilon, FIRST(e) = {e}
        first['e'] = {'e'}

        #Algoritmo para calcular FIRST
        while True:
            updated = False

            for non_terminal, productions in self.productions.items():
                for production in productions:
                    if production == 'e':
                        if 'e' not in first[non_terminal]:
                            first[non_terminal].add('e')
                            updated = True
                    else:
                        first_pos = 0
                        eps_in_everything = True

                        for symbol in production:
                            #Si el simbolo no tiene un conjunto FIRST
                            if symbol not in first:
                                if symbol.isupper():  #Es un no terminal
                                    first[symbol] = set()
                                else:  #Es un terminal
                                    first[symbol] = {symbol}

                            for term in first[symbol]:
                                if term != 'e' and term not in first[non_terminal]:
                                    first[non_terminal].add(term)
                                    updated = True

                            if 'e' not in first[symbol]:
                                eps_in_everything = False
                                break

                            first_pos += 1

                        if eps_in_everything and 'e' not in first[non_terminal]:
                            first[non_terminal].add('e')
                            updated = True

            if not updated:
                break

        return first

    def get_follow_set(self, first_sets):
        follow = {non_terminal: set() for non_terminal in self.non_terminals}

        #Añadir $ al FOLLOW del simbolo inicial
        follow[self.start_symbol].add('$')

        #Algoritmo para calcular FOLLOW
        while True:
            updated = False

            for non_terminal, productions in self.productions.items():
                for production in productions:
                    if production == 'e':
                        continue

                    for i, symbol in enumerate(production):
                        if not symbol.isupper():
                            continue

                        if i < len(production) - 1:
                            rest = production[i + 1:]

                            first_rest = set()
                            all_have_epsilon = True

                            for sym in rest:
                                if sym not in first_sets:
                                    if sym.isupper():
                                        continue
                                    else:
                                        first_rest.add(sym)
                                        all_have_epsilon = False
                                        break

                                for term in first_sets[sym]:
                                    if term != 'e':
                                        first_rest.add(term)

                                if 'e' not in first_sets[sym]:
                                    all_have_epsilon = False
                                    break

                            for term in first_rest:
                                if term != 'e' and term not in follow[symbol]:
                                    follow[symbol].add(term)
                                    updated = True

                            if all_have_epsilon:
                                for term in follow[non_terminal]:
                                    if term not in follow[symbol]:
                                        follow[symbol].add(term)
                                        updated = True
                        else:
                            for term in follow[non_terminal]:
                                if term not in follow[symbol]:
                                    follow[symbol].add(term)
                                    updated = True

            if not updated:
                break

        return follow

    def __str__(self):
        result = "Gramática:\n"
        for non_terminal, productions in self.productions.items():
            result += f"{non_terminal} -> {' | '.join(productions)}\n"
        return result


class LL1Parser:

    def __init__(self, grammar):
        self.grammar = grammar
        self.first_sets = grammar.get_first_set()
        self.follow_sets = grammar.get_follow_set(self.first_sets)
        self.parse_table = self.build_parse_table()
        self.is_ll1 = self.check_if_ll1()

    def get_first_of_string(self, string):
        if not string or string == 'e':
            return {'e'}

        first_set = set()
        all_derive_epsilon = True

        for symbol in string:
            if symbol not in self.first_sets:
                #Si es un terminal su conjunto FIRST es solo el terminal
                first_set.add(symbol)
                all_derive_epsilon = False
                break

            symbol_first = self.first_sets[symbol].copy()
            if 'e' in symbol_first:
                symbol_first.remove('e')
            first_set.update(symbol_first)

            if 'e' not in self.first_sets[symbol]:
                all_derive_epsilon = False
                break

        if all_derive_epsilon:
            first_set.add('e')

        return first_set

    def build_parse_table(self):
        parse_table = {}

        for non_terminal in self.grammar.non_terminals:
            parse_table[non_terminal] = {}

        #Llenar la tabla usando los conjuntos FIRST y FOLLOW
        for non_terminal, productions in self.grammar.productions.items():
            for production in productions:
                first_of_production = self.get_first_of_string(production)

                for terminal in first_of_production:
                    if terminal != 'e':
                        if terminal in parse_table[non_terminal]:
                            parse_table[non_terminal][terminal] = None
                        else:
                            parse_table[non_terminal][terminal] = production

                if 'e' in first_of_production:
                    for terminal in self.follow_sets[non_terminal]:
                        if terminal in parse_table[non_terminal]:
                            parse_table[non_terminal][terminal] = None
                        else:
                            parse_table[non_terminal][terminal] = production

        return parse_table

    def check_if_ll1(self):
        for non_terminal, table_row in self.parse_table.items():
            for terminal, production in table_row.items():
                if production is None:
                    return False
        return True

    def parse(self, input_string):
        if not self.is_ll1:
            return False

        #Asegurarse de que la cadena termina con $
        if not input_string.endswith('$'):
            input_string += '$'

        stack = ['$', self.grammar.start_symbol]
        input_ptr = 0

        while stack:
            #Obtener simbolo en la cima de la pila
            top = stack.pop()

            #Obtener simbolo actual de entrada
            current_input = input_string[input_ptr] if input_ptr < len(input_string) else '$'

            if top == 'e':
                continue
            elif not top.isupper():
                if top == current_input:
                    input_ptr += 1
                else:
                    return False
            else:
                if current_input in self.parse_table[top]:
                    production = self.parse_table[top][current_input]
                    if production is None:
                        return False
                    elif production != 'e':
                        for symbol in reversed(production):
                            stack.append(symbol)
                else:
                    return False

        #La cadena es aceptada si hemos consumido toda la entrada
        return input_ptr >= len(input_string) or (input_ptr == len(input_string) - 1 and input_string[-1] == '$')

    def is_grammar_ll1(self):
        return self.is_ll1


class SLR1Parser:

    def __init__(self, grammar):
        self.grammar = grammar
        self.augmented_grammar = self.augment_grammar()
        self.first_sets = self.augmented_grammar.get_first_set()
        self.follow_sets = self.augmented_grammar.get_follow_set(self.first_sets)
        self.canonical_collection = self.build_canonical_collection()
        self.action_table, self.goto_table = self.build_parsing_tables()
        self.is_slr1 = self.check_if_slr1()

    def augment_grammar(self):
        aug_grammar = Grammar()

        for non_terminal, productions in self.grammar.productions.items():
            for production in productions:
                aug_grammar.add_production(non_terminal, [production])

        #Agregar produccion para el simbolo inicial aumentado S' -> S
        aug_grammar.add_production("S'", [self.grammar.start_symbol])
        aug_grammar.start_symbol = "S'"

        return aug_grammar

    def closure(self, items):
        closure = set(items)

        while True:
            new_items = set()

            for item in closure:
                non_terminal, production, dot_pos = item

                #Si el punto esta al final de la produccion no agregar nuevos items
                if dot_pos >= len(production) or production == 'e':
                    continue

                symbol_after_dot = production[dot_pos]

                if symbol_after_dot in self.augmented_grammar.non_terminals:
                    for prod in self.augmented_grammar.productions[symbol_after_dot]:
                        new_item = (symbol_after_dot, prod, 0)
                        if new_item not in closure:
                            new_items.add(new_item)

            if not new_items:
                break

            closure.update(new_items)

        return closure

    def goto(self, items, symbol):
        goto_items = set()

        for item in items:
            non_terminal, production, dot_pos = item

            if dot_pos >= len(production) or production == 'e':
                continue

            if production[dot_pos] == symbol:
                new_item = (non_terminal, production, dot_pos + 1)
                goto_items.add(new_item)

        return self.closure(goto_items)

    def build_canonical_collection(self):
        initial_item = ("S'", self.grammar.start_symbol, 0)
        initial_items = self.closure({initial_item})

        states = [initial_items]
        transitions = {}

        symbols = self.augmented_grammar.terminals.union(self.augmented_grammar.non_terminals)

        i = 0
        while i < len(states):
            current_state = states[i]

            for symbol in symbols:
                goto_result = self.goto(current_state, symbol)

                if goto_result and goto_result not in states:
                    states.append(goto_result)
                    transitions[(i, symbol)] = len(states) - 1
                elif goto_result:
                    transitions[(i, symbol)] = states.index(goto_result)

            i += 1

        return states, transitions

    def build_parsing_tables(self):
        states, transitions = self.canonical_collection
        action_table = {}
        goto_table = {}

        for i in range(len(states)):
            action_table[i] = {}
            goto_table[i] = {}

        #Construir tabla GOTO
        for (state, symbol), next_state in transitions.items():
            if symbol in self.augmented_grammar.non_terminals:
                goto_table[state][symbol] = next_state

        #Construir tabla ACTION
        for state_idx, state in enumerate(states):
            for item in state:
                non_terminal, production, dot_pos = item

                if dot_pos < len(production) and production != 'e':
                    symbol = production[dot_pos]
                    if not symbol.isupper() and (state_idx, symbol) in transitions:
                        next_state = transitions[(state_idx, symbol)]
                        action = f"s{next_state}"

                        if symbol in action_table[state_idx] and action_table[state_idx][symbol] != action:
                            action_table[state_idx][symbol] = None
                        else:
                            action_table[state_idx][symbol] = action

                elif (dot_pos >= len(production) and production != 'e') or (production == 'e' and dot_pos == 0):
                    for terminal in self.follow_sets[non_terminal]:
                        if non_terminal == "S'" and production == self.grammar.start_symbol:
                            action = "acc"
                        else:
                            prod_idx = 0
                            for nt, prods in self.grammar.productions.items():
                                if nt == non_terminal:
                                    for p_idx, p in enumerate(prods):
                                        if p == production:
                                            prod_idx = p_idx
                                            break

                            action = f"r{non_terminal}->{production}"

                        if terminal in action_table[state_idx] and action_table[state_idx][terminal] != action:
                            action_table[state_idx][terminal] = None
                        else:
                            action_table[state_idx][terminal] = action

        return action_table, goto_table

    def check_if_slr1(self):
        for state, actions in self.action_table.items():
            for terminal, action in actions.items():
                if action is None:
                    return False
        return True

    def parse(self, input_string):
        if not self.is_slr1:
            return False

        #Asegurarse de que la cadena termina con $
        if not input_string.endswith('$'):
            input_string += '$'

        stack = [0]
        input_ptr = 0

        while True:
            current_state = stack[-1]
            current_input = input_string[input_ptr] if input_ptr < len(input_string) else '$'

            if current_input not in self.action_table[current_state]:
                return False

            action = self.action_table[current_state][current_input]

            if action is None:
                return False
            elif action.startswith('s'):
                next_state = int(action[1:])
                stack.append(current_input)
                stack.append(next_state)
                input_ptr += 1
            elif action.startswith('r'):
                production_parts = action[1:].split('->')
                non_terminal = production_parts[0]
                production = production_parts[1]

                if production != 'e':
                    for _ in range(2 * len(production)):
                        stack.pop()

                top_state = stack[-1]

                #Usar tabla GOTO para obtener siguiente estado
                if non_terminal in self.goto_table[top_state]:
                    next_state = self.goto_table[top_state][non_terminal]
                    stack.append(non_terminal)
                    stack.append(next_state)
                else:
                    return False
            elif action == 'acc':
                return True
            else:
                return False

    def is_grammar_slr1(self):
        return self.is_slr1


def main():
    try:
        num_non_terminals = int(input())

        input_lines = [str(num_non_terminals)]

        for _ in range(num_non_terminals):
            line = input()
            input_lines.append(line)

        grammar = Grammar()
        grammar.read_grammar(input_lines)

        ll1_parser = LL1Parser(grammar)
        slr1_parser = SLR1Parser(grammar)

        is_ll1 = ll1_parser.is_grammar_ll1()
        is_slr1 = slr1_parser.is_grammar_slr1()

        if is_ll1 and is_slr1:
            while True:
                time.sleep(.8)
                print("Select a parser (T: for LL(1), B: for SLR(1), Q: quit):")
                time.sleep(.8)
                choice = input().strip()

                if choice == 'Q':
                    break
                elif choice == 'T':
                    parse_strings(ll1_parser)
                elif choice == 'B':
                    parse_strings(slr1_parser)
        elif is_ll1:
            time.sleep(.8)
            print("Grammar is LL(1).")
            time.sleep(.8)
            parse_strings(ll1_parser)
        elif is_slr1:
            time.sleep(.8)
            print("Grammar is SLR(1).")
            time.sleep(.8)
            parse_strings(slr1_parser)
        else:
            time.sleep(.8)
            print("Grammar is neither LL(1) nor SLR(1).")
            time.sleep(.8)

    except Exception as e:
        print(f"Error: {e}")


def parse_strings(parser):
    while True:
        string = input().strip()

        if not string:
            break

        result = parser.parse(string)
        time.sleep(.8)
        print("yes" if result else "no")
        time.sleep(.8)


if __name__ == "__main__":
    main()