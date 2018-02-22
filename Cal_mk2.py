import calendar
import datetime
from Tkinter import *
from PIL import Image, ImageTk
import Pathfinder
import ContactTrie
import json
root = Tk()
root.geometry('724x605')
root.config(bg='#FFFFFF')
colors = ['#0C090D','#E8E9F3','#2D3142','#BFC0C0','#FFFFFF']

now = datetime.datetime.now()
Months = {1:'January',
          2:'February',
          3:'March',
          4:'April',
          5:'May',
          6:'June',
          7:'July',
          8:'August',
          9:'September',
          10:'October',
          11:'November',
          12:'December'}
days = {'Sunday':None,
        'Monday':None,
        'Tuesday':None,
        'Wednesday':None,
        'Thursday':None,
        'Friday':None,
        'Saturday':None}

daylist = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']

## this function will be open a specified tkinter object
def inherit(child,parent):
    child.master = parent.master
    child.startday = parent.startday
    
    child.taskpath = parent.taskpath
    child.settingspath = parent.settingspath
    child.contactpath = parent.contactpath
    child.overridepath = parent.overridepath

    child.taskjson = parent.taskjson
    child.settingsjson = parent.settingsjson
    child.contactjson = parent.contactjson
    child.overridesjson = parent.overridesjson

    child.cal = parent.cal
    child.month = parent.month

    child.customers = parent.customers
    child.firstnames = parent.firstnames
    child.lastnames = parent.lastnames
    child.activedays = parent.activedays

    child.jobtypes = parent.jobtypes

    child.startlocation = parent.startlocation
##This is a job object, specifying where the job is, who placed the order, and how long it will take
class Task:
    def __init__(self,date,street,city,job,name,phone):
        self.date = date
        self.address = (street,city)
        self.job = job
        self.duration = 0
        self.addressString = str(street) + ' ' +str(city)
        self.name = name
        self.phone = phone

    def addTime(self,duration):
        self.duration = duration

    #this is just to make sure it doesnt fuck up
    def showYourself(self):
        print self.date
        print self.address
        print self.job
        print self.duration
##This is a calendar day object,
class Timeslot:
    def __init__(self):
        self.date = False
        self.outframe = None
        self.button = None
        self.label = None
        self.inframe = None
        self.tasklist = []
        self.tasktitle = False

    def addTask(self,task):
        self.tasklist.append(task)

    def getTotalTime(self):
        net = 0
        for x in self.tasklist:
            net+=x.duration
        return net

