import tkinter as tk
import json 
import datetime
from tkinter import messagebox
from PIL import Image, ImageTk


#this is the main window for our app
root = tk.Tk()
root.title("Home page")
root.geometry("1000x1000")
#this is to set a light blue background 
root.configure(bg="#b3e5fc")

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

# Opening the skin care quiz page
def open_page1():
    page1 = tk.Toplevel(root)
    page1.title("Skincare Quiz")
    

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






# this opens the product recommendation page
def open_page2():
    page2 = tk.Toplevel(root)
    page2.title("Product Recommendations")
    tk.Label(page2, text="Here are some products for your skin type!", font=("Arial", 14)).pack(pady=30)
    tk.Button(page2, text="home", command=page2.destroy).pack()

def open_page3():
    page3 = tk.Toplevel(root)
    page3.title("Skincare Usage Tracker")
    tk.Label(page3, text= "This is where you can track your usage cycle for your skincare products!", font= ("Arial", 14)).pack(pady=30)
    tk.Button(page3, text="home", command=page3.destroy).pack()

# main page 
tk.Label(root, text="Main Page", font=("Arial", 16, "bold")).pack(pady=20)
quizButton = tk.Button(root, text="Take Skincare quiz", command=open_page1, width=20).pack(pady=5)
#quizButton.place(x= 400, y= 900) #It dont work
catalogueButton = tk.Button(root, text="Product Catalogue", command=open_page2, width=20).pack(pady=5)
#catalogueButton.place(x= 550, y= 900) #It dont work
prodTrackerButton = tk.Button(root, text="Skincare Product Tracker", command=open_page3, width=20).pack(pady=5)
#prodTrackerButton.place(x = 600, y = 900) #It dont work

# Run the app
root.mainloop()
