from Tutor import *
import time

# Obtain the OpenAI API key. Please place your Open AI API key in the '.\Tutor Architecture' directory in a file named API_KEY.txt for this to work. Or, just replace this code block with API_KEY = <your open AI API key>
with open('API_KEY.txt', 'r') as file:
    API_KEY = file.read()

# Obtain the student's name
studentName = "Blake"

# Obtain the subject being taught
lessonSubject = "History of AI"

# Define questions to parse
questionBank = [{'q':'What characteristics are shared by both biological and artificial neurons? a) They both have dendrites b) Both can aggregate and process input values c) They both have axons d) Both can transmit outputs depending on certain criteria',
                 'a':'A, C: biological neurons have these properties and artificial neurons try to mimic them'}]

# Define tutors
tutorNoKB = Tutor(API_KEY = API_KEY, studentName = studentName, lessonSubject = lessonSubject, model = 3, topicsInformationIncluded=False, lectureMaterialIncluded=False)
tutorPartialKB = Tutor(API_KEY = API_KEY, studentName = studentName, lessonSubject = lessonSubject, model = 3, topicsInformationIncluded=True, lectureMaterialIncluded=False)

# Ensure docker is running, otherwise the Haystack instantiation will run into an error
tutorWKB = Tutor(API_KEY = API_KEY, studentName = studentName, lessonSubject = lessonSubject, model = 3, topicsInformationIncluded=True, lectureMaterialIncluded=True)

# Iterate through questions & answers, then assess them
for i in range(len(questionBank)):
    time.sleep(15)
    print("\n\nNew Question: ")
    question = questionBank[i]["q"]
    answer = questionBank[i]["a"]

    print("Question:",question)
    print("Answer:",answer)
    print("\n")

    print("Without KB:")
    tutorNoKB.answerRating(question,answer)


    print("\nPartial KB")
    tutorPartialKB.answerRating(question,answer)


    print("\nFull KB:")
    tutorWKB.answerRating(question,answer)
