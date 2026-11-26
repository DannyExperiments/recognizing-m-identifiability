"""Rotate the worked two-center matching in 3D."""

from math import cos, sin, tau
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 800, 480
BG, PANEL = "#101b2e", "#192a43"
INK, MUTED = "#f0f6ff", "#bacee7"
MINT, AMBER, BLUE = "#80e8cf", "#ffc385", "#7998be"
NODES = {
    "v": (0, -.19, 1.13), "h": (0, -.58, .51), "r": (0, .58, -.45),
    "a": (-1.45, .27, .41), "b": (1.45, .27, .41),
    "c": (-1.45, -.15, -.65), "d": (1.45, -.15, -.65),
}
OTHER_EDGES = [("v","h"),("a","r"),("b","r")]
MATCHED_EDGES = [("a","h"),("h","b"),("c","r"),("r","d")]


def font(name, size):
    try:
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default(size=size)


def project(pos, angle):
    x,y,z=pos
    side=x*cos(angle)-y*sin(angle)
    toward=x*sin(angle)+y*cos(angle)
    up=z*cos(.30)-toward*sin(.30)
    depth=toward*cos(.30)+z*sin(.30)
    zoom=7/(7-depth)
    return 401+side*151*zoom,253-up*107*zoom,depth


def draw_frame(angle, fonts):
    title, label, node_label, strong=fonts
    image=Image.new("RGB",(WIDTH,HEIGHT),BG)
    draw=ImageDraw.Draw(image)
    draw.text((27,20),"When the pivot certifies a factor",font=title,fill=INK)
    draw.rounded_rectangle((26,86,774,369),14,fill=PANEL)
    draw.text((45,103),"Left side",font=label,fill=MUTED)
    draw.text((618,103),"Right side",font=label,fill=MUTED)
    points={name:project(pos,angle) for name,pos in NODES.items()}
    for edges,color,width in ((OTHER_EDGES,BLUE,3),(MATCHED_EDGES,MINT,7)):
        for u,v in edges:
            draw.line([points[u][:2],points[v][:2]],width=width,fill=color)
    for name,(x,y,_) in sorted(points.items(),key=lambda item:item[1][2]):
        radius=18 if name in ("h","r","v") else 15
        fill=AMBER if name in ("h","r") else MINT if name!="v" else INK
        draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill=fill,outline=PANEL,width=2)
        draw.text((x,y-1),name,font=node_label,fill=BG,anchor="mm")
    draw.text((29,385),"Base 2/2",font=strong,fill=MINT)
    draw.text((267,385),"With pivot 2/3",font=strong,fill=AMBER)
    draw.text((30,437),"A third path needs a third center. Certify h.",font=label,fill=INK)
    return image


def main():
    fonts=(font("Arial Bold.ttf",43),font("Arial.ttf",29),
           font("Arial Bold.ttf",25),font("Arial Bold.ttf",39))
    frames=[draw_frame(.59*sin(tau*i/72)-.17,fonts) for i in range(72)]
    frames[0].save(Path(__file__).with_name("certify-pivot.gif"),save_all=True,
                   append_images=frames[1:],duration=84,loop=0,optimize=False)


if __name__=="__main__":
    main()
