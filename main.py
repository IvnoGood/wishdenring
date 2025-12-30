#! Boilerplate prise sur github

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import subprocess
import threading
import queue
import sys
import os
import json
import time
from pypresence import Presence
import asyncio


def setup_demo(master):
    root = ttk.Frame(master, padding=10)
    style = ttk.Style()
    style.theme_use("solar")  # ? vapor
    theme_names = style.theme_names()

    Header = ttk.Frame(root, padding=(10, 10, 10, 0))
    Header.pack(fill=X, expand=YES)
    title = ttk.Label(
        master=Header,
        text="WishDenRing",
        font="-size 24 -weight bold"
    )
    title.pack(side=LEFT)
    ttk.Separator(root).pack(fill=X, pady=10, padx=10)

# ---
    """     nb = ttk.Notebook(root)
    nb.pack(
        side=LEFT,
        padx=(0, 0),
        expand=YES,
        fill=BOTH
    ) """
    # ----- LISTE DE BOUTONS -----
    """     # Icons: warning, icon, error, question, info
    grpIco = ImageTk.PhotoImage(Image.open("./assets/icons/group.png"))
    settIco = ImageTk.PhotoImage(Image.open("./assets/icons/settings.png"))
    playIco = ImageTk.PhotoImage(Image.open("./assets/icons/play.png"))

    play = ttk.Button(color_group, text="Jouer",
                      image=playIco, compound=LEFT, bootstyle="dark")
    play.image = playIco
    play.pack(side=LEFT, expand=YES, padx=10, fill=X)
    # ---

    settings = ttk.Button(color_group, text="Paramètres",
                          image=settIco, compound=LEFT, bootstyle="dark")
    settings.image = settIco
    settings.pack(side=LEFT, expand=YES, padx=10, fill=X)
    # ---

    multi = ttk.Button(color_group, text="Multijoueur (WIP)",
                       image=grpIco, compound=LEFT, bootstyle="dark")
    multi.image = grpIco
    multi.pack(side=LEFT, expand=YES, padx=10, fill=X) """
    # ----- FIN LISTE DE BOUTONS -----

    playFrame = ttk.Frame(root)

    gameFrame = ttk.Frame(playFrame, padding=2)
    configFrame = ttk.Frame(playFrame, padding=2)

    log_queue = queue.Queue()
    log_text = ttk.Text(
        gameFrame,
        wrap="word",
        state="disabled",
        background="#0f172a",
        foreground="#e5e7eb",
        insertbackground="white"
    )
    log_text.pack()
    process = None

    def append_log(text):
        log_text.configure(state="normal")
        log_text.insert(END, text)
        log_text.see(END)
        log_text.configure(state="disabled")

    def poll_log_queue():
        while not log_queue.empty():
            append_log(log_queue.get())
        app.after(50, poll_log_queue)

    # sys de logs fait avec IA

    # -------------------------------
    # Subprocess execution
    # -------------------------------

    def run_program():
        nonlocal process
        COMMAND = [sys.executable, "./game.py"]
        if (useMulti_value.get()):
            COMMAND.extend(["--multiplayer", multiType.get()])
        if (useConfig_value.get()):
            COMMAND.extend(["--config", "./config.json"])
        try:
            process = subprocess.Popen(
                COMMAND,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in process.stdout:
                log_queue.put(line)

            process.stdout.close()
            process.wait()
            log_queue.put("\n[Process exited]\n")

        except Exception as e:
            log_queue.put(f"\n[ERROR] {e}\n")

    def start_program():
        append_log("\n--- Starting program ---\n")
        thread = threading.Thread(target=run_program, daemon=True)
        thread.start()
        RPC.update(
            state="Joue a WishDenRing",
            details="Est entrain de combattre des monstres",
            large_image=(
                "eldenwish"
            ),
            large_text="Killing !",
            small_image=(
                "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnk4aTU0cXBlaW5lNzIxcDl5NmlnenAzZXl0emRrejkwZWMwbnoxaSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/dyI6cxt3iM154xESjP/giphy.gif"),
            small_text="WAAAZAAA !",
        )

    def stop_program():
        nonlocal process
        if process and process.poll() is None:
            process.terminate()
            append_log("\n--- Process terminated ---\n")
            RPC.update(
                state="Joue a WishDenRing",
                details="Est actuellement dans le luncher",
                large_image=(
                    "eldenwish"
                ),
                large_text="Killing !",
                small_image=(
                    "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnk4aTU0cXBlaW5lNzIxcDl5NmlnenAzZXl0emRrejkwZWMwbnoxaSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/dyI6cxt3iM154xESjP/giphy.gif"),
                small_text="WAAAZAAA !",
            )

    start_btn = ttk.Button(
        gameFrame,
        text="Lancer",
        bootstyle=SUCCESS,
        command=start_program
    )

    start_btn.pack(side=LEFT, padx=5, pady=15)

    stop_btn = ttk.Button(
        gameFrame,
        text="Arrêter",
        bootstyle=DANGER,
        command=stop_program
    )
    stop_btn.pack(side=LEFT, padx=5, pady=15)
    poll_log_queue()

    configGroup = ttk.Labelframe(
        master=configFrame,
        text="Options de lancement",
        padding=(10, 5)
    )
    configGroup.pack(fill=Y)

    useConfig_value = tk.BooleanVar()
    useConfig = ttk.Checkbutton(
        master=configGroup,
        text="Configuration Personalisée",
        bootstyle=(SUCCESS, ROUND, TOGGLE),
        variable=useConfig_value
    )
    useConfig.invoke()
    useConfig.pack(pady=5, fill=X)

    useMulti_value = tk.BooleanVar()
    useMulti = ttk.Checkbutton(
        master=configGroup,
        text="Multijoueur (WIP)",
        bootstyle=(SUCCESS, ROUND, TOGGLE),
        variable=useMulti_value
    )
    useMulti.invoke()
    useMulti.pack(pady=5, fill=X)
    useMulti_value.set(False)

    frameIP = ttk.Frame(configGroup)
    multiIP_Label = ttk.Label(
        frameIP, text="Adresse IP + port : ").pack(side=LEFT)

    multiIP = ttk.Entry(frameIP)
    multiIP.pack(fill=X)
    multiIP.insert(END, "ws://localhost:3030")
    multiIP.bind("<FocusIn>", lambda args: multiIP.delete('0', 'end'))
    frameIP.pack(fill=X, pady=2)

    frameType = ttk.Frame(configGroup)
    multiType_Label = ttk.Label(
        frameType, text="Type de multijoueur : ").pack(side=LEFT)
    multiType = ttk.Combobox(
        master=frameType,
        values=["host", "client"],
        exportselection=True,
        state=READONLY
    )
    multiType.pack(fill=X)
    multiType.current(0)
    frameType.pack(fill=X, pady=2)

    configFrame.pack(side=RIGHT, fill=Y)
    gameFrame.pack(side=LEFT)

    playIco = ImageTk.PhotoImage(Image.open("./assets/icons/play.png"))
    playIco.image = playIco
    playFrame.pack()
    # nb.add(playFrame, text="Jouer", image=playIco, compound=LEFT)

    # ---
    nb = ttk.Notebook(configGroup)
    nb.pack(pady=16)

    settingsFrame = ttk.Frame(configGroup)

    sensiFrame = ttk.Frame(settingsFrame)
    sensiLabel = ttk.Label(
        sensiFrame, text="Sensibilité de la souris").pack(side=LEFT, fill=X)
    sensi = ttk.Spinbox(
        master=sensiFrame,
        from_=0,
        to=100
    )
    sensi.pack(side=LEFT, fill=X)
    sensi.set(45)
    sensiFrame.pack(fill=X, padx=3, pady=5)

    labelFrame = ttk.Frame(settingsFrame)
    renderLabel = ttk.Label(
        labelFrame, text="Render distance").pack(side=LEFT, fill=X)
    render = ttk.Spinbox(
        master=labelFrame,
        from_=0,
        to=100
    )
    render.pack(side=LEFT, fill=X)
    render.set(45)
    labelFrame.pack(fill=X, padx=3, pady=5)

    def save():
        configFile = {
            "user": {
                "sensi": int(sensi.get()),
                "renderDistance": int(render.get())
            }
        }
        with open("./config.json", "w") as config:
            json.dump(configFile, config)

    def load(path):
        with open(path, "r") as f:
            jsondat = json.load(f)
            sensi.set(jsondat['user']['sensi'])
            render.set(jsondat['user']['renderDistance'])

    def browseFiles():
        filename = filedialog.askopenfilename(initialdir="./",
                                              title="Select a File",
                                              filetypes=(("JSON",
                                                          "*.json*"),
                                                         ("all files",
                                                         "*.*")))
        if (filename):
            load(filename)

    # ---

    settButtFrame = ttk.Frame(settingsFrame)

    saveIco = ImageTk.PhotoImage(Image.open("./assets/icons/download.png"))
    save = ttk.Button(
        master=settButtFrame,
        text="Enregistrer",
        bootstyle="Primary",
        command=save,
        image=saveIco,
        compound=LEFT
    )
    save.image = saveIco
    save.pack(side=LEFT, pady=15)

    uplIco = ImageTk.PhotoImage(Image.open("./assets/icons/upload.png"))

    loadBtn = ttk.Button(
        master=settButtFrame,
        text="Charger",
        bootstyle="Secondary",
        command=browseFiles,
        image=uplIco,
        compound=LEFT,
    )
    loadBtn.image = uplIco
    loadBtn.pack(side=RIGHT, pady=15)

    settButtFrame.pack(fill=X, padx=15)

    settIco = ImageTk.PhotoImage(Image.open("./assets/icons/game.png"))
    settIco.image = settIco
    nb.add(settingsFrame, text="Jeu", image=settIco, compound=LEFT)

    # ---

    multiFrame = ttk.Frame(configGroup)

    grpIco = ImageTk.PhotoImage(Image.open("./assets/icons/group.png"))
    grpIco.image = grpIco
    nb.add(multiFrame, text="Multijoueur", image=grpIco, compound=LEFT)

    # ---

    soundsFrame = ttk.Frame(configGroup)

    grpIco = ImageTk.PhotoImage(Image.open("./assets/icons/volume.png"))
    grpIco.image = grpIco
    nb.add(soundsFrame, text="Audio", image=grpIco, compound=LEFT)
    return root


if __name__ == '__main__':
    client_id = "1433129828181082223"
    RPC = Presence(client_id=client_id)
    RPC.connect()
    RPC.update(
        state="Joue a WishDenRing",
        details="Est actuellement dans le luncher",
        large_image=(
            "eldenwish"
        ),
        large_text="Killing !",
        small_image=(
            "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnk4aTU0cXBlaW5lNzIxcDl5NmlnenAzZXl0emRrejkwZWMwbnoxaSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/dyI6cxt3iM154xESjP/giphy.gif"),
        small_text="WAAAZAAA !",
    )

    app = ttk.Window("WishDenRing Luncher",
                     iconphoto="./assets/icons/eldenwish.png")
    app.resizable(width=False, height=False)

    bagel = setup_demo(app)
    bagel.pack(fill=BOTH, expand=YES)
    app.mainloop()

    while True:
        time.sleep(15)
