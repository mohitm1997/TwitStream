import tweepy
import Tkinter
import tkMessageBox
import threading
from threading import Thread
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re

consumerKey = "MODo4mbISF1ousAIkk4oWxut6"
consumerSecret = "HHDf2q5MMVWYMXcDuN0m31VoKKMSlMnC48PX2sPeV3hkixdOmB"

accessToken = "255744934-AD3JLr0Uul6ok4EnVLVjpBnyEffAOdI1da2O6DZR"
accessSecret = "8o9PUwrJRORoOabEgrrQ8tBaiH7W9npzVvy3ZRfwKdNx7"

auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
auth.set_access_token(accessToken, accessSecret)
api = tweepy.API(auth)

app = None
totalNumTweets = 0
posTweets = 0
negTweets = 0
neuTweets = 0
pattern = re.compile("^,*$")

class streamThread(threading.Thread):
	def __init__(self, keywordString):
		Thread.__init__(self)
		self.keywordString = keywordString

	def run(self):
		keywords = self.keywordString.split(',')
		for word in keywords:
			word.strip()
		self.listener = twitterListener()
		self.myStream = tweepy.Stream(auth = api.auth, listener=self.listener)
		self.listener.stopStream = False
		print keywords
		self.myStream.filter(languages=['en'], track=keywords)

		self.myStream.disconnect()

		return

	def stop(self):
		self.listener.stopStream = True



class twitterListener(tweepy.StreamListener):
	def on_status(self, status):
		global app
		global totalNumTweets
		global posTweets
		global negTweets
		global neuTweets
		sid = SentimentIntensityAnalyzer()
		if self.stopStream == False: 
			if "RT" not in status.text[0:3]:
				tweet = "".join(i for i in status.text if ord(i)<128)
				totalNumTweets += 1
				app.totalNum['text'] = str(totalNumTweets)
				print tweet
				scores = sid.polarity_scores(tweet)
				print(scores)
				app.textOut.insert(Tkinter.END, "-----------------------\n" + tweet + "\n\nScore: " + str(scores['compound']) + "\n\n")
				app.textOut.see(Tkinter.END)

				if scores['compound'] >= .3:
					posTweets += 1;
					app.posNum['text'] = str(posTweets)
				elif scores['compound'] <= -.3:
					negTweets += 1;					
					app.negNum['text'] = str(negTweets)
				else:					
					neuTweets += 1;
					app.neuNum['text'] = str(neuTweets)
				return True
		else:
			return False

class app_tk(Tkinter.Tk):
	def __init__(self,parent):
		Tkinter.Tk.__init__(self, parent)
		self.initialize()
		self.startedStream = False

	def initialize(self):
		self.grid()

		self.keywordString = Tkinter.StringVar()
		self.keywordText = Tkinter.Label(self, text="Keywords: ")
		self.totalText = Tkinter.Label(self, text="Total Tweets: ")
		self.posText = Tkinter.Label(self, text="Positive: ")
		self.neuText = Tkinter.Label(self, text="Neutral: ")
		self.negText = Tkinter.Label(self, text="Negative: ")
		self.totalNum = Tkinter.Label(self, text="0")
		self.posNum = Tkinter.Label(self, text="0")
		self.neuNum = Tkinter.Label(self, text="0")
		self.negNum = Tkinter.Label(self, text="0")
		self.keywordEntry = Tkinter.Entry(self, textvariable=self.keywordString)
		self.keywordButton = Tkinter.Button(self, text="Start Stream", command=self.onStartButtonClick)
		self.stopStreamButton = Tkinter.Button(self, text="Stop Stream", command=self.onStopButtonClick)
		self.clearOutButton = Tkinter.Button(self, text="Clear Output", command=self.onClearButtonClick)
		self.textOut = Tkinter.Text(self)
		self.outScroll = Tkinter.Scrollbar(self)
		self.textOut.grid(column=0,row=1,columnspan=2,pady=(10,10),padx=(10,25),sticky='NSEW')
		self.textOut.bind("<Key>", lambda e: "break")
		self.totalText.grid(column=2,row=1,sticky='NW',pady=(10,0))
		self.totalNum.grid(column=3,row=1,sticky='NW',pady=(10,0))
		self.posText.grid(column=2,row=1,sticky='NW',pady=(30,0))
		self.posNum.grid(column=3,row=1,sticky='NW',pady=(30,0))
		self.neuText.grid(column=2,row=1,sticky='NW',pady=(50,0))
		self.neuNum.grid(column=3,row=1,sticky='NW',pady=(50,0))
		self.negText.grid(column=2,row=1,sticky='NW',pady=(70,0))
		self.negNum.grid(column=3,row=1,sticky='NW',pady=(70,0))
		self.keywordText.grid(column=0,row=0,sticky='W',pady=(10,0))
		self.keywordEntry.grid(column=1,row=0,sticky='EW',padx=(0,10),pady=(10,0))
		self.keywordButton.grid(column=2,row=0,padx=(0,10),pady=(10,0))
		self.clearOutButton.grid(column=2,row=1,sticky='S',pady=(0,10))
		self.stopStreamButton.grid(column=3,row=0,padx=(0,5),pady=(10,0))
		self.textOut.configure(yscrollcommand=self.outScroll.set)
		self.outScroll.configure(command=self.textOut.yview)
		self.outScroll.grid(column=1,row=1,sticky='NSE',padx=(10,10),pady=(10,10))
		self.grid_columnconfigure(1,weight=1)
		self.grid_rowconfigure(1,weight=1)

	def onStartButtonClick(self):
		if pattern.match(self.keywordString.get()):
			tkMessageBox.showwarning("Warning", "No keywords input. Please enter a keyword to start streaming tweets.")
		else:
			if not self.startedStream:
				self.startedStream = True
				self.textOut.insert(Tkinter.END, "Started Stream\n")
				self.textOut.see(Tkinter.END)
				self.t = streamThread(self.keywordString.get())
				self.t.daemon = True
				self.t.start()
			else:
				tkMessageBox.showwarning("Warning", "Tweets are currently streaming. Please stop the current stream before starting another.")

	def onStopButtonClick(self):
		if self.startedStream:
			self.t.stop()
			self.textOut.insert(Tkinter.END, "Ended Stream\n")
			self.textOut.see(Tkinter.END)
			self.startedStream = False
		else: 
			tkMessageBox.showwarning("Warning", "There is currently no stream running to stop.")

	def onClearButtonClick(self):
		global totalNumTweets
		global posTweets
		global neuTweets
		global negTweets
		self.textOut.delete('1.0',Tkinter.END)
		self.totalNum['text'] = "0"
		self.posNum['text'] = "0"
		self.neuNum['text'] = "0"
		self.negNum['text'] = "0"
		totalNumTweets = 0
		posTweets = 0
		negTweets = 0
		neuTweets = 0

def main():
	global app
	app = app_tk(None)
	app.title('TwitStream')
	app.minsize(830,445)
	app.mainloop()
	
if __name__ == '__main__':
	main()
