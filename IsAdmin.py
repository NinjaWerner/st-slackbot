def IsAdmin(split_command): #See main 1

    users = slack.users.list() #Keeps appending unique responses
    users = users.body['members']


    for user_data in users:
        for word in split_command:
            if user_data['name'] == word:
                if user_data['is_admin'] == True:
                    return word + ' is an admin!'
                else:
                    return word + ' is not an admin! :('
    return 'I do not recognize that user! :('
