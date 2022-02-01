import json
import re


def process_result(guess, result, excluded, included, fixed):
    for i, (letter, result) in enumerate(zip(guess, result)):
        if result == '_':
            excluded.add(letter)
        elif result == 'y':
            # Only add if not in fixed set
            if letter not in [f[1] for f in fixed]:
                included.add(letter)
        elif result == 'g':
            fixed.add((i, letter))
            # Remove from included if there
            if letter in included:
                included.remove(letter)
        else:
            raise ValueError(f'dafuq is {result}? I said [_yg] only!')

    print(f'Excluded: {", ".join(sorted(excluded))}')
    print(f'Included: {", ".join(sorted(included))}')
    print(f'Fixed: {fixed}')

    return excluded, included, fixed


def has_chars(word, char_list):
    exp = re.compile("|".join(char_list))
    return re.search(exp, word) is not None


def has_all_chars(word, char_list):
    return all([c in word for c in char_list])


def fixed_match(word, fixed_chars):
    # Accepts iterable of (pos, chr) tuples and verifies the word has each one in position
    for pos, char in fixed_chars:
        if word[pos] != char:
            return False

    return True


def filter_answers(answers, excluded, included, fixed):
    # Filter answers by excluded characters
    answers = [a for a in answers if not has_chars(a, excluded)]
    print(len(answers), answers)

    # Filter answers by fixed position characters
    answers = [a for a in answers if fixed_match(a, fixed)]
    print(len(answers), answers)

    # Filter answers by included characters
    answers = [a for a in answers if has_all_chars(a, included)]
    print(len(answers), answers)

    return answers


def get_result(guess, answer):
    guess = list(guess.lower())
    answer = list(answer.lower())

    # Default to grey
    result = ['_'] * len(guess)

    # Check for greens first and reserve that index so it can't be yellow
    for x in range(len(guess)):
        if guess[x] == answer[x]:
            result[x] = 'g'
            guess[x] = '_'
            answer[x] = '_'

    # Check for yellows
    for x in range(len(guess)):
        if guess[x] != '_':
            if guess[x] in answer:
                result[x] = 'y'
                answer[answer.index(guess[x])] = '_'

    return ''.join(result)


def get_best_guess(answers):
    with open('guess_words.json', 'r') as f:
        guesses = json.load(f)

    score = [-1] * len(guesses)
    for i, guess in enumerate(guesses):
        possible_constellations = set()

        for answer in answers:
            possible_constellations.add(get_result(guess, answer))

        score[i] = len(possible_constellations)

    max_score = max(score)

    # Check if any of the remaining answers match the max score, if so suggest them
    max_score_answers = [a for a in answers if score[guesses.index(a)] == max_score]

    if max_score_answers:
        return max_score_answers
    else:
        return guesses[score.index(max(score))]


def run_algo():
    with open('answers.json', 'r') as f:
        answers = json.load(f)

    excluded = set()
    included = set()
    fixed = set()

    # Best first word is always 'TRACE' - you can validate it with get_best_guess() on the entire answer list
    guess = 'trace'
    result = input(f'Enter result for `{guess.upper()}` [_yg]: ').lower()
    excluded, included, fixed = process_result(guess, result, excluded, included, fixed)
    answers = filter_answers(answers, excluded, included, fixed)

    while 1:
        if len(answers) == 1:
            print(f'Final answer: {answers[0]}')
            break

        guess = get_best_guess(answers)
        if isinstance(guess, list):
            print(f'Guess any of the following: {guess}')
            guess = input('What word did you use? ')

        result = input(f'Enter result for `{guess.upper()}` [_yg]: ').lower()
        excluded, included, fixed = process_result(guess, result, excluded, included, fixed)
        answers = filter_answers(answers, excluded, included, fixed)


if __name__ == '__main__':
    run_algo()

