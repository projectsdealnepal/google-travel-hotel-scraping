
import pyautogui
import time
import random
end_time = "02:00 AM"
while True:
    # current_time = datetime.datetime.now().strftime("%I:%M %p")
    # if current_time == end_time:
    #     break
    values = list([100, 200, 300, 400, 500])
    pixel = list([100, 200, 300, 400, 500])
    # print(values)
    x1 = random.choice(values)
    x2 = random.choice(values)
    y = random.choice(pixel)
    # print(y)
    pyautogui.click(x1, x1)
    pyautogui.moveTo(x1, x2)
    pyautogui.moveRel(0, y)  # move mouse 10 pixels down
    pyautogui.dragTo(x1, x2)
    pyautogui.dragRel(0, y)  # drag mouse 10 pixels down
    pyautogui.scroll(y)  # scroll up 10 "clicks"
    pyautogui.scroll(-y)  # scroll down 10 "clicks"
    pyautogui.scroll(y, x=x1, y=x2)  #
    pyautogui.hscroll(y)  # scroll right 10 "clicks"
    pyautogui.hscroll(-y)  # scro
    time.sleep(20)


