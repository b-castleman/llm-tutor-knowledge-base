import openai
import json
import os


import logging
from pathlib import Path

logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
logging.getLogger("haystack").setLevel(logging.INFO)

# You will need pip install 'farm-haystack[all]' to obtain Haystack dependencies; this will take a couple of minutes.
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.utils import fetch_archive_from_http, print_answers, launch_es
from haystack.nodes import FARMReader, BM25Retriever
from haystack.nodes.file_classifier import FileTypeClassifier
from haystack.nodes.preprocessor import PreProcessor
from haystack.nodes.file_converter import TextConverter
from haystack.pipelines import Pipeline


class Tutor:
    ''' Define the intelligent tutor and its aspects'''
    def __init__(self, API_KEY: str = None, studentName: str = None, lessonSubject: str = None, model: int = None, topicsInformationIncluded: bool = False, lectureMaterialIncluded: bool = False):
        ''' OpenAI API Key '''
        # Saves API key, if present
        if API_KEY is None:
            raise Exception("No Open AI API key is present")
        else:
            openai.api_key = API_KEY

        ''' Model Number (3 or 4)  '''
        if model not in {3,4}:
            raise Exception("Bad model number")
        elif model == 3:
            self.model = "gpt-3.5-turbo"
        elif model == 4:
            self.model = "gpt-4-0314"


        ''' Knowledge Base Depth Parameters '''
        # Saves lesson subject, if present
        if lessonSubject is None:
            raise Exception("No lesson subject is present")
        else:
            self.lessonSubject = lessonSubject


        ''' Student Name '''
        # Saves student name, if present
        if studentName is None:
            raise Exception("No student name is present")
        else:
            self.studentName = studentName

        # If True, allows the topicsList.json file to be read (where subtopic information should exist)
        self.topicsListIncluded = topicsInformationIncluded

        # If True, allows the topicsInformationList.json file to be read (where subtopic descriptions should exist)
        self.topicsInformationIncluded = topicsInformationIncluded

        # If True, allows the lectureMaterial.json file to be read (where lecture information is taken)
        self.lectureMaterialIncluded = lectureMaterialIncluded


        # Checks to ensure the subtopics list is reflected correctly in the lectureMaterial.txt file
        self.supervisorFileReading()


        ''' Keywords File Creation & Lecture Material Processing'''
        self.createKeywordsFile()

        ''' Haystack Initialization '''
        self.haystackInitialization()
        print("Done!")


    ''' Read the supervisor files given '''
    def supervisorFileReading(self):
        ''' Read supervisor files and extract information from them '''


        ''' Create placeholders for potential information '''
        self.topicEncodings = None
        self.topicsList = None
        self.lectureMaterial = None
        self.predefinedQuestions = None

        ''' Extract necessary information '''
        if self.topicsListIncluded:
            self.topicsList = self.jsonToDict('topicsList.json')
            self.topicEncodings = list(self.topicsList.keys())

        if self.topicsInformationIncluded:
            self.topicsInformation = self.jsonToDict('topicsInformationList.json')

        if self.lectureMaterialIncluded:
            self.lectureMaterial = self.jsonToDict('lectureMaterial.json')


        ''' Ensure proper formatting '''
        if self.topicsListIncluded:
            for encoding in self.topicEncodings:
                if self.topicsInformationIncluded and encoding not in self.topicsInformation:
                    raise Exception('Encoding "' + encoding + '" is not present in topicsInformationList.json file.')

                if self.lectureMaterialIncluded and encoding not in self.lectureMaterial:
                    raise Exception('Encoding "' + encoding + '" is not present in lectureMaterial.json file.')


    ''' Convert a json file from the Supervisor folder into a dict '''
    def jsonToDict(self,fn: str = None):
        if fn is None:
            return None

        # Convert the json file into a dictionary
        fh = open("./SupervisorFiles/" + fn)
        outputDict = json.load(fh)
        fh.close()

        return outputDict


    ''' Create the main tutor prompt used '''
    def createMainTutorPrompt(self):
        ''' Creates a learning stage/quizzing stage prompt '''

        # Option 1: nothing given but the overall subject
        learningStagePrompt = 'You are a teacher named Athena, whose goal is to teach a student (named ' + self.studentName + ') about the lesson subject: "' + self.lessonSubject + '". You should accurately and enthusiastically answer all questions or clarifications that the student has.'

        # Option 2: additionally given a topics list
        if self.topicsListIncluded and not self.lectureMaterialIncluded:
            learningStagePrompt = learningStagePrompt + '\nSpecifically, topics on this subject you are teaching include: '

            # Add in all topics
            for encoding in self.topicEncodings:
                learningStagePrompt = learningStagePrompt + ' "' + self.topicsList[encoding] + '",'
            learningStagePrompt = learningStagePrompt[:-1] + '.'

        # Option 3: additionally given details/background about each topic
        if self.topicsInformationIncluded and not self.lectureMaterialIncluded:
            # Add in all topics
            for encoding in self.topicEncodings:
                learningStagePrompt = learningStagePrompt + '\nThe topic titled "' + self.topicsList[encoding] + '" has the description: "' + self.topicsInformation[encoding] + '".'

        return learningStagePrompt

    def gptResponse(self,concatenatedConversation = None):
        ''' Returns a GPT generated response to the given conversation '''

        if concatenatedConversation is None:
            return None

        completedConversation = openai.ChatCompletion.create(model=self.model, messages=concatenatedConversation)

        return completedConversation['choices'][0]['message']['content'].replace("\n"," ")


    ''' Create questions about the lecture material '''
    def questionCreator(self):
        # if no lecture material, error!
        if not self.lectureMaterialIncluded:
            raise Exception("No lecture material is included! This cannot occur!")

        mainPrompt = self.createMainTutorPrompt()

        questionCount = "three"

        for encoding in self.topicEncodings:
            for subtopic in self.lectureMaterial[encoding]:
                gptQuery = [{'role': 'system', 'content': mainPrompt},
                            {'role': 'user',
                             'content': f"Please create " + questionCount + ", difficult questions within the subtopic, " + subtopic["name"] + ", within the topic " + self.topicsList[encoding] + " about the lecture material. All questions choosen should be of the type, ""select all that apply"". The questions may ONLY pertain to the following lecture material: \n\n" + subtopic["information"]},
                            ]

                gptResponse = self.gptResponse(gptQuery)

                print("For subtopic " + subtopic["name"] + ", here are the questions generated: ")
                print(gptResponse)
                print("\n\n")


    ''' The answer rating function. This is the only function needed to be ran by the programmer in order to have an intelligent assess a question-answer pair'''
    def answerRating(self,question,answer):
        # Part 1: the internal ranking
        ranking_prompt = 'You are a ranking system. You will be given a conversation between a teacher (named Athena) and a student (named ' + self.studentName + ') about ' + self.lessonSubject + ', and then you will rank how accurate their response is.' #+ ' You will pay specific attention to the wording of each question and answer, as well as the semantics of each, in order to observe the accuracy of the response.'
        qaQuery = 'The question asked by the teacher was, "' + question + '".\nThe answer given by the student was, "' + answer + '".\n Based on the student''s response to the teacher''s question, rank the student''s response quality and accuracy on an integer scale from 1-5. Do not include any other words or tokens aside from my response quality.'

        ratingGptQuery = [{'role':'system','content':ranking_prompt},
                          {'role':'user','content':qaQuery}]

        # Add topic info, if relevant
        if self.topicsInformationIncluded and not self.lectureMaterialIncluded:
            topicAdditionalInfoPrompt = 'Information on this subject you are teaching include: '

            # Add in all topics
            for encoding in self.topicEncodings:
                topicAdditionalInfoPrompt = topicAdditionalInfoPrompt + ' "' + self.topicsList[encoding] + '",'
            topicAdditionalInfoPrompt = topicAdditionalInfoPrompt[:-1] + '.'

            topicInfoAddition = {'role':'system',
                                 'content': topicAdditionalInfoPrompt}
            ratingGptQuery.insert(1,topicInfoAddition)

        finalAdditionList = self.haystackLectureMaterialConcatenationForCustomQuestionTest(question, answer)

        for i in range(len(finalAdditionList)):
            ratingGptQuery.insert(len(ratingGptQuery) - 1,finalAdditionList[i])  # always add the information right before the question/answer to rate

        ratingGptResponse = self.gptResponse(ratingGptQuery)

        rating = None
        if "5" in ratingGptResponse or "five" in ratingGptResponse:
            rating = 5
        elif "4" in ratingGptResponse or "four" in ratingGptResponse:
            rating = 4
        elif "3" in ratingGptResponse or "three" in ratingGptResponse:
            rating = 3
        elif "2" in ratingGptResponse or "two" in ratingGptResponse:
            rating = 2
        elif "1" in ratingGptResponse or "one" in ratingGptResponse:
            rating = 1

        if rating is None:
            raise Exception("GPT Response did not contain a number. The output was:" + ratingGptResponse)


        # Part 2: the response to the student
        mainPrompt = self.createMainTutorPrompt()

        gptQuery = [{'role': 'system', 'content': mainPrompt},
                    {'role': 'assistant', 'content': 'I will now proceed you quiz you.\n\nCheck all that apply: ' + question},
                    {'role': 'user', 'content': answer},
                    {'role': 'system',
                     'content': 'Please proceed to respond to the student''s answer. A third party rating of the student''s answer was a ' + str(rating) + '/5. Explain what about the answer was accurate or inaccurate as well as what can use improvement for a more complete knowledge, helping clear any misconceptions. Please use less than 75 words in this response.'}]

        # Use the last final addition list since it's the same
        for i in range(len(finalAdditionList)):
            gptQuery.insert(len(gptQuery)-3,finalAdditionList[i]) # always add the information right before the question/answer


        gptResponse = self.gptResponse(gptQuery)

        print("Athena: " + gptResponse)


    ''' Concatenate information from the lecture material (if full KB is on) to the GPT request'''
    def lectureMaterialConcatenationForCustomQuestionTest(self,question,answer):
        ''' Keyword detection to see if any lecture material should be concatenated to the GPT request '''
        # If lecture material concatenation is off, just return an empty list
        if not self.lectureMaterialIncluded:
            return []

        # Define output information to append
        relatedInformation = []

        # Set of lines to add
        addSet = set()

        # Attach any relevant keyword to the list
        i = 0
        for encoding in self.topicEncodings:
            for subtopic in self.lectureMaterial[encoding]:
                i += 1
                for keyword in subtopic["keywords"]:
                    if keyword.lower() in question.lower():
                        addSet.add(i)

        i = 0
        for encoding in self.topicEncodings:
            for subtopic in self.lectureMaterial[encoding]:
                i += 1
                for keyword in subtopic["keywords"]:
                    if keyword.lower() in answer.lower():
                        addSet.add(i)

        i = 0
        for encoding in self.topicEncodings:
            for subtopic in self.lectureMaterial[encoding]:
                i += 1
                if i in addSet:
                    relatedInformation.append({"role": "system", "content": ('Please note the following lecture material that may be related to this topic: "' + subtopic["information"] + '".')})
                    break

        # Return back the updated conversation
        return relatedInformation


    ''' Create a file of all the generated keywords, if one does not exist. If you are changing the lecture material attached, please regenerate this file by deleting the old one.'''
    def createKeywordsFile(self):
        if not self.lectureMaterialIncluded:
            return

        outFilePath = "./SupervisorFiles/generatedKeywords.json"
        if os.path.exists(outFilePath):
            self.createLectureInformationParseFile()
            return

        generatedKeywords = dict()

        for encoding in self.topicEncodings:
            generatedKeywords[encoding] = dict()
            for subtopic in self.lectureMaterial[encoding]:
                generatedKeywords[encoding][subtopic["name"]] = self.createKeywordsFromInformation(encoding,subtopic["name"],subtopic["information"])

        # Create file
        with open(outFilePath, "w") as outfile:
            json.dump(generatedKeywords, outfile)

        self.createLectureInformationParseFile()

    ''' Generate keywords for the specific subtopic given by the createKeywordsFile() method.'''
    def createKeywordsFromInformation(self,encoding,name,information):
            background = "You are a keyword generator. Your job is to generate keywords that students might use about certain topics when discussing them so that information can be retrieved."
            prompt = 'You are creating information about the subtopic called "' + name + '", a subtopic of the topic "' + self.topicsList[encoding] + '", which is a part of the lesson subject "' + self.lessonSubject + '". Keywords should be outputted in the format [<keyword 1>, <keyword 2>,...]. Nothing else should be outputted. Please create an exhaustive keyword list for the following lecture material:\n\n' + information

            gptQuery = [{'role':'system','content':background},
                        {'role':'user','content':prompt}]

            gptResponse = self.gptResponse(gptQuery)

            bracketStart = gptResponse.find('[')
            bracketEnd = gptResponse.find(']')
            substring = gptResponse[bracketStart + 1:bracketEnd]
            keywordList = substring.split(',')
            for i in range(len(keywordList)):
                keywordList[i] = keywordList[i].strip().lower()

            return keywordList


    ''' Create the actual lecture information file that Haystack will iterate through. This includes the keywords and the lecture material. '''
    def createLectureInformationParseFile(self):
        keywordFile = "generatedKeywords.json"
        outFilePath = "./HaystackSearch/processedLectureMaterial.txt"
        outMappingPath = "./SupervisorFiles/lineToInformation.json"
        outMapping = dict()

        generatedKeywords = self.jsonToDict(keywordFile)
        with open(outFilePath, 'w') as fh:
            lineNumber = 1
            for encoding in self.topicEncodings:
                for subtopic in self.lectureMaterial[encoding]:
                    curKeywords = generatedKeywords[encoding][subtopic["name"]]

                    fh.write("\tTopic Name: " + subtopic["name"] + ".")

                    fh.write("\tTopic Keywords: [")
                    for keyword in curKeywords:
                        fh.write(keyword + ", ")
                    fh.write("].\t")

                    fh.write("Topic Information: " + subtopic["information"])

                    outMapping[lineNumber] = subtopic["information"]

                    fh.write('\n')
                    lineNumber+=1

        with open(outMappingPath, "w") as outfile:
            json.dump(outMapping, outfile)


    ''' Initializes Haystack from the Tutor Constructor. This code is adapted from https://github.com/deepset-ai/haystack/blob/main/examples/basic_qa_pipeline.py '''
    def haystackInitialization(self):
        if not self.lectureMaterialIncluded:
            return

        print("Initializing Haystack...")

        # Launch Elastic Search
        launch_es()

        document_store = ElasticsearchDocumentStore(host="localhost", username="", password="", index="document")
        document_store.delete_documents()  # remove unrelated documents that were processed earlier

        # fetch, pre-process and write documents
        doc_dir = "./HaystackSearch/"
        file_paths = [p for p in Path(doc_dir).glob("**/*")]
        files_metadata = [{"name": 'processedLectureMaterial.txt'}]  # fore ach file

        # Indexing Pipeline
        indexing_pipeline = Pipeline()

        # Makes sure the file is a TXT file (FileTypeClassifier node)
        classifier = FileTypeClassifier()
        indexing_pipeline.add_node(classifier, name="Classifier", inputs=["File"])

        # Converts a file into text and performs basic cleaning (TextConverter node)
        text_converter = TextConverter(remove_numeric_tables=True)
        indexing_pipeline.add_node(text_converter, name="Text_converter", inputs=["Classifier.output_1"])

        # - Pre-processes the text by performing splits and adding metadata to the text (Preprocessor node)
        preprocessor = PreProcessor(
            clean_whitespace=True,
            clean_empty_lines=True,
            split_length=100,
            split_overlap=50,
            split_respect_sentence_boundary=True,
        )
        indexing_pipeline.add_node(preprocessor, name="Preprocessor", inputs=["Text_converter"])

        # - Writes the resulting documents into the document store
        indexing_pipeline.add_node(document_store, name="Document_Store", inputs=["Preprocessor"])

        # Then we run it with the documents and their metadata as input
        indexing_pipeline.run(file_paths=file_paths, meta=files_metadata)

        # Initialize Retriever & Reader
        retriever = BM25Retriever(document_store=document_store)
        reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True)

        # Query Pipeline
        pipeline = Pipeline()
        pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
        pipeline.add_node(component=reader, name="Reader", inputs=["Retriever"])

        self.pipeline = pipeline

    ''' Given a list of strings from the tutor (i..e the question and the answer), return the relevant lecture material. This is the overarching function that determines lecture material inclusion. Please note it calls all the functions that are defined below to accomplish its task. '''
    def stringListToInformationHaystack(self,strList):
        ''' From a list of strings, outputs all lines of relevant informaton determined by Haystack '''
        file_path = './HaystackSearch/processedLectureMaterial.txt'

        lineSet = set()
        for query in strList:
            try:
                prediction = self.pipeline.run(
                    query=query, params={"top_k": 3}
                )
            except:
                prediction = self.pipeline.run(
                    query=query, params={"top_k": 4}
                )
            for lineNum in self.obtainLineNumber(prediction):
                lineSet.add(lineNum)


        # Line number -> information
        outInformation = []
        linesToAdd = list(lineSet)
        linesToAdd.sort()
        lineToInformation = self.jsonToDict("lineToInformation.json")
        for line in linesToAdd:
            outInformation.append(lineToInformation[str(line)])

        return outInformation


   ''' Return the line numbers for the information that Haystack finds relevant. It takes this information in as an input. Multiple lines may be found as a result of the implementation. '''
    def findLineNumber(self, context: str):
        file_path = './HaystackSearch/processedLectureMaterial.txt'
        with open(file_path, 'r') as file:
            lines = file.readlines()
        ls = []
        for index, line in enumerate(lines):
            if context in line:
                ls.append(1 + index)

        return ls

    ''' Multiple outputs are likely to be given by Haystack. As a result, we choose to use every output to concatenate the relevant information and feed it all back for GPT concatenation.'''
    def obtainLineNumber(self,prediction):
        answers = prediction["answers"]
        outLineNumberList = []

        for answer in answers:
            outLineNumberList.extend(self.findLineNumber(answer.context))

        return outLineNumberList


    ''' Given the question and answer, yields all relevant information in a format ready for GPT concatenation '''
    def haystackLectureMaterialConcatenationForCustomQuestionTest(self,question,answer):
        ''' Keyword detection to see if any lecture material should be concatenated to the GPT request '''
        # If lecture material concatenation is off, just return an empty list
        if not self.lectureMaterialIncluded:
            return []

        # Define output information to append

        outAdditions = []
        try:
            relatedInformation = self.stringListToInformationHaystack([question,answer])
        except: # If there's a pop error, concatenate the information together so that there's a greater chance of something being found
            relatedInformation = self.stringListToInformationHaystack([question + answer])

        for i in range(len(relatedInformation)):
            outAdditions.append({"role": "system", "content": ('Please note the following lecture material that may be related to this topic: "' + relatedInformation[i] + '".')})

        # Return back the updated conversation
        return outAdditions












