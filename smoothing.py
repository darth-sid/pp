from tkinter import *
from tkinter import ttk
from PIL import ImageTk,Image
import time
import random
import copy
import math

#draw lines between pts
l = False
#mouse coords
x,y = 0,0
#dot radius
r = 1
#path points
start_pts = [[300,100,-1],[300,300,0],[200,300,-1]]
#index of clicked path point
clicked_index = -1
#range in which a dot should be clickable
click_r = 10
#stores all drawn elements for easy deletion
items = []
#last lookahead index
pli = 0
#updates mouse pos 
def trackmouse(event):
    global x,y
    x,y = event.x,event.y
#creates new path point
def newpt(event):
    global l
    if event.char == 'p': start_pts.append([100,100])
    elif event.char == 'l': l = not l
#click a dot makes it draggable + sets focus in window
def click(event):
    canvas.focus_set()
    global clicked_index
    for pt in start_pts:
        if abs(event.x - pt[0])<click_r and abs(event.y - pt[1])<click_r:
            clicked_index = start_pts.index(pt)
#resets clicked dot to none when click is released
def release(event):
    global clicked_index
    #if clicked_index != -1: start_pts[clicked_index] = [event.x,event.y]
    clicked_index = -1  

#gets distance between two points
def distance(pt1,pt2):
    x1,y1 = pt1[:2]
    x2,y2 = pt2[:2]
    dx = abs(x1-x2)
    dy = abs(y1-y2)
    return pow((pow(dx,2)+pow(dy,2)),0.5)

#dotproduct
def dot(v1,v2):
    s = 0
    for i in range(len(v1)):
        s += v1[i]*v2[i]
    return s

#represents the driving object
class Bot:
    def __init__(self,x,y,size,color,angle,lookahead):
        self.x = x
        self.y = y
        self.color = color
        self.size = size*math.sin(math.pi/4)
        self.angle = angle
        self.img = None
        self.circle = None
        self.lookahead = lookahead
        self.draw()
    def move(self,dx,dy):
        self.x += dx
        self.y += dy
        self.draw()
    def fwd(self,d):
        self.move(math.cos(self.angle)*d,math.sin(self.angle)*d)
    def draw(self):
        v = []
        for i in range(4):
            v.append([self.x+math.cos(self.angle+math.pi*i/2+math.pi/4)*self.size,self.y+math.sin(self.angle+math.pi*i/2+math.pi/4)*self.size])
        canvas.delete(self.img)
        canvas.delete(self.circle)
        self.img = canvas.create_polygon(v,fill=self.color,outline=self.color)
        self.circle = canvas.create_oval(self.x-self.lookahead,self.y-self.lookahead,self.x+self.lookahead,self.y+self.lookahead,outline=self.color)
    def rotate(self,da):
        self.angle += da*math.pi/180
    def sim_move(self,l,r):
        self.fwd((l+r)/2)
        self.rotate((r-l)/10)
    def getRect(self):
        return self.img
    def getCoords(self):
        return self.x,self.y
    def getLookAhead(self,pts):
        global pli
        p = None
        for i in range(len(pts)-1):
            d = [pts[i+1][0]-pts[i][0],pts[i+1][1]-pts[i][1]]
            f = [pts[i][0]-self.x,pts[i][1]-self.y]
            a = dot(d,d)
            b = 2*dot(f,d)
            c = dot(f,f) - self.lookahead ** 2
            discriminant = b*b - 4*a*c
            if discriminant > 0:
                discriminant = pow(discriminant,0.5)
                t1 = (-b-discriminant)/(2*a)
                t2 = (-b+discriminant)/(2*a)
                if (t1 >= 0 and t1 <= 1 and (i+t1) > pli):
                    pli = i+t1
                    return [pts[i][0] + t1*d[0], pts[i][1] + t1*d[1]]
                if (t2 >= 0 and t2 <= 1 and (i+t2) > pli):
                    pli = i+t1
                    return [pts[i][0] + t2*d[0], pts[i][1] + t2*d[1]]
            '''d = distance([self.x,self.y],pt)
            if d < self.lookahead and (p is None or d > distance([self.x,self.y],p)):
                p = pt
        return p'''
    #finds point nearest to passed in position (used to find closest point to bot)
    def nearestPt(self,pts):
        p = pts[0]
        for pt in pts:
            if distance([self.x,self.y],pt) < distance([self.x,self.y],p):
                p = pt
        return p


#screen setup
root = Tk()
root.title("test")
root.configure(width=500,height=500,bg='white')
root.geometry(f"{500}x{500}")
width = root.winfo_reqwidth()
height = root.winfo_reqheight()
root.geometry(f"+{int(root.winfo_screenwidth()/2-width/2)}+{int(root.winfo_screenheight()/2-height/2)}")

canvas = Canvas(root)
canvas.configure(bg="black")
#mouse+keyboard events
canvas.bind("<Button-1>",click)
canvas.bind("<ButtonRelease-1>",release)
canvas.bind("<Motion>",trackmouse)
canvas.bind("<KeyPress>",newpt)
canvas.pack(fill="both",expand=True)
#img bg
#img = ImageTk.PhotoImage(Image.open("field_layout.png"))
#canvas.create_image(0,0, anchor=NW, image=img)

#injects waypoints between path points
def inject(n):
    pts = []
    for i in range(len(start_pts)-1):
        pts.append(start_pts[i])
        for j in range(1,n+1):
            x = start_pts[i][0]-(start_pts[i][0]-start_pts[i+1][0])*j/(n+1)
            y = start_pts[i][1]-(start_pts[i][1]-start_pts[i+1][1])*j/(n+1)
            pts.append([x,y,0])
    pts.append(start_pts[-1])
    return pts