class Schedule:
    def __init__(self,master,contactpath,taskpath,settingspath,overridepath):
        self.master = master#the containing box (root)
        self.month = now.month
        self.activedays = [] #this will contain a list of all days with jobs on them
        self.contactpath = contactpath
        self.taskpath = taskpath
        self.settingspath = settingspath
        self.overridepath = overridepath

        '''
        self.contactpath = 'C:\Timely\Files\contacts.json'
        self.taskpath = 'C:\Timely\Files\\tasklog.json'
        self.settingspath = 'C:\Timely\Files\settings.json'
        self.overridepath = 'C:\Timely\Files\overrides.json'
        '''
        self.sidebool = False ## If the side panel is open or not
        self.cal = {}## dictionary of calendar objects (by index, meaning they start at 0 on the first sunday. They are separate from date)
        self.customers = ['No customer data']

        self.firstnames = ContactTrie.Trie()##empty trie objects, used to store first and last names
        self.lastnames = ContactTrie.Trie()

        self.create(now.month,now.year)## this runs all the neccessary functions to open the calendar widget

    ##load all of the data from the specified paths
    '''
    Contacts.json will contain the following data structure
        {
           contacts:{name:[phone,address,[(job,date),(job,date)]},
           lastnames: {lastname:[associated names]},
           firstnames: {firstnames:[associated names]}
        }

    tasklog.json will contain the following data structure
        {
            Month:{
                index:[[date,street,city,job,name,phone],[date,street,city,job,name,phone]]
            }
        }
     settingsjson will have the folling data structure
        {
           'jobtypes':{name:average time},
           'startlocation':address,
           'emails':{name:email},
        }
    Overrides.json will have the following data structure
        {
            Month:{
                index: list or False
            }
        }
    '''
    def loadCon(self):
        try:
            with open(self.contactpath,'r+') as contactval:
                self.contactjson = json.load(contactval)
                if len(self.contactjson['contacts']) > 0:
                       self.customers = [x.title() for x in self.contactjson['contacts']]
        except ValueError:
            self.contactjson = {'contacts':{},'lastnames':{},'firstnames':{}}
        for x in self.contactjson['firstnames']:
            self.firstnames.add(x.lower())
        for x in self.contactjson['lastnames']:
            self.lastnames.add(x.lower())

    def loadTask(self,month):
        try:
            with open(self.taskpath,'r+') as taskval:
                self.taskjson = json.load(taskval)
        except ValueError:
            self.taskjson = {str(x):{} for x in range(1,13)}

        for index in self.taskjson[str(month)]:
            for task in self.taskjson[str(month)][str(index)]:
                newTask = Task(task[0],task[1],task[2],task[3],task[4],task[5])
                newTask.addTime(int(self.settingsjson['jobtypes'][task[3]]))
                Addys = [x.address for x in self.cal[int(index)].tasklist]
                if (task[1],task[2]) in Addys:
                    pass
                else:
                    self.cal[int(index)].addTask(newTask)
    def loadSet(self):
        try:
            with open(self.settingspath,'r+') as setval:
                self.settingsjson = json.load(setval)

        except ValueError:
            self.settingsjson = {'jobtypes':{'job1':0,'job2':0},'startlocation':'','emails':{}}
        self.jobtypes = [x.title() for x in self.settingsjson['jobtypes']]
        self.startlocation = self.settingsjson['startlocation']

    def loadOver(self):
        try:
            with open(self.overridepath,'r+') as overval:
                self.overridesjson = json.load(overval)
        except ValueError:
            self.overridesjson = {x:None for x in range(1,13)}
            for x in self.overridesjson:
                self.overridesjson[x] = {y:False for y in range(36)}

    def load(self,month):
        self.loadOver()
        self.loadSet()
        self.loadCon()
        self.loadTask(month)
        
    def create(self,month,year):
        self.build(month,year)
        self.load(month)
        self.display()
        
    #Now to build the calendar
    def getMonthLength(self,year,month):
        return calendar.monthrange(year,month)[1]

    def build(self,month,year):
        self.startday = self.startday = calendar.monthrange(year,month)[0]
        if self.startday ==6:
            self.startday=-1
            
        self.titsle = Label(self.master,
                            font = ('Verdana',14),
                            text='Be Timely.',
                            bg='#fffffc',
                            height=1)
        self.titsle.grid(row=0,column=0,)
        
        self.line = Canvas(self.master,width=650,height=3,bg='#fffffc',relief='flat')
        self.line.create_line(-100,0,1024,0,width=13,fill='#2F97C1')
        self.line.grid(row=1,columnspan=7,sticky='NW',padx=5)
        #GLOBAL BUTTONS
        #These buttons are on the opening page
        self.options = Button(self.master,
                              height=2,
                              width=5,
                              relief='flat',
                              text='Open',
                              bg='#2F97C1',
                              font=('Verdana',10),
                              fg='#fffffc',
                              activebackground = '#2F97C1',
                              activeforeground='#fffffc',
                              command = lambda: self.openSidebar())
        self.options.grid(row=0,column=6,sticky='NE')
        
        self.header = Label(self.master,
                            text=Months[month]+' ' + str(year),
                            width="30",
                            height="2",
                            fg=colors[2],
                            bg=colors[4],
                            font= ("Verdana",18),
                            justify='center',
                            borderwidth=1)
        self.header.grid(row=2,column=0,columnspan=7)
        
        self.nextmonth = Button(self.master,
                                text='Next Month',
                                relief='flat',
                                command=lambda x=(month+1)%12: self.create(x,year),
                                font=('Verdana',10),
                                fg='#fffffc',
                                bg='#2F97C1',
                                activebackground = '#2F97C1',
                                activeforeground='#fffffc')
        self.nextmonth.grid(row=2,column=6)

        self.lastmonth = Button(self.master,
                                text='Last Month',
                                relief='flat',
                                command=lambda x=(month-1)%12: self.create(x,year),
                                bg='#2F97C1',
                                font=('Verdana',10),
                                fg='#fffffc',
                                activebackground = '#2F97C1',
                                activeforeground='#fffffc')
        self.lastmonth.grid(row=2,column=0)

        
        self.sidebar = Frame(self.master,height = 700,width=200,bg='#fcfcfc')
        
        ##The following buttons appear in the sidebar and are only visible when open
        self.settings = Button(self.sidebar,
                               text='Settings',
                               command = lambda:Settings(self),
                               width = 19,
                               font=('Verdana',10),
                                fg='#fffffc',
                                bg='#2F97C1',
                                activebackground = '#2F97C1',
                                activeforeground='#fffffc')

        

        self.addjobC = Button(self.sidebar,
                               text='Add Job & Customer',
                               command = lambda:Job(self),
                               font=('Verdana',10),
                                width = 19,
                                fg='#fffffc',
                                bg='#2F97C1',
                                activebackground = '#2F97C1',
                                activeforeground='#fffffc')

        self.addjobNC = Button(self.sidebar,
                               text='Add Job from Customer',
                               command = lambda: Job(self,False),
                               font=('Verdana',10),
                                width = 19,
                                fg='#fffffc',
                                bg='#2F97C1',
                                activebackground = '#2F97C1',
                                activeforeground='#fffffc')
        
        
