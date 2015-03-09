import sys
import uuid
import re
import unirest
import pickledb
import time
import rules
import json
from bottle import route, run, get, post, static_file, request, response, default_app, auth_basic
from constants import SUBMISSIONS
from paste import httpserver

db = pickledb.load('cmpe273-spring15.db', False)
global_moderator_id = None
global_poll_id = None

def init_db():
    if not db.get('scores'):
        print "'scores' dictionary doesn't seem to exist. So, creating one..."
        if db.dcreate('scores') and db.dump():
            print "Successfully created a dictionary in DB"
        else:
            print "Failed to create a dictionary in DB"
    else:
        print "Found 'scores' dictionary in DB"
    
def check(user, passwd):
    if user == rules.login['user'] and passwd == rules.login['password']:
        return True
    
    return False
    

@get('/')
def index():
    return "OK"
  
@get('/scores/all')
@auth_basic(check)
def get_scores():
    return db.dgetall('scores'):
        
@get('/students/<id>')
@auth_basic(check)
def grades(id=None):
    return db.dget('scores', id)
    
@post('/submit')
def accept_submission():
    global global_moderator_id
    id = request.forms.get('sjsu_id')
    if len(id) != 9 or not id.isdigit():
        return { 'error' : "Invalid 'sjsu_id'. Use 9-digit id." }
         
    name = request.forms.get('full_name')
    if not name or len(name.strip()) < 5:
        return { 'error' : "'full_name' is required." } 
       
    submit_for = request.forms.get('submit_for')
    if submit_for not in SUBMISSIONS:
        return { 'error' : "Invalid 'submit_for'" }
    
    current = int(submit_for[-1:]) - 1 
    type = submit_for[:-1]
    if type == 'lab':
        rule = rules.labs[current]
    else:
        rule = rules.assignments[current]
        
    score = 0
    step = 1
    fails = []
    steps = []
    
    url = request.forms.get('api_url')
    if type == 'assignment':
        if not url:
            return { 'error' : "'api_url' field is required." }
            
        p = re.compile('^http://.*:8080/api/v1')
        # p = re.compile('^http://')
        if not p.match(url):
            return { 'error' : "Invalid 'api_url'. Expected format => ^http://.*:8080/api/v1"}
    
    while step <= len(rule.keys()):
        if type == 'lab':
            currStep = 'step_%d' % step
            input = request.forms.get(currStep)
            if input is None or len(input.strip()) < 1:
                input = ""
            steps.append(input)      
            currScore = calculate(rule['step_%d' % step], input)
        else: 
            currScore = check_endpoint(url, rule['step_%d' % step])
          
        if currScore == -1:
            print "prep step - skipping"
        elif currScore == 0:
            desc = rule['step_%d' % step]['desc']
            fails.append(url + desc + ' failed')
        else:
            score = score + currScore
        
        step = step + 1
        
    # basic auth +1
    auth_url = "%s/moderators/%s/polls" % (url, global_moderator_id)
    print "Http Basic Auth check URL=", auth_url
    if check_http_basic_auth(auth_url):
        score = score + 1
    else:
        fails.append("No Http Basic Auth protected")
      
    submission_id = uuid.uuid1().bytes.encode('base64').rstrip('=\n').replace('/', '_')
    response = { 'sjsu_id': id, 'your_score': score, 'submission_id' : submission_id }
    
    # Store the score
    now = time.strftime("%c")
    value = {
        'name' : name,
        'your_score' : score,
        'submission_id' : submission_id,
        'submission_date' : now,
        'steps' : steps,
    }
    if len(fails) > 0:
        response['missed'] = fails
        value['missed'] = fails
        
    db.dadd('scores', (id, { submit_for : value }))
    if not db.dump():
        return { 'error' : "Failed to save the data!" }
        
    
    return response
        
 
def calculate(rule, input):
    regexPass = True
    if 'regex' in rule.keys():
        p = re.compile(rule['regex'])
        regexPass = p.match(input)
            
    httpPass = True
    if 'http' in rule.keys():
        httpPass = check_http_GET(input)
        
    if regexPass and httpPass:
        return rule['point']
    else:    
        return 0
 
def preconditions(url, preconditions, mid, pid):
    if 'global_moderator_id' in preconditions and 'global_poll_id' in preconditions:
        url = url % ( str(mid) , str(pid) )
    elif 'global_moderator_id' in preconditions:
        url = url % str(mid)
    elif 'global_poll_id' in preconditions:
        url = url % str(pid)
    else:
        print "No preconditions"
        
    return url
 
def postconditions(postconditions, newId):
    if not newId or not postconditions:
        return 
        
    global global_moderator_id
    global global_poll_id
    
    if 'global_moderator_id' in postconditions:
        global_moderator_id = newId
    elif 'global_poll_id' in postconditions:
        global_poll_id = newId
    else:
        print "No postconditions"
       
