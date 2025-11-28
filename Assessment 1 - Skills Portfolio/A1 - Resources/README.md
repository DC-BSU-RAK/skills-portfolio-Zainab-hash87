# Exercise 1 - Maths Quiz

Develop a GUI using Tkinter that presents the user with quiz of arithmetic problems. Each "play" of the quiz should be 10 questions. The user should initially be presented with a short menu of options to select a difficulty level. It could look something like this:

    DIFFICULTY LEVEL
     1. Easy
     2. Moderate
     3. Advanced

The difficulty levels determine the number of digits in the numbers to be added or subtracted. Easy means only single digit numbers; moderate means double digit numbers; and advanced means 4-digit numbers. After the user picks the level they desire, your program presents problems that look like this:

    45 + 9 =
    34 - 88 =
    etc

For each problem presented, the user is given a chance to answer. If the answer is correct, another problem is presented. If the answer is wrong, the user is to be given one more chance at that problem. The program should keep a tally of the users score, awarding 10 points for a correct answer on first attempt and 5 points on the second attempt. You should implement a random number generator (see the resources folder) to determine:
- The values to be added or subtracted
- Whether the problem is addition or subtraction

&nbsp;
The program should include the functions listed below. These functions should make use of parameters and return values as appropriate. You may include others or extend the functionality of the program if you see fit.
- **displayMenu**: A function that displays the difficulty level menu at the beginning of the quiz.
- **randomInt**: A function that determines the values used in each question. The min and max values of the numbers should be based on the difficulty level chosen as described above.
- **decideOperation**: A function that randomly decides whether the problem is an addition or subtraction problem and returns a char.
- displayProblem: A function that displays the question to the user and accepts their answer.
-** isCorrect**: A function that checks whether the users answer was correct and outputs an appropriate message
- **displayResults**: function that outputs the users final score out of a possible 100 and ranks the user based on their score (e.g. A+ for a score over 90)

&nbsp;
Once the user has finished the quiz, prompt them to see if they'd like to play it again

&nbsp;
**HINT :**
- Use Labels to display questions and instructions.
- Use Entry widgets to accept answers.
- Use Buttons for submitting answers, selecting difficulty, and replaying.
- Use Label/messagebox to display results or feedback messages.

# Exercise 2 - Alexa tell me a Joke

The randomJokes.txt file in the resources folder contains a dataset of random jokes. Each joke is on a new line and consists of a setup and punchline separated by a question mark. For example:

    - Why did the chicken cross the road?To get to the other side.
    - What happens if you boil a clown?You get a laughing stock.
  
Develop a Tkinter GUI application that acts like a joke-telling assistant. The program should:

- Display a window with a button labeled "Alexa tell me a Joke".
- When the button is clicked, randomly select a joke from the randomJokes.txt file, display the setup of the joke in a label.
- Provide another button labeled "Show Punchline"- When clicked, display the punchline below the setup.
- Include a "Next Joke" button so the user can request another random joke.
- Additionally , provide a "Quit" button to close the application.

&nbsp;
# Exercise 3 - Student Manager

A list of student marks are held in the studentMarks.txt file available in the resources folder. These need to be loaded into a program to analyse the data. The first line is a single integer that gives the number of students in the class. Each subsequent line of the file comprises a student code (between 1000 and 9999), three course marks (each out of 20) and an examination mark (out of 100).

There is one line of data for each student in the class, with each piece of data separated by a comma (see example below).

8439,Jake Hobbs,10,11,10,43

Your task is to create a Tkinter GUI App that enables the user to manage this data. As a minimum expectation your app should include the following menu and use appropriate programming techniques to handle the functionality required by each menu item.


    1. View all student records
    2. View individual student record
    3. Show student with highest total score
    4. Show student with lowest total score

Below are the expectations for each menu item:


                
### 1. View all student records:
The program should output the following information for each student:
- Students Name
- Students Number
- Total coursework mark
- Exam Mark
- Overall percentage (coursework and examination marks contributing in direct proportion to the marks available i.e. the percentage is based on the potential total of 160 marks).
- Student grade ( ‘A’ for 70%+, ‘B’ for 60%-69%, ‘C’ for 50%-59%, ‘D’ for 40%-49%, ‘F’ for under 40% )

&nbsp;Once all students have been output you should also output a summary stating the number of students in the class and the average percentage mark obtained.


### 2. View individual student record
Allow the user to select a student then output their results as per menu item 1.
How you enable the user to select the individual student is up to you, this could be done via a menu code, or by allowing the user to enter a students name and/or student number.
### 3. Show student with highest overall mark
Identify the student with the highest mark and output their results in same format as menu item 1.
### 4. Show student with lowest overall mark
Identify the student with the lowest mark and output their results in same format as menu item 1.


&nbsp;
# Student Manager - Extension Problem 

&nbsp;For an additional challenge add the following options to your menu
    
    5. Sort student records
    6. Add a student record
    7. Delete a student record
    8. Update a students record
    
### 5. Sort student records
Allow the user to sort the student records in ascending or descending order then output in the same format as menu item 1.
### 6. Add a student record
Add a student with all the required information.
### 7. Delete a student record
Allow the user to select a student by name and/or student code and delete their record from the file.
### 8. Update a students record
Allow the user to select a student by name and/or student code and update their records. You may wish to present a sub-menu so the user can pick which item they wish to update.

&nbsp;Edits made by menu items 6, 7 and 8 need to be reflected in the “studentMarks.txt” file.
