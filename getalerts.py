import argparse
import requests
import json
import sys


def flatten(d):
    out = {}
    for key, val in d.items():
        if isinstance(val, dict):
            val = [val]
        if isinstance(val, list):
            for subdict in val:
                deeper = flatten(subdict).items()
                out.update({key + '_' + key2: val2 for key2, val2 in deeper})
        else:
            out[key] = val
    return out


def clear(obj):
    for key in obj:
        obj[key] = ""

def get_alerts(startdate, enddate, filename, serviceid, token):
    ismore = True
    limit = 100
    offset = 0

    results = []

    url = "https://api.pagerduty.com/alerts"

    headers = {
        'Accept': "application/vnd.pagerduty+json;version=2",
        'Content-Type': "application/json",
        'Authorization': f'Token token={token}',
        }


    output_columns = {}
    count = 0
    while ismore:

        querystring = {"time_zone":"UTC","since":startdate,"until":enddate,"offset":offset,"limit":limit,"total":"True"}

        response = requests.request("GET", url, headers=headers, params=querystring)

        if response.text == "":
            print(f'Error calling PagerDuty REST API: {response}')
            return

        js = response.json()
        if "error" in js:
            print(f'Error calling PagerDuty REST API: {js["error"]["message"]}')
            return

        total = js['total']
        for alert in js['alerts']:
            count = count + 1
            print("\r{:.0%} Complete".format(count / total), end='', flush=True)
            if (serviceid == None or alert['service']['id'] == serviceid) and 'incident' in alert and alert['incident'] != None:
                clear(output_columns)
                output_columns.update({"id": alert['id'], "incident_id": alert['incident']['id'] })

                if alert['body']['details'] != None \
                        and "Resource" in alert['body']['details'] \
                        and isinstance(alert["body"]["details"],dict):
                    flat_json = flatten(alert['body']['details'])
                    #print(flat_json)
                    for key, val in flat_json.items():
                        if val.find('\n') > 0 or val.find('"') > 0:
                            val = val.replace('\n', ' ')
                            val = val.replace('"', '')
                            flat_json[key] = val
                    output_columns.update(flat_json)

                results.append(output_columns.copy())

        ismore = js['more']
        offset += limit
        #print('is there more? ' + str(ismore))

    print('\n')
    file = open(filename,'w')
    if len(output_columns) > 0:
        firstCol = True
        for col in output_columns:
            if firstCol:
                firstCol = False
            else:
                file.write(',')
            file.write(str(col))
        file.write('\n')

    for result in results:
        firstCol = True
        #print(result)
        for col in result:
            if firstCol:
                firstCol = False
            else:
                file.write(',')
            file.write(f'"{str(result[col])}"')
        file.write('\n')

    file.close()

if __name__ == '__main__':
    # print(date.today())
    ap = argparse.ArgumentParser(description="Adds responders to a slack channel")
    ap.add_argument('-k', "--pd-token", required=True, help="(Required) REST API key")
    ap.add_argument('-s', "--start-date", required=True, help="(Required) Start Date (YYYYMMDD)")
    ap.add_argument('-e', "--end-date", required=True, help="(Required) End Date (YYYYMMDD)")
    ap.add_argument('-f', "--filename", required=True, help="(Required) Output file name")
    ap.add_argument('-v', "--service", required=False, help="(Optional) PagerDuty Service Id")
    ap.add_argument('-d', "--debug", required=False, help="(Optional) Debug flag", action="store_true")
    args = ap.parse_args()

    get_alerts(args.start_date, args.end_date, args.filename, args.service, args.pd_token)