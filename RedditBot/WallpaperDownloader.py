import threading

import praw
import requests
import tkinter as tk
from tkinter.filedialog import *

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        # Threads for each time so the user can downloaded from multiple time ranges but not the same time range at the
        # same time
        self.threads_running = {
            "Day": False,
            "Week": False,
            "Month": False,
            "Year": False,
            "All": False
        }

        # Change limit (MAX = 1000)
        self.amount = 100

        # Some reddit API stuff
        self.user_agent = "wallpaper_downloader"
        self.sub = "wallpapers" # Can be changed to another sub
        self.reddit_con = praw.Reddit(user_agent=self.user_agent)

        self.pack(side=LEFT, fill=X, padx=5)

        # Setting the default directory for wallpapers
        self.output_dir = StringVar()
        self.output_dir.set((os.getcwd() + "\\wallpapers\\"))

        # The default time range for reddit posts
        self.time = StringVar()
        self.time.set("All")

        # The amount of images that have been loaded
        self.status = StringVar()
        self.status.set("Ready!")

        self.menu_frame = Frame(self)

        # ****************  DIRECTORY FRAME ******************
        self.directory_frame = Frame(self.menu_frame)

        # Output directory options and display
        self.folder_output_label = tk.Label(self.directory_frame, textvariable=self.output_dir)
        self.folder_output_label.pack(side=LEFT)
        self.folder_output_button = tk.Button(self.directory_frame, text="...",
                                              command=lambda: self.select_output_folder())
        self.folder_output_button.pack(side=LEFT)

        self.directory_frame.pack(side=TOP, fill=X)
        # ****************  END DIRECTORY FRAME ******************

        # ****************  OPTIONS FRAME ******************
        self.options_frame = Frame(self.menu_frame)
        # Load stuff button
        self.get_button = tk.Button(self.options_frame, text="Get Wallpapers", command=lambda: self.get_wallpapers())
        self.get_button.pack(side=RIGHT, fill=X)

        # Time range button for reddit posts
        self.date_range_optionbox = tk.OptionMenu(self.options_frame, self.time, "Day", "Week", "Month", "Year", "All")
        self.date_range_optionbox.pack(side=RIGHT, fill=X)
        self.time_range_label = tk.Label(self.options_frame, text="Select top from")
        self.time_range_label.pack(side=RIGHT, fill=X)

        self.options_frame.pack(side=TOP, fill=X)
        # ****************  END OPTIONS FRAME ******************

        self.menu_frame.pack(side=TOP, fill=X)

        # Display for amount of images done
        self.count_label = tk.Label(self, textvariable=self.status, bd=1, relief=SUNKEN, anchor=W)
        self.count_label.pack(side=BOTTOM, fill=X)

    # Chooses the output folder for the downloaded images
    def select_output_folder(self):

        selected_dir = askdirectory(title="Choose output folder for wallpapers")
        if selected_dir != "":
            self.output_dir.set(selected_dir)

    # Downloads the wallpapers into the specified directory using threads
    def get_wallpapers(self):
        # First, check if output dir has been created
        if not os.path.isdir(self.output_dir.get()):
            os.mkdir(self.output_dir.get())

        def callback():

            allowed_extensions = ["jpg", "png", "gif"]  # Default extensions that are allowed for wallpapers
            time = self.time.get()

            self.status.set("Getting top " + str(self.amount) + " from " + time + "...")

            # Depending on users choice
            if time == "Day":
                submissions = self.reddit_con.get_subreddit(self.sub).get_top_from_day(limit=self.amount)
            elif time == "Week":
                submissions = self.reddit_con.get_subreddit(self.sub).get_top_from_week(limit=self.amount)
            elif time == "Month":
                submissions = self.reddit_con.get_subreddit(self.sub).get_top_from_month(limit=self.amount)
            elif time == "Year":
                submissions = self.reddit_con.get_subreddit(self.sub).get_top_from_year(limit=self.amount)
            else:
                submissions = self.reddit_con.get_subreddit(self.sub).get_top_from_all(limit=self.amount)

            count = 0
            for x in submissions:
                url = x.url
                extension = url.split(".")[-1]
                if extension in allowed_extensions:
                    self.status.set("Downloading: " + x.title[0:50])
                    # Remove all bad title elements from title and set save name with extensions
                    title = x.title.split("[")[0]
                    title = title.replace("-", "").replace("/", "").replace("\\", "").replace("?", "") \
                        .replace("\"", "") \
                        .replace("'", "") \
                        .replace("|", "")
                    title = str(title.encode("ascii", errors="ignore"))
                    save_name = self.output_dir.get() + "/" + title + "." + extension
                    # Open file and save loaded image from URL then close
                    f = open(save_name, "wb")
                    try:
                        f.write(requests.get(url).content)
                    finally:
                        f.close()

                # Set progress
                count += 1
                self.status.set("Finished downloading for " + time)

            self.status.set("0/" + str(self.amount))
            self.threads_running[time] = False

        # Run each time on a thread. Prevent same times running multiple threads causing collisions and also
        # prevents tkinter not responding when downloading
        if not self.threads_running[self.time.get()]:
            t = threading.Thread(target=callback)
            t.start()
            self.threads_running[self.time.get()] = True


# Run the application using standard Tkinter stuff
if __name__ == "__main__":
    app = Application()
    app.master.title("Reddit Wallpaper Downloader")
    app.master.resizable(0, 0)
    app.mainloop();
