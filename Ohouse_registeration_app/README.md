
## Description

The Registration App is used to register user with the clearing House [Ohouse](https://github.com/motine/Ohouse). It implements the registration server API i.e., "register_user". The registration client, 
sends user's information such as: 
- First Name 
- Last Name 
- User Name 
- Email 

Furthermore, the registration app provides the user with an option to either let the app generate SSH keys for him / her, or let the users provide the key to the client themselves. 


## Dependencies

The registration app has some package dependencies, Python dependencies can then be installed using: pip install -r requirements.txt.  
Furthermore, the method that is currently used to generate SSH keys is ssh-keygen, so it should also be installed beforehand. 
 
## Configuration 

To Configure the Registration App, follow these steps: 
- cp registation_app_config.json.example registation_app_config.json 
- Open registation_app_config.json and configure it with the registration server IP and Port defined [here](https://github.com/eict/Ohouse)

An example can be found [here](https://gist.github.com/zanetworker/ee4fedbeab782d797d0b) 


## Run 

To run the registration app, run "python  registration_client.py" 


## Samples 

The repository contains a sample code to test looking up values such as SSH keys. To use the sample code, 
- First create a new user with the username 'alice' using the registration app as described in the "Run" section.  
- run "python lookup.py" 

If you want to change the test username, then modify the lookup_data in lookup.py with another user name. For example, 
instead of 'urn:publicid:IDN+test:fp7-ofelia:eu+user+alice' use 'urn:publicid:IDN+test:fp7-ofelia:eu+user+<new_user_name>'


