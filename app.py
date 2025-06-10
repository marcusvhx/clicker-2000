from tkinter import ttk, Toplevel, messagebox
import tkinter as tk
import pyautogui as pa
import pynput.keyboard as ppkb
import pynput.mouse as mouse
import keyboard as kb
import copy
import json
import time

functions = [pa.click, pa.rightClick, pa.middleClick]
works = []
worksNames = ["empty"]  # lista dos nomes das ações

newWork = {"name": "", "actions": []}  # modelo de ação
mouseAction = {"x": 0, "y": 0, "button": ""}  # coordenadas do mouse
""" action: 
        w -> write, key -> palavra
        p -> press, key-> tecla
"""
keyboardAction = {"action": "", "key": ""}  # ação do teclado
isRecording = False  # é necessario para gravação das ações
isPaused = False
alreadyOpen = False  # necessario pra saber se ja tem algum modal aberto
filters = [isRecording, not isPaused, not alreadyOpen]
# Mapeamento completo de VK para Scan Code
VK_TO_SCANCODE = {
    # Letters
    65: 30,  # A
    66: 48,  # B
    67: 46,  # C
    68: 32,  # D
    69: 18,  # E
    70: 33,  # F
    71: 34,  # G
    72: 35,  # H
    73: 23,  # I
    74: 36,  # J
    75: 37,  # K
    76: 38,  # L
    77: 50,  # M
    78: 49,  # N
    79: 24,  # O
    80: 25,  # P
    81: 16,  # Q
    82: 19,  # R
    83: 31,  # S
    84: 20,  # T
    85: 22,  # U
    86: 47,  # V
    87: 17,  # W
    88: 45,  # X
    89: 21,  # Y
    90: 44,  # Z
    # Numbers
    48: 11,  # 0
    49: 2,  # 1
    50: 3,  # 2
    51: 4,  # 3
    52: 5,  # 4
    53: 6,  # 5
    54: 7,  # 6
    55: 8,  # 7
    56: 9,  # 8
    57: 10,  # 9
    # Functins
    112: 59,  # F1
    113: 60,  # F2
    114: 61,  # F3
    115: 62,  # F4
    116: 63,  # F5
    117: 64,  # F6
    118: 65,  # F7
    119: 66,  # F8
    120: 67,  # F9
    121: 68,  # F10
    122: 87,  # F11
    123: 88,  # F12
    #
    8: 14,  # Backspace
    9: 15,  # Tab
    13: 28,  # Enter
    16: 42,  # Shift
    17: 29,  # Ctrl
    18: 56,  # Alt
    20: 58,  # Caps Lock
    27: 1,  # Esc
    32: 57,  # Espaço
    33: 73,  # Page Up
    34: 81,  # Page Down
    35: 79,  # End
    36: 71,  # Home
    37: 75,  # Left Arrow
    38: 72,  # Up Arrow
    39: 77,  # Right Arrow
    40: 80,  # Down Arrow
    45: 82,  # Insert
    46: 83,  # Delete
    # NumPad
    96: 82,  # NumPad 0
    97: 79,  # NumPad 1
    98: 80,  # NumPad 2
    99: 81,  # NumPad 3
    100: 75,  # NumPad 4
    101: 76,  # NumPad 5
    102: 77,  # NumPad 6
    103: 71,  # NumPad 7
    104: 72,  # NumPad 8
    105: 73,  # NumPad 9
    106: 55,  # NumPad Multiply
    107: 78,  # NumPad Add
    109: 74,  # NumPad Subtract
    110: 83,  # NumPad Decimal
    111: 181,  # NumPad Divide
    # Specal
    144: 69,  # Num Lock
    145: 70,  # Scroll Lock
    186: 39,  # ;
    187: 13,  # =
    188: 51,  # ,
    189: 12,  # -
    190: 52,  # .
    191: 53,  # /
    192: 41,  # `
    219: 26,  # [
    220: 43,  # \
    221: 27,  # ]
    222: 40,  # '
}


def vkToScancode(vk):
    return VK_TO_SCANCODE.get(vk)


def checkFilters():
    global filters
    filters = [isRecording, not isPaused, not alreadyOpen]
    return not filters.__contains__(False)


def startRunning():
    global isRecording
    isRecording = True


def stopRunning():
    global isRecording
    isRecording = False


def toggleRunning():
    if isRecording:
        stopRunning()
        return
    startRunning()


def pause():
    global isPaused
    isPaused = True


def unpause():
    global isPaused
    isPaused = False