##        self.closebutton = Button(self.sidebar,
##                               text='Close',
##                               command = lambda:self.close(),
##                               font=('Verdana',10),
##                                width = 19,
##                                fg='#fffffc',
##                                bg='#2F97C1',
##                                activebackground = '#2F97C1',
##                                activeforeground='#fffffc')
        self.contacts = Button(self.sidebar,
                               text='Contacts',
                               command = lambda:Contacts(self),
                               font=('Verdana',10),
                                width = 19,
                                fg='#fffffc',
                                bg='#2F97C1',
                                activebackground = '#2F97C1',
                                activeforeground='#fffffc')
        
        self.settings.grid(row=5,pady=5,padx=2)
        self.addjobC.grid(row=1,pady=5,padx=2)
        self.addjobNC.grid(row=2,pady=5,padx=2)
        self.contacts.grid(row=4,pady=5,padx=2)
        #self.closebutton.grid(row=3,pady=5,padx=2)
        ##END OF GLOBAL BUTTONS
        count=0
        for x in days:
            days[x] = Label(self.master,
                            text=daylist[count],
                            width=14,
                            height=2,
                            bg = '#fffffc',
                            fg = '#0f0f0f',
                            relief='sunken',
                            borderwidth=1,
                            font=('Arial Bold',9))
            days[x].grid(column=count,row=3)
            count+=1

        #Now to build the actual blocks on the calendar
        col=0
        r=4
        for x in range(36):
            if x > self.startday and (x- self.startday) <= self.getMonthLength(year,month):
                self.cal[x] = Timeslot()
                
                self.cal[x].date = x-self.startday
                
                self.cal[x].outframe = Frame(self.master,
                                             width=103,
                                             height=90,
                                             bg='#fffffd',
                                             relief='raised',
                                             borderwidth=1,)
                
                self.cal[x].button = Button(self.cal[x].outframe,
                                            text='View',
                                            relief='flat',
                                            width=7,
                                            height=1,
                                            bg='#fffffd',
                                            #fg = '#0f0f0f',
                                            fg='#2F97C1',
                                            borderwidth=1,
                                            command = lambda y=x: View(self,y))
                ###THE ABOVE MIGHT BE SUBJECT TO CHANGE
                
                self.cal[x].label = Label(self.cal[x].outframe,
                                          text=self.cal[x].date,
                                          width=2,
                                          height=1,
                                          bg='#fffffd',
                                          fg = '#0f0f0f',
                                          justify='left')
                
                self.cal[x].inframe = Frame(self.cal[x].outframe,
                                             width=100,
                                             height=65,
                                             bg=colors[1])
                self.cal[x].tasklist = []
                
                self.cal[x].outframe.grid(column=col,row=r)
                self.cal[x].button.grid(sticky='NW',row=1,column=4,ipadx=0)
                self.cal[x].label.grid(sticky='NE',row=1,column=0,ipadx=0)
                self.cal[x].inframe.grid(sticky='S',row=2,column=0,columnspan=5)

            else:
                self.cal[x] = Timeslot()
                self.cal[x].date = False
                self.cal[x].outframe = Frame(self.master,
                                             width=103,
                                             height=90,
                                             bg=colors[1],
                                             relief='raised',
                                             borderwidth=1,)
                                       
                self.cal[x].outframe.grid(column=col,row=r)
            if col == 6:
                col=0
                r+=1
            else:
                col+=1
    def display(self):
        for x in self.cal:
            if self.cal[x].date:
                length = len(self.cal[x].tasklist)
                if length>0:
                    if self.cal[x].tasktitle:
                        self.cal[x].tasktitle.config(text = str(length) + ' tasks',)
                    else:
                        self.cal[x].tasktitle = Label(self.cal[x].inframe,
                                                      text = str(length) + ' task',
                                                      width=13,
                                                      height=4,
                                                      font = ('Arial Bold',9),
                                                      bg='#f0ffff',
                                                      fg = '#0f0f0f')
                    self.cal[x].tasktitle.pack()
                
    def openSidebar(self):
        self.sidebool = not self.sidebool
        if self.sidebool:
            self.options.config(text='Close')
            self.sidebar.grid(column=7,row=0,rowspan=10)
            root.geometry('892x605')
        if not self.sidebool:
            self.options.config(text='Open')
            self.sidebar.grid_forget()
            root.geometry('724x605')
    def warning(self,alist):
        window = Toplevel(self.master,bg='#fffffc')
        
        count = 0
        labels = [Label(window,text=x) for x in alist]
        for x in range(len(labels)):
            labels[x].grid(row=count)
            count+=1
            
    def save(self,f=False,warning=False):
        if not f:
            with open(self.taskpath,'w+') as f:
                json.dump(self.taskjson,f)
            with open(self.contactpath,'w+') as g:
                json.dump(self.contactjson,g)
            with open(self.settingspath,'w+') as h:
                json.dump(self.settingsjson,h)
            with open(self.overridepath,'w+') as j:
                json.dump(self.overridesjson,j)
        else:
            if f==1:
                with open(self.taskpath,'w+') as f:
                        json.dump(self.taskjson,f)
            elif f==2:
                with open(self.contactpath,'w+') as g:
                    json.dump(self.contactjson,g)
            elif f==3:
                
                with open(self.settingspath,'w+') as h:
                    json.dump(self.settingsjson,h)
                if warning:
                    self.warning(['All Settings Saved Successfully'])
                self.loadSet()
            elif f==4:
                with open(self.overridepath,'w+') as j:
                    json.dump(self.overridepath,j)

