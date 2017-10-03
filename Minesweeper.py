###############################################################################
#                                                                             #
#       Name: Eemeli Saari                                                    #
#       Course: TIE-02100                                                     #
#                                                                             #
# --------------------------------------------------------------------------- #
#                                                                             #
#       This is a simple game of Minesweeper done with the Pythons            #
#       built-in GUI tkinter. It uses "settings.txt" as a tool to             #
#       configure between different options available. The game is            #
#       inspired by the original Microsoft's Minesweeper.                     #
#                                                                             #
#       Any modification done to the "settings.txt" file outside the          #
#       software may end up causing an error. Software deals with any         #
#       of those errors accordingly.                                          #
#                                                                             #
#       For detailed info about the software see: README.txt or inside        #
#       the program use sub-menu "About" --> "Instructions".                  #
#                                                                             #
# --------------------------------------------------------------------------- #
#                                                                             #
#       NOT FOR COMMERCIAL USE                                                #
#                                                                             #
###############################################################################

from tkinter import *
import tkinter.messagebox as tm
import random


class GameData:
    """Handling all the settings in the game"""

    def __init__(self):
        # To add more options: we simply add them to this data structure.
        # Needs to be in the format {option:[option_0,...,option_n]}.
        # The first option_0 is the default.
        self.__settings = {"mode": ["beginner",
                                    "normal",
                                    "advanced"],
                           "time": ["yes",
                                    "no"],
                           "flags": ["yes",
                                     "no"]}

        # To add new difficulties need to update this data structure and
        # specify the amount of mines and the grids [y,x] coordinates.
        self.__mode = {"beginner": {"mines": 10, "grid": [9, 9]},
                       "normal": {"mines": 40, "grid": [16, 16]},
                       "advanced": {"mines": 99, "grid": [16, 30]}}

    def get_default(self):
        """Returns simple information package about settings attribute"""

        default = {}

        for var in self.__settings:

            # default option is the available options first option.
            default[var] = self.__settings[var][0]

        return default

    def get_list(self, key):
        """Returns list of options for given key"""
        return self.__settings[key]

    def get_keys(self):
        """Returns list of keys in settings attribute"""
        key_list = []
        [key_list.append(x) for x in self.__settings]
        return key_list

    def get_mode(self, key):
        """Returns information about mode"""
        return self.__mode[key]


class MainWindow:
    """Main window for software. From here we can start different core
       functions."""

    def __init__(self):
        self.__root = Tk()
        self.__root.wm_title("Minesweeper")

        self.menus()

        # Game will always be on the screen.
        self.g = Game(self.__root)
        self.g.start()

    def menus(self):
        """Creates the menu bar and adds all
           the sub-menus"""
        self.__menu = Menu(master=self.__root)

        file_menu = Menu(master=self.__menu,
                         tearoff=0)
        file_menu.add_command(label="New Game",
                              command=self.new_game)
        file_menu.add_command(label="Settings",
                              command=self.options_window)
        file_menu.add_command(label="Help",
                              command=self.help_window)
        file_menu.add_command(label="Exit",
                              command=self.__root.destroy)

        about_menu = Menu(master=self.__menu,
                          tearoff=0)
        about_menu.add_command(label="Credits",
                               command=self.credits)
        about_menu.add_command(label="Instructions",
                               command=self.instructions)

        self.__menu.add_cascade(label="Game",
                                menu=file_menu)
        self.__menu.add_cascade(label="About",
                                menu=about_menu)

        self.__root.config(menu=self.__menu)

        self.__box = Frame()
        self.__box.pack()

    def instructions(self):
        """Displays the README.txt file. Containing viable information about the
           program."""

        new_frame = Toplevel()
        new_frame.wm_title("Instructions")

        # Disables the Main frame.
        new_frame.grab_set()
        new_frame.focus_set()
        try:
            with open("README.txt", "r") as file:
                scrollbar = Scrollbar(new_frame)
                scrollbar.pack(side=RIGHT, fill=BOTH)

                listbox = Listbox(new_frame, yscrollcommand=scrollbar.set, width=70, height=30)
                for line in file:
                    listbox.insert(END, line)
                listbox.pack(side=LEFT, fill=BOTH)

                scrollbar.config(command=listbox.yview)

            file.close()
        except FileNotFoundError:
            tm.showerror(title="ERROR",detail="File not found")

    def help_window(self):
        """Tips to help player to complete the game"""

        tm.showinfo(title="Help",
                    detail="How to play:\n\n"
                           "Step 1.\n"
                           "Click a square, if you get a number. "
                           "That number is the number of how many "
                           "mines are surrounding it.\n\n"
                           "Step 2.\n"
                           "Mark all the mines that are downright obvious. "
                           "Such as eight 1's "
                           "surrounding an unopened square."
                           " Remember to use flag mode for those.\n\n"
                           "Step 3.\n"
                           "Don't be afraid to fail and start again. "
                           "It requires multiple tries.",
                    icon="question")

    def options_window(self):
        options = Options(self.__root)
        options.start()

    def new_game(self):
        # Game can only be restarted.
        self.g.restart()

    def credits(self):
        """Simple information window about the creator."""

        new_frame = Toplevel()
        new_frame.wm_title("Credits")

        # Disables the Main frame.
        new_frame.grab_set()
        new_frame.focus_set()

        info = LabelFrame(master=new_frame,
                          text="Info",
                          padx=5, pady=5)
        info.pack(padx=10, pady=10)

        Label(master=info,
              text="Eemeli Saari\n"
                   "TIE-02100\n\n") \
            .pack(padx=5, pady=5)

        material = LabelFrame(master=new_frame,
                              text="Material",
                              padx=5, pady=5)
        material.pack(padx=10, pady=10)

        Label(master=material,
              text="http://effbot.org\n"
                   "http://wikihow.com/Play-Minesweeper\n"
                   "https://docs.python.org/3") \
            .pack(padx=5, pady=5)

    def start(self):
        self.__root.mainloop()


