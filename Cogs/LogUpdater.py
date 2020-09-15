import json

def updatelog(log):
    entries = 0
    try:
        for server in log:
            for channel in log[server]['channels']:
                for message in log[server]['channels'][channel]['messages']:
                    if not "links" in log[server]['channels'][channel]['messages'][message]:
                        log[server]['channels'][channel]['messages'][message]['links'] = {}
                    if type(log[server]['channels'][channel]['messages'][message]['links']) != dict:
                        #print(type(log[server]['channels'][channel]['messages'][message]['links']))
                        a = {}
                        for num, val in enumerate(log[server]['channels'][channel]['messages'][message]['links']):
                            print(num, val)
                            a[num] = val
                        log[server]['channels'][channel]['messages'][message]['links'] = a
                    entries += 1
        return log, entries
    except:
        return False