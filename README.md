# Separate Quiz Platform for progressive minds

### Added CI Workflow (Testing Runserver)

## REST API DOCUMENTATION

Documentation of our API endpoints starts here

## To create a quiz

### Request

`POST http://127.0.0.1:8000/api/create-quiz`

    {
        "title": "Quiz for documentation",
        "creator": 566,
        "starttime": "2020-03-16T00:00:00+05:30",
        "endtime": "2021-07-16T05:30:00+05:30",
        "duration": "00:45:00",
        "desc": "This quiz is being created solely for documentation purpose"
    }

### Response

    {
        "id": "1440a8a6-5a47-42b7-bd2a-88d4bbd84b70",
        "title": "Quiz for documentation",
        "creator": 566,
        "starttime": "2020-03-16T00:00:00+05:30",
        "endtime": "2021-07-16T05:30:00+05:30",
        "duration": "00:45:00",
        "desc": "This quiz is being created solely for documentation purpose"
    }

## To get a quiz

### Request

`GET http://127.0.0.1:8000/api/get-quiz/<slug:quiz_id>`

### Response

    {
    "quiz_details": {
        "id": "e58408d8-d1e5-42a7-a6f8-41f78ce88db7",
        "title": "Quiz for testing 4",
        "creator": 566,
        "starttime": "2020-03-16T00:00:00+05:30",
        "endtime": "2021-07-16T05:30:00+05:30",
        "duration": "00:45:00",
        "desc": "This quiz is being created solely for testing purpose"
    },
    "quiz_questions": [
        {
            "id": "5b54301e-ad1a-41f3-b123-d24445e5d603",
            "question": "<p>A road connecting two mountain</p>",
            "correct_marks": 6,
            "negative_marks": 3,
            "option": {
                "1": "Yes",
                "2": "No"
            },
            "answer": 1,
            "text": "",
            "subject_tag": "Mathematics",
            "topic_tag": "Algebra",
            "subtopic_tag": "Elementary Algebra",
            "dificulty_tag": "Easy",
            "skill": "Elementary Algebra"
        },
        {
            "id": "f423f295-ea08-4dd7-9a18-ab35c86c833c",
            "question": "<p>The Mumbai city Chess committee is organising a Chess</p>",
            "correct_marks": 6,
            "negative_marks": 2,
            "option": {},
            "answer": null,
            "text": "153",
            "subject_tag": "Mathematics",
            "topic_tag": "Combinatorics",
            "subtopic_tag": "Combinations",
            "dificulty_tag": "Easy",
            "skill": "Combinations"
        }
    ]
}
    
## To edit a quiz

### Request

`PUT http://127.0.0.1:8000/api/edit-quiz/<slug:quiz_id>`

    {
        "title": "Quiz for documentation(rename)",
        "creator": 566,
        "starttime": "2020-03-16T00:00:00+05:30",
        "endtime": "2021-07-16T05:30:00+05:30",
        "duration": "00:45:00",
        "desc": "This quiz is being created solely for documentation purpose(rename)"
    }

### Response

    {
        "id": "1440a8a6-5a47-42b7-bd2a-88d4bbd84b70",
        "title": "Quiz for documentation(rename)",
        "creator": 566,
        "starttime": "2020-03-16T00:00:00+05:30",
        "endtime": "2021-07-16T05:30:00+05:30",
        "duration": "00:45:00",
        "desc": "This quiz is being created solely for documentation purpose(rename)"
    }
    
## To delete a quiz

### Request

`DELETE http://127.0.0.1:8000/api/edit-quiz/<slug:quiz_id>`

### Response

    {
        "message": "Quiz deleted successfully"
    }

## To create a question

### Request

`POST http://127.0.0.1:8000/api/create-question`

    {
        "quiz": "1440a8a6-5a47-42b7-bd2a-88d4bbd84b70",
        "question": "what is 1+1",
        "option": [
            {
            "key":"1",
            "option":"1"
            },
            {
            "key":"2",
            "option":"2"
            }

        ],
        "correct_marks": "2",
        "negative_marks": "1",
        "answer": "2",
        "creator":1,
        "subject_tag": "Maths",
        "topic_tag": "Arithmetic",
        "subtopic_tag": "Algebra",
        "dificulty_tag": "Easy",
        "skill": "Parity"
    }
    
