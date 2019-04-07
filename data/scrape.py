import glob
import pathlib
import random
import os
import sys
import json
from pprint import pprint

import lxml.html
import requests
from lxml.cssselect import CSSSelector


xp_advisor_list = '//*[@id="txtHint"]/div'
sel_title = CSSSelector("div.dbg0pd")
sel_details = CSSSelector("span.rllt__details.lqhpac")

with open("fsu_adv_src.html") as f:
    page_src = f.read()

tree = lxml.html.fromstring(page_src)

fsu_advisors = {}
major_name = ""
found_major_advisor_section = False

for div in [el for el in tree.xpath(xp_advisor_list) if "underline2" not in el.classes]:
    # if a valid name of a major
    if list(div.classes) == ["row"] and div.text_content():
        found_major_advisor_section = True
        major_name = div.text_content()
        fsu_advisors[major_name] = []
        print(f"\n***{major_name}***\n")
    elif found_major_advisor_section:
        if len(list(div.iterchildren())) != 3:
            continue

        advisor = {}

        should_add_advisor = False
        for i, col in enumerate(div.iterchildren()):
            if i == 0:
                advisor["name"] = col.text.replace("\xa0", " ")
                advisor["email"] = [
                    c for c in col.getchildren() if c.tag not in ("br",)
                ][0].text
            elif i == 1:
                advises_for = col.text_content().split("Advisor")
                if advises_for[0].strip().lower() != "academic":
                    continue
                should_add_advisor = True  # only add academic advisors
                advisor["advises_for"] = advises_for[-1].split()
            elif i == 2:
                advisor["info"] = col.text_content()

        if should_add_advisor:
            fsu_advisors[major_name].append(advisor)

fsu_advisors = {k: v for k, v in fsu_advisors.items() if len(v)}


with open("advisors.json", "w") as f:
    json.dump(fsu_advisors, f, sort_keys=True, indent=4)