def togglePause():
    if isPaused:
        unpause()
        lb_isPaused.configure(text="")
        return
    pause()
    lb_isPaused.configure(text="⏸")


def setAlreadyOpen():
    global alreadyOpen
    alreadyOpen = True


def unsetAlreadyOpen():
    global alreadyOpen
    alreadyOpen = False


def center_window(window):
    window.update_idletasks()  # Ensure window information is updated
    width = window.winfo_width()
    height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


def updateActions():
    global works
    with open("./config.json", "r", encoding="UTF-8") as file:
        works = json.load(file)  # lista de ações


def updateActionsNames():
    global worksNames
    newList = list(map(lambda x: x["name"], works))
    if len(newList) > 0:
        worksNames = newList
        combo_actions.configure(values=worksNames)
        combo_actions.set(worksNames[0])
    else:
        combo_actions.set(["empty"])


def updateLists():
    updateActions()
    updateActionsNames()


def alertError(msg):
    return messagebox.showerror(title="error", message=msg)


def alertInfo(msg):
    return messagebox.showinfo(title="info", message=msg)


def recordAction(x, y, button, pressed):  # coleta os dados do mouse
    if (
        pressed and isRecording and not isPaused
    ):  # se o botão for pressionado, o programa estiver rodando e não estiver pausado
        mouseAction["x"] = x  # grava a posição x
        mouseAction["y"] = y  # grava a posição y

        match button:  # botão precionado
            case mouse.Button.left:
                mouseAction["button"] = 0  # grava o botão esquedo
            case mouse.Button.right:
                mouseAction["button"] = 1  # grava o botão direito
            case mouse.Button.middle:
                mouseAction["button"] = 3  # grava o botão direito
            case _:
                alertError("Undefined Button")
                return True
        newWork["actions"].append(mouseAction.copy())  # guarda localmente
        print(list(newWork["actions"]))

    return isRecording


def cancelAction():
    global btn_record
    global mouseListener
    stopRunning()
    unpause()
    if mouseListener:  # evita execuções com um null
        mouseListener.stop()  # para o monitoramento do mouse
    newWork["actions"].clear()  # limpa a lista com as antigas ações
    print("canceled")
    btn_record.configure(text="⏺")
    alertInfo("Recording Canceled")


def saveAction():
    global btn_record
    stopRunning()
    unpause()
    # coleta o tempo de pausa entre as ações
    works.insert(0, copy.deepcopy(newWork))  # adiciona a nova ação a lista de ações
    combo_actions.set(worksNames[0])  # mostra a nova ação selecionada na tela

    with open("./config.json", "w", encoding="UTF-8") as file:  # abre o json
        json.dump(works, file, ensure_ascii=False, indent=4)  # salva os dados no json

    updateLists()  # atualiza a lista de ações
    print(f"ação {newWork['name']} salva")  # avisa que foi concluido
    newWork["actions"] = []  # limpa a lista de ações para uma nova gravação
    btn_record.configure(text="⏺")
    alertInfo(f"Work {newWork['name']} saved")  # avisa que foi concluido


def popupWrite():
    setAlreadyOpen()
    pause()
    popup = Toplevel(frame)
    popup.geometry("220x150")
    popup.grab_set()
    center_window(popup)

    ttk.Label(popup, text="Text to write:").pack(pady=10)

    input_text = ttk.Entry(popup, takefocus=True, width=20)
    input_text.pack(pady=10)
    input_text.focus_force()

    def saveKeyAction():
        text = input_text.get()
        if len(text) == 0:
            return alertError("Inset a text")
        newAction = copy.deepcopy(keyboardAction)
        newAction["action"] = "w"
        newAction["key"] = text
        newWork["actions"].append(newAction)
        popup.destroy()
        unpause()
        unsetAlreadyOpen()

    ttk.Button(popup, text="Add", command=saveKeyAction).pack(pady=10)

    def cancel():
        popup.destroy()
        unpause()
        unsetAlreadyOpen()

    def listener(keysym):
        if keysym == "Escape":  # se for esc, cancela a ação
            cancel()
        if keysym == "Return":  # se for enter, salva a ação
            saveKeyAction()

    popup.bind(
        "<Key>", lambda e: listener(e.keysym)
    )  # liga o evento de tecla pressionada

    popup.protocol("WM_DELETE_WINDOW", cancel)


