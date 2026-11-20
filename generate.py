#!/usr/bin/env python3
"""Blattwerk · reproduzierbarer SVG/PNG-Export. Aufruf: python generate.py"""
from pathlib import Path
import html, json
import cairosvg
ROOT=Path(__file__).resolve().parent
# I Kontur, B Körper, L Papier, M Schatten, H Licht, A Akzent, D dunkles Detail
pal={
'fern':('#174c40','#58bd8b','#d5f2cf','#328862','#f5fff0','#dbec79','#255e49'),
'cobalt':('#29476a','#609cde','#d7eaff','#477cb6','#f4faff','#f6c770','#345978'),
'iris':('#493d70','#ac92d8','#e8ddf8','#8269b5','#fcf6ff','#ffd589','#63508b'),
'coral':('#703e4a','#ed98a0','#ffe0d4','#cf7685','#fff5e9','#ffc979','#965660'),
'honey':('#624d2d','#eac365','#fff0bc','#cc9845','#fffae3','#f39c71','#876936'),
'sea':('#28555c','#63bcb6','#d1eeeb','#418f94','#f3fffb','#f4c775','#346d74'),
'ember':('#743d34','#ee876a','#ffdfb9','#c46552','#fff5d8','#ffcf62','#94503e')}
keys='IBLMHAD'; mono=dict(zip(keys,['white','white','black','white','black','black','white']))
# Shape constructors use palette tokens, not hard-coded colours.
def col(k):return colors.get(k,k)
def attrs(f,s,w):return f'fill="{col(f)}" stroke="{col(s)}" stroke-width="{w}"'
def p(d,f='none',s='I',w=2.6,extra=''):return f'<path d="{d}" {attrs(f,s,w)} {extra}/>'
def r(x,y,w,h,rr,f='B',s='I',sw=2.6):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rr}" {attrs(f,s,sw)}/>'
def c(x,y,rad,f='B',s='I',w=2.6):return f'<circle cx="{x}" cy="{y}" r="{rad}" {attrs(f,s,w)}/>'
def line(d,s='I',w=2):return p(d,'none',s,w)
def group(content,t):return f'<g transform="{t}">{content}</g>'
def tilt(z,a=38):return group(z,f'rotate({a} 32 32)')
def nibpen():return tilt(r(26,5,12,31,4,'B')+r(26,10,12,5,1,'A','I',1.8)+line('M29 19v12','H')+p('M26 35h12l3 8-9 16-9-16Z','L')+line('M32 56V46')+c(32,44,2,'I','none'))
def standard():return tilt(r(18,17,28,33,5,'B')+p('M18 34h28v11q0 5-5 5H23q-5 0-5-5Z','L')+line('M23 23h12','H',2.6)+line('M22 39h20','M'),42)
def shapes():return r(8,12,27,29,5,'B')+p('m40 9 15 26H25Z','A')+c(38,43,13,'L')+line('M30 43q0-6 6-8','M')
def page():return p('M17 8h22l10 10v34q0 4-4 4H17q-4 0-4-4V12q0-4 4-4Z','L')+p('M38 8v11h11Z','B','I',2)
def icon(k):
 if k=='stift':return tilt(r(26,7,12,36,4,'B')+p('M26 37h12v7l-6 13-6-13Z','L')+p('m29 51 3 7 3-7Z','I','I',1.5)+r(26,14,12,4,0.7,'A','I',1.6)+line('M29.5 21v12','H',2))
 if k=='freihandlasso':return p('M19 42C6 36 9 19 22 13c13-7 31-1 32 12 1 14-15 22-29 18','none','I',6)+p('M19 42C6 36 9 19 22 13c13-7 31-1 32 12 1 14-15 22-29 18','none','B',2.8)+line('M23 43c10 11 18 17 23 8 3-6-4-9-6-5','I',3.2)+c(22,42,4.8,'A')
 if k=='boxlasso':return r(12,14,40,34,3,'L','none')+p('M14 14h36q2 0 2 2v30q0 2-2 2H14q-2 0-2-2V16q0-2 2-2Z','none','I',2.8,'stroke-dasharray="4 5"')+''.join(r(x-3.3,y-3.3,6.6,6.6,1.5,'B') for x,y in [(12,14),(52,14),(12,48),(52,48)])
 if k=='radiergummi':return tilt(r(20,9,24,44,5,'B')+p('M20 30h24v18q0 5-5 5H25q-5 0-5-5Z','L')+line('M24 16v9','H',2.5)+line('M24 35h16','M'),43)+line('M32 55h19','I',2.4)
 if k=='textfeld':return r(9,12,46,40,4,'L')+p('M21 23h22v6h-3l-1-2h-4v15h4v3H25v-3h4V27h-4l-1 2h-3Z','I','none')+r(6,9,7,7,1.5,'B','I',2)+r(51,48,7,7,1.5,'B','I',2)
 if k=='formen':return shapes()
 if k=='sticker':return p('M11 23q0-8 8-9l24-4q8-1 9 7l3 18q0 4-3 8L40 54q-2 2-6 2l-15 1q-6 0-7-7Z','B')+p('M37 55q4-7 3-14 7 2 14-3Z','L')+c(24,29,2.5,'F','none')+c(39,26,2.5,'F','none')+line('M25 37q7 6 13-2','F',2.8)+line('m17 22 7-1','H')
 if k=='bilder':return group(r(9,16,42,34,4,'M'),'rotate(-9 30 33)')+r(14,14,42,34,4,'L')+c(45,23,3.8,'A','I',1.6)+p('m17 43 11-15 9 10 5-6 11 11v2H17Z','B','I',1.9)
 if k=='notizzettel':return group(r(13,11,39,44,4,'M'),'rotate(-6 32 32)')+p('M14 10h36q2 0 2 3v27L38 53H15q-3 0-3-3V13q0-3 2-3Z','L')+p('M38 53V40h14Z','B')+r(22,7,20,7,1,'A','I',1.8)+line('M19 24h25m-25 7h19m-19 7h10','D',2.3)
 if k=='laserpointer':return tilt(r(26,23,12,34,4,'B')+r(26,23,12,7,2,'L','I',2)+r(30,34,4,8,2,'F','none')+line('M32 18v-9m-6 10-3-4m15 4 3-4','I',2.8)+c(32,5,2,'A','I',1.5))
 if k=='seitenleiste':return r(7,13,50,38,5,'L')+p('M12 13h13v38H12q-5 0-5-5V18q0-5 5-5Z','B')+line('M12 22h8m-8 7h6m-6 7h6','H',2.2)+line('M32 22h17m-17 7h12','D',2)
 if k=='suche':return p('m38 40 4-4 13 13q3 3 0 6t-6 0Z','B')+c(27,27,18,'B')+c(27,27,12,'L','I',2)+line('M19 27q0-7 7-8','M',2.3)
 if k=='weltkugel':return c(32,32,23,'B')+p('M32 9c-16 11-16 35 0 46 16-11 16-35 0-46Z','L','I',2)+line('M10 32h44M15 18q17 10 34 0M15 46q17-10 34 0M32 10v44','I',2)
 if k=='lesemodus':return page()+line('M20 23h12m-12 7h14','D')+p('M22 43q16-22 36 0-18 22-36 0Z','B')+c(40,43,6,'L','I',2)+c(40,43,2.6,'I','none')
 if k=='seite-hinzufuegen':return page()+line('M20 24h12m-12 7h13','D')+c(47,46,12,'B')+line('M41 46h12m-6-6v12','H',3)
 if k=='seiten':return r(9,16,33,40,4,'M')+r(16,11,33,40,4,'B')+r(23,7,32,40,4,'L')+r(29,14,20,8,1.5,'B','I',1.7)+line('M29 29h19m-19 6h13','D')
 if k=='mehr':return r(6,19,52,26,13,'B')+''.join(c(x,32,2.8,'I','none') for x in [19,32,45])+line('M17 23h15','H',1.7)
 if k=='fueller':return nibpen()
 if k=='kugelschreiber':return tilt(r(29,4,6,7,1,'L','I',2)+r(27,10,10,34,3,'B')+p('M27 39h10l-1 8-4 10-4-10Z','L')+line('M32 54v4','I',2.6)+line('M36 13h5v14','I',2.7)+line('M30 18v15','H'))
 if k=='pinsel':return tilt(p('M29 31 30 9q0-5 3-5t3 5l-1 23Z','B')+p('m26 31 11 1-1 10-12-1Z','L')+p('M24 40q-6 4-4 11t-5 9q18 1 21-12 1-4-1-7Z','M')+line('M30 44q0 7-6 11','H',2)+line('m26 36 9 1','D',1.8),29)
 if k=='textmarker':return tilt(r(23,7,18,34,4,'B')+p('M23 35h18l-3 11H26Z','L')+p('M27 46h10v7l-10 5Z','A')+line('M27 14v15','H',3)+line('M24 11h16','I',1.7))
 if k=='bleistift':return tilt(r(26,6,12,41,2,'B')+r(26,5,12,8,2,'A','I',2)+r(26,13,12,4,0,'L','I',1.6)+line('M30 18v26','F',1.8)+p('m26 45 6 14 6-14-3 2-3-2-3 2Z','L','I',1.9)+p('m30 53 2 6 2-6Z','I','I',1.3))
 if k=='tape':return p('M27 21h14v12q1 6 7 8l11 3-4 3 2 5-16-4q-14-3-14-15Z','L')+p('M26 12q20-2 20 17t-17 20l-8-1Z','M')+f'<ellipse cx="24" cy="30" rx="16" ry="18" {attrs("B","I",2.6)}/>'+f'<ellipse cx="24" cy="30" rx="7" ry="8.5" {attrs("L","I",2.3)}/>'+line('m46 42-3 5m8-4-3 5','D',1.6)+line('M13 25q2-6 7-8','H')
 if k=='formen-werkzeug':return p('M31 7 56 53H7Z','B')+p('m31 24 10 19H21Z','L','I',2)+line('m17 44 3 2m0-9 3 2m1-9 3 2','I',1.8)+c(46,18,9,'A')
 if k=='praezisionsradierer':return tilt(r(27,7,10,35,3,'B')+p('M27 36h10l-1 10h-8Z','L')+p('M29 46h6v8q-1 4-5 3l-1-2Z','A')+line('M30 15v15','H'))+line('M35 51h4m4 0h3m4 0h2','D',2)
 if k=='standardradierer':return standard()
 if k=='strichradierer':return line('M7 49q4-7 9-2t11 4','D',3.6)+p('M30 51q9 1 13-7t12-7','none','M',2.5,'stroke-dasharray="3 5"')+group(standard(),'translate(2 -5) scale(.91)')
 if k in ('rueckgaengig','vorgaengig'):
  a=p('M8 28 25 12q2-2 2 1v8h7c16 0 23 12 22 28q0 4-2 1c-5-11-12-17-22-17h-5v9q0 2-2 0L8 30q-1-1 0-2Z','I','I',1.6);return a if k=='rueckgaengig' else group(a,'translate(64 0) scale(-1 1)')
 if k=='haus':return p('M7 30 30 10q2-2 4 0l23 20q2 2 0 4l-2 2q-1 1-3 0l-3-3v19q0 3-3 3h-9V39H27v16h-9q-3 0-3-3V33l-3 3q-2 1-3 0l-2-2q-2-2 0-4Z','I','none')
 if k=='schliessen':return line('m17 17 30 30m0-30L17 47','I',7)
 raise KeyError(k)
