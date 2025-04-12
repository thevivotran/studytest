I want to develop python webapp that can run in every users local machine. the app is packaged in a container, so everyone will be able to docker up it (or podman up it). the app can be writen in django or flask, or what ever framework that easy to maintain in the future.

the webapp's name is "Flashcard", this is a flashcard app. this app will have a database (sqlite3). this database stores questions, answers and correct answer of the question. each question has only 1 correct answer. the database will be initiated at every first run. at first, user will provide a csv file that have 7 columns and a name for the dataset:
- question
- correct answer
- answer choice 1
- answer choice 2
- answer choice 3
- answer choice 4
- answer choice 5 (optional)

when successfuly inject data into sqlite3 database, user will be able to choose between dataset to learn. after selecting a desired dataset, user will be moved to a flashcards feature. 

in the flashcards feature, user will be able to go through all the questions by swiping the flashcard. at each flashcard, user will always see the question and 4 (or 5) answers will be listed out at first, when tap to the flashcard, the correct answer will be showed.

in the flashcards feature, the learning progress will be cached for each dataset. whenever user choose the dataset to learn, the flashcards will resume at the last learning.

in the flashcards feature, user will be able to get back to the choose dataset page.