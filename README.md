Recommender-of-Problem-Solvers-on-Twitter
=========================================
This is the project of Network Science course. It mainly helps the user to find the real problem solver from twitter followers according to the specific questions.

Usage:
======
To run our application, please open the command line, run:

>> python recommender.py

Then the user interface would show up. please follow the instructions:

 First, click on the hyperlink “”Authorization, it would redirect to a webpage to login to Twitter, and authorize our application, which may generate a PIN code.

 Please input that PIN code in our user interface, remember that there would be a default space in the text box, and that must be cleared, or the authorization would not succeed.

 Now you can input your problem, and click the button “Ok” to start searching.

 The searching process may take a while, and when it finishes, a new window would appear, with the visualized graph in it. The graph can be zoomed in or zoomed out with the tools it provides at down side.

 If you want to send a message to one of your followers, you could input his name in the text box, and write your message, then click on send button. Again, when input the name, please remember to clear the default space first.
The rt-polaritydata is the training data set for the Naive Bayes Classifier.

Note:
=====
To use the application, please install the following modules:
1. Python-Twitter
2. NLTK
3. NetworkX
4. MatPlotLib
5. WxPython
6. Oauth2