### Response

      `{
            "id": "a60a3844-24ba-4ce8-ba2f-0e0cd63b9181",
            "question": "what is 1+1",
            "correct_marks": 2,
            "negative_marks": 1,
            "option": [
                {
                    "key": 1,
                    "option": "1"
                },
                {
                    "key": 2,
                    "option": "2"
                }
            ],
            "answer": 2,
            "text": "",
            "subject_tag": "Maths",
            "topic_tag": "Arithmetic",
            "subtopic_tag": "Algebra",
            "dificulty_tag": "Easy",
            "skill": "Parity"
        }`

## To edit a question

### Request

`PUT http://127.0.0.1:8000/api/edit-question/<slug:question_id>`

     `{
        "quiz": "1440a8a6-5a47-42b7-bd2a-88d4bbd84b70",
        "question": "what is 1+1(rename)",
        "option": [
            {
            "key":"1",
            "option":"1"
            },
            {
            "key":"2",
            "option":"2"
            }
        ],
        "correct_marks": "4",
        "negative_marks": "1",
        "answer": "2",
        "creator":1,
        "subject_tag": "Maths",
        "topic_tag": "Arithmetic",
        "subtopic_tag": "Algebra",
        "dificulty_tag": "Easy"
    }`
  
### Response

    {
    "id": "a60a3844-24ba-4ce8-ba2f-0e0cd63b9181",
    "question": "what is 1+1(rename)",
    "correct_marks": 4,
    "negative_marks": 1,
    "option": [
        {
            "key": 1,
            "option": "1"
        },
        {
            "key": 2,
            "option": "2"
        }
    ],
    "answer": 2,
    "text": "",
    "subject_tag": "Maths",
    "topic_tag": "Arithmetic",
    "subtopic_tag": "Algebra",
    "dificulty_tag": "Easy",
    "skill": "Parity"
    }

## To delete a question

### Request

`DELETE http://127.0.0.1:8000/api/edit-question/<slug:question_id>`

### Response

    {
        "message": "Question deleted successfully"
    }

## To get student response

### Request

`GET http://127.0.0.1:8000/api/get-response/<slug:quiz_id>/<int:user_id>`

### Response

    {
        "id": 1,
        "response": "{'c8215cfc-0d4e-48a0-8b98-5a8f5827f018': '1', '2513e723-15ed-4777-9a00-19bf214ce97f': 'Abhinay'}",
        "marks": 1,
        "quiz": "994245ef-4a78-40d6-8dcf-c2f1dfdff74f",
        "user": 2
    }

## To create response

### Request

`POST http://127.0.0.1:8000/api/create-response`

    {
        "quiz": "24b3e35f-a0e2-45bb-9578-2e582e4ab0ce",
        "user": 2,
        "response": ""
    }

### Response

    {
        "id": 2,
        "response": "",
        "marks": 0,
        "quiz": "24b3e35f-a0e2-45bb-9578-2e582e4ab0ce",
        "user": 2
    }

## To get quiz marks

### Request

`GET http://127.0.0.1:8000/api/get-quiz-marks/<slug:quiz_id>/<int:user_id>`

### Response

 
    
## To add student

### Request

`POST http://127.0.0.1:8000/api/add-student`

### Response

    

## To get all quizzes

### Request

`GET http://127.0.0.1:8000/api/get-all-quizzes/<slug:userid>`

### Response

    [
        {
            "id": "96dd7e19-a309-4c19-9a85-e857a7b5ccb1",
            "title": "Quiz for testing 3",
            "creator": 566,
            "starttime": "2020-03-16T00:00:00+05:30",
            "endtime": "2021-06-16T05:30:00+05:30",
            "duration": "00:45:00",
            "desc": "This quiz is being created solely for testing purpose",
            "creator_username": "administrator"
        },
        {
            "id": "e58408d8-d1e5-42a7-a6f8-41f78ce88db7",
            "title": "Quiz for testing 4",
            "creator": 566,
            "starttime": "2020-03-16T00:00:00+05:30",
            "endtime": "2021-07-16T05:30:00+05:30",
            "duration": "00:45:00",
            "desc": "This quiz is being created solely for testing purpose",
            "creator_username": "administrator"
        }
    ]



