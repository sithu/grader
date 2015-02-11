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