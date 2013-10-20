Bentanglement
=============

My clone of the [entanglement game](http://entanglement.gopherwoodstudios.com/). I was inspired to write this game in an attempt to beat my brother Pule's high score.

Sadly, the AI is not yet good enough to do so. But I learned a lot from it. :)

# Installation
Make sure you have python installed.

## Set up a virtualenv

    virtualenv vendor

Your virtualenv is so you don't install python packages that conflict with your other projects.
Whenever you want to run bentanglement, make sure you are in your virtualenv. Do so now:

    source ./vendor/bin/activate

## Install the python requirements

    pip install -r requirements.txt

## Running it

    python bentanglement.py

You can also add a 0, 1, 2 option as a second argument to use different ai's to solve it for you.