## To post Feedback

### Request

`POST http://127.0.0.1:8000/api/postFeedback/`

    {
        "learn_new": 3,
        "like_participating": 3,
        "difficulty": 4,
        "participate_again": "yes",
        "time_sufficient": "yes",
        "attend_webinar": "yes",
        "language_english": "yes",
        "mini_course": "yes",
        "next_contest": "Puzzle Solving",
        "suggestions": "amazing work, add some esy questions too",
        "user": 77,
        "quiz_id": "5fc3d69c-26d1-420c-92b0-1c20e372fb88",
        "username":"abhishek-st"
    }

### Response

    {
        "id": "ebfdc10d-e24a-4da6-a688-a95adfc94414",
        "learn_new": 3,
        "like_participating": 3,
        "difficulty": 4,
        "participate_again": "yes",
        "time_sufficient": "yes",
        "attend_webinar": "yes",
        "language_english": "yes",
        "mini_course": "yes",
        "next_contest": "Puzzle Solving",
        "suggestions": "amazing work, add some esy questions too",
        "username": "abhishek-st",
        "user": 77,
        "quiz_id": "5fc3d69c-26d1-420c-92b0-1c20e372fb88"
    }
    
## To check quiz assigned

### Request

`POST http://127.0.0.1:8000/api/check-quiz-assigned`

    {
        "user":"440",
        "quiz":"4cbbbe73-c086-4e22-b4d7-efd0776dbb85"
    }
    
 ### Response 
     {
        "message": "You have already attempted the test"
    }
    


## To post UserSession at the start of the test

### Request

    `POST http://127.0.0.1:8000/api/userSession/`

    {
        "user": 8,
        "quiz_id": "4f66e07d-91a3-428d-86e0-31187898a975"
    }


### Response

    {
        "id": "e3164b8c-a8c7-46a2-8a15-77de33ee2a4d",
        "start_time": "2021-03-26T15:06:10.685197+05:30",
        "remaining_duration": "01:30:00",
        "user": 8,
        "quiz_id": "4f66e07d-91a3-428d-86e0-31187898a975"
    }


## To get UserSession 

### Request

`GET http://127.0.0.1:8000/api/getUserSession/e3164b8c-a8c7-46a2-8a15-77de33ee2a4d`

<slug: session_id>

### Response

    {
        "id": "e3164b8c-a8c7-46a2-8a15-77de33ee2a4d",
        "start_time": "2021-03-26T15:06:10.685000+05:30",
        "remaining_duration": "01:26:00.975000",
        "user": 8,
        "quiz_id": "4f66e07d-91a3-428d-86e0-31187898a975"
    }


## To get Result

### Request

`GET http://localhost:8000/api/getresult/<username>`


### Response

    {
    "data": {
        "Quiz Name": "Mathematics in Real life Problems (High School) by heyMatheists",
        "totalquestion": 20,
        "correctquestion": 9,
        "incorrectquestion": 10,
        "attempted": 19,
        "not_attempted": 1,
        "marks_obtained": 19,
        "responses": {
            "Question 1": {
                "correct answer": "option 1",
                "your answer": "option 2"
            },
            "Question 2": {
                "correct answer": "option 2",
                "your answer": "option 2"
            },
            "Question 3": {
                "correct answer": "option 1",
                "your answer": "option 2"
            },
            "Question 4": {
                "correct answer": "option 3",
                "your answer": "option 12"
            }
        },
        "analysis": {
            "subject: Mathematics": {
                "total_questions": 20,
                "incorrect_or_not_attempted": 11,
                "correct_questions": 9
            },
            "topic: Parity": {
                "total_questions": 2,
                "incorrect_or_not_attempted": 1,
                "correct_questions": 1
            }
            "dificulty: Hard": {
                "total_questions": 4,
                "incorrect_or_not_attempted": 3,
                "correct_questions": 1
            }
        }
    }
}
    
## To add question to Quiz

### Request

`POST http://127.0.0.1:8000/api/addQuestionToQuiz`


    `{
     "quiz_id": "1440a8a6-5a47-42b7-bd2a-88d4bbd84b70",
     "quest_id": ["dc3fd2a8-0a5a-4765-8f03-31463b95ccf5"]
     }`

### Response

    {
    "message": "added successfully"
    }


