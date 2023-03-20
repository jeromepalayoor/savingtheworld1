# Blogoont
### Saving the World 1 - Term 1 Project for my Computing Class.
---------------

A one stop website to share your thoughts and feelings about school or post helpful tutorials about certain topics or subjects to help others. It is very user freindly and secure. With a very user friendly UI and intuitive UX, this website is very effective in getting your content to others.

Created using [Python Flask](https://flask.palletsprojects.com/en/2.2.x/) as backend support, and [HTML](https://en.wikipedia.org/wiki/HTML) and [Bootstrap 5.3](https://getbootstrap.com/docs/5.3/getting-started/introduction/) for frontend support.

[Project Details](https://docs.google.com/document/d/1D4Daka6xcuZB8Wg_MbTXhbfrMkL9DZG11iMpqvgu2Dg/edit)

Website link: [check it out here](https://wizardly-water-19056.pktriot.net/)

Note: Since my code has sensitive information, I did not use a remote hosting environment due to privacy concerns. Instead I am running a server from my computer and using [Packetriot](https://packetriot.com/) to use a tunnel sevice and host my local server onto the internet, hence the weird link. It may be down for a while when I am updating my code. This website may not work on school wifi.

------------

### Setting it up on you own server

First clone the project

`https://github.com/jeromepalayoor/savingtheworld1.git`

Remember to add the files and folders necessary:

```
/secret.py
/db/
/db/datapost/
/db/datapost/ids
/db/datauser/
/db/sessions
/db/users
/db/verification
```

Add you email details into secret.py file ([example](https://github.com/jeromepalayoor/savingtheworld1/blob/main/secret_example.py)).

After setting it up, run the following command to start the local site:

`flask run`

Then visit your site at [localhost](http://127.0.0.1:5000), or whichever port you had set.