def popupHelp():
    setAlreadyOpen()
    popup = Toplevel(frame)
    popup.geometry("320x220")
    popup.configure(padx=10, pady=10)
    popup.focus_force()
    popup.grab_set()
    center_window(popup)

    ttk.Label(popup, text="short keys:").grid(column=0, row=1)
    ttk.Label(popup, text="T: record a writing action").grid(
        column=0, row=2, sticky="w"
    )
    ttk.Label(popup, text="Right Shift: do the selected work").grid(
        column=0, row=3, sticky="w"
    )
    ttk.Label(popup, text="Esc: while running, stop").grid(column=0, row=4, sticky="w")
    ttk.Label(popup, text="Esc: while recording, cancel").grid(
        column=0, row=5, sticky="w"
    )
    ttk.Label(popup, text="Enter: while recording, save the work").grid(
        column=0, row=6, sticky="w"
    )
    ttk.Label(popup, text="F7: while recording, pause/continue").grid(
        column=0, row=7, sticky="w"
    )
    popup.protocol("WM_DELETE_WINDOW", lambda: (popup.destroy(), unsetAlreadyOpen()))


pressedKey = 0


def popupPressAction():
    setAlreadyOpen()
    pause()

    def stopListener():
        listener.stop()
        unsetAlreadyOpen()
        unpause()
        popup.destroy()

    def saveAction():
        global pressedKey
        keyboardAction["action"] = "p"
        keyboardAction["key"] = pressedKey
        newWork["actions"].append(keyboardAction.copy())

        stopListener()

    def getPressedKey(key):
        global pressedKey
        try:
            lb_key.configure(text=key.char)  # atualiza o label com a tecla pressionada
            pressedKey = key.vk
        except AttributeError:
            # Tecla especial (ex: shift, ctrl, enter)
            # atualiza o label com a tecla pressionada
            lb_key.configure(text=str(key).replace("Key.", ""))
            pressedKey = key.value.vk

    popup = Toplevel(frame)
    popup.title("key")
    popup.geometry("240x80")
    popup.configure(padx=10, pady=10)

    popup.focus_force()
    center_window(popup)

    ttk.Label(popup, text="Pressed key:").grid(column=0, row=0)

    lb_key = ttk.Label(popup, text="", width=10, background="#FFFFFF", anchor="center")
    lb_key.grid(column=1, row=0)

    ttk.Button(popup, text="add action", command=saveAction).grid(column=0, row=1)
    ttk.Button(popup, text="cancel", command=stopListener).grid(column=1, row=1)

    popup.protocol("WM_DELETE_WINDOW", stopListener)
    listener = ppkb.Listener(getPressedKey)
    listener.start()


def watchKeyboard(key):  # desempenha uma função dependendo da tecla pressionada
    try:
        match key.char:
            case "t":  # se for t, pode abrir o popup de escrita
                if checkFilters():  # se nenhum filtro for False passa
                    popupWrite()  # se for t, abre o popup de escrita
            case "p":
                if checkFilters():  # se for p
                    popupPressAction()
    except AttributeError:  # se a tecla precionada for uma letra, n faz nada
        match key:
            case ppkb.Key.shift_r:  # shift direito ativa a ação selecionada
                if not isRecording:
                    playActions()
            case ppkb.Key.esc:  # se for esc, cancela tudo
                if checkFilters():
                    cancelAction()
            case ppkb.Key.enter:  # se for enter, salva a ação
                if checkFilters():
                    saveAction()
            case ppkb.Key.f1:
                popupHelp()  # abre o popup de ajuda
            case ppkb.Key.f7:
                if isRecording:
                    togglePause()
                print(f"isRecording: {isRecording}")
                print(f"isPaused: {isPaused}")


def startWatching():  # liga os listeners
    startRunning()
    mouseListener = mouse.Listener(on_click=recordAction)  # monitora o mouses
    mouseListener.start()


