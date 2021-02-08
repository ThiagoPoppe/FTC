from sys import argv

def apply_parentheses(string):
    """ Método auxiliar que coloca parênteses em uma expressão regular evitando ambiguidades """
    # Colocamos parênteses caso a expressão não possua parênteses e tem tamanho maior que 1
    if len(string) > 1 and (string[0] != '(' and string[-1] != ')'):
        return '(' + string + ')'
    
    # Caso contrário o uso de parênteses é desnecessário
    return string

def has_transition(delta, src, dest):
    """ Método auxiliar que retorna se há transição entre os estados src e dest """
    return delta[src][dest] != []

def get_paths(state, delta, parent):
    """ Método auxiliar que retorna um caminho de 3 estados que passa por 'state' """
    paths = list()
    for dest in delta[state]:
        if has_transition(delta, state, dest) and (dest != state):
            for prev in parent[state]:
                paths.append((prev, state, dest))

    return paths

if __name__ == '__main__':
    if len(argv) != 2:
        print('usage: python {} <input file>'.format(argv[0]))
        exit(1)

    # ------ CONSTRUINDO O AUTÔMATO FINITO ------ #
    # Lendo todas as linhas do arquivo, armazenando em uma lista
    with open(argv[1], 'r') as f:
        lines = f.read().splitlines()

    # Lendo estados, símbolos, estados iniciais e finais
    states         = lines[0].split(',')
    symbols        = lines[1].split(',')
    initial_states = lines[2].split(',')
    final_states   = lines[3].split(',')

    # Inicializando função de transição (estados x estados -> lista de símbolos)
    delta = dict()
    for src in states:
        delta[src] = dict()
        for dest in states:
            delta[src][dest] = list()

    # Inicializando lista de pais para cada estado
    parent = dict()
    for state in states:
        parent[state] = list()

    # Lendo as transições (restante das linhas do arquivo)
    for i in range(4, len(lines)):
        line = lines[i].split(',')
        src, symbol, dest = line[0], line[1], line[2:]

        # Atualizando função de transição
        for state in dest:
            delta[src][state].append(symbol)

        # Atualizando lista de pais
        # Não iremos inserir pais repetidos e não queremos que um estado seja pai dele mesmo
        for state in dest:
            if (src != state) and (src not in parent[state]):
                parent[state].append(src)


    # ------ CONSTRUINDO O DIAGRAMA ER ------ #
    # Atualizando função de transição com novo estado inicial e final
    delta['RegEx_initial_state'] = dict()
    delta['RegEx_final_state']   = dict()
    delta['RegEx_initial_state']['RegEx_final_state'] = list()

    for state in states:
        delta['RegEx_initial_state'][state] = list()
        delta[state]['RegEx_final_state']   = list()
    
    # Inserindo transições lambda entre o novo estado inicial/final
    # e os antigos estados iniciais/finais
    for state in initial_states:
        delta['RegEx_initial_state'][state] = ''

    for state in final_states:
        delta[state]['RegEx_final_state'] = ''

    # Atualizando lista de pais de cada estado
    parent['RegEx_initial_state'] = list()
    parent['RegEx_final_state']   = final_states
    for state in initial_states:
        parent[state].append('RegEx_initial_state')

    # Convertendo transições para expressões regulares, utilizando parênteses quando necessário
    # para evitar possíveis ambiguidades na expressão
    for src in states:
        for dest in delta[src]:
            if has_transition(delta, src, dest):
                delta[src][dest] = apply_parentheses('+'.join(delta[src][dest]))


    # ------ ALGORITMO DE ELIMINAÇÃO DE ESTADOS ------ #
    for state in states:
        for (e1, e, e2) in get_paths(state, delta, parent):
            # Construíndo a expressão regular equivalente ao caminho e1 -> e -> e2
            regex = delta[e1][e]
            if has_transition(delta, e, e):
                regex += apply_parentheses(delta[e][e]) + '*'
            regex += delta[e][e2]

            # Adicionando transição do estado e1 para e2
            if has_transition(delta, e1, e2):
                delta[e1][e2] = apply_parentheses(delta[e1][e2] + '+' + regex)
            else:
                delta[e1][e2] = regex

            # Atualizando lista de pais
            if e in parent[e2]:
                parent[e2].remove(e)

            if e1 != e2 and e1 not in parent[e2]:
                parent[e2].append(e1)

    print(delta['RegEx_initial_state']['RegEx_final_state'])