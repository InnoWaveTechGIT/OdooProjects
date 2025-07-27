import requests
import json

def send_notification(self,deviceToken,payload):
    serverToken = 'AAAAmP4zE2k:APA91bE44rRlmk44y2BASpsjkKxOmIkfFvWGZHyfrS_IV5FPoFrXYV8ODJXiyiwUFL5Up-jD8gY_q7pBrIba5duUqO2EXm7nrAFL2yFqcmqp748FnxkfG5ByH94vhzBssMVJ3wbQgilf'
   

    headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + serverToken,
        }
    body = {
            'notification': {'title': payload['title'],
                                'body': payload['comment']
                                },
            'to':
                deviceToken,
            'priority': 'high',
              'data':payload,
            }
    response = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(body))