import tkinter as tk
import json 
import datetime
from tkinter import messagebox
from PIL import Image, ImageTk


# #this is the main window for our app
# root = tk.Tk()
# root.title("Home page")
# root.geometry("1000x1000")
# #this is to set a light blue background 
# root.configure(bg="#b3e5fc")

root = tk.Tk()
root.title("Skinovate Skincare Assistant")
root.geometry("800x600")
root.configure(bg="#f9f9fb")


header_frame = tk.Frame(root, bg="#b3e5fc", height=150)
header_frame.pack(fill="x")

tk.Label(
    header_frame,
    text="Skinovate Skincare Assistant",
    font=("Helvetica", 26, "bold"),
    bg="#b3e5fc",
    fg="#333"
).pack(pady=(40, 5))

tk.Label(
    header_frame,
    text="Your daily skincare tracker",
    font=("Helvetica", 14),
    bg="#b3e5fc",
    fg="#555"
).pack()







# appends quiz results to JSON file

def save_results(username,skin_type, advice):

    # dictionary
    result = {
        "username" : username,
        "skin_type" : skin_type,
        "advice" : advice,
        "timestamp" : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # load existing data
    try:
        with open("results.json", "r") as f:
            data = json.load(f)
    
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    # add new result
    data.append(result)

    # write back to file
    with open("results.json", "w") as f:
        json.dump(data,f , indent=4)
    
    print("Your results were saved!")

def create_navbar(parent):
    nav = tk.Frame(parent, bg="#b3e5fc", height=50)
    nav.pack(fill="x")

    # Navigation buttons
    tk.Button(nav, text="Home", command=parent.destroy,
              bg="#4a90e2", fg="white", font=("Arial", 10, "bold"),
              relief="flat", padx=10, pady=5).pack(side="right", padx=5, pady=5)

    tk.Button(nav, text="View Results", command=view_quiz,
              bg="#4a90e2", fg="white", font=("Arial", 10, "bold"),
              relief="flat", padx=10, pady=5).pack(side="right", padx=5, pady=5)

    tk.Button(nav, text="Product Tracker", command=open_page3,
              bg="#4a90e2", fg="white", font=("Arial", 10, "bold"),
              relief="flat", padx=10, pady=5).pack(side="right", padx=5, pady=5)

    tk.Button(nav, text="Quiz", command=open_page1,
              bg="#4a90e2", fg="white", font=("Arial", 10, "bold"),
              relief="flat", padx=10, pady=5).pack(side="right", padx=5, pady=5)

# Opening the skin care quiz page
def open_page1():
    page1 = tk.Toplevel(root)
    page1.title("Skincare Quiz")

    # navigation
    create_navbar(page1)
    

    #this is like the intro to the app
    tk.Label(page1, text="Let's see what type of skin you have!", font=("Arial", 14, "bold")).pack(pady=20)




    # the 5 questions we ask the user and also the three options they can pick
    tk.Label(page1, text="How does your skin feel before washing your face or applying product?").pack(anchor="w", padx=20)
    q1 = tk.StringVar(value="")
    tk.Radiobutton(page1, text="Tight and/or dry", variable=q1, value="dry").pack(anchor="w", padx=40)
    tk.Radiobutton(page1, text="Oily", variable=q1, value="oily").pack(anchor="w", padx=40)
    tk.Radiobutton(page1, text="Normal", variable=q1, value="normal").pack(anchor="w", padx=40)





    tk.Label(page1, text="How does your skin feel after washing your face?").pack(anchor="w", padx=20)
    q2 = tk.StringVar(value="")
    tk.Radiobutton(page1, text="Tight and/or dry", variable=q2, value="dry").pack(anchor="w", padx=40)
    tk.Radiobutton(page1, text="Oily", variable=q2, value="oily").pack(anchor="w", padx=40)
    tk.Radiobutton(page1, text="Normal", variable=q2, value="normal").pack(anchor="w", padx=40)





    tk.Label(page1, text="How does your skin feel and look by the end of the day?").pack(anchor="w", padx=20)
    q3 = tk.StringVar(value="")
    tk.Radiobutton(page1, text="Flaky or rough", variable=q3, value="dry").pack(anchor="w", padx=40)
    tk.Radiobutton(page1, text="Greasy", variable=q3, value="oily").pack(anchor="w", padx=40)
    tk.Radiobutton(page1, text="Matte", variable=q3, value="normal").pack(anchor="w", padx=40)




    tk.Label(page1, text="How often do you get breakouts?").pack(anchor="w", padx=20)
    q4 = tk.StringVar(value="")
    tk.Radiobutton(page1, text="Rarely", variable=q4, value="dry").pack(anchor="w", padx=40)
    tk.Radiobutton(page1, text="Sometimes", variable=q4, value="normal").pack(anchor="w", padx=40)
    tk.Radiobutton(page1, text="Often", variable=q4, value="oily").pack(anchor="w", padx=40)




    tk.Label(page1, text="What is your age group?").pack(anchor="w", padx=20)
    q5 = tk.StringVar(value="")
    tk.Radiobutton(page1, text="Under 18", variable=q5, value="teen").pack(anchor="w", padx=40)
    tk.Radiobutton(page1, text="18-25", variable=q5, value="young_adult").pack(anchor="w", padx=40)
    tk.Radiobutton(page1, text="26-40", variable=q5, value="adult").pack(anchor="w", padx=40)
    tk.Radiobutton(page1, text="41+", variable=q5, value="mature").pack(anchor="w", padx=40)








    # used chat here to show the result of the quiz
    def submit_quiz():
        answers = [q1.get(), q2.get(), q3.get(), q4.get(), q5.get()]
        if "" in answers:
            messagebox.showwarning("Incomplete", "Please answer all questions before submitting!")
            return

        # Count responses
        dry = answers.count("dry")
        oily = answers.count("oily")
        normal = answers.count("normal")
        age_group = q5.get()

        # Determine skin type
        if dry > oily and dry > normal:
            skin_type = "dry"
            result = "You have dry skin."
        elif oily > dry and oily > normal:
            skin_type = "oily"
            result = "You have oily skin."
        else:
            skin_type = "normal"
            result = "You have normal or combination skin."

        # Add age-based advice
        if age_group == "teen":
            advice = "Since you're a teen, try gentle, oil-free cleansers."
        elif age_group == "young_adult":
            advice = "At your age, hydration and SPF are key!"
        elif age_group == "adult":
            advice = "Consider adding antioxidants and vitamin C to your routine."
        else:
            advice = "Try products with retinol or peptides to support mature skin."

        messagebox.showinfo("Quiz Result", f"{result}\n\n{advice}")

        username = "User"
        save_results(username, skin_type, advice)




     # teh submit button and home button
    tk.Button(page1, text="Submit Quiz", command=submit_quiz, bg="#f4a6a6").pack(pady=20)
    tk.Button(page1, text="Home", command=page1.destroy, bg="#f4a6a6").pack()






# # this opens the product recommendation page
# def open_page2():
#     page2 = tk.Toplevel(root)
#     page2.title("Product Recommendations")
#     tk.Label(page2, text="Here are some products for your skin type!", font=("Arial", 14)).pack(pady=30)
#     tk.Button(page2, text="home", command=page2.destroy).pack()
#     frame = tk.Frame(page2)
#     frame.pack(padx=20, pady=20)

#     image_paths = [
#         "images/DrySensitiveStep1.jpg",
#         "images/DrySensitiveStep2.jpg",
#         "images/DrySensitiveStep3.jpg",
#         "images/DrySensitiveStep4.jpg",
#         "images/DrySensitiveOlder25.jpg",
#         "images/CetaphilOily.jpg",
#         "images/MixedOlder25.jpg",
#         "images/NormalStep1.jpg",
#         "images/NormalStep2.jpg",
#         "images/NormalStep3.jpg",
#         "images/NormalStep4.jpg",
#         "images/OilyStep1.jpg",
#         "images/OilyStep2.jpg",
#         "images/OilyStep3.jpg",
#         "images/OilyStep4.jpg",
#         "images/OilyOlder25.jpg"
#     ]

    
#     imgs = []
    
#     columns = 4

#     for i, path in enumerate(image_paths):
#         img = Image.open(path)
#         img = img.resize((150, 150)) 
#         tk_img = ImageTk.PhotoImage(img)
#         imgs.append(tk_img)

#         label = tk.Label(frame, image=tk_img)
#         label.grid(row=i // columns, column=i % columns, padx=10, pady=10)

#     # keep a reference to all images 
#     frame.images = imgs

        
        

# this opens the product recommendation page
def open_page2():
    page2 = tk.Toplevel(root)
    page2.title("Product Recommendations")

    # nav bar function call
    create_navbar(page2)

    tk.Label(page2, text="Here are some products for your skin type!", font=("Arial", 14)).pack(pady=30)
    tk.Button(page2, text="Home", command=page2.destroy).pack()
    frame = tk.Frame(page2)
    frame.pack(padx=20, pady=20)

    image_paths = [
        "images/DrySensitiveStep1.jpg",
        "images/DrySensitiveStep2.jpg",
        "images/DrySensitiveStep3.jpg",
        "images/DrySensitiveStep4.jpg",
        "images/DrySensitiveOlder25.jpg",
        "images/CetaphilOily.jpg",
        "images/MixedOlder25.jpg",
        "images/NormalStep1.jpg",
        "images/NormalStep2.jpg",
        "images/NormalStep3.jpg",
        "images/NormalStep4.jpg",
        "images/OilyStep1.jpg",
        "images/OilyStep2.jpg",
        "images/OilyStep3.jpg",
        "images/OilyStep4.jpg",
        "images/OilyOlder25.jpg"
    ]

    product_names = [
        "CeraVe Hydrating Facial Cleanser",
        "Thayers Alcohol-Free Rose Petal Toner",
        "The Ordinary Hyaluronic Acid 2% + B5",
        "Nivea Soft Moisturizing Cream",
        "The Ordinary Retinol 0.2% in Squalane",
        "Cetaphil Daily Facial Cleanser",
        "CeraVe Resurfacing Retinol Serum",
        "Cetaphil Daily Facial Cleanser",
        "e.l.f. Keep Your Balance Toner",
        "Good Molecules Niacinamide Brightening Toner",
        "e.l.f. Holy Hydration Face Cream SPF 30",
        "ANUA Heartleaf Deep Cleansing Foam",
        "BYOMA Hydrating Milky Toner",
        "The Ordinary Niacinamide 10% + Zinc 1%",
        "Cetaphil Oil Absorbing Moisturizer SPF 30",
        "The Ordinary Retinol 1% in Squalane"
    ]

    imgs = []
    columns = 4

    for i, (path, name) in enumerate(zip(image_paths, product_names)):
        try:
            img = Image.open(path)
            img = img.resize((150, 150))
            tk_img = ImageTk.PhotoImage(img)
            imgs.append(tk_img)

            product_frame = tk.Frame(frame, padx=10, pady=10)
            product_frame.grid(row=i // columns, column=i % columns)

            # show the image
            label = tk.Label(product_frame, image=tk_img)
            label.pack()

            # show the product name under it
            name_label = tk.Label(product_frame, text=name, wraplength=150, justify="center", font=("Arial", 10, "bold"))
            name_label.pack(pady=5)

        except Exception as e:
            print(f"Error loading {path}: {e}")

    # keep references so images don't get garbage-collected
    frame.images = imgs



def open_page3():
    # open a new window for the product tracker
    page3 = tk.Toplevel(root)
    page3.title("Skincare Usage Tracker")
    page3.geometry("600x600")
    page3.configure(bg="#f0f4f8")  # light blue background to match the theme

    # add nav bar
    create_navbar(page3)

    # create a header section that stands out
    header_frame = tk.Frame(page3, bg="#4a90e2", height=80)
    header_frame.pack(fill="x")

    # title in the header
    tk.Label(
        header_frame,
        text="Skincare Product Tracker",
        font=("Helvetica", 18, "bold"),
        bg="#4a90e2",
        fg="white"
    ).pack(pady=20)

    # try to load old saved usage data
    try:
        with open("usage_log.json", "r") as f:
            usage_log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        usage_log = {}  


    display_frame = tk.Frame(page3, bg="#ffffff", bd=2, relief="groove")
    display_frame.pack(pady=20, padx=20, fill="both", expand=True)

    # text box to display logged products in blue
    display_box = tk.Text(display_frame, height=15, width=70, bg="#ffffff", fg="#4a90e2", font=("Arial", 11, "bold"))
    display_box.pack(padx=10, pady=10, fill="both", expand=True)

    # function that updates the display box with all saved products user logged before
    def update_display():
        display_box.delete(1.0, tk.END)
         # newest dates first
        for date, products in sorted(usage_log.items(), reverse=True):  
            display_box.insert(tk.END, f"{date}: {', '.join(products)}\n")

    update_display()

    # input area for adding new products
    input_frame = tk.Frame(page3, bg="#f0f4f8")
    input_frame.pack(pady=10)




    # label telling the user what to do
    tk.Label(
        input_frame,
        text="Enter products used today (please use a comma to separate products!):",
        bg="#f0f4f8",
        fg="#4a90e2",
        font=("Arial", 11, "bold")
    ).pack(pady=5)




    # entry box for typing products
    products_entry = tk.Entry(input_frame, width=50, font=("Arial", 11))
    products_entry.pack(pady=5)




    # function to save products the user typed
    def log_usage():
        products = [p.strip() for p in products_entry.get().split(",") if p.strip()]  
         # if user didn't type anything
        if not products:  
            messagebox.showwarning("No Entry", "Please enter one or more product.")
            return






        # this get today's date and adds it to the log
        today = datetime.date.today().isoformat() 
        usage_log[today] = usage_log.get(today, []) + products   

        # write updated log to file
        with open("usage_log.json", "w") as f:
            json.dump(usage_log, f, indent=4)

        messagebox.showinfo("Saved", f"Logged: {', '.join(products)} for {today}") 
        # clear last entry so they can type again
        products_entry.delete(0, tk.END) 
        update_display()

    # button to save 
    tk.Button(input_frame, text="Log Usage", command=log_usage, bg="#4a90e2", fg="#4a90e2", font=("Arial", 11, "bold")).pack(pady=10)

    # button to go back home
    tk.Button(input_frame, text="Home", command=page3.destroy, bg="#4a90e2", fg="#4a90e2", font=("Arial", 11, "bold")).pack(pady=5)

def open_page4():
    page4 = tk.Toplevel(root)
    page4.title("Saved Products")
    page4.geometry("600x600")

    # add navigation bar
    create_navbar(page4)
    
    tk.Label(page4, text="View your saved products", font=("Arial", 14, "bold")).pack(pady=20)


def view_quiz():
    page = tk.Toplevel(root)
    page.title("View your quiz results!")
    page.geometry("600x600")
    page.configure(bg="#f9f9fb")

    # acts as the header
    header = tk.Frame(page, bg="#4a90e2", height=80)
    header.pack(fill="x")

    tk.Label (
        header,
        text= "View previous quiz results!",
        font=("Arial", 18, "bold"),
        bg="#4a90e2",
        fg="white"
    ).pack(pady=20)

    #load saved quiz results
    try:

        with open("results.json", "r") as f:
            data = json.load(f)

    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    
    # check if there is no data
    if not data:
        tk.Label(page, text="No quiz results found!", font=("Arial", 13, "bold"), bg="#f9f9fb", fg="#4a90e2").pack(pady=15)
        tk.Button(page, text="Home", command=page.destroy, bg="#4a90e2", fg="white", font=("Arial", 11, "bold")).pack(pady=15)
        return
    
    #results area
    area = tk.Canvas(page, bg="#f9f9fb", highlightthickness=0)
    area.pack_propagate(False)
    scroll_bar = tk.Scrollbar(page, orient="vertical", command=area.yview)
    scroll_frame = tk.Frame(area, bg="#f9f9fb")

    scroll_frame.bind("<Configure>", lambda e: area.configure(scrollregion=area.bbox("all")))
    area.create_window((0,0), window = scroll_frame, anchor="nw")
    area.configure(yscrollcommand=scroll_bar.set)

    # display results
    for q in reversed(data):
        quiz_text = (
            f"User: {q['username']}\n"
            f"Skin Type: {q['skin_type'].capitalize()}\n"
            f"Advice: {q['advice']}\n"
            f"Date: {q['timestamp']}\n"
        )

        tk.Label(
            scroll_frame,
            text=quiz_text,
            justify= "left",
            bg= "#ffffff",
            fg="#333",
            font=("Arial", 12),
            relief="solid",
            wraplength=550,
            padx=10,
            pady=5
        ).pack(pady=5, fill="x", padx=10)
    
    area.pack(side="left", fill="both", expand=True)
    scroll_bar.pack(side="right", fill="y")

    #home button
    tk.Button(page, text="Home", command=page.destroy, bg="#4a90e2", fg="white", font=("Arial", 12, "bold")).pack(pady=15)




    





# # main page 
# # tk.Label(root, text="Main Page", font=("Arial", 16, "bold")).pack(pady=20)
# quizButton = tk.Button(root, text="Take Skincare quiz", command=open_page1, width=20).pack(pady=5)
# #quizButton.place(x= 400, y= 900) #It dont work
# catalogueButton = tk.Button(root, text="Product Catalogue", command=open_page2, width=20).pack(pady=5)
# #catalogueButton.place(x= 550, y= 900) #It dont work
# prodTrackerButton = tk.Button(root, text="Skincare Product Tracker", command=open_page3, width=20).pack(pady=5)
# #prodTrackerButton.place(x = 600, y = 900) #It dont work
# savedProdButton = tk.Button(root, text="Saved Products", command = open_page4, width=20).pack(pady=5)

# main page buttons are now in blue
# main page 
quizButton = tk.Button(root, text="Take Skincare quiz", command=open_page1, width=20, bg="#4a90e2", fg="#4a90e2").pack(pady=5)
catalogueButton = tk.Button(root, text="Product Catalogue", command=open_page2, width=20, bg="#4a90e2", fg="#4a90e2").pack(pady=5)
prodTrackerButton = tk.Button(root, text="Skincare Product Tracker", command=open_page3, width=20, bg="#4a90e2", fg="#4a90e2").pack(pady=5)
savedProdButton = tk.Button(root, text="Saved Products", command=open_page4, width=20, bg="#4a90e2", fg="#4a90e2").pack(pady=5)
resultsButton= tk.Button(root, text="View Quiz Results", command=view_quiz, width=20, bg="#4a90e2", fg="#4a90e2").pack(pady=5)

# copyright to let user know which team we are at the bottom
tk.Label(root, text="© 2025 Skinovate | Designed by Team 8 TBD!", font=("Arial", 10), bg="white", fg="#555").pack(side="bottom", pady=10)




# Run the app
root.mainloop()