class View:
    def __init__(self,schedule,C=True):
        inherit(self,schedule)
        self.schedule = schedule
        self.master = Toplevel(schedule.master)
        cal_index = C
        self.go(self.month,cal_index)

    def go(self,month,cal_index):
        if not self.overridesjson[month][cal_index]:
            if len(self.startlocation)>0:
                ll = ''
                header = Label(self.master,
                               text='Schedule for ' + str(Months[month])+' '+str(self.cal[cal_index].date),
                               bg = '#fffffc',
                               font = ('Verdana',11))
                header.grid(row=1,sticky='NW')
                
                self.line = Canvas(self.master,width=256,height=3,bg='#fffffc',relief='flat')
                self.line.create_line(-100,0,300,0,width=13,fill='#2F97C1')
                self.line.grid(row=2,columnspan=7,sticky='NW')
                
                listbox = Listbox(self.master,
                                  height=20,
                                  width=40,
                                  bg = "#ffffff",
                                  font = ('Arial Bold',10),
                                  fg = '#0f0f0f',
                                  selectbackground = '#fffffc',
                                  selectforeground = '#0f0f0f',
                                  relief = 'flat',
                                  activestyle = None)
                listbox.grid(pady=5,column=0)
                try:
                    tasklist = self.cal[cal_index].tasklist
                    jobandAddy = {}
                    for x in tasklist:
                        jobandAddy[x.addressString] = x.job
                    addressbook = Pathfinder.addressbook([x.addressString for x in tasklist] + [self.startlocation])
                    travelPath = addressbook.traveller(self.startlocation)[0]
                    count = 1
                    for x in travelPath:
                        listbox.insert(END,str(count)+'.    '+x)
                        listbox.insert(END,'         > '+ jobandAddy[x].title())
                        count+=1
                except KeyError:
                    #warning(['Error: Address on',self.cal[cal_index].date,'Not Recognized']
                    pass
            else:
                #warning(['Please enter a start location in settings','before a list can be viewed'])
                pass
        else:
            print 'eat a balls'

