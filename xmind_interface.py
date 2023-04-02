import xmind
import zipfile
import answer_getter
import tree
import re

def parse_answer(answer: str):
    '''
    Parse the answer from the OpenAI API. Return a list of strings.
    '''
    return re.findall(r'[0-9]+[.] (.*)', answer)


def manipulate_sheet(sheet, sheettree: tree.Tree):
    '''
    Interact with users with actions like insert, update, and delete.
    '''
    current_node = sheettree.root
    current_topic = sheet.getRootTopic()
    previous_topic = None
    choice = None
    while choice != "exit":
        print("You are at node **" + current_node.get_name() + "**. The following nodes are available:\n")
        for i, child in enumerate(current_node.get_children()):
            print(str(i + 1) + ": " + child.get_name() + "\n")
        
        choice = input('''PLEASE READ CAREFULLY
Please choose a node by number to manipulate, or type 'new' to create a new node, or type 'back' to go to its parent node (if any),
or type "insert" to ask a question-answer pair generted by ChatGPT and insert them, or type 'exit' to exit.\n''')

        if choice == "exit":
            break
        elif choice == "new":
            # new a node in the tree
            new_node = tree.treeNode(parent = current_node, title = input("Please input the name of the new node.\n"))
            current_node.add_child(new_node)

            # new a node in the xmind
            subtopic = current_topic.addSubTopic()
            subtopic.setTitle(new_node.get_name())

        elif choice == "back":
            # navigate the tree
            if current_node.get_parent():
                current_node = current_node.get_parent()
            else:
                print("You are already at the root node. Please choose another node.")
            
            # navigate the xmind
            if previous_topic:
                current_topic = previous_topic

        elif choice == "insert":

            # insert a node in the tree
            question = answer_getter.get_question()
            answer = answer_getter.get_answer(question = question)
            answer_list = parse_answer(answer)

            new_node = tree.treeNode(parent = current_node, title = question)
            current_node.add_child(new_node)
            current_node = new_node

            for answer in answer_list:
                new_node = tree.treeNode(parent = current_node, title = answer)
                current_node.add_child(new_node)

            # insert a node in the xmind
            subtopic = current_topic.addSubTopic()
            subtopic.setTitle(question)

            previous_topic = current_topic
            current_topic = subtopic

            for answer in answer_list:
                subtopic = current_topic.addSubTopic()
                subtopic.setTitle(answer)
        
        elif choice.isdigit():
            choice = int(choice) - 1
            if choice < len(current_node.get_children()):
                # navigate the tree
                current_node = current_node.get_children()[choice]

                # navigate the xmind
                previous_topic = current_topic
                current_topic = current_topic.getSubTopics()[choice]
            else:
                print("Invalid choice. Please choose another node.")
        else:
            print("Invalid input. Treat as exit.")
            break
    return 

def manipulate_xmind(filename: str):
    '''
    Open a xmind file. Interact with users with actions like insert, update, and delete. Finally save the changes.
    '''

    # load xmind file, if not exist, create a new one
    workbook = xmind.load(filename)
    sheets = workbook.getSheets()

    # if the sheet is the default sheet, give it a name
    if len(sheets) == 1:
        sheet = workbook.getPrimarySheet()
        if not sheet.getTitle():
            sheet.setTitle("first sheet")
            root_topic = sheet.getRootTopic()
            root_topic.setTitle("root node")
    
    # enter the main loop
    while True:
        sheets = workbook.getSheets()
        # now the sheet is not empty, ask user to choose one
        print("The following sheets are available:")

        for i, sheet in enumerate(sheets):
            print(str(i + 1) + ": " + sheet.getTitle() + "\n")

        choice = input("Please choose a sheet by number to manipulate, or type 'new' to create a new sheet, or type 'exit' to exit.\n")
        if choice == "exit":
            break
        elif choice == "new":
            # create a new sheet
            sheetname = input("----------Please input the name of the new sheet.----------\n")
            sheet = workbook.createSheet()
            sheet.setTitle(sheetname)
            root_topic = sheet.getRootTopic()
            root_topic.setTitle("root node")
        elif choice.isdigit():
            sheet = sheets[int(choice) - 1]
            # manipulate the sheet
            sheettree = tree.Tree(sheet.getData())
            manipulate_sheet(sheet, sheettree)
        else:
            print("Invalid input. Treat as exit.")
            break

    # save the xmind file
    xmind.save(workbook, filename)
    repair(filename)

def repair(fname):
    zip_file = zipfile.ZipFile(fname, 'a')
    zip_file.writestr('META-INF/manifest.xml', '<?xml version="1.0" encoding="UTF-8" standalone="no"?><manifest xmlns="urn:xmind:xmap:xmlns:manifest:1.0" password-hint=""></manifest>')
    zip_file.close()
