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
allTweetsOut = ""
posTweetsOut = ""
negTweetsOut = ""
neuTweetsOut = ""
showVar = None
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
		global posTweetsOut
		global negTweetsOut
		global neuTweetsOut
		global allTweetsOut
		sid = SentimentIntensityAnalyzer()
		if self.stopStream == False: 
			if "RT" not in status.text[0:3]:
				tweet = "".join(i for i in status.text if ord(i)<128)
				totalNumTweets += 1
				app.totalNum['text'] = str(totalNumTweets)
				print tweet
				scores = sid.polarity_scores(tweet)
				print(scores)				

				if scores['compound'] >= .3:
					posTweets += 1;
					app.posNum['text'] = str(posTweets)
					insert1 = "--------------------------------------------------------------------------------\n"
					insert2 = tweet + "\n\nScore: " + str(scores['compound']) + "\n\n"
					if app.currView == "Pos" or app.currView == "All":
						app.textOut.insert(Tkinter.END, insert1)
						app.textOut.insert(Tkinter.END, insert2, "POS")
					allTweetsOut += insert1 + insert2
					posTweetsOut += insert1 + insert2			
					app.textOut.see(Tkinter.END)					
				elif scores['compound'] <= -.3:
					negTweets += 1;					
					app.negNum['text'] = str(negTweets)
					insert1 = "--------------------------------------------------------------------------------\n"
					insert2 = tweet + "\n\nScore: " + str(scores['compound']) + "\n\n"
					if app.currView == "Neg" or app.currView == "All":
						app.textOut.insert(Tkinter.END, insert1)
						app.textOut.insert(Tkinter.END, insert2, "NEG")
					allTweetsOut += insert1 + insert2
					negTweetsOut += insert1 + insert2
					app.textOut.see(Tkinter.END)				
				else:					
					neuTweets += 1;
					app.neuNum['text'] = str(neuTweets)
					insert1 = "--------------------------------------------------------------------------------\n"
					insert2 = tweet + "\n\nScore: " + str(scores['compound']) + "\n\n"
					if app.currView == "Neu" or app.currView == "All":
						app.textOut.insert(Tkinter.END, insert1)
						app.textOut.insert(Tkinter.END, insert2, "NEU")
					allTweetsOut += insert1 + insert2
					neuTweetsOut += insert1 + insert2
					app.textOut.see(Tkinter.END)
				return True
		else:
			return False

