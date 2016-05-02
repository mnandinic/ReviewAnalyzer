from Tkinter import *
import tkMessageBox
from stripogram import html2text
import requests
from nbtestLatest import classifyReviews
from BeautifulSoup import BeautifulSoup


class App:
  def __init__(self, master):
    "Code to make the APP full screen"
    self.reviewList=[]
    self.ratingList=[]
    self.positiveRatings=0
    self.negativeRatings=0
    self.URLtext=StringVar()
    self.requestCriteria="?sort_by=date_desc"
    self.master=master
    "This is a label widget that holds the result"
    self.RatingSummary=None
    "Configure the Master Layout"
    pad=3
    self._geom='200x200+0+0'
    master.geometry("{0}x{1}+0+0".format(
    master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
    master.bind('<Escape>',self.toggle_geom)
    for r in range(6):
        self.master.rowconfigure(r, weight=1)
    for c in range(5):
        self.master.columnconfigure(c, weight=1)
        #Button(master, text="Button {0}".format(c)).grid(row=6,column=c,sticky=E+W)
    "Configure Buttons"
    buttonFrame = Frame(master, bg="red")
    buttonFrame.grid(row = 0, column = 0, rowspan = 3, columnspan = 1, sticky = W+E+N+S)

    self.analyze = Button(buttonFrame,background="antiquewhite",
                          text="Analyze Reviews",
                          command=self.analyze_results,font="Arial 10 bold",height =23)
    self.analyze.pack(fill=X)
    self.display = Button(buttonFrame,background="antiquewhite",
                            text="Display Results",
                            command=self.display_results,font="Arial 10 bold",height =23)
    self.display.pack(fill=X)
    self.dataFrame = Frame(master)
    self.dataFrame.grid(row = 0, column = 1, rowspan = 6, columnspan = 5, sticky = W+E+N+S)
    self.addressBar = Entry(self.dataFrame,textvariable=self.URLtext)
    self.addressBar.pack(fill=X)
    self.addressBar.focus_set()

    self.scrollBar = Scrollbar(self.dataFrame)
    self.scrollBar.pack(side=RIGHT, fill=Y)

    self.dataText=Text(self.dataFrame, height=50,width=100)
    self.dataText.pack(fill=Y)

    self.scrollBar.config(command=self.dataText.yview)
    self.dataText.config(yscrollcommand=self.scrollBar.set)


  def reset_data(self):
        self.reviewList=[]
        self.ratingList=[]
        self.positiveRatings=0
        self.negativeRatings=0

  def analyze_results(self):
    #print "Put the code here to analyze the reviews"
    try:
        self.reset_data()
        if self.RatingSummary is not None:
            self.RatingSummary.pack_forget()
        self.dataText.pack(fill=Y)
        rdata=requests.get(self.URLtext.get()+self.requestCriteria)
        #url=self.URLtext.get()
        soup=BeautifulSoup(rdata.content)
        reviewSections=soup.findAll("div",{"class":"review-wrapper"})
        if len(reviewSections) !=0:
            reviewSections.pop(0)
        for reviewSection in reviewSections:
            reviewContent= reviewSection.findAll('p')[0]
            self.reviewList.append(html2text(reviewContent.text))
        #tkMessageBox.showinfo("URL entered",self.reviewList[0])
        self.dataText.delete('1.0',END)
        reviewText=""
        for review in self.reviewList:
            reviewText=reviewText+review+("\n"*3)
        self.dataText.insert(END, reviewText)
        reviewSentiments=classifyReviews(self.reviewList)
        for reviewSentiment in reviewSentiments:
            if(reviewSentiment)=="pos":
                self.positiveRatings+=1
            if(reviewSentiment)=="neg":
                self.negativeRatings+=1



    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise


  def display_results(self):
     #tkMessageBox.showinfo("Display Results","Display Results")
     self.dataText.pack_forget()
     if len(self.reviewList)==0:
        sentimentAnalysisResultText="No reviews available"
        self.RatingSummary = Label(self.dataFrame, text=sentimentAnalysisResultText,font="Arial 20 bold",width=45)
        self.RatingSummary.pack(fill=Y)
     else:
         sentimentAnalysisResultText=("Number of positive reviews: "+str(self.positiveRatings)+"\n"\
                                 +"Number of negative reviews:"+str(self.negativeRatings))
         self.RatingSummary = Label(self.dataFrame, text=sentimentAnalysisResultText,font="Arial 20 bold",width=45)
         self.RatingSummary.pack(fill=Y)

         # rankmeterlength=(positiveRatings/numberOfRatings)*100
         # rankmeterColor="green"
         # if rankmeterlength==50:
         #     rankmeterColor="yellow"
         # if rankmeterlength<50:
         #     rankmeterColor="red"



  def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        print(geom,self._geom)
        self.master.geometry(self._geom)
        self._geom=geom


root = Tk()
app = App(root)
root.mainloop()