import quip

client = quip.QuipClient(access_token="Wk9EQU1BcDZFS04=|1483091850|CF037JVoITJPnAET8aHWnZwEZACvrIm7jtkRIQCaX3g=")
theURL = "Z0R5AhbLjUxu" # test doc 0309-c
theID = client.get_document(id=theURL)['thread']['id']

client.edit_document(thread_id=theID, content=r"Hi", format="markdown", 
                             operation=client.APPEND)
