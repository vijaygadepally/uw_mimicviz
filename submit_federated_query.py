#!/usr/bin/env python

"""Submit a query to the myria-federated appserver instance.

appengine authentication logic adapted from:
http://stackoverflow.com/questions/101742/how-do-you-access-an-authenticated-google-app-engine-service-from-a-non-web-py

See also google's logic for posting updates to appengine:
https://code.google.com/p/googleappengine/source/browse/trunk/python/google/appengine/tools/appengine_rpc.py
"""

import json
import requests
import os
# Don't make this repository public without removing these!
users_email_address = "bigdogintel@gmail.com"
users_password      = "BigDawg!"

workers_uri = 'https://myria-federated.appspot.com/rest/workers'
execute_uri = 'https://myria-federated.appspot.com/execute'
dataset_uri = 'https://myria-federated.appspot.com/rest/dataset/user-public/program-adhoc/relation-%s/data?format=json'
app_name = "myria-federated"

def get_auth_cookies():
    # Step 1: get an AuthToken from Google accounts
    auth_uri = 'https://www.google.com/accounts/ClientLogin'
    auth_params = {"Email":   users_email_address,
                   "Passwd":  users_password,
                   "service": "ah",
                   "source":  app_name,
                   "accountType": "HOSTED_OR_GOOGLE"}

    res = requests.get(auth_uri, params=auth_params)

    auth_resp_dict = dict(x.split("=")
                          for x in res.text.split("\n") if x)
    authtoken = auth_resp_dict["Auth"]

    # Step 2: obtain an authentication cookie from the app
    # Continue parameter is required; see appengine_rpc.py
    login_uri = "https://%s.appspot.com/_ah/login" % app_name
    login_params = {'auth': authtoken, 'continue': 'http://localhost'}
    login_res = requests.get(login_uri, params=login_params, allow_redirects=False)

    return login_res.cookies

def get_workers(auth_cookies=None):
    if not auth_cookies:
        auth_cookies = get_auth_cookies()
    res = requests.get(workers_uri, cookies=auth_cookies)
    print res.text

def submit_query(query, auth_cookies=None):
    print query
    if not auth_cookies:
        auth_cookies = get_auth_cookies()

    data={
        'query': query,
        'language': 'myrial'
    }
    res = requests.post(execute_uri, cookies=auth_cookies, data=data)

    print res

def download_dataset(name, auth_cookies=None):
    if not auth_cookies:
        auth_cookies = get_auth_cookies()

    res = requests.get(dataset_uri % name, cookies=auth_cookies)
    print res
    return res.text

query = '''
connect(%afl, "http://vega.cs.washington.edu:8080");

waveform = scan(public:adhoc:patient_to_waveform);
X = [from waveform
     where waveform.patient_id={0}
     emit min(waveform.waveform_id)];
store(X, mimic_patient_min_waveform);
exportMyriaToSciDB(mimic_patient_min_waveform, "PP0");

%afl("remove(tmp_time)");
%afl("remove(PP0T)");
%afl("store(redimension(apply(PP0, RecordNum, i),<RecordNum:int64> [RecordName=1:1000000000000, 10, 0]), PP0T)");
%afl("create array tmp_time<msec:int64>[RecordName=1:1000000000000,10,0,x=0:1000000,1000000,0]");
%afl("redimension_store(filter(redimension(cross_join(waveform_signal_table as X, PP0T as Y, X.RecordName, Y.RecordName),<signal:double>[RecordName=1:1000000000000,10,0,msec=0:1000000000,100000,0]), pow(signal,2) > 0.5),tmp_time)");
'''
VIZ_PATH = '/vega4/MIMIC2/scidb/pipeline/Step5_Viz/trunk/meteor_viz/'
PATIENT_PATH = VIZ_PATH + 'file_io/patientID.tsv'
MED_PATH = VIZ_PATH + 'file_io/medName.tsv'
OUTPUT_PATH = VIZ_PATH+ 'file_io/waveformID.tsv'

if __name__ == '__main__':
    patient_id = '124'

    with open(PATIENT_PATH) as fh:
       patient_id = fh.read()

    # TODO: delete patient file, med file

    cookies = get_auth_cookies()
    submit_query(query.format(patient_id), cookies)

    result_json = download_dataset('mimic_patient_min_waveform', cookies)
    result_obj = json.loads(result_json)
    wid = result_obj[0]['_COLUMN0_']
    print wid
    print OUTPUT_PATH
    with open(OUTPUT_PATH, 'w') as fh:
        fh.write(str(wid))
   
   # os.system(OCTAVE_SCRIPT)
 