def check_endpoint(url, rule):
    verb = rule['http']
    url = url + rule['path']
    httpPass = False
    global global_moderator_id
    global global_poll_id
    
    if 'preconditions' in rule.keys():
        url = preconditions(url, rule['preconditions'], global_moderator_id, global_poll_id)
    
    print "url=", url
    
    basicAuth = rule['basic_auth']
    if basicAuth == 'true':
        basicAuth = ('foo', 'bar')
    else:
        basicAuth = ()
    
    newPOSTid = None
    if verb == 'GET_ALL':
        httpPass = check_http_GET_all(url, basicAuth, rule['response_size'])
    elif verb == 'GET':
        httpPass = check_http_GET(url, basicAuth, rule['response'], rule['response_code'])
    elif verb == 'POST_validation':
        httpPass = check_http_POST_validation(url, basicAuth, rule['request'], rule['response_code'])
    elif verb == 'POST':
        httpPass, newPOSTid = check_http_POST(url, basicAuth, rule['request'], rule['response'], rule['response_code'])
    elif verb == 'PUT':
        httpPass = check_http_PUT(url, basicAuth, rule['request'], rule['response'], rule['response_code'])
    elif verb == 'DELETE':
        httpPass = check_http_DELETE(url, basicAuth, rule['response_code'])
    else:
        print "%s not supported" % verb
    
    postconditions(rule['postconditions'], newPOSTid)
    
    if httpPass:
        return rule['point']
    else:
        return 0

def check_http_GET_all(url, basicAuth, size):
    
    try:
        response = unirest.get(url, auth = basicAuth)
        return len(response.body) > size
    except Exception, e:
        print e 
    
    return False;
            
def check_http_GET(url, basicAuth, _response=None, _resp_code=200):
    if url is None or len(url) < 1:
        return False;
    
    try:
        response = unirest.get(url, auth = basicAuth)
        return response.code == _resp_code and check_response(_response, response.body)
    except Exception, e:
        print e 
    
    return False;
    
def check_http_DELETE(url, basicAuth, _resp_code=200):
    if url is None or len(url) < 1:
        return False;
    
    try:
        response = unirest.delete(url, auth = basicAuth)
        return response.code == _resp_code
    except Exception, e:
        print e 
    
    return False;
    
def check_http_POST(_url, basicAuth, _request, _response, _resp_code):
    id = ''
    try:
        request = json.dumps(_request)
        response = unirest.post(
            _url, 
            headers={ "Accept": "application/json", "Content-Type": "application/json" }, 
            params=request, auth = basicAuth)
        
        print response.body
        print "response_code=%s, id=%s" % (response.code, response.body['id'])
        id = response.body['id']
        return (response.code == int(_resp_code), id)
    except Exception, e:
        print e 
    
    return (False, id)

def check_http_POST_validation(_url, basicAuth, _request, _resp_code):
    try:
        request = json.dumps(_request)
        response = unirest.post(
            _url, 
            headers={ "Accept": "application/json", "Content-Type": "application/json" }, 
            params=request)
        
        print response.body
        print "response_code=%s, body=%s" % (response.code, response.body)
        return response.code == int(_resp_code)
    except Exception, e:
        print e 
    
    return False
    
def check_http_PUT(url, basicAuth, _request=None, _response=None, _resp_code=200):
    if url is None or len(url) < 1:
        return False;
    
    try:
        request = json.dumps(_request) if _request else None
        response = unirest.put(
            url, 
            headers={ "Accept": "application/json", "Content-Type": "application/json" }, 
            params=request, auth = basicAuth)
        
        if not _response:
            return response.code == _resp_code and check_response(_response, response.body)
        else:
            return response.code == _resp_code
    except Exception, e:
        print e 
    
    return False;
 
def check_http_basic_auth(_url):
    try:
        response = unirest.get(
            _url, 
            headers={ "Accept": "application/json", "Content-Type": "application/json" })
        
        print "http basic auth check: response_code=%s" % (response.code)
        return response.code == 401
    except Exception, e:
        print e 
    
    return False
           
def check_response(expected, actual):
    ok = True
    for key in expected.keys():
        if key == 'id':
            continue
        value = actual[key]
        if isinstance(expected[key], list):
            for each in expected[key]:
                if not each in value:
                    print "%s not found in the response" % each
                    return False
            continue
                
        p = re.compile(expected[key])
        ok = p.match(value)
        if not ok:
            print "expected=%s, actual=%s" % (expected[key], value)
            break        
        
    return ok
    
def main(_port):
    init_db()
    application = default_app()
    httpserver.serve(application, host='0.0.0.0', port=_port)
    
if __name__ == "__main__":
   # Default port is 9000
   port = 9000
   if len(sys.argv) > 1:
      port = int(sys.argv[1])
   
   main(port)
