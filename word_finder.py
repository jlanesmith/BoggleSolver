from typing import List, Set
import nltk
from nltk.corpus import words
from nltk.corpus import brown
def find_boggle_words(grid):

    # TODO: Find a better dictionary
    # nltk.download('words')
    nltk.download('brown')
    # # Get the most common words
    word_freq = nltk.FreqDist(brown.words())
    simple_words = [word for word, freq in word_freq.most_common(200000)]

    dictionary = set(words.words())
    # dictionary = set(simple_words)
    print("Dictionary length: ", len(dictionary))

    def is_valid_word(word: str) -> bool:
        """Check if a word is in the dictionary."""
        return word in dictionary

    def has_prefix(prefix: str) -> bool:
        """Check if there are any words in the dictionary that start with the given prefix."""
        return any(word.startswith(prefix) for word in dictionary)

    def dfs(x: int, y: int, visited: Set[tuple], current_word: str):
        """Perform DFS to find all words starting from a cell."""
        # Add the current letter to the word
        letter_to_add = "qu" if grid[x][y].lower() == "q" else grid[x][y].lower()
        current_word += letter_to_add

        # If the prefix is invalid, stop searching
        if not has_prefix(current_word):
            return

        # Check if the current word is valid
        if is_valid_word(current_word):
            found_words.add(current_word)

        # Explore neighbors
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 5 and 0 <= ny < 5 and (nx, ny) not in visited:
                visited.add((nx, ny))
                dfs(nx, ny, visited, current_word)
                visited.remove((nx, ny))

    # Initialize variables
    found_words = set()
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Start DFS from each cell in the grid
    for i in range(5):
        for j in range(5):
            dfs(i, j, {(i, j)}, "")
            print(f"Checking index {i},{j}")

    print(sorted(found_words, key=lambda word: (-len(word), word)))
    # Return sorted words by length (longest first) and alphabetically for ties
    return sorted(found_words, key=lambda word: (-len(word), word))


