from itertools import cycle
from random import randrange
from tkinter import Canvas, Tk, messagebox, font
import math

canvas_width = 800
canvas_height = 400

root = Tk()
root.title("Balloon Shooter")
c = Canvas(root, width=canvas_width, height=canvas_height)
c.pack()

# Membuat pola latar belakang dengan warna-warna lucu: hitam, putih, pink, ungu
colors = ["#FFC0CB", "#FF69B4", "#BA55D3", "#8A2BE2"]  # Pink cerah, Pink hot, Ungu sedang, Ungu tua
square_size = 50
for row in range(0, canvas_height, square_size):
    for col in range(0, canvas_width, square_size):
        color = colors[(row // square_size + col // square_size) % len(colors)]
        c.create_rectangle(col, row, col + square_size, row + square_size, fill=color, width=0)

color_cycle = cycle(["light blue", "light green", "light pink", "light yellow", "light cyan"])
balloon_radius = 25
balloon_score = 10
balloon_speed = 500
balloon_interval = 2000
difficulty = 0.95
shooter_color = "blue"
shooter_width = 100
shooter_height = 20
shooter_startx = canvas_width / 2 - shooter_width / 2
shooter_starty = canvas_height - shooter_height - 20

shooter = c.create_rectangle(shooter_startx, shooter_starty, shooter_startx + shooter_width, shooter_starty + shooter_height, fill=shooter_color)

game_font = font.nametofont("TkFixedFont")
game_font.config(size=18)

score = 0
score_text = c.create_text(10, 10, anchor="nw", font=game_font, fill="darkblue", text="Score: " + str(score))

lives_remaining = 3
lives_text = c.create_text(canvas_width - 10, 10, anchor="ne", font=game_font, fill="darkblue", text="Lives: " + str(lives_remaining))

balloons = []
bullets = []
explosions = []

def create_balloon():
    x = randrange(10, canvas_width - balloon_radius * 2)
    y = 40
    new_balloon = c.create_oval(x, y, x + balloon_radius * 2, y + balloon_radius * 2, fill=next(color_cycle), width=0, tags="balloon")
    balloons.append(new_balloon)
    root.after(balloon_interval, create_balloon)

def move_balloons():
    for balloon in balloons:
        (balloonx, balloony, balloonx2, balloony2) = c.coords(balloon)
        c.move(balloon, 0, 10)
        if balloony2 > canvas_height:
            balloon_dropped(balloon)
    root.after(balloon_speed, move_balloons)

def balloon_dropped(balloon):
    balloons.remove(balloon)
    c.delete(balloon)
    lose_a_life()
    if lives_remaining == 0:
        messagebox.showinfo("Game Over!", "Final Score: " + str(score))
        root.destroy()

def lose_a_life():
    global lives_remaining
    lives_remaining -= 1
    c.itemconfigure(lives_text, text="Lives: " + str(lives_remaining))

def check_hit():
    for bullet in bullets:
        (bulletx, bullety, bulletx2, bullety2) = c.coords(bullet)
        for balloon in balloons:
            (balloonx, balloony, balloonx2, balloony2) = c.coords(balloon)
            if balloonx < bulletx2 and bulletx < balloonx2 and balloony < bullety2 and bullety < balloony2:
                balloons.remove(balloon)
                bullets.remove(bullet)
                c.delete(bullet)
                create_explosion(balloonx, balloony)
                increase_score(balloon_score)
                break
    root.after(100, check_hit)

def create_explosion(x, y):
    num_particles = 10
    for _ in range(num_particles):
        angle = randrange(360)
        distance = randrange(20, 50)
        x_end = x + distance * math.cos(math.radians(angle))
        y_end = y + distance * math.sin(math.radians(angle))
        particle = c.create_oval(x, y, x + 5, y + 5, fill="orange", width=0)
        explosions.append((particle, x_end, y_end))
    animate_explosion()

def animate_explosion():
    for explosion in explosions:
        particle, x_end, y_end = explosion
        c.move(particle, (x_end - c.coords(particle)[0]) / 5, (y_end - c.coords(particle)[1]) / 5)
    root.after(50, lambda: [c.delete(particle) for particle, _, _ in explosions[:]])
    explosions.clear()

def increase_score(points):
    global score, balloon_speed, balloon_interval
    score += points
    balloon_speed = int(balloon_speed * difficulty)
    balloon_interval = int(balloon_interval * difficulty)
    c.itemconfigure(score_text, text="Score: " + str(score))

def move_left(event):
    (x1, y1, x2, y2) = c.coords(shooter)
    if x1 > 0:
        c.move(shooter, -20, 0)

def move_right(event):
    (x1, y1, x2, y2) = c.coords(shooter)
    if x2 < canvas_width:
        c.move(shooter, 20, 0)

def shoot(event):
    (shooterx1, shootery1, shooterx2, shootery2) = c.coords(shooter)
    x = (shooterx1 + shooterx2) / 2
    new_bullet = c.create_line(x, shootery1, x, shootery1 - 10, fill="red", width=2, tags="bullet")
    bullets.append(new_bullet)
    move_bullets()

def move_bullets():
    for bullet in bullets:
        (bulletx, bullety, bulletx2, bullety2) = c.coords(bullet)
        c.move(bullet, 0, -10)
        if bullety < 0:
            bullets.remove(bullet)
            c.delete(bullet)
    root.after(50, move_bullets)

def move_shooter(event):
    x = event.x
    (shooterx1, shooter_y1, shooterx2, shooter_y2) = c.coords(shooter)
    if 0 <= x <= canvas_width - shooter_width:
        c.coords(shooter, x, shooter_y1, x + shooter_width, shooter_y2)

def balloon_click(event):
    items = c.find_closest(event.x, event.y)
    if "balloon" in c.gettags(items[0]):
        balloons.remove(items[0])
        balloon_coords = c.coords(items[0])
        create_explosion(balloon_coords[0], balloon_coords[1])
        c.delete(items[0])
        increase_score(balloon_score)

c.bind("<Left>", move_left)
c.bind("<Right>", move_right)
c.bind("<space>", shoot)
c.bind("<Motion>", move_shooter)
c.bind("<Button-1>", balloon_click)  # Bind mouse click event to balloon_click function
c.focus_set()
root.after(1000, create_balloon)
root.after(1000, move_balloons)
root.after(1000, check_hit)
root.mainloop()
