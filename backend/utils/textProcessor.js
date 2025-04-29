const natural = require('natural');
const stopwords = require('natural').stopwords;
const stemmer = natural.PorterStemmer;

exports.preprocessText = (text) => {
  // Convert to lowercase
  text = text.toLowerCase();
  
  // Remove special characters and numbers
  text = text.replace(/[^a-zA-Z\s]/g, '');
  
  // Tokenize
  const tokenizer = new natural.WordTokenizer();
  let tokens = tokenizer.tokenize(text);
  
  // Remove stopwords
  tokens = tokens.filter(token => !stopwords.includes(token));
  
  // Stemming
  tokens = tokens.map(token => stemmer.stem(token));
  
  return tokens.join(' ');
};