#smooths out sharp path
def smooth(ogpts,pts_,a,b,n):
    pts = copy.deepcopy(pts_)
    newpts = copy.deepcopy(pts)
    for i in range(n):
        for i in range(n):
            for i in range(1,len(pts)-1):
                newpts[2] = pts[2]
                for j in range(len(pts[i][:2])):
                    avg = (pts[i-1][j] + pts[i+1][j])/2
                    newpts[i][j] += a*(ogpts[i][j]-newpts[i][j]) + b*(avg-newpts[i][j])
        pts = newpts
    return pts
#redraws all pts on screen (updates positions)
def draw(pts):
    global l
    #canvas.create_oval(-500,-500,2000,2000,outline='red',fill='black')
    for item in items:
        canvas.delete(item)
    for pt in pts:
        if pt in start_pts:
            pass#items.append(canvas.create_oval(pt[0]-r,pt[1]-r,pt[0]+r,pt[1]+r,outline='lime',fill='lime'))
        else:
            items.append(canvas.create_oval(pt[0]-r,pt[1]-r,pt[0]+r,pt[1]+r,outline='red',fill='red'))
    for pt in start_pts:
        items.append(canvas.create_oval(pt[0]-r,pt[1]-r,pt[0]+r,pt[1]+r,outline='lime',fill='lime'))
    if l:
        for i in range(len(pts[:-1])):
            items.append(canvas.create_line(pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1]))
#gets curvature of path at any given point using neighbor pts
def curvature(pts):
    x1,y1 = pts[0][:2]
    x1 += 0.0000001
    x2,y2 = pts[1][:2]
    x3,y3 = pts[2][:2]
    k1  = 0.5*(x1*x1-x2*x2+y1*y1-y2*y2)/(x1-x2)
    k2 = (y1-y2)/(x1-x2)
    b = 0.5*(x2*x2 - 2*x2*k1 + y2*y2 - x3*x3 + 2*x3*k1 - y3*y3)/(x3*k2 - y3 + y2 - x2*k2)
    a = k1-k2*b
    r_sq = (x1-a)*(x1-a) + (y1-b)*(y1-b)
    r = pow(r_sq,0.5)
    return 1/r
#center of the circle that passes through some 3 points
def center(pts):
    x1,y1 = pts[0][:2]
    x2,y2 = pts[1][:2]
    x3,y3 = pts[2][:2]
    r = 1/curvature(pts)
    d = pow((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1),0.5)
    a = (d*d)/(2*d)
    ix = x1+((x2-x1)*a/d)
    iy = y1+((y2-y1)*a/d)
    h = pow(((r*r)-(a*a)),0.5)
    rx = -(y2-y1)*h/d
    ry = -(x2-x1)*h/d
    ipx1 = ix+rx
    ipy1 = iy+ry
    ipx2 = ix-rx
    ipy2 = iy-ry
    p1 = [ipx1,ipx2]
    p2 = [ipy1,ipy2]
    for px in p1:
        for py in p2:
            z = pow(pow(x3-px,2)+pow(y3-py,2),0.5)
            #print(z,r)
            if abs(z - r) < 2: 
                return (px,py)    

#setup
og = inject(2)
currpts = copy.deepcopy(og)
check = copy.deepcopy(start_pts)
bot = Bot(start_pts[0][0],start_pts[0][1],10,'blue',math.pi/2,100)

#circle stuff :p
cr = 1/curvature(currpts[:3])
cx,cy = center(currpts[:3])
corcle = canvas.create_oval(cx-cr,cy-cr,cx+cr,cy+cr,outline='green')

lastpt = 0
#mainloop
while True:
    #redraws circle
    canvas.delete(corcle)
    cr = 1/curvature(currpts[:3])
    cx,cy = center(currpts[:3])
    corcle = canvas.create_oval(cx-cr,cy-cr,cx+cr,cy+cr,outline='green')
    
    #drag points around
    if clicked_index != -1: 
        start_pts[clicked_index] = [x,y]

    #updates path and waypoints if path points are moved
    if check != start_pts:
        og = inject(5)
        currpts = copy.deepcopy(og)
        check = copy.deepcopy(start_pts)

    #smooths path again if path changes
    currpts = smooth(og,currpts,0.25,0.75,100)
    temp = [currpts[0]]
    temp[0][2] = (-1)
    for i in range(1,len(currpts)-1):
        temp.append([ currpts[i][0] , currpts[i][1] , curvature(currpts[i-1:i+2]) ])  
    temp.append([ currpts[-1][0] , currpts[-1][1] , -1 ])
    #print(temp)
    #update/redraw pts
    draw(currpts)

    #bot movement
    #lookahead pt
    #lp = bot.getLookAhead(currpts[lastpt:])
    #closest pt
    lp = lp if bot.getLookAhead(currpts) is None else bot.getLookAhead(currpts)
    cp = bot.nearestPt(currpts)

    #items.append(canvas.create_oval(lp[0]-r-1,lp[1]-r-1,lp[0]+r+1,lp[1]+r+1,outline='yellow'))
    items.append(canvas.create_oval(lp[0]-r-1,lp[1]-r-1,lp[0]+r+1,lp[1]+r+1,outline='yellow'))
    items.append(canvas.create_oval(cp[0]-r-1,cp[1]-r-1,cp[0]+r+1,cp[1]+r+1,outline='orange'))
    bot.fwd(1)
    bot.rotate(0)
    for pt in currpts:
        if(distance(bot.getCoords(),pt) < 10):
            lastpt = currpts.index(pt)
    #update tk window
    root.update();
    time.sleep(1/60);