class Game(Frame):
    """The game with the interactive UI"""

    def __init__(self, parent):
        Frame.__init__(self, master=parent)
        self.__parent = parent
        self.pack()

        # Keeping track of all the
        # revealed tiles.
        self.__pressed = []

        # Keeping track of flagged tiles
        self.__flagged = []

    def initialize(self):
        """Sets the game board according to settings"""

        # Resets the two tracking lists.
        self.__pressed.clear()
        self.__flagged.clear()

        self.__settings = read_settings()
        self.__mode = self.__settings["mode"]

        self.__info = GameData()

        self.__x = self.__info.get_mode(self.__mode)["grid"][1]
        self.__y = self.__info.get_mode(self.__mode)["grid"][0]
        self.__mines_count = self.__info.get_mode(self.__mode)["mines"]

        self.__data, self.__mines = self.create_board()

        # String variable that we can modify
        self.__default_text = StringVar()
        self.__default_text.set("Press any tile to start the game.")

        # Text at the bottom
        self.__text_label = Label(master=self,
                                  textvariable=self.__default_text,
                                  pady=2, padx=2,
                                  bd=2)

        self.__text_label.pack(pady=5, padx=5)

        # Creates the timer if it's enabled
        if self.__settings["time"] == "yes":
            self.timer()

        self.__grid_frame = Frame(master=self,
                                  bd=1,
                                  bg="black")
        self.__grid_frame.pack(pady=10, padx=10)

        self.__flag = IntVar(value=0)

        total_free_tiles = (self.__x * self.__y) - self.__mines_count
        # Total number of legal tiles in the game
        self.__count = total_free_tiles

        if self.__settings["flags"] == "yes":

            # Check button which enables player to flag tiles as potential
            # mine locations. Disabled by default
            self.__flag_state = Checkbutton(master=self,
                                            variable=self.__flag,
                                            text="Flag Mode",
                                            state=DISABLED)

            self.__flag_state.pack(side=RIGHT,
                                   padx=10)

            # Gives player information about the remaining flags count
            self.__flag_box = Frame(master=self,
                                    bd=1,
                                    bg="black")

            self.__flag_box.pack(side=LEFT,
                                 padx=10, pady=5)

            Label(master=self.__flag_box, text="Remaining Flags:").pack(side=LEFT)

            self.__remaining_flags = IntVar(value=self.__mines_count)
            self.__flag_counter = Label(master=self.__flag_box,
                                        textvariable=self.__remaining_flags)

            self.__flag_counter.pack(side=LEFT)

        self.create_grid()

    def game_state(self):
        """
        Checks if game is not won and updates the information text.

        :return: True if there's still viable tiles
                    to play.
                 False if player has won."""

        if self.__count == 0:
            return False
        else:
            # Gives player different encouragement text each time
            # a tile is pressed
            if self.__count % 3 == 0 and self.__count % 7 == 0:
                self.__default_text.set("You're doing great!")
            else:
                if self.__count % 3 == 0:
                    self.__default_text.set("Good thinking!")
                elif self.__count % 7 == 0:
                    self.__default_text.set("Well played")
                else:
                    self.__default_text.set("Nice!")

            return True

    def timer(self):
        """Creates the timer to be displayed"""

        self.__time = Timer(self)

    def create_grid(self):
        """Creates the interactive game board containing
           the buttons and numeric labels"""

        self.__buttons_matrix = []
        self.__label_matrix = []

        for y in range(self.__y):
            row = Frame(master=self.__grid_frame)

            buttons_row = []
            label_row = []
            for x in range(self.__x):
                self.__bg = Frame(master=row, width=5, height=5)
                self.__bg.pack(pady=0, padx=0, side=LEFT)

                self.__num = Label(master=self.__bg,
                                   text="")

                if self.__data[y][x] is not 0:
                    self.__num.config(text=self.__data[y][x])

                self.b = Button(master=self.__num,
                                width=2,
                                height=1,
                                command=lambda row_i=x, column_i=y:
                                self.select_button(y=column_i, x=row_i))

                self.b.pack(fill=BOTH)
                self.__num.pack()

                label_row.append(self.__num)
                buttons_row.append(self.b)

            row.pack()
            self.__label_matrix.append(label_row)
            self.__buttons_matrix.append(buttons_row)

    def create_board(self):
        """Creates the game board matrix containing info
           about the bomb locations and number indicators
           for each tile

           :returns: game board matrix,
                     bomb locations coordinates in list"""

        mines = self.__mines_count

        # Matrix
        data = []
        # Mine locations
        mine_data = []

        # Creating extra row and column each side to ease
        # mine placement and avoid index errors later on.
        for i in range(self.__y + 2):

            row = []
            for p in range(self.__x + 2):
                row.append(0)

            data.append(row)

        # Place the bombs into the pseudo-random location
        while mines > 0:
            r_y = random.randrange(1, self.__y + 1)
            r_x = random.randrange(1, self.__x + 1)

            if data[r_y][r_x] != "x":
                data[r_y].insert(r_x, "x")
                data[r_y].pop(r_x + 1)
                mines -= 1
                mine_data.append([r_y - 1, r_x])

        # add's the numeric indicators around the bombs
        for y in range(1, len(data) - 1):

            for x in range(1, len(data[y]) - 1):

                bomb_count = 0
                if data[y][x] != "x":
                    if data[y + 1][x] == "x":
                        bomb_count += 1
                    if data[y + 1][x + 1] == "x":
                        bomb_count += 1
                    if data[y + 1][x - 1] == "x":
                        bomb_count += 1
                    if data[y][x + 1] == "x":
                        bomb_count += 1
                    if data[y][x - 1] == "x":
                        bomb_count += 1
                    if data[y - 1][x] == "x":
                        bomb_count += 1
                    if data[y - 1][x + 1] == "x":
                        bomb_count += 1
                    if data[y - 1][x - 1] == "x":
                        bomb_count += 1

                    data[y][x] = bomb_count

        # Deletes the extra rows that were added
        data.pop(len(data) - 1)
        data.pop(0)
        for row in data:
            row.pop(len(row) - 1)
            row.pop(0)

        return data, mine_data

    def select_button(self, y, x):
        """Method for every button in the grid"""

        # Only the first time button is pressed the timer will start
        # and player can start using flags.
        if len(self.__pressed) == 0:
            if self.__flag.get() == 0:
                if self.__settings["flags"] == "yes":
                    self.__flag_state.config(state=NORMAL)
                if self.__settings["time"] == "yes":
                    self.__time.start()

        if self.__flag.get() == 0:

            # x meaning the bomb
            if self.__data[y][x] != "x":

                # Reveal an area of adjusted empty tiles.
                if self.__data[y][x] == 0:
                    self.reveal(x=x, y=y)
                    self.__storage.clear()
                else:
                    self.__pressed.append([y, x])
                    self.__buttons_matrix[y][x].destroy()

                    if [y, x] in self.__flagged:
                        self.__flagged.pop(self.__flagged.index([y, x]))

                        self.__remaining_flags \
                            .set(self.__mines_count - len(self.__flagged))

                    self.__count -= 1

                    if not self.game_state():
                        self.win()
            else:
                self.defeat()
        else:
            self.flag_method(x, y)

    def flag_method(self, x, y):
        """Changes the tile text to indicate ether flagged
           or not flagged."""

        if [y, x] not in self.__flagged:

            # Restricting the number of flags tobe equal to number of bombs
            if self.__mines_count - len(self.__flagged) > 0:
                self.__buttons_matrix[y][x].config(text="f")
                self.__flagged.append([y, x])

                self.__remaining_flags \
                    .set(self.__mines_count - len(self.__flagged))

            else:
                self.__default_text.set("No more Flags left")

        else:
            self.__buttons_matrix[y][x].config(text="")
            self.__flagged.pop(self.__flagged.index([y, x]))

            self.__remaining_flags \
                .set(self.__mines_count - len(self.__flagged))

            self.game_state()

    def reveal(self, x, y):
        """Method that'll execute the empty area
           filter algorithm"""

        # list of all the tiles to be revealed
        self.__storage = []
        self.trigger(x, y)

        # Parsing the duplicates
        parsed = []
        for i in self.__storage:
            if i not in parsed:
                parsed.append(i)

        for coordinate in parsed:
            if coordinate not in self.__pressed:
                self.__buttons_matrix[coordinate[0]][coordinate[1]].destroy()
                self.__count -= 1
                # Store the destroyed buttons coordinates
                # so we don't count it multiple times.
                self.__pressed.append(coordinate)
                if coordinate in self.__flagged:
                    self.__flagged.pop(self.__flagged.index(coordinate))

                    self.__remaining_flags \
                        .set(self.__mines_count - len(self.__flagged))

        # Clears the storage every time the method is used
        parsed.clear()
        # Small chance that revealed area contains
        # the last remaining buttons.
        if not self.game_state():
            self.win()

    def trigger(self, x, y):
        """Main loop for reveal method"""

        # Temporary storage for all the empty tiles
        self.__temp = []
        self.search(x, y)

        while len(self.__temp) > 0:
            for coordinate in self.__temp:
                # Every empty tile will get run through the
                # search method.
                self.search(y=coordinate[0], x=coordinate[1])
                self.__storage.append(coordinate)
                self.__temp.pop(self.__temp.index(coordinate))

    def search(self, x, y):
        """Checks all the adjusting tiles
           in the 3x3 area around x,y

           If tile is NOT empty:
                    add's to main storage
           If tile IS empty:
                    add's to temp storage"""

        for i in range(y - 1, y + 2):
            for p in range(x - 1, x + 2):
                # Checks if the coordinates are inside the matrix
                # to avoid index errors
                if self.__x > p > -1 and self.__y > i > -1:
                    coordinate = [i, p]
                    if coordinate not in self.__storage:

                        if self.__data[coordinate[0]][coordinate[1]] == 0:
                            self.__temp.append(coordinate)
                        else:
                            self.__storage.append(coordinate)

    def defeat(self):
        """If the game is lost popup will appear and board will be locked"""

        self.lock_mine_buttons()
        self.__default_text.set("Game lost!")
        self.__time.stop()
        if self.__settings["flags"] == "yes":
            self.__flag_state.config(state=DISABLED)

        if tm.askyesno(title="Defeat", detail="Want to start a new game?"):
            self.restart()
        else:
            self.lock_all_buttons()

    def win(self):
        """If game is won popup will appear and rest of the mines will be
           locked"""

        self.__default_text.set("Game won!")
        self.lock_mine_buttons()
        self.__time.stop()
        if self.__settings["flags"] == "yes":
            self.__flag_state.config(state=DISABLED)

        if tm.askyesno(title="Victory!", detail="Want to start a new game?"):
            self.restart()

    def lock_mine_buttons(self):
        """Disables all the buttons on the mine tiles"""

        for coordinate in self.__mines:
            column = coordinate[0]
            row = coordinate[1]

            self.__buttons_matrix[column][row - 1] \
                .config(state=DISABLED, bg="red")

    def lock_all_buttons(self):
        """Disables all the buttons"""

        for row in self.__buttons_matrix:
            for buttons in row:
                buttons.config(state=DISABLED)

    def restart(self):
        """Clears the board and runs it again"""

        self.__grid_frame.destroy()
        self.__text_label.destroy()
        if self.__settings["flags"] == "yes":
            self.__flag_box.destroy()
            self.__flag_state.destroy()
        if self.__settings["time"] == "yes":
            self.__time.destroy()
        self.start()

    def start(self):

        self.initialize()


