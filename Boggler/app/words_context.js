import React, { createContext, useState, useContext } from 'react';

// Create a context for the words
const WordsContext = createContext();

// Create a provider component to manage the state
export const WordsProvider = ({ children }) => {
  const [words, setWords] = useState([]); // State to hold the list of words

  return (
    <WordsContext.Provider value={{ words, setWords }}>
      {children}
    </WordsContext.Provider>
  );
};

// Create a custom hook to use the WordsContext easily
export const useWords = () => useContext(WordsContext);
