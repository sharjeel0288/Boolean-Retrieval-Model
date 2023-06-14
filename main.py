from tkinter import *
from stemmer import stem
from helperFunctions import *
import timeit
import os


results = []
query = None

stop_words = stopWordList("Stopword-List.txt")
docs_tokens = documentTokenizer(30, stop_words)
extract_documnets = get_document_extracts(30)
inverted_index = invertedIndex(docs_tokens)
# a,o,n,k=parse_query('babar')
# # print(boolean_query_search(inverted_index,a,o,n))
# print(search(inverted_index,'england   '))
# # print(stem('Mumtaz'))
# # print(inverted_index)
# # q="Mumtaz: and injury /100"
# # a,o,n,k=parse_query(q)
# # # print(proximity_query(inverted_index,a,o,n,int(k)))
# # print(search(inverted_index,q))


def clicked():
    start_time = timeit.default_timer()
    global query
    global results
    query = searchQuery.get()
    searchQuery.delete(0, END)
    print(query)
    print(parse_query(query))
    results = (search(inverted_index, query))
    length = len(results)
    print(results)
    searchStats.config(
        text=f'Processed {len(docs_tokens)} documents in {len(inverted_index.keys())}ms , fetched {len(results)} results')
    for label in scrollable_frame.winfo_children():
        label.destroy()
    for i in range(0, len(results)):
        try:
            label_text = f"Document {results[i]}  : extract \"{extract_documnets[int(results[i])-1]}\""
            label = Label(scrollable_frame, text=label_text,
                          anchor="w", wraplength=450)
            label.pack(pady=5, padx=10)

            label.bind("<Button-1>", lambda event,
                       index=int(results[i])-1: open_file(index))

        except ValueError:
            pass

    end_time = timeit.default_timer()
    execution_time_in_microseconds = (end_time - start_time) * 1_000_000
    print(len(results))
    print((results))
    searchStats.config(text="Processed in "+str(execution_time_in_microseconds) +
                       'ms , fetched '+str(length)+' results')


def open_file(index):
    # set the exact path of the folder dataset
    file_name = f"E:/study/IR/IR assignment 1/Dataset/{index+1}.txt"
    print(file_name)
    os.startfile(file_name)


window = Tk()
window.title("Boolean Retrieval Model")
window.geometry('500x500')
window.resizable(False, False)

window.configure(bg="#f5f5f5")

exampleHeading = Label(
    window,
    text="Write your boolean query like \"t1 and t2 or t3\"\nOr proximity query like \"t1 and t2 or t3 /k\"\nor enter phrase query like \"what a shot\"",
    font=("Arial", 8),
    fg="#333",
    bg="#f5f5f5"
)
exampleHeading.grid(column=0, row=0, columnspan=2, pady=10, padx=100)

header_label = Label(
    window,
    text="Search Here",
    font=("Arial Bold", 20),
    fg="#333",
    bg="#f5f5f5"
)
header_label.grid(column=0, row=1)

searchQuery = Entry(
    window,
    width=50,
    font=("Arial", 10),
    bd=0,
    bg="#f9f9f9",
    highlightcolor="#333",
    highlightthickness=1,
    highlightbackground="#ccc"
)
searchQuery.grid(column=0, row=2, padx=100)

searchStats = Label(
    window,
    text="Welcome",
    font=("Arial Bold", 8),
    fg="#333",
    bg="#f5f5f5"
)
searchStats.grid(column=0, row=3)

searchBtn = Button(
    window,
    text="Search",
    font=("Arial Bold", 14),
    bg="#333",
    fg="#fff",
    bd=0,
    activebackground="#555",
    activeforeground="#fff",
    command=clicked
)
searchBtn.grid(column=0, row=4, padx=100, pady=10)

canvas = Canvas(window, width=500, height=400, bg="#fff")
scrollbar = Scrollbar(window, orient=VERTICAL, command=canvas.yview)
scrollable_frame = Frame(canvas, bg="#fff")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)


canvas.grid(column=0, row=5, sticky="nsew")
scrollbar.grid(column=1, row=5, sticky="ns")

window.grid_columnconfigure(0, weight=1)
window.grid_rowconfigure(5, weight=1)

window.mainloop()