class Timer(Frame):
    """Creates a simple timer to display and keep track of seconds"""

    def __init__(self, parent):

        Frame.__init__(self, master=parent, bd=1, bg="black")
        self.pack(side=TOP)
        # Display of the seconds
        Label(master=self, text="Time:").pack(side=LEFT)
        self.__text_var = StringVar()
        self.__text = Label(master=self,
                            textvariable=self.__text_var)
        self.__text.pack(side=LEFT)

        # Numeral value of the seconds.
        self.__count = 0
        self.__text_var.set(self.__count)

        # If the clock is on or off
        # Default is off.
        self.__state = False

    def initialize(self):
        """Starting the loop"""

        self.__state = True
        self.tic()

    def state(self):
        """Change the state."""
        if self.__state:
            self.__state = False
        else:
            self.__state = True

    def tic(self):
        """Actual loop structure itself"""

        if self.__state:
            self.after(1000, self.count)

    def count(self):
        """Updates the display and runs tic method"""

        if self.__state:
            self.__count += 1
            self.__text_var.set(self.__count)

        self.tic()

    def start(self):
        self.initialize()

    def stop(self):
        self.state()


class Options(Toplevel):
    """Options menu that saves the wanted settings into
       settings.txt file"""

    def __init__(self, parent):

        Toplevel.__init__(self, master=parent)
        self.wm_title("Settings")

        window = Frame(self)
        window.pack(padx=5, pady=5)

        # Modifies this dict.
        self.__settings = read_settings()

        # All the available settings
        self.__info = GameData()

        # Creating LabelFrames to indicate a group of settings
        self.__group_difficulties = LabelFrame(master=self,
                                               text="Difficulties",
                                               padx=20, pady=15)
        self.__group_difficulties.pack(padx=10, pady=10)

        self.__group_options = LabelFrame(master=self,
                                          text="Settings",
                                          padx=20, pady=10)
        self.__group_options.pack(padx=5, pady=5)

        # Creates the buttons
        self.radio_buttons()
        self.check_buttons()
        self.button_box()

        # Disables the Main window
        self.grab_set()
        # Focuses the Option window
        self.focus_set()

    def check_buttons(self):
        """Constructs the check buttons."""

        check_options = []
        for var in self.__info.get_keys():

            # "mode" settings will get handled as radio buttons.
            if var != "mode":
                check_options.append(var)

        # Check buttons need a variable to work properly so we'll save them
        # into a list.
        self.__var_list = []
        for i in range(len(check_options)):

            variable = StringVar()
            self.__var_list.append(variable)

            # Using lambda function, each time the check button is pressed
            # it will trigger the configure_check function
            cb = Checkbutton(self.__group_options,
                             text=check_options[i].capitalize(),
                             variable=variable,
                             onvalue="yes",
                             offvalue="no",
                             command=lambda x=check_options[i],i=i:
                             self.configure_check(text=x,index=i))

            cb.pack(side=TOP, pady=5, anchor="w")

            if self.__settings[check_options[i]] == "yes":
                cb.select()
            else:
                cb.deselect()

    def configure_check(self, text,index, event=None):
        """Saves the selected check buttons on/off value to
           self.__settings dict"""

        self.__settings[text.lower()] = self.__var_list[index].get()

    def radio_buttons(self):
        """Constructs a list of radio buttons with a int variable
           that will mark their spot in the radio buttons list"""

        self.var = IntVar()
        self.__difficulties_list = []

        i = 0
        for mode in self.__info.get_list("mode"):

            rb = Radiobutton(self.__group_difficulties,
                             text="{:s}\n{:d} mines\n{:d}x{:d} grid"
                             .format(mode.capitalize(),
                                     self.__info.get_mode(mode)["mines"],
                                     self.__info.get_mode(mode)["grid"][0],
                                     self.__info.get_mode(mode)["grid"][1]),
                             variable=self.var,
                             value=i,
                             command=self.configure_radio)

            # Selects current setting.
            if mode in self.__settings["mode"]:
                rb.select()
            else:
                rb.deselect()

            i += 1
            rb.pack(side=TOP, anchor="w")

            self.__difficulties_list.append(rb)

    def configure_radio(self, event=None):
        """Saves the current selection into self.__settings dict"""

        mode = self.__info.get_list("mode")[self.var.get()]
        self.__settings["mode"] = mode

    def button_box(self):
        """Constructs a default Save and Cancel buttons and binds them as
           keyboard keys"""
        box = Frame(self)

        save = Button(box, text="Save",
                      width=10,
                      command=self.save,
                      default=ACTIVE)
        save.pack(side=LEFT,
                  padx=10, pady=5)

        cancel = Button(box, text="Cancel",
                        width=10,
                        command=self.close)
        cancel.pack(side=LEFT,
                    padx=10, pady=5)

        self.bind("<Return>", func=self.save)
        self.bind("<Escape>", func=self.close)

        box.pack()

    def save(self, event=None):
        """Saves the settings attribute into input file"""

        save_file(self.__settings)
        self.close()

    def close(self, event=None):
        """Closes the Settings window"""

        self.destroy()

    def start(self):
        """Opens the Settings Frame"""

        self.mainloop()