def playActions():
    global newWork
    namesList = list(map(lambda x: x["name"], works))  # ['name', 'name']
    selectedActionName = combo_actions.get()  # 'name'
    print(f"action started {selectedActionName}")

    if selectedActionName == "empty":  # se não houver ações, avisa ao usuario
        return alertError("record an action")

    # como a lista de nomes é ordenada com as mesmas posições da lista de ações, os indices de ambas são os mesmos
    actionIndex = namesList.index(
        selectedActionName
    )  # pega index do *nome da ação desejada* na *lista de nomes*
    selectedWork = works[actionIndex]  # ação selecionada
    pauseValue = input_pause.get()
    if not pauseValue:
        alertError("insert a value in milliseconds in the interval input")

    try:  # try porque quero converter uma string em int
        intPauseValue = int(pauseValue) / 1000  # valor do intervalo em int depois float
        actions = selectedWork["actions"]  # açoes do mouse
        times = int(input_repeat.get())  # vezes que a ação vai se repetir
        if len(actions) > 0:
            rep = 0  # repetições
            while rep < times:
                rep += 1
                for action in actions:  # pra cada ação na lista de ações do mouse
                    if kb.is_pressed("esc"):  # apertar esc cancela a ação
                        break
                    pa.PAUSE = intPauseValue

                    if action.__contains__("action"):
                        match action["action"]:
                            case "p":
                                kb.press(vkToScancode(action["key"]))
                                time.sleep(intPauseValue)
                            case "w":
                                pa.write(action["key"], interval=0.03)
                                time.sleep(intPauseValue)
                    else:
                        #  clica nas coordenadas
                        pa.moveTo(action["x"], action["y"])
                        functions[action["button"]]()
    except ValueError:  # caso o input de intervalo receba algo que não é um numero
        alertError("valor de intervalo invalido")
    deleteActions()  # limpa a lista de ações após a execução
    updateActions()  # atualiza a lista de ações do json


def deleteActions():
    works.clear()


def openInputNewAction():  # abre o popup de registro de ação
    global btn_record
    global worksNames

    if not isRecording:
        setAlreadyOpen()
        popup = Toplevel(frame)  # popup
        popup.geometry("180x150")  # tamanho do popup
        popup.grab_set()  # popup modal
        center_window(popup)  # centraliza o popup na tela

        ttk.Label(popup, text="Action name:").pack(pady=10)

        input_actionName = ttk.Entry(popup, takefocus=True, width=15)
        input_actionName.pack(pady=10)
        input_actionName.focus_force()  # foca no input ao abrir o popup

        def startRec():  # começa a gravação
            actionName = input_actionName.get()
            nameExists = worksNames.__contains__(
                actionName
            )  # verifica se o nome ja existe

            if nameExists:
                return alertError(
                    "there's already an action with this name"
                )  # avisa que não existe

            if len(actionName) > 0:
                newWork["name"] = actionName  # guarda o nome da ação

                print("new action:", newWork["name"])
                popup.destroy()  # fecha o popup
                unsetAlreadyOpen()  # desmarca o popup como aberto
                startWatching()  # começa a gravação
                btn_record.configure(text="⏹")

        ttk.Button(popup, text="Start Recording", command=startRec).pack(pady=10)

        def listener(keysym):
            if keysym == "Escape":  # se for esc, cancela a ação
                unsetAlreadyOpen()
                popup.destroy()

            if keysym == "Return":  # se for enter, salva a ação
                startRec()

        popup.bind(
            "<Key>", lambda e: listener(e.keysym)
        )  # liga o evento de tecla pressionada


mouseListener = None  # futuramente vai monitorar o mouse, agora ele é nulo pra renovar a thread quando for fazer uma nova gravação após o cancelamento
keyListener = ppkb.Listener(on_press=watchKeyboard)  # monitora o teclado

root = tk.Tk()
root.title("Clicker 2000")

keyListener.start()

frame = ttk.Frame(root)
frame.grid()
frame.configure(padding=10)


ttk.Label(frame, text="Record new action:").grid(column=0, row=0)
btn_record = ttk.Button(frame, text="⏺", command=openInputNewAction)
btn_record.grid(column=1, row=0)
lb_isPaused = tk.Label(frame, text="")
lb_isPaused.grid(column=2, row=0)
lb_isPaused.configure(foreground="red")

ttk.Label(frame, text="Works list").grid(column=0, row=1)
combo_actions = ttk.Combobox(frame, values=worksNames)
combo_actions.grid(column=1, row=1)
combo_actions.configure(width=10)
combo_actions.set(worksNames[0])

btn_reload = ttk.Button(frame, text="↻", command=updateLists)
btn_reload.grid(column=2, row=1)
# btn_reload.configure(width=10)

ttk.Label(frame, text="Start work").grid(column=0, row=2)
btn_play = ttk.Button(frame, text="▶", command=playActions).grid(column=0, row=3)

ttk.Label(frame, text="rep").grid(column=1, row=2)
input_repeat = ttk.Entry(frame)
input_repeat.grid(column=1, row=3)
input_repeat.insert(0, 1)
input_repeat.configure(width=3)


ttk.Label(frame, text="interval").grid(column=2, row=2)
input_pause = ttk.Entry(frame)
input_pause.grid(column=2, row=3)
input_pause.insert(0, 300)
input_pause.configure(width=5)


updateLists()
center_window(root)


frame.mainloop()