class Job:
    def __init__(self,schedule,C=True):
        colo = '#E8E9F3'
        colo2 = '#fffff9'
        inherit(self,schedule)
        self.schedule = schedule
        Adder = Toplevel(schedule.master)
        newjob = Frame(Adder,
                       width = 500,
                       height=300,
                       bg = colors[1])
        newjob.pack()

        street = Label(newjob,
                       text='Street Address',
                       justify='left',
                       font=('Arial',12),
                       bg = colo)
        
        city = Label(newjob,
                     text='City and Province',
                     justify='left',
                     font=('Arial',12),
                     bg = colo)
        
        self.streetEntry = Entry(newjob,
                            width=40,
                            bg = colo2)
        
        self.cityEntry = Entry(newjob,
                          width=40,
                          bg = colo2)
        
        customername = Label(newjob,
                       text='Customer Name',
                       justify='left',
                       font=('Arial',12),
                       bg = colo)
        
        self.CustomerFNameEntry = Entry(newjob,width=18,bg=colo2)
        self.CustomerLNameEntry = Entry(newjob,width=18,bg=colo2)

        customerphone = Label(newjob,
                              text='Customer Phone',
                              font=('Arial',12),
                              bg=colo)
        
        self.CustomerPhoneEntry = Entry(newjob,width=40,bg=colo2)
        
        self.jobvar = StringVar(self.master)
        self.jobvar.set('Select a Job type                ')
        
        jobtype = OptionMenu(newjob,self.jobvar,*self.jobtypes)
        jobtype.config(width=30)

        jobdate = Label(newjob,
                        text='Job Date',
                        justify='left',
                        font=('Arial',12),
                        bg = colo)

        self.dateEntry = Entry(newjob,
                          width=40,
                          bg = colo2)
        self.dateEntry.insert(END,'Optimal')
        
        
        AddJob = Button(newjob,
                        text='Add Job',
                        width=13,
                        height=5,
                        font=('Verdana',10),
                        fg='#fffffc',
                        bg='#2F97C1',
                        activebackground = '#2F97C1',
                        activeforeground='#fffffc',)
        if C:
            AddJob.config(command = lambda: self.NewJob(self.month))
        if not C:
            AddJob.config(command = lambda: self.NewJob(self.month,False))
                 
            
        
        
        self.cvar = StringVar(self.master)
        self.cvar.set('No Customer')
        
        self.CustomerSelect = OptionMenu(newjob,self.cvar,*self.customers)
        self.CustomerSelect.config(width=30)
        self.CustomerSelect['menu'].config(bg='#fffffc')

        street.grid(row=2,column=0,columnspan=2)
        city.grid(row=2,column=2)
        
        
        if C:
            customername.grid(row=0,column=0,pady=5)
            self.CustomerFNameEntry.grid(row=1,column=0,padx=5)
            self.CustomerLNameEntry.grid(row=1,column=1,padx=5)
            customerphone.grid(row=0,column=2,pady=5)
            self.CustomerPhoneEntry.grid(row=1,column=2,padx=5)

        if not C:
            self.CustomerSelect.grid(row=9,columnspan=2)
            

        self.streetEntry.grid(row=3,column=0,columnspan=2,padx=5)
        self.cityEntry.grid(row=3,column=2,padx=5)
        self.dateEntry.grid(row=6,column=0,columnspan=2)
        jobtype.grid(row=7,column=0,columnspan=2,pady=10)
        jobdate.grid(row=5,column=0,columnspan=2,padx=5,pady=10)
        
        AddJob.grid(column=2,row=4,rowspan=5,pady=5)
    def NewJob(self,month,C=True):
        ##determine if they are adding a customer or not
        if C:
            task = Task(self.dateEntry.get(),
                        self.streetEntry.get(),
                        self.cityEntry.get(),
                        self.jobvar.get(),
                        (self.CustomerFNameEntry.get(),self.CustomerLNameEntry.get()),
                        self.CustomerPhoneEntry.get())

            task.addTime(self.settingsjson['jobtypes'][self.jobvar.get().lower()])
            NameValue = self.CustomerFNameEntry.get()+' '+self.CustomerLNameEntry.get()
            
        if not C:
            NameValue = self.cvar.get().split()[0] + ' ' + self.cvar.get().split()[1]
            task = Task(self.dateEntry.get(),
                        self.streetEntry.get(),
                        self.cityEntry.get(),
                        self.jobvar.get(),
                        (self.cvar.get().split()[0],self.cvar.get().split()[1]),
                        self.contactjson['contacts'][NameValue.lower()][0])
            task.addTime(self.settingsjson['jobtypes'][self.jobvar.get().lower()])

        ## display the new task
        if task.date != 'Optimal':
            index = int(task.date) + self.startday 
            if len(self.cal[int(task.date) + self.startday].tasklist) ==0:
                self.activedays.append(int(task.date) + self.startday)
            self.cal[index].tasklist.append(task)
        else:
            ###Add to the day that adds the least amount of time
            ### not the day with the least jobs, but the day that adding the job adds the least amount of time
            ### open warning stating what day
            ###show the top 3 possible days
            pass
        self.schedule.display()

        newtask = [self.dateEntry.get().lower(),
                       self.streetEntry.get().lower(),
                       self.cityEntry.get().lower(),
                       self.jobvar.get().lower(),
                       NameValue.lower(),
                       self.CustomerPhoneEntry.get()]
        
        if index not in self.taskjson[str(self.month)]:
            self.taskjson[str(month)][index] = [newtask]
        else:
            pass
        if newtask not in self.taskjson[str(self.month)][index]:
            self.taskjson[str(self.month)][index].append(newtask)
        else:
            pass
        self.addContact(NameValue,
                        self.CustomerPhoneEntry.get(),
                        self.streetEntry.get(),
                        self.cityEntry.get(),
                        self.jobvar.get(),
                        self.dateEntry.get(),
                        month)
        ##save the file
        ## go through activedays searching for 2 similar addresses, in the future
        self.schedule.taskjson = self.taskjson
        self.schedult.contactjson = self.contactjson
        self.schedule.save()
        self.schedule.loadCon()
        
    def addContact(self,NameValue,phone,street,city,job,date,month):
        #Contacts.json will contain the following data structure
        #{
        #   contacts:{name:[phone,address,[(job,date),(job,date)]},
        #   lastnames: {lastname:[associated names]},
        #   firstnames: {firstnames:[associated names]}
        #}
        newcontact = (NameValue.lower(),
                          [
                              phone,
                              (street.lower(),city.lower()),
                              [(job.lower(),Months[month]+' '+date.lower())]
                           ])
        ##add to contacts
        if newcontact[0] in self.contactjson['contacts']:
            if newcontact[1][2][0] in self.contactjson['contacts'][newcontact[0]][2]:
                self.warning(['Job already added'])
            else:
                self.contactjson['contacts'][newcontact[0]][2].append(newcontact[1][2][0])
        else:
            self.contactjson['contacts'][newcontact[0]] = newcontact[1]
        ##add to first and last names
        firstname = NameValue.split()[0].lower()
        lastname = NameValue.split()[1].lower()
        if firstname in self.contactjson['firstnames']:
            if NameValue.lower() not in self.contactjson['firstnames'][firstname]:
                self.contactjson['firstnames'][firstname].append(NameValue.lower())
        else:
            self.contactjson['firstnames'][firstname] = [NameValue.lower()]
            
        if lastname in self.contactjson['lastnames']:
            if NameValue.lower() not in self.contactjson['lastnames'][lastname]:
                self.contactjson['lastnames'][lastname].append(NameValue.lower())
        else:
            self.contactjson['lastnames'][lastname] = [NameValue.lower()]

        self.schedule.contactjson = self.contactjson
        self.schedule.save(2)
    

