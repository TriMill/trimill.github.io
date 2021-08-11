#!/usr/bin/python3
import os
import re
import pathlib
import time

fieldre = re.compile(r"(?sm)^<!--([A-Z_]+)\s([^-]*)-->$")
replre = re.compile(r"\{\{([A-Z_]+)\}\}")

templatename = "_template_.html"
path = pathlib.Path().absolute()
while True:
    if templatename in os.listdir(path):
        with open(os.path.join(path, templatename)) as templatefile:
            print(f"found {templatename}")
            template = templatefile.read()
            break
    if path == path.parent:
        raise Exception("Could not find template file in any superdirectory.")
    path = path.parent

time_begin = time.perf_counter()
count = 0
for subdir, dirs, files in os.walk("."):
    for file in files:
        if file.startswith("_t_") and file.endswith(".html"):
            with open(os.path.join(subdir, file)) as readfile:
                text = readfile.read()
            fields = {}
            for match in fieldre.finditer(text):
                groups = match.groups()
                fields[groups[0]] = groups[1]
            fields["BODY"] = text
            newtext = ""
            lastidx = 0
            for match in replre.finditer(template):
                span = match.span()
                field = match.groups()[0]
                newtext += template[lastidx:span[0]]
                if field in fields:
                    newtext += fields[field]
                lastidx = span[1]
            newtext += template[lastidx:]
            for k,v in fields.items():
                newtext = newtext.replace("{{"+k+"}}", v)
            outfilename = os.path.join(subdir, file[3:])
            with open(outfilename, "w") as outfile:
                print(f"generated {outfilename}")
                outfile.write(newtext)
            count += 1

time_elapsed = (time.perf_counter() - time_begin)*1000
print(f"done! generated {count} pages in {time_elapsed:.2f}ms")