class app_tk(Tkinter.Tk):
	def __init__(self,parent):
		Tkinter.Tk.__init__(self, parent)
		self.initialize()
		self.startedStream = False

	def initialize(self):
		global showVar
		self.grid()

		self.keywordString = Tkinter.StringVar()
		self.keywordText = Tkinter.Label(self, text="Keywords: ", background="#62c5ef")
		self.totalText = Tkinter.Label(self, text="Total Tweets: ", background="#62c5ef")
		self.posText = Tkinter.Label(self, text="Positive: ", fg="darkgreen", background="#62c5ef")
		self.neuText = Tkinter.Label(self, text="Neutral: ", fg="blue", background="#62c5ef")
		self.negText = Tkinter.Label(self, text="Negative: ", fg="red", background="#62c5ef")
		self.totalNum = Tkinter.Label(self, text="0", background="#62c5ef")
		self.posNum = Tkinter.Label(self, text="0", background="#62c5ef")
		self.neuNum = Tkinter.Label(self, text="0", background="#62c5ef")
		self.negNum = Tkinter.Label(self, text="0", background="#62c5ef")
		self.keywordEntry = Tkinter.Entry(self, textvariable=self.keywordString, background="#e3ebf7")
		self.keywordButton = Tkinter.Button(self, text="Start Stream", command=self.onStartButtonClick, background="#e3ebf7")
		self.stopStreamButton = Tkinter.Button(self, text="Stop Stream", command=self.onStopButtonClick, background="#e3ebf7")
		self.clearOutButton = Tkinter.Button(self, text="Clear Output", command=self.onClearButtonClick, background="#e3ebf7")
		self.showButton = Tkinter.Button(self, text="Show", command=self.onShowButtonClick, background="#e3ebf7")
		showVar = Tkinter.StringVar(self)
		showVar.set("")
		self.showMenu = Tkinter.OptionMenu(self, showVar, "All", "Pos", "Neu", "Neg")
		self.textOut = Tkinter.Text(self, background="#e3ebf7")
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
		self.keywordButton.grid(column=2,row=0,padx=(0,10),pady=(10,0),sticky='W')
		self.showButton.grid(column=2,row=1,pady=(103,0), sticky='NEW', padx=(0,10))
		self.showMenu.grid(column=3,row=1,sticky='NEW',pady=(100,0), padx=(0,10))
		self.clearOutButton.grid(column=2,row=1,sticky='S',pady=(0,10))
		self.stopStreamButton.grid(column=3,row=0,padx=(0,5),pady=(10,0), sticky='W')
		self.textOut.configure(yscrollcommand=self.outScroll.set)
		self.textOut.insert(Tkinter.END, "Welcome to TwitStream!\n\nEnter a keyword(s) separated by commas, and click \"Start Stream\" to get started.")
		self.outScroll.configure(command=self.textOut.yview)
		self.outScroll.grid(column=1,row=1,sticky='NSE',padx=(10,10),pady=(10,10))
		self.grid_columnconfigure(1,weight=1)
		self.grid_rowconfigure(1,weight=1)

		self.textOut.tag_configure("NEU", foreground="blue")		
		self.textOut.tag_configure("POS", foreground="darkgreen")		
		self.textOut.tag_configure("NEG", foreground="red")

		self.currView = "All"

	def onStartButtonClick(self):
		if pattern.match(self.keywordString.get()):
			tkMessageBox.showwarning("Warning", "No keywords input. Please enter a keyword to start streaming tweets.")
		else:
			if not self.startedStream:
				if totalNumTweets == 0:
					self.textOut.delete('1.0',Tkinter.END)
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
		global allTweetsOut
		global posTweetsOut
		global negTweetsOut
		global neuTweetsOut
		self.textOut.delete('1.0',Tkinter.END)
		self.totalNum['text'] = "0"
		self.posNum['text'] = "0"
		self.neuNum['text'] = "0"
		self.negNum['text'] = "0"
		totalNumTweets = 0
		posTweets = 0
		negTweets = 0
		neuTweets = 0
		allTweetsOut = ""
		posTweetsOut = ""
		neuTweetsOut = ""
		negTweetsOut = ""

	def onShowButtonClick(self):
		global allTweetsOut
		global posTweetsOut
		global negTweetsOut
		global neuTweetsOut
		global showVar

		if showVar.get() == None or showVar.get() == "":
			tkMessageBox.showwarning("Warning", "No view has been selected to show.")
		elif showVar.get() == "All" and self.currView != "All":
			self.textOut.delete('1.0',Tkinter.END)
			self.textOut.insert(Tkinter.END, allTweetsOut)
			self.currView = "All"
		elif showVar.get() == "Pos" and self.currView != "Pos":
			self.textOut.delete('1.0',Tkinter.END)
			self.textOut.insert(Tkinter.END, posTweetsOut)
			self.currView = "Pos"
		elif showVar.get() == "Neg" and self.currView != "Neg":
			self.textOut.delete('1.0',Tkinter.END)
			self.textOut.insert(Tkinter.END, negTweetsOut)
			self.currView = "Neg"
		elif showVar.get() == "Neu" and self.currView != "Neu":
			self.textOut.delete('1.0',Tkinter.END)
			self.textOut.insert(Tkinter.END, neuTweetsOut)
			self.currView = "Neu"

		self.textOut.see(Tkinter.END)

def main():
	global app
	app = app_tk(None)
	app.title('TwitStream')
	app.minsize(845,445)
	app.configure(background="#62c5ef")
	app.iconbitmap('twitstream.ico')
	app.mainloop()
	
if __name__ == '__main__':
	main()
