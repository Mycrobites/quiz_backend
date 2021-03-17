# Separate Quiz Platform

## REST API DOCUMENTATION

Documentation of our API endpoints starts here

## To create a quiz

### Request

`POST http://127.0.0.1:8000/api/create-quiz`

    {
      "title": "Quiz 3",
      "creator": 1,
      "desc": "This is for testing",
      "endtime": "2021-03-16T00:00:00Z"
    }

### Response

    {
        "id": "a3db5155-cc6b-4ed6-90e0-8bb09598aa48",
        "title": "Quiz 3",
        "time": "2021-03-16T05:01:27.410233Z",
        "desc": "This is for testing",
        "endtime": "2021-03-16T00:00:00Z",
        "creator": 1
    }

## To get a quiz

### Request

`GET http://127.0.0.1:8000/api/get-quiz/<slug:quiz_id>`

### Response

    {
        "quiz_details": {
            "id": "994245ef-4a78-40d6-8dcf-c2f1dfdff74f",
            "title": "Quiz 1",
            "time": "2021-03-15T14:53:09.939730Z",
            "desc": "This is a test quiz",
            "endtime": "2021-03-16T00:00:00Z",
            "creator": 1
        },
        "quiz_questions": [
            {
                "id": "c8215cfc-0d4e-48a0-8b98-5a8f5827f018",
                "question": "LMS Full Form?",
                "correct_marks": 1,
                "negative_marks": -1,
                "option": "{'1': 'Learning Management System', '2': 'Learning Manager System', '3': 'Learner Machine System', '4': 'Lesson Making System'}",
                "answer": 1,
                "text": "",
                "quiz": "994245ef-4a78-40d6-8dcf-c2f1dfdff74f"
            },
            {
                "id": "2513e723-15ed-4777-9a00-19bf214ce97f",
                "question": "What is your full name?",
                "correct_marks": 0,
                "negative_marks": 0,
                "option": "",
                "answer": null,
                "text": "",
                "quiz": "994245ef-4a78-40d6-8dcf-c2f1dfdff74f"
            }
        ]
    }
    
## To edit a quiz

### Request

`PUT http://127.0.0.1:8000/api/edit-quiz/<slug:quiz_id>`

    {
        "title": "Quiz 4 for testing",
        "creator": 1,
        "desc": "This is for testing",
        "endtime": "2021-03-18T00:00:00Z"
    }

### Response

    {
        "id": "e9e34d7c-28a0-4e5f-a320-89d69322d311",
        "title": "Quiz 4 for testing",
        "time": "2021-03-17T09:16:48.033800Z",
        "desc": "This is for testing",
        "endtime": "2021-03-18T00:00:00Z",
        "creator": 1
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
        "quiz": "e9e34d7c-28a0-4e5f-a320-89d69322d311",
        "question": "CORS Full Form?",
        "option": "",
        "correct_marks": "2",
        "negative_marks": "-1",
        "text": "Cross-Origin Resource Sharing"
    }
    
### Response

    {
        "id": "b43d3a4d-67a8-450d-85e4-d713bd11679b",
        "question": "CORS Full Form?",
        "correct_marks": 2,
        "negative_marks": -1,
        "option": "",
        "answer": null,
        "text": "Cross-Origin Resource Sharing",
        "quiz": "e9e34d7c-28a0-4e5f-a320-89d69322d311"
    }

## To edit a quesion

### Request

`PUT http://127.0.0.1:8000/api/edit-question/<slug:question_id>`

    {
        "question": "What is CORS Full Form?",
        "correct_marks": 2,
        "negative_marks": -1,
        "option": "",
        "answer": null,
        "text": "Cross-Origin Resource Sharing",
        "quiz": "e9e34d7c-28a0-4e5f-a320-89d69322d311"
    }
  
### Response

    {
        "id": "5796aa80-328e-4159-af70-9126276e7ebe",
        "question": "What is CORS Full Form?",
        "correct_marks": 2,
        "negative_marks": -1,
        "option": "",
        "answer": null,
        "text": "Cross-Origin Resource Sharing",
        "quiz": "e9e34d7c-28a0-4e5f-a320-89d69322d311"
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

    {
        "quiz": "994245ef-4a78-40d6-8dcf-c2f1dfdff74f",
        "user": 2,
        "marks": 1
    }