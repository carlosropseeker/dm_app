from collections import defaultdict

def filter_responses(response, c1, c2):
    if(response['choiceOne'] == c1) & (response['choiceTwo'] == c2):
        return True
    else:
        return False

def get_priorities(matrix):
    subm = elevate_matrix(matrix, 10)
    sum_array = [sum(row) for row in subm]
    priorities = [elem/sum(sum_array) for elem in sum_array]
    return priorities

def elevate_matrix(matrix, power):
    iteration = 0
    toret = matrix
    while(iteration < power):
        toret = matrix_multiplication(toret, matrix)
        iteration = iteration + 1
    return toret

def matrix_multiplication(m1, m2):
    result = [[0 for _ in range(len(m1))] for _ in range(len(m2[0]))]
    for i in range(len(m1)):
        for j in range(len(m2[0])):
            for k in range(len(m2)):
                result[i][j] += m1[i][k] * m2[k][j]
    return result

def gen_matrix(factors, responses):
    matrix = [[0 for _ in range(len(factors))] for _ in range(len(factors))]
    for i, row in enumerate(factors):
        for j, col in enumerate(factors):
            if i == j:
                matrix[i][j] = 1
            else:
                answer = list(
                    filter(lambda x: filter_responses(x, row, col), responses))
                if len(answer) == 1:
                    answer = answer[0]
                    if answer['value'] < 0:
                        matrix[j][i] = abs(answer['value']) + 1
                        matrix[i][j] = 1/(abs(answer['value']) + 1)
                    elif answer['value'] == 0:
                        matrix[j][i] = 1
                        matrix[i][j] = 1
                    else:
                        matrix[j][i] = 1/(answer['value'] + 1)
                        matrix[i][j] = answer['value'] + 1
    return matrix


def calculate_random_consistency_index(n):
    cr = {
        1: 0.00001,
        2: 0.001,
        3: 0.58,
        4: 0.9,
        5: 1.12,
        6: 1.24,
        7: 1.32,
        8: 1.41,
        9: 1.45,
        10: 1.49
    }
    return cr.get(n)


def calculate_consistency_index(matrix, priorities):
    eigen = sum(get_eigen(matrix, priorities))
    n = len(matrix)
    return (eigen-n)/(n-1)


def calculate_consistency_ratio(ci, cr):
    return ci/cr


def get_eigen(matrix, priorities):
    toret = [sum(map(lambda x: x[i], matrix)) * priorities[i]
             for i in range(len(matrix))]
    return toret


def get_explode(priorities):
    explode = [0, 0, 0, 0]  # only "explode" the 2nd slice (i.e. 'Hogs')
    explode[priorities.index(max(priorities))] = 0.2
    return explode


def add_prior_by_attribute(factors, resp):
    result = {}
    for att in factors:
        toret = {}
        fact = list(filter(lambda y: y[0] == att,sum(map(lambda x: x['values'], resp), [])))
        rank = list(map(lambda x: x[1], fact))
        priorities = get_attribute_submatrix(
            data=rank)
        for index, action in enumerate(list(map(lambda x: x['alternative'],resp))):
            toret[action] = priorities[index]
        result[att] = toret
    return result


def filter_ranking(rank, att, user):
    split = rank['sk'].split('#')
    return ((split[2] == att) & (split[1] == user))


def get_attribute_submatrix(data, inverse=False):
    x = [elem + 0.0001 if elem == 0 else elem for elem in data]
    toret = []
    for col in x:
        if not inverse:
            column = [col/row for row in x]
        else:
            column = [row/col for row in x]
        toret.append(column)
    return get_priorities(toret)


def add_endpoint_prior_by_action(result, factors,  priorities):
    weights = {f:p for f,p in zip(factors, priorities)}
    result['priorities'] = defaultdict(list)
    for key in factors:
        data = result[key]
        weights_values = weights[key]
        for action in data.keys():
            result['priorities'][action].append({
                key: weights_values * data.get(action)
            })
    return result


def add_weights(result):
    result['weights'] = {}
    for action in list(result['priorities']):
        result['weights'][action] = sum(
            map(lambda x: list(x.values())[0], list(result['priorities'][action])))
    return result