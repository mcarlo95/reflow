from tkinter import *
import tkinter as tk
import tkinter.messagebox
import tkinter.simpledialog
import copy
import datetime
groceryList = []

##########################################################
import uuid
import tkinter as tk
from tkinter import ttk

from tkinter import filedialog

def j_tree(tree, parent, dic):
    for key in sorted(dic.keys()):
        uid = uuid.uuid4()
        if isinstance(dic[key], dict):
            tree.insert(parent, 'end', uid, text=key)
            j_tree(tree, uid, dic[key])
        elif isinstance(dic[key], tuple):
            tree.insert(parent, 'end', uid, text=str(key) + '()')
            j_tree(tree, uid,
                   dict([(i, x) for i, x in enumerate(dic[key])]))
        elif isinstance(dic[key], list):
            tree.insert(parent, 'end', uid, text=str(key) + '[]')
            j_tree(tree, uid,
                   dict([(i, x) for i, x in enumerate(dic[key])]))
        else:
            value = dic[key]
            if isinstance(value, str):
                value = value.replace(' ', '_')
            tree.insert(parent, 'end', uid, text=key, value=value)


##def tk_tree_view(data):
##    # Setup the root UI
##    root = tk.Tk()
##    root.title("tk_tree_view")
##    root.columnconfigure(0, weight=1)
##    root.rowconfigure(0, weight=1)
##
##    # Setup the Frames
##    tree_frame = ttk.Frame(root, padding="3")
##    tree_frame.grid(row=0, column=0, sticky=tk.NSEW)
##
##    # Setup the Tree
##    tree = ttk.Treeview(tree_frame, columns=('Values'))
##    tree.column('Values', width=100, anchor='center')
##    tree.heading('Values', text='Values')
##    j_tree(tree, '', data)
##    tree.pack(fill=tk.BOTH, expand=1)
##
##    # Limit windows minimum dimensions
##    root.update_idletasks()
##    root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())
##    root.mainloop()
##
##if __name__ == "__main__":
##    # Setup some test data
##    data = {
##        "firstName": "John",
##        "lastName": "Smith",
##        "gender": "male",
##        "age": 32,
##        "address": {
##            "streetAddress": "21 2nd Street",
##            "city": "New York",
##            "state": "NY",
##            "postalCode": "10021"},
##        "phoneNumbers": [
##            {"type": "home", "number": "212 555-1234"},
##            {"type": "fax",
##             "number": "646 555-4567",
##             "alphabet": [
##                 "abc",
##                 "def",
##                 "ghi"]
##             }
##        ]}


###############################################################
    

def doNothing():
    print("ok nothing works")
#*************for list title ***************    
class My_QueryString(tkinter.simpledialog._QueryString):

      def body(self, master):
          self.bind('<KP_Enter>', self.ok) # KeyPad Enter
          super().body(master)

def myaskstring(title, prompt, **kw):
    d = My_QueryString(title, prompt, **kw)
    return d.result
#************for defining what is in the list*******************    
class My_QueryString(tkinter.simpledialog._QueryString):

      def body(self, master):
          self.bind('<KP_Enter>', self.ok) # KeyPad Enter
          super().body(master)

def list_data(title, prompt, **kw):
    d = My_QueryString(title, prompt, **kw)
    return d.result
root = Tk()

#list
def liststagering(New_List):
   for item in New_List:
      print(item)


def New_List():
    newdict = filedialog.askopenfilename()
    from importlib.util import spec_from_loader, module_from_spec
    from importlib.machinery import SourceFileLoader 
    config_module = spec_from_loader("config_file", SourceFileLoader("config_file", newdict))
    config_data = module_from_spec(config_module)
    config_module.loader.exec_module(config_data)
    dict_name= myaskstring("dict name", "what is the name of the dictionary")
    global data
    data=getattr(config_data, dict_name)
    print(data)
    
    
##    new_list = myaskstring("list", "what do you want to name this list")
##    List_Data = list_data("list","what should be in this list")
##    if str(new_list):
##        print(new_list)
##        newList = dict()
##        newList['title'] = new_list
##        newList['listData'] = List_Data
##        List_MASTER.append(newList)
##        print("title : "+new_list)
##        print(List_Data)
        
List_MASTER = []




lll=print (List_MASTER)
def printtext():
    
    
    #T = Text(root)
    #T.pack(expand=True, fill='both')

    # Setup the Frames
    tree_frame = ttk.Frame(root, padding="3")
    #tree_frame.grid(row=0, column=0, sticky=tk.NSEW)
    tree_frame.pack(expand=True, fill='both')

    #setup tree
    tree = ttk.Treeview(tree_frame, columns=('Values'))
    tree.column('Values', width=100, anchor='center')
    tree.heading('Values', text='Values')
    j_tree(tree, '', data)
    tree.pack(fill=tk.BOTH, expand=1)

    root.update_idletasks()
    root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())
    root.mainloop()
    
##    printData = ""
##    print(List_MASTER)
##    for i in range(len(List_MASTER)):
##        printData += List_MASTER[0]['title'] +"\n"+List_MASTER [i]['listData'] + "\n";
##    T.insert(END,
##
##            printData
##            ,
##
##            )
##    
##    for printData in T:
##        T.delete(0,END)
#main menu
    
menu = Menu(root)
root.config(menu=menu)

submenu = Menu(menu)
menu.add_cascade(label="file" ,  menu=submenu)
submenu.add_command(label="Save File" , command=doNothing)
submenu.add_command(label="Open File" , command=New_List)
submenu.add_separator()
submenu.add_command(label="exit", command=lll)


#***********for printing list***************

#toolbar


toolbar = Frame(root, bg="black")

insertbutt = Button(toolbar, text= "insert" , command=doNothing)
insertbutt.pack(side=LEFT, padx=2, pady=2)
printbutt = Button(toolbar, text= "print" , command=printtext)
printbutt.pack(side=LEFT, padx=2, pady=2)

toolbar.pack(side=TOP, fill=X)




root.mainloop()

