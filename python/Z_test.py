def setup_main_window(self):
    self.canvas = Canvas(self.window, width=640, height=512, bg=YELLOW, highlightthickness=0)  # CANVAS-PŁÓTNO

    self.latarnie_img = PhotoImage(file="./images/latarnie.png")  # wczytanie obrazka
    self.canvas.create_image(320, 256, image=self.latarnie_img)  # POZYCJA X, Y TO POŁOWA WIELKOŚCI OBRAZKA
    self.canvas.grid(row=1, column=1)  # pozycja obrazka w oknie

    title_label = Label(
        self.window, text="Analizer wyników oświetleniowych (RELUX)", bg=YELLOW, fg=GREEN,
        font=(FONT_NAME, 20, "bold")
    )  # tytuł napisu nad obrazkiem
    title_label.grid(row=0, column=1)  # pozycja napisu nad obrazkiem

    start_button = Button(
        self.window, width=7, height=2, text="Start", command=self.start_results_window
    )  # przycisk start_button, inicjacja
    start_button.grid(row=2, column=0)  # pozycja przycisku start_button w oknie

    reset_button = Button(
        self.window, width=7, height=2, text="Reset"
    )  # tu w nawiasie wstawisz command= i nazwa funkcji która coś robi )
    reset_button.grid(row=2, column=2)  # pozycja przycisku reset_button w oknie

    select_folder_button = Button(
        self.window, text="Wybierz folder z plikami .csv", command=self.select_csv_folder,
        bg=GREEN, font=(FONT_NAME, 12)
    )
    select_folder_button.grid(row=3, column=1, pady=10)

    self.folder_label = Label(
        self.window, text="", bg=YELLOW, fg=PINK, font=(FONT_NAME, 10), justify=LEFT, anchor="w"
    )  # poprawienie wyglądu labela
    self.folder_label.grid(row=4, column=1, pady=5)