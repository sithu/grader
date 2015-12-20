login = {  'user' : 'cmpe273sec1', 'password' : 'ShowMeAll'  }

labs = [
    {
        'step_1': {
            'desc': 'Github Check',
            'regex': '^https://github.com/.*', 
            'http': 'GET', 
            'point': 1 
        },
        'step_2': {
            'desc': 'Bitbucket Check',
            'regex': '^https://bitbucket.org/.*/cmpe273submission', 
            'http': 'GET', 
            'point': 1 
        },
        'step_3': {
            'desc': 'Python Hello World Server Check',
            'regex': '^http://ec2.*compute.amazonaws.com:8000', 
            'http': 'GET', 
            'point': 4 
        },
        'step_4': {
            'desc': 'Spring Boot App: curl -I http://localhost:8080 Output line#3 Check',
            'regex': 'Allow:.*GET', 
            'point': 4 
        }
    }
]

assignments = [
    {   
        'step_1': {
            'postconditions' : [ 'global_moderator_id' ],
            'desc': '/moderators [POST] Call',
            'path': '/moderators', 
            'http': 'POST',
            'basic_auth' : 'false',
            'request': {
                'name' : 'Foo Bar',
                'email' : 'foobar@gmail.com',
                'password' : 'secret'
            },
            'response_code' : 201,
            'response': {
                'name' : 'Foo Bar',
                'email' : 'foobar@gmail.com',
                'password' : 'secret',
                'created_at' : '2015-03-.*'
            },
            'point': 1       
        },
        'step_2': {
            'preconditions' : [ 'global_moderator_id' ],
            'postconditions' : [],
            'desc': '/moderators/id [GET] Call',
            'path': '/moderators/%s', 
            'http': 'GET',
            'basic_auth' : 'true',
            'response_code' : 200,
            'response': {
                'name' : 'Foo Bar',
                'email' : 'foobar@gmail.com',
                'password' : 'secret',
                'created_at' : '^2015-03-.*'
            },
            'point': 1       
        },
        'step_3': {
            'preconditions' : [ 'global_moderator_id' ],
            'postconditions' : [],
            'desc': '/moderators/{moderator_id} [Update] Call',
            'path': '/moderators/%s', 
            'http': 'PUT',
            'basic_auth' : 'true',
            'request': {
                'email' : 'foobar2@gmail.com'
            },
            'response_code' : 200,
            'response': {
                'name' : 'Foo Bar',
                'email' : 'foobar2@gmail.com',
                'password' : 'secret'
            },
            'point': 1       
        },
        'step_4': {
            'preconditions' : [ 'global_moderator_id' ],
            'postconditions' : [ 'global_poll_id' ],
            'desc': '/moderators/{moderator_id}/polls [Create] Poll Call',
            'path': '/moderators/%s/polls', 
            'http': 'POST',
            'basic_auth' : 'true',
            'request': {
                "question": "What type of smartphone do you have?",
                "started_at": "2015-03-23T13:00:00.000Z",
                "expired_at" : "2015-03-24T13:00:00.000Z",
                "choice": [ "Android", "iPhone" ]
            },
            'response_code' : 201,
            'response': {
                "question": "What type of smartphone do you have?",
                "started_at": "2015-03-23.*",
                "expired_at" : "2015-03-24.*",
                "choice": [ "Android", "iPhone" ]
            },
            'point': 1       
        },
        'step_5': {
            'preconditions' : [ 'global_poll_id' ],
            'postconditions' : [ 'global_poll_id' ],
            'desc': '/polls/{poll_id} [GET] Poll Call',
            'path': '/polls/%s', 
            'http': 'GET',
            'basic_auth' : 'false',
            'response_code' : 200,
            'response': {
                "question": "What type of smartphone do you have?",
                "started_at": "2015-03-23.*",
                "expired_at" : "2015-03-24.*",
                "choice": [ "Android", "iPhone" ]
            },
            'point': 1       
        },
        'step_6': {
            'preconditions' : [ 'global_moderator_id', 'global_poll_id' ],
            'postconditions' : [],
            'desc': '/polls/{poll_id} [DELETE] Poll Call',
            'path': '/moderators/%s/polls/%s', 
            'http': 'DELETE',
            'basic_auth' : 'true',
            'response_code' : 204,
            'response': {},
            'point': 1       
        },
        'step_7': {
            'preconditions' : [ 'global_moderator_id' ],
            'postconditions' : [ 'global_poll_id' ],
            'desc': '/moderators/{moderator_id}/polls [Create] Preparation for List Call',
            'path': '/moderators/%s/polls', 
            'http': 'POST',
            'basic_auth' : 'true',
            'request': {
                "question": "What type of smartphone do you have?",
                "started_at": "2015-03-23T13:00:00.000Z",
                "expired_at" : "2015-03-24T13:00:00.000Z",
                "choice": [ "Android", "iPhone" ]
            },
            'response_code' : 201,
            'response': {
                "question": "What type of smartphone do you have?",
                "started_at": "2015-03-23.*",
                "expired_at" : "2015-03-24.*",
                "choice": [ "Android", "iPhone" ]
            },
            'point': -1       
        },
        'step_8': {
            'preconditions' : [ 'global_moderator_id' ],
            'postconditions' : [ 'global_poll_id' ],
            'desc': '/moderators/{moderator_id}/polls [Create] Preparation for List Call',
            'path': '/moderators/%s/polls', 
            'http': 'POST',
            'basic_auth' : 'true',
            'request': {
                "question": "What type of smartphone do you have?",
                "started_at": "2015-03-18T13:00:00.000Z",
                "expired_at" : "2015-03-19T13:00:00.000Z",
                "choice": [ "Android", "iPhone" ]
            },
            'response_code' : 201,
            'response': {
                "question": "What type of smartphone do you have?",
                "started_at": "2015-03-18.*",
                "expired_at" : "2015-03-19.*",
                "choice": [ "Android", "iPhone" ]
            },
            'point': -1       
        },
        'step_9': {
            'preconditions' : [ 'global_moderator_id' ],
            'postconditions' : [],
            'desc': '/moderators/{moderator_id}/polls [GET] List All Polls Call',
            'path': '/moderators/%s/polls', 
            'http': 'GET_ALL',
            'basic_auth' : 'true',
            'response_size' : 1,
            'point': 1       
        },
        'step_10': {
            'preconditions' : [ 'global_poll_id' ],
            'postconditions' : [],
            'desc': '/polls/{poll_id}?choice=x [PUT] Vote Call',
            'path': '/polls/%s?choice=0', 
            'http': 'PUT',
            'basic_auth' : 'false',
            'response_code' : 204,
            'request': {},
            'response': {},
            'point': 1       
        },
        'step_11': {
            'postconditions' : [],
            'desc': '/moderators [POST] Validation Check Call',
            'path': '/moderators', 
            'http': 'POST_validation',
            'basic_auth' : 'false',
            'request': {
                'name' : 'Foo Bar',
                'password' : 'secret'
            },
            'response_code' : 400,
            'response': {},
            'point': 1       
        },
    }
]