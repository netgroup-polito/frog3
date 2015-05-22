'''
Created on May 19, 2015

@author: fabiomignini
'''
from constants import TIMEOUT, SERVICE_LAYER
import requests
import json

def instantiate(token):
    request_body = {"session":{"session_param" : {}}} 
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
    resp = requests.put(SERVICE_LAYER, headers=headers, data=json.dumps(request_body), timeout=(TIMEOUT*8))
    return resp.status_code

def delete(token):
    request_body = {"session":{"session_param" : {}}} 
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
    resp = requests.delete(SERVICE_LAYER, headers=headers, data=json.dumps(request_body), timeout=(TIMEOUT*8))
    return resp.status_code

#token = "MIIKwgYJKoZIhvcNAQcCoIIKszCCCq8CAQExDTALBglghkgBZQMEAgEwggkQBgkqhkiG9w0BBwGgggkBBIII-XsiYWNjZXNzIjogeyJ0b2tlbiI6IHsiaXNzdWVkX2F0IjogIjIwMTUtMDUtMTlUMTQ6MTU6MjcuNzUxOTM0IiwgImV4cGlyZXMiOiAiMjAxNS0wNS0xOVQxNToxNToyN1oiLCAiaWQiOiAicGxhY2Vob2xkZXIiLCAidGVuYW50IjogeyJkZXNjcmlwdGlvbiI6ICJEZW1vIFRlbmFudCIsICJlbmFibGVkIjogdHJ1ZSwgImlkIjogImIyZTI4ZGRiMjU1ODQyOTlhNjA3MmRlZDhmZTdjOTA1IiwgIm5hbWUiOiAiZGVtbyJ9fSwgInNlcnZpY2VDYXRhbG9nIjogW3siZW5kcG9pbnRzIjogW3siYWRtaW5VUkwiOiAiaHR0cDovL2NvbnRyb2xsZXI6ODc3NC92Mi9iMmUyOGRkYjI1NTg0Mjk5YTYwNzJkZWQ4ZmU3YzkwNSIsICJyZWdpb24iOiAicmVnaW9uT25lIiwgImludGVybmFsVVJMIjogImh0dHA6Ly9jb250cm9sbGVyOjg3NzQvdjIvYjJlMjhkZGIyNTU4NDI5OWE2MDcyZGVkOGZlN2M5MDUiLCAiaWQiOiAiYzkwYjJlZTBmMjM3NDQyYWExOTQ4OGI0NWEyNDY4YjYiLCAicHVibGljVVJMIjogImh0dHA6Ly9jb250cm9sbGVyOjg3NzQvdjIvYjJlMjhkZGIyNTU4NDI5OWE2MDcyZGVkOGZlN2M5MDUifV0sICJlbmRwb2ludHNfbGlua3MiOiBbXSwgInR5cGUiOiAiY29tcHV0ZSIsICJuYW1lIjogIm5vdmEifSwgeyJlbmRwb2ludHMiOiBbeyJhZG1pblVSTCI6ICJodHRwOi8vY29udHJvbGxlcjo5Njk2IiwgInJlZ2lvbiI6ICJyZWdpb25PbmUiLCAiaW50ZXJuYWxVUkwiOiAiaHR0cDovL2NvbnRyb2xsZXI6OTY5NiIsICJpZCI6ICIzMDAwMGMzMmM2NWY0ZWQ1YmNlZjk5ZGY2N2M4ZjY1ZCIsICJwdWJsaWNVUkwiOiAiaHR0cDovL2NvbnRyb2xsZXI6OTY5NiJ9XSwgImVuZHBvaW50c19saW5rcyI6IFtdLCAidHlwZSI6ICJuZXR3b3JrIiwgIm5hbWUiOiAibmV1dHJvbiJ9LCB7ImVuZHBvaW50cyI6IFt7ImFkbWluVVJMIjogImh0dHA6Ly9jb250cm9sbGVyOjkyOTIiLCAicmVnaW9uIjogInJlZ2lvbk9uZSIsICJpbnRlcm5hbFVSTCI6ICJodHRwOi8vY29udHJvbGxlcjo5MjkyIiwgImlkIjogIjJlYmY3NjJhYjNjZTRiYjdhYmFhNjViOWI5MTk1OTdjIiwgInB1YmxpY1VSTCI6ICJodHRwOi8vY29udHJvbGxlcjo5MjkyIn1dLCAiZW5kcG9pbnRzX2xpbmtzIjogW10sICJ0eXBlIjogImltYWdlIiwgIm5hbWUiOiAiZ2xhbmNlIn0sIHsiZW5kcG9pbnRzIjogW3siYWRtaW5VUkwiOiAiaHR0cDovL2NvbnRyb2xsZXI6ODAwMC92MSIsICJyZWdpb24iOiAicmVnaW9uT25lIiwgImludGVybmFsVVJMIjogImh0dHA6Ly9jb250cm9sbGVyOjgwMDAvdjEiLCAiaWQiOiAiMThlY2ZmODMxMjBhNDQwMzkzN2ExYjBiN2Y0ZTAxMzEiLCAicHVibGljVVJMIjogImh0dHA6Ly9jb250cm9sbGVyOjgwMDAvdjEifV0sICJlbmRwb2ludHNfbGlua3MiOiBbXSwgInR5cGUiOiAiY2xvdWRmb3JtYXRpb24iLCAibmFtZSI6ICJoZWF0LWNmbiJ9LCB7ImVuZHBvaW50cyI6IFt7ImFkbWluVVJMIjogImh0dHA6Ly9jb250cm9sbGVyOjgwMDQvdjEvYjJlMjhkZGIyNTU4NDI5OWE2MDcyZGVkOGZlN2M5MDUiLCAicmVnaW9uIjogInJlZ2lvbk9uZSIsICJpbnRlcm5hbFVSTCI6ICJodHRwOi8vY29udHJvbGxlcjo4MDA0L3YxL2IyZTI4ZGRiMjU1ODQyOTlhNjA3MmRlZDhmZTdjOTA1IiwgImlkIjogIjI0NGE4MWYyNTIwYzQzZmRiN2I4ODJmMTI5MTkwMGFmIiwgInB1YmxpY1VSTCI6ICJodHRwOi8vY29udHJvbGxlcjo4MDA0L3YxL2IyZTI4ZGRiMjU1ODQyOTlhNjA3MmRlZDhmZTdjOTA1In1dLCAiZW5kcG9pbnRzX2xpbmtzIjogW10sICJ0eXBlIjogIm9yY2hlc3RyYXRpb24iLCAibmFtZSI6ICJoZWF0In0sIHsiZW5kcG9pbnRzIjogW3siYWRtaW5VUkwiOiAiaHR0cDovL2NvbnRyb2xsZXI6MzUzNTcvdjIuMCIsICJyZWdpb24iOiAicmVnaW9uT25lIiwgImludGVybmFsVVJMIjogImh0dHA6Ly9jb250cm9sbGVyOjUwMDAvdjIuMCIsICJpZCI6ICI1M2UzYWFjZWQyNjQ0NmEyYjNlZjg2ODYwNGIzN2FjMyIsICJwdWJsaWNVUkwiOiAiaHR0cDovL2NvbnRyb2xsZXI6NTAwMC92Mi4wIn1dLCAiZW5kcG9pbnRzX2xpbmtzIjogW10sICJ0eXBlIjogImlkZW50aXR5IiwgIm5hbWUiOiAia2V5c3RvbmUifV0sICJ1c2VyIjogeyJ1c2VybmFtZSI6ICJkZW1vIiwgInJvbGVzX2xpbmtzIjogW10sICJpZCI6ICIwZGNiMGIxNzFjODY0ZTU4OGY1MmRmZjE3NjEwMDE3MCIsICJyb2xlcyI6IFt7Im5hbWUiOiAiX21lbWJlcl8ifV0sICJuYW1lIjogImRlbW8ifSwgIm1ldGFkYXRhIjogeyJpc19hZG1pbiI6IDAsICJyb2xlcyI6IFsiOWZlMmZmOWVlNDM4NGIxODk0YTkwODc4ZDNlOTJiYWIiXX19fTGCAYUwggGBAgEBMFwwVzELMAkGA1UEBhMCVVMxDjAMBgNVBAgMBVVuc2V0MQ4wDAYDVQQHDAVVbnNldDEOMAwGA1UECgwFVW5zZXQxGDAWBgNVBAMMD3d3dy5leGFtcGxlLmNvbQIBATALBglghkgBZQMEAgEwDQYJKoZIhvcNAQEBBQAEggEAluWgghMMnDA7AdpE-FJERT-6beDFJmqAS5rLIMwpGhoyAvTBhXPpcRRal3kHR0ri0FR+FLBbFrp9rAiis-ekXRbSxB0lOoLObHnW7R0I3WNkGzCkM6UmjbZt0bGdcNKddNlB01sLFH-yILJn3Cx+2hT0yenH4vTmiQDf2qO+DkfctjkGt28Os9MfH8kK+tjEhtl3p7-qr2hn6+yGrkrFfKSIL-KXmnn-YlkkNTP4WWUamR9VvlmWwF-8wpeA+Y7rAnmY+1DUaGgcWh5sHh6Zt6ba5sy3FZxl7dmZnsW+jT0mduGglXVHW88qnXWWXSPB9aLCl9FVb9EanRMIPc8Org=="
#print instantiate(token)