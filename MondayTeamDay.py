def MondayTeamDay(): # Function is called monday morning at 7:00
    text2 = 'Monday is team day and you are the chosen one! Submit a question here and I will send it to the core and collect their responses.'
    ims = slack.im.list().body['ims'] ## im is object type for direct message channels
    user_and_im = {}
    im_list = []
    user_list = []
    for im in ims: #fills dictionary with {user: direct message id} and fills lists
        if im['user'] != 'USLACKBOT':
            user_list.append(im['user'])
            user_and_im[im['user']] = im['id']
            im_list.append(im['id'])

    rand_int = randint(0,len(user_and_im)-1) #Random integer
    chosen_user = user_list[0] # Pick random user
    for userr in user_list:
        slack.im.open(user = userr) # Open DM channel if user does not have one#Keeps appending unique responses
    slack_client.api_call("chat.postMessage", channel = user_and_im[chosen_user],text = text2)

    wait_for_response = True
    while wait_for_response: #Wait for chosen user to respond
        command, channel = parse_bot_commands(slack_client.rtm_read())
        if command and channel == user_and_im[chosen_user]: #If question from chosen user
            slack_client.api_call("chat.postMessage", channel = channel,text = "Your question has been registered!")
            question = command #Saving this command as variable for later
            text3 = 'Monday is team day. A random person has been chosen to ask the core a question. When everyone has responded, the answers will be revealed. The question asked was:'
            text4 = ' Please write your answer below.'
            k = text3 + '\n' + question + '\n' + text4
            for im in im_list: #Post direct message with question to everyone.
                slack_client.api_call("chat.postMessage", channel = im,text = k)

            wait_for_response = False
        time.sleep(RTM_READ_DELAY) #Wait delay before repeating while loop

    responses = []
    while len(im_list) != 1: #Keeps appending unique responses to responses until everyone has answered.
        command, channel = parse_bot_commands(slack_client.rtm_read())
        if command and channel in im_list:
            slack_client.api_call("chat.postMessage", channel = channel,text = 'Your answer has been registered!')
            im_list.remove(channel) #remove the channel from list to avoid duplicated
            responses.append(command) #add the response from removed channel.
        time.sleep(RTM_READ_DELAY)


    answers = '\n'.join(responses)
    full_response = 'Here are the answers to the question: \n' + answers
    for user in user_list: #Sends full set of responses to everyone.
        slack_client.api_call("chat.postMessage", channel = user_and_im[user],text = full_response)


        time.sleep(RTM_READ_DELAY)