class Contacts:
    def __init__(self,schedule,c=True):
        inherit(self,schedule)
        self.ContactWindow = Toplevel(self.master)
        self.schedule = schedule
        header = Label(self.ContactWindow,
                       text='Contacts:',
                       bg = '#fffffc',
                       font = ('Verdana',11))
        header.grid(row=0,sticky='NW',column=0,columnspan=2)
        addcontact = Button(self.ContactWindow,
                            text='Add Contact',
                            height=1,
                            width=12,
                            relief = 'flat',
                            bg='#2F97C1',
                            font=('Verdana',10),
                            fg='#fffffc',
                            activebackground = '#2F97C1',
                            activeforeground='#fffffc',)
        #addcontact.grid(row=0,column=1)
        self.line = Canvas(self.ContactWindow,width=256,height=3,bg='#fffffc',relief='flat')
        self.line.create_line(-100,0,300,0,width=13,fill='#2F97C1')
        self.line.grid(row=1,columnspan=7,sticky='NW')
        ContactButtons = {}
        count=2
        for x in self.customers:
            ContactButtons[x] = Button(self.ContactWindow,
                                       height=2,
                                       width=20,
                                       text=x,
                                       relief = 'flat',
                                       bg = '#fffffc',
                                       fg = '#0d75a0',
                                       activeforeground = '#fffffc',
                                       activebackground = '#0d75a0',
                                       border = 1,
                                       font = 16,
                                       command = lambda y=x: self.viewContact(y))
            ContactButtons[x].grid(row=count,column=0)
            count+=1

    def viewContact(self,contact):
        #Contacts.json will contain the following data structure
        #{
        #   contacts:{name:[phone,address,[(job,date),(job,date)]},
        #   lastnames: {lastname:[associated names]},
        #   firstnames: {firstnames:[associated names]}
        #}
        self.ContactView = Toplevel(self.master)
        contactfile = self.contactjson['contacts'][contact.lower()]
        conFrame = Frame(self.ContactView,bg='#fffffc',height=300,width=400)
        conFrame.pack()
        title = Label(conFrame,
                      text=contact,
                      fg = '#0d75a0',
                      font=17,
                      bg='#fffffc')
        title.grid(column=0,row=0)
        PNL = Label(conFrame,text='Phone Number: ',bg='#fffffc')
        PN = Entry(conFrame,width=40)
        PN.insert(END,contactfile[0])

        PNL.grid(row=1,column=0,pady=20,padx=7)
        PN.grid(row=1,column=1,pady=20,padx=7)

        AL = Label(conFrame,text='Address: ',bg='#fffffc')
        A = Entry(conFrame,width=40)
        A.insert(END,contactfile[1][0]+' '+contactfile[1][1])

        AL.grid(row=2,column=0,pady=20,padx=7)
        A.grid(row=2,column=1,pady=20,padx=7)

        JHL = Label(conFrame,text='Job History: ',bg='#fffffc')
        jobhistory = Listbox(conFrame,width=40)

        for x in contactfile[2]:
            jobhistory.insert(END,'  '+ x[0] +':                 '+ x[1])
        JHL.grid(row=3,column=0)
        jobhistory.grid(row=3,column=1)

        conSave = Button(conFrame,
                         text='Save',
                         width=24,
                         height=1,
                         font=('Verdana',10),
                         fg='#fffffc',
                         bg='#2F97C1',
                         activebackground = '#2F97C1',
                         activeforeground='#fffffc',
                         command = lambda: self.updateContact(contact,PN.get(),A.get()))

        conSave.grid(row=4,columnspan=2,pady=10)

        conDelete = Button(conFrame,
                         text='Delete Contact',
                         width=24,
                         height=1,
                         font=('Verdana',10),
                         fg='#fffffc',
                         bg='#2F97C1',
                         activebackground = '#2F97C1',
                         activeforeground='#fffffc',
                         command = lambda: self.deleteContact(contact))

        conDelete.grid(row=5,columnspan=2,pady=10)
        
    def newContact(self):
        contactwindow = Toplevel(self.master)
        
    def updateContact(self,contact,pn=False,addy=False):
        if pn and addy:
            self.contactjson['contacts'][contact][0] = pn
            self.contactjson['contacts'][contact][1] = addy
        elif pn:
            self.contactjson['contacts'][contact][0] = pn
        elif addy:
            self.contactjson['contacts'][contact][1] = addy

        self.schedule.contactjson = self.contactjson
        self.schedule.save(2)
            
    def deleteContact(self,contact):
        del self.contactjson['contacts'][contact.lower()]
        self.customers.remove(contact)
        self.ContactView.destroy()
        self.ContactWindow.destroy()
        Contacts(self)

