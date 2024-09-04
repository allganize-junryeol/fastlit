import re
import json
from fastapi import APIRouter

def logfmt_to_dict(logfmt_str):
    logfmt_pattern = r'(\w+)=("[^"]*"|\S+)'
    matches = re.findall(logfmt_pattern, logfmt_str)
    logfmt_dict = {}
    
    for key, value in matches:
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        logfmt_dict[key] = value
    
    return logfmt_dict

router = APIRouter()

@router.get("/events")
async def get_events():
    
    events = []
    
    with open("data/fortinet_syslog.log") as f:
        for line in f:
            event = logfmt_to_dict(line)
            if event["type"] == "utm" and event["subtype"] == "virus":
                events.append(event)
            if event["type"] == "utm" and event["subtype"] == "ips":
                events.append(event)
            if event["type"] == "utm" and event["subtype"] == "anomaly":
                events.append(event)

    return events