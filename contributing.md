# Contributing to cubers.io

So you're both a cuber **and** a software developer, and would like to contribute to this project? Great! Please read below for a guide on how to get a local copy of cubers.io up and running so you can begin contributing.

## Development environment

### Python environment

cubers.io is a Python application. If you don't already have Python 3 installed locally, [head here](https://www.python.org/downloads/), grab the latest Python 3.x release and install that.

It's handy to work in sandboxed Python environments called *virtual environments*. If you aren't familiar, [read about them here](https://realpython.com/python-virtual-environments-a-primer/) and get a local virtual environment setup to use for this app.

### Clone cubers.io from GitHub

Once you have a Python environment setup, create a directory on your computer where you'd like to work on the app. Create a fork of this repository on GitHub, pull down the code locally, and get ready to get your hands dirty.

### 3rd-party Python dependencies

This app leverages several great 3rd party libraries for some of the heavy lifting. *Activate* your virtual environment you created above using the appropriate steps for your operating system. Usually this involves running a script, something like this:

```shell
. <path to your virtualenv>/scripts/activate

OR

<path to your virtualenv>/bin/activate
```

After your virtualenv is activated, install all of the app's dependencies using Python's package manager *pip*. Navigate to the root of your project (where `requirements.txt` is located), and install dependencies using the following command:

```shell
pip install -r requirements.txt
```

### Node.js and LESS

cubers.io relies on [pyTwistyScrambler](https://github.com/euphwes/pyTwistyScrambler) for generating puzzle scrambles, which in turn requires a Javascript runtime available to do the heavy lifting. [Download and install Node.js](https://nodejs.org/en/download/) for your system.

The app also compiles LESS style sheets down to CSS using `lessc`, which is available as a Node.js package via NPM (Node Package Manager). Install LESS using the following command:

```
npm install -g less
```

### Database setup

By default, cubers.io will create a sqlite database in your app's root directory named `cube_competitions.sqlite`. This is a small file which contains a database that the app can talk to. This is lightweight, convenient, and great for local development.

If you are familiar with PostgreSQL and would prefer to use a PostgreSQL database, create an environment variable on your machine named `DATABASE_URL` whose value is the Postgres connection URI for the database you'd like to use.

cubers.io uses Alembic migrations to manage the state of your database schema. To add all the relevant tables to your local database, run the following command:

```
flask db upgrade
```

This will check the current state of your database, and apply the *migrations* to bring your database up-to-date. *Migrations* are a history of the alterations to the database schema over time.

### Scramble pool

cubers.io pre-generates a pool of scrambles for every event, so that generating a new competition can happen as quickly as possible. Before generating your first competition locally, you'll need to ensure that there is a pool of scrambles to use.

Scrambles are generated using a background task queue. A periodic task runs to check to make sure you have enough scrambles handy, and if the scramble pool is low, will generate new scrambles and top off the pool.

To fire up the task queue, run the following command:

```
huey_consumer.py app.huey -k thread -w 4
```

You should see some startup messages, and within a minute you should see some logging indicating that scrambles are being generated. It's ok to leave this task queue running, or stop it with `Ctrl-C` and restart it again at a later time.

## One-time setup pieces

## Flask secret key

Flask expects to find an environment variable called ``FLASK_SECRET_KEY`` to perform encryption tasks. [Flask documentation](https://flask.palletsprojects.com/en/1.1.x/quickstart/) suggests that we generate secret keys using the following command:

```
$ python3 -c 'import os; print(os.urandom(16).hex())'
```
Now you just have to export the env variable with ``export FLASK_SECRET_KEY=some_random_value_python_generated_for_you``


### Reddit API/application setup

For Reddit-related functionality, you'll need to create your own "application" on Reddit to receive a Reddit API key.

Visit Reddit.com, click the `Preferences` link at the top of the homepage, and navigate to the `apps` tab.

Scroll to the bottom of the page, and click the `Create another app` button. Give it a name (something like `my cubers.io` for future reference), and ensure you've selected `web app` for the application type. For the `redirect uri`, input this value:

```
http://localhost:5000/authorize
```

This URL is where Reddit will redirect you after logging in, so it points to a URL on your own machine.

Click the `create app` button to finish your application creation and receive your Reddit API credentials. A new application will show up in your Reddit preferences page.

The string of random characters under your app's name is your *client ID*. Copy that set that as a local environment variable on your machine named `CUBERS_CLIENT_ID`. The field named `secret` is your API secret key. Don't share this with anybody! Copy that value and set it as an environment variable on your machine named `CUBERS_SECRET`. Finally, take the redirect URL you set earlier (`http://localhost:5000/authorize`), and also set that as an environment variable named `REDDIT_OAUTH_REDIRECT_URI`.

### Create your first local competition

Fire up the background task queue as described above:

```
huey_consumer.py app.huey -k thread -w 4
```

In a new terminal/tab (where your virtualenv has been activated), create your first competition by running the following command:

```
flask generate_new_comp_only
```

You should see some logging activity in your background task queue indicating that a competition is being generated.

### Create your local Reddit admin user

cubers.io requires an admin user which is used to post competition results to Reddit when a competition has ended.

Launch your local cubers.io instance locally (for the first time, yay!) by running the following commands:

```
export FLASK_ENV=development

flask run
```

This should fire up a local development web server, serving cubers.io on your very own computer, listening on port 5000 by default.

Next, login with the user you want to use as your admin user by visiting `http://localhost:5000/admin_login`. If everything above is configured correctly, you should be redirected to Reddit to log in as your desired user. Complete the login, and you should be redirected back to cubers.io running on your own machine. Congratulations! If something went wrong, please double check that you completed your Reddit application setup correctly using the steps defined above, and that the relevant values are set as environment variables on your machine (your client ID, client secret, and redirect URL).

Set your user account as an admin by running:

```
flask set_admin -u <reddit_username>
```

This flags your user as an admin, so you can perform admin-related functions like blacklisting event results, etc.

You can use this admin user to also participate in the competitions. However, if you'd like to login as a different user, simply visit `http://localhost:5000/` to go to the main cubers.io page, and then log out using the menu at the top of the app. You'll be redirected to a page which prompts you to log-in with Reddit as a normal user.

Finally, set up the application to know to use your admin account for posting results. Set your admin's Reddit username as the value for an environment variable named `DEVO_CUBERSIO_ACCT`.

## Next steps

At this point, you should be set up to run your own cubers.io application locally, and you're free to start contributing!

Dive into the code, read around a bit, and figure out where you'd like to start. Once you've completed work on a new feature, bug fix, etc, submit a pull request on GitHub and we'll take a look.

If you run into any trouble getting started using the steps above, please feel free to [open an issue](https://github.com/euphwes/cubers.io/issues), or ping me (/u/euphwes) directly on Reddit with questions and I'll respond to you as soon as I can.

There may be some stuff missing from this guide, but with your help, we can iron out the bugs and make this a comprehensive guide for getting started with development on cubers.io!