groups=[('Werkzeugleiste', [('stift','Stift','fern'),('freihandlasso','Freihandlasso','fern'),('boxlasso','Boxlasso','sea'),('radiergummi','Radiergummi','coral'),('textfeld','Textfeld','fern'),('formen','Formen','iris'),('sticker','Objekte · Sticker','honey'),('bilder','Bilder','cobalt'),('notizzettel','Notizzettel','honey'),('laserpointer','Laserpointer','ember')]),('Navigation & Seiten',[('seitenleiste','Seitenleiste','fern'),('suche','Suche','fern'),('weltkugel','Weltkugel · Internet','fern'),('lesemodus','Nur Lesemodus','fern'),('seite-hinzufuegen','Seite hinzufügen','fern'),('seiten','Seiten','fern'),('mehr','Mehr','fern')]),('Schreibspitzen',[('fueller','Füller','fern'),('kugelschreiber','Kugelschreiber','cobalt'),('pinsel','Pinsel','ember')]),('Zeichenwerkzeuge',[('textmarker','Textmarker','fern'),('bleistift','Bleistift','honey'),('tape','Tape','sea'),('formen-werkzeug','Formen','iris')]),('Radierer',[('praezisionsradierer','Präzisionsradierer','sea'),('standardradierer','Standardradierer','coral'),('strichradierer','Strichradierer','iris')]),('Verlauf',[('rueckgaengig','Rückgängig','fern'),('vorgaengig','Vorgängig','fern')]),('App-Navigation',[('haus','Haus · Startseite','fern'),('schliessen','Kreuz · Schließen','fern')])]
variants=[['farbe','schwarz','weiss'],['gruen'],['farbe','schwarz','weiss'],['farbe','schwarz','weiss'],['farbe'],['schwarz','weiss'],['schwarz','weiss']]
import io,base64
from PIL import Image
HEADER='<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">'
def paint(raw):return '<g stroke-linecap="round" stroke-linejoin="round">'+raw+'</g>'
def render(i,k,label,palette,v):
 global colors
 ism=v in ('schwarz','weiss');colors=mono.copy() if ism else dict(zip(keys,pal[palette]));colors['F']='black' if ism else colors['I'];raw=icon(k)
 layers=paint(raw);ink='#000000' if v=='schwarz' else '#ffffff';key=f'g{i:02}-{k}-{v}';body=layers
 if ism:body=f'<defs><mask id="m-{key}" maskUnits="userSpaceOnUse" x="0" y="0" width="64" height="64">{layers}</mask></defs><rect width="64" height="64" fill="{ink}" mask="url(#m-{key})"/>'
 svg=HEADER+f'<title>{html.escape(label)} · {v}</title>'+body+'</svg>';folder=ROOT/'SVG'/f'G{i:02}';folder.mkdir(parents=True,exist_ok=True);(folder/(key+'.svg')).write_text(svg)
 # Supersample once. For masks rasterize luminance explicitly (CairoSVG masks use alpha).
 source=HEADER+('<rect width="64" height="64" fill="black"/>' if ism else '')+layers+'</svg>';img=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=source.encode(),output_width=768,output_height=768))).convert('RGBA')
 if ism:
  alpha=img.convert('L');img=Image.new('RGBA',img.size,ink);img.putalpha(alpha)
 for size in (32,64,96,256):
  folder=ROOT/'PNG'/str(size)/f'G{i:02}';folder.mkdir(parents=True,exist_ok=True);img.resize((size,size),Image.Resampling.LANCZOS).save(folder/(key+'.png'))
 asset=ROOT/'Blattwerk.xcassets'/(key+'.imageset');asset.mkdir(parents=True,exist_ok=True);entries=[]
 for n in (1,2,3):
  fname=f'{key}@{n}x.png';(asset/fname).write_bytes((ROOT/'PNG'/str(32*n)/f'G{i:02}'/(key+'.png')).read_bytes());entries.append(dict(idiom='universal',filename=fname,scale=f'{n}x'))
 info=dict(version=1,author='xcode');(asset/'Contents.json').write_text(json.dumps(dict(images=entries,info=info,properties={'template-rendering-intent':'original'}),indent=2));(ROOT/'Blattwerk.xcassets'/'Contents.json').write_text(json.dumps(dict(info=info)))
 return 'data:image/svg+xml;base64,'+base64.b64encode(svg.encode()).decode()
def main():
 data=[]
 for i,(name,items) in enumerate(groups,1):
  data.append(dict(name=name,items=[dict(label=l,id=k,icons={v:render(i,k,l,pa,v) for v in variants[i-1]}) for k,l,pa in items]))
 (ROOT/'Vorschau.html').write_text((ROOT/'vorschau.template').read_text().replace('/*ICON_DATA*/',json.dumps(data,ensure_ascii=False)))
if __name__=='__main__':main()