class Settings:
    def __init__(self,schedule,c=True):
        inherit(self,schedule)
        self.schedule = schedule
        settings = Toplevel(schedule.master)
        SettingHeader = Label(settings,
                              font = ('Verdana',11),
                              text='Timely Settings',
                              bg=colors[1],
                              height=1)
        SettingHeader.grid(row=0,columnspan=2,sticky='W')
        setline = Canvas(settings,width=256,height=3,bg=colors[1],relief='flat')
        setline.create_line(0,0,300,0,width=17,fill='#2F97C1')

        jobsetLabel = Label(settings,
                            text='Jobtypes         ',
                            bg=colors[1],
                            fg='#000000',
                            font=('Arial Bold',9))
        
        self.joblist = Listbox(settings,width=40,height=10)
        
        
        self.jobEntry = Entry(settings,
                         width=19)
        self.jobEntry.insert(END,'Job Title')
        
        self.timeEntry = Entry(settings,
                         width=16)
        self.timeEntry.insert(END,'Time required')
        
        jobsetButton = Button(settings,
                              text='Add',
                              font=('Verdana',9),
                              width = 12,
                              fg='#fffffc',
                              bg='#2F97C1',
                              activebackground = '#2F97C1',
                              activeforeground='#fffffc',
                              command = lambda: self.editSettings('job'))
        jobremoveButton = Button(settings,
                                text='Remove Selected',
                                font=('Verdana',9),
                                width = 15,
                                fg='#fffffc',
                                bg='#2F97C1',
                                activebackground = '#2F97C1',
                                activeforeground='#fffffc',
                                 command = lambda: self.editSettings('job',remove=True))
        
        startlocLabel = Label(settings,
                            text='Business Location ',
                            bg=colors[1],
                            fg='#000000',
                            font=('Arial Bold',9))
        
        self.startlocEntry = Entry(settings,
                              width=55)
        self.startlocEntry.insert(END,self.settingsjson['startlocation'])
        
        emailLabel = Label(settings,
                           text='Emails',
                           bg=colors[1],
                           fg='#000000',
                           font=('Arial Bold',9))
        
        self.emaillist = Listbox(settings,width=55,height=7)
        
        self.nameEntry = Entry(settings,width=25)
        self.nameEntry.insert(END,'Name')
        self.emailEntry = Entry(settings,width=27)
        self.emailEntry.insert(END,'Email')

        namesetButton = Button(settings,
                              text='Add',
                              font=('Verdana',9),
                              width = 18,
                              fg='#fffffc',
                              bg='#2F97C1',
                              activebackground = '#2F97C1',
                              activeforeground='#fffffc',
                               command = lambda:self.editSettings('email'))
        nameremoveButton = Button(settings,
                                  text='Remove Selected',
                                  font=('Verdana',9),
                                  width = 18,
                                  fg='#fffffc',
                                  bg='#2F97C1',
                                  activebackground = '#2F97C1',
                                  activeforeground='#fffffc',
                                  command = lambda:self.editSettings('email',remove=True))
        SaveButton = Button(settings,
                              text='Save',
                              font=('Verdana',9),
                              width = 50,
                              fg='#fffffc',
                              bg='#2F97C1',
                              activebackground = '#2F97C1',
                              activeforeground='#fffffc',
                            command = lambda: schedule.save(3,True))
        self.refreshSettings(schedule)
        
        setline.grid(row=1,column=0,columnspan=9,sticky='NW')
        jobsetLabel.grid(column=0,row=2,columnspan=2,sticky=W,padx=3,pady=2)
        self.joblist.grid(row=3,column=0,columnspan=2,rowspan=4,sticky=W,padx=3,pady=2)
        self.jobEntry.grid(column=0,row=8,sticky=W,padx=3,pady=2)
        self.timeEntry.grid(column=1,row=8,sticky=W,padx=3,pady=2)
        jobsetButton.grid(column=1,row=9,sticky=W,pady=4,padx=3)
        jobremoveButton.grid(column=0,row=9,pady=4,padx=3,sticky=W)
        startlocLabel.grid(column=2,row=2,sticky=W,padx=3,pady=2,columnspan=2)
        self.startlocEntry.grid(column=2,row=3,padx=3,pady=2,columnspan=2)
        emailLabel.grid(column=2,row=4,sticky=W,columnspan=2)
        self.emaillist.grid(column=2,row=5,rowspan=2,columnspan=2)
        self.nameEntry.grid(column=2,row=8,padx=3,pady=2,sticky=W)
        self.emailEntry.grid(column=3,row=8,padx=3,pady=2,sticky=W)
        namesetButton.grid(column=3,row=9,sticky=W,pady=4,padx=3)
        nameremoveButton.grid(column=2,row=9,pady=4,padx=3,sticky=W)
        SaveButton.grid(column=0,row=10,columnspan=5,pady=10)

    def refreshSettings(self,schedule):
        self.joblist.delete(0,END)
        self.joblist.insert(END,' Job type                   Job Hours')
        self.emaillist.delete(0,END)
        self.emaillist.insert(END,' Name                              Email')
        
        for key in self.settingsjson['jobtypes']:
            self.joblist.insert(END,' '+key.title() + ':                                    ' + str(self.settingsjson['jobtypes'][key]))
            
        for key in self.settingsjson['emails']:
            self.emaillist.insert(END,' '+key.title()+ ':                       ' + self.settingsjson['emails'][key])
        self.settingsjson['startlocation'] = self.startlocEntry.get()
    
        self.schedule.settingsjson = self.settingsjson
        
        schedule.save(3)
        schedule.loadSet()
        
    def editSettings(self,addtype,remove=False):#actions include add and remove
        if addtype == 'job' and not remove:
            self.settingsjson['jobtypes'][self.jobEntry.get().lower()] = float(self.timeEntry.get())
        elif addtype == 'job':
            jobinfo = self.joblist.get(self.joblist.curselection()).split()
            del self.settingsjson['jobtypes'][jobinfo[0][:-1].lower()]

        if addtype == 'email' and not remove:
            self.settingsjson['emails'][self.nameEntry.get().lower()] = self.emailEntry.get()
        elif addtype == 'email':
            emailinfo = self.emaillist.get(self.emaillist.curselection()).split()
            del self.settingsjson['emails'][emailinfo[0][:-1].lower()]

        self.refreshSettings(self.schedule)
        
def main():
          Schedule(root,
                   'C:\Timely\Files\contacts.json',
                   'C:\Timely\Files\\tasklog.json',
                   'C:\Timely\Files\settings.json',
                   'C:\Timely\Files\overrides.json')
          root.mainloop()
if __name__ == "__main__":
    main()
