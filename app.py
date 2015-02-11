import sys
import uuid
import re
import unirest
import pickledb
import json
import time
import rules
from bottle import route, run, get, post, static_file, request, response
from constants import SUBMISSIONS

db = pickledb.load('cmpe273-spring15.db', False)

@get('/')
def index():
    return "OK"
    
@get('/students/<id>/labs/<labNum>')
def grades(id, labNum):
    key = '%s:lab%s' % (id, labNum)
    return db.get(key)
    
@post('/submit')
def accept_submission():
    id = request.forms.get('sjsu_id')
    if len(id) != 9 or not id.isdigit():
        return { 'error' : "Invalid 'sjsu_id'. Use 9-digit id." }
         
    submit_for = request.forms.get('submit_for')
    if submit_for not in SUBMISSIONS:
        return { 'error' : "Invalid 'submit_for'" }
    
    current = int(submit_for[-1:]) - 1 
    rule = rules.labs[current]
    score = 0
    step = 1
    fails = []
    
    while step <= len(rule.keys()):
        currStep = 'step_%d' % step
        input = request.forms.get(currStep)
        if input is None or len(input.strip()) < 1:
            input = ""
            
        currScore = calculate(rule['step_%d' % step], input)
        if currScore < 1:
            fails.append(rule['step_%d' % step]['desc'] + ' failed')
        
        score = score + currScore
        step = step + 1;
        
        
    submission_id = uuid.uuid1().bytes.encode('base64').rstrip('=\n').replace('/', '_')
    
    # Store the score
    now = time.strftime("%c")
    key = '%s:%s' % (id, submit_for)
    value = {
        'your_score' : score,
        'submission_id' : submission_id,
        'submission_date' : now
    }
    db.set(key, value)
    if not db.dump():
        return { 'error' : "Failed to save the data!" }
        
    response = { 'sjsu_id': id, 'your_score': score, 'submission_id' : submission_id }
    if len(fails) > 0:
        response['missed'] = fails
    
    return response
        
 
def calculate(rule, input):
    regexPass = True
    if 'regex' in rule.keys():
        p = re.compile(rule['regex'])
        regexPass = p.match(input)
            
    httpPass = True;
    if 'http' in rule.keys():
        httpPass = check_http_GET(input)
    
    if regexPass and httpPass:
        return rule['point']
    else:    
        return 0
        
def check_http_GET(url):
    if url is None or len(url) < 1:
        return False;
    
    try:
        response = unirest.get(url)
        return response.code == 200
    except Exception, e:
        print e 
    
    return False;
    
    
def main(_port):
    run(host='0.0.0.0', port=_port)
    
if __name__ == "__main__":
   # Default port is 9000
   port = 9000
   if len(sys.argv) > 1:
      port = int(sys.argv[1])
   
   main(port)