def check_settings(dict_variable):
    """
    Looks for any illegal modifications that might occur
    in the "settings.txt" file.

    :param dict_variable: settings in the dict format.
    :return: True if none were found
             False if any were found"""

    info = GameData()

    try:
        i = 0
        # Need to be as many settings
        if len(dict_variable) == len(info.get_default()):

            for settings in dict_variable:

                # Need to found in existing dict/list
                if settings in info.get_keys():
                    a = dict_variable[settings]
                    if a in info.get_list(settings):
                        i += 1

            if i == len(dict_variable):
                return True
            else:
                return False
        else:
            return False

    except KeyError:
        return False


def save_file(dict_variable):
    """Overwrites the settings file"""

    with open("settings.txt", "w") as file:

        if check_settings(dict_variable):
            for var in sorted(dict_variable):
                file.write("{:s}={:s}\n"
                           .format(var, dict_variable[var]))

            file.close()

        else:
            file_error()
            print("asd")
            default = GameData().get_default()
            for var in default:
                file.write("{:s}={:s}\n"
                           .format(var, default[var]))

            file.close()


def read_settings():
    """
    Reads the "settings.txt" file where we fetch the settings
    and save it into dict to use.

    :return: dict containing the setting and it's value.
    """

    data = {}
    try:
        with open("settings.txt", "r") as file:

            for line in file:
                if line != "\n":
                    parts = line.split("=")
                    data[parts[0]] = parts[1].rstrip()

        # Checks if the file is acceptable
        if check_settings(data):
            return data
        # Raises the general IndexError in all the other cases
        else:
            raise IndexError

    except IndexError:
        # Resets the file and displays the error popup.
        default = GameData().get_default()
        save_file(default)
        file_error()
        return default
    except FileNotFoundError:
        # Creates the new "settings.txt" using default settings.
        default = GameData().get_default()
        save_file(default)
        file_error()
        return default


def file_error():
    """Simple generic popup informing about file reading/writing
       related error"""

    tm.showinfo(title="Error",
                detail="There was an Error reading the file.\n"
                       "Restoring default settings.",
                icon="error")


if __name__ == '__main__':
    ui = MainWindow()
    ui.start()