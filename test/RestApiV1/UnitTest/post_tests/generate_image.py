#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2023 Regents of the University of Minnesota
Authors:
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
    Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy

Test RestApiV1 functions related to getting images
"""

import os
import random
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError

def generate_image(filename, seed=None):
    
    if seed is not None:
        random.seed(seed)

    template_path = os.path.join(os.path.dirname(__file__), "images", "templates")
    
    template = os.path.join(template_path, random.choice(os.listdir(template_path)))
    quote_top, quote_bottom = random.choice(quotes)

    image = Image.open(template)
    w, h = image.size

    draw = ImageDraw.Draw(image)
    
    
    fontsize = w // 25 + 1
    shadow_offset = min(1, fontsize // 20)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", fontsize)
    except:
        font = ImageFont.default_font()

    if quote_top is not None:
        draw.multiline_text( (w//2-shadow_offset, fontsize-shadow_offset),
                quote_top.upper(),
                anchor="ma", align="center", font=font,
                fill=0x00000000)
        draw.multiline_text( (w//2+shadow_offset, fontsize+shadow_offset),
                quote_top.upper(),
                anchor="ma", align="center", font=font,
                fill=0xffffffff)
    if quote_bottom is not None:
        draw.multiline_text( (w//2-shadow_offset, h-fontsize-shadow_offset),
                quote_bottom.upper(),
                anchor="md", align="center", font=font,
                fill=0x00000000)
        draw.multiline_text( (w//2+shadow_offset, h-fontsize+shadow_offset),
                quote_bottom.upper(),
                anchor="md", align="center", font=font,
                fill=0xffffffff)
    
    image.save(filename)

quotes = \
[
    (None, "Do not be afraid of competition."),
    (None, "An exciting opportunity\nlies ahead of you"),
    (None, "You will always be surrounded\nby true friends."),
    (None, "You should be able to undertake\nand complete anything."),
    (None, "You are kind and friendly."),
    (None, "You are wise beyond your years."),
    (None, "Your ability to juggle many tasks\nwill take you far."),
    (None, "A routine task will turn\ninto an enchanting adventure."),
    ("Beware of all enterprises", "that require new clothes."),
    (None, "Be true to your work,\nyour word, and your friend."),
    ("A journey of a thousand miles", "begins with a single step"),
    ("Forget injuries", "never forget kindnesses"),
    (None, "Respect yourself\nand others will respect you."),
    (None, "A man cannot be comfortable\nwithout his own approval."),
    ("Always do right.", "This will gratify some people\nand astonish the rest"),
    ("It is easier to stay out", "than to get out"),
    (None, "Sing everyday\nand chase the mean blues away."),
    (None, "You will receive money\nfrom an unexpected source."),
    (None, "Attitude is a little thing\nthat makes a big difference."),
    (None, "Experience is the best teacher."),
    (None, "You will be happy\nwith your spouse."),
    (None, "Expect the unexpected."),
    ("Stay healthy", "Walk a mile"),
    ("The family that plays together", "stays together"),
    (None, "Eat chocolate to have\na sweeter life."),
    ("Once you make a decision", "the universe conspires\nto make it happen"),
    (None, "Make yourself necessary\nto someone."),
    ("The only way to have a friend", "is to be one"),
    ("Nothing great was ever achieved", "without enthusiasm"),
    (None, "Dance as if no one is watching."),
    (None, "Live this day as if\nit were your last."),
    (None, "Your life will be\nhappy and peaceful."),
    (None, "Reach for joy\nand all else will follow."),
    (None, "Move in the direction\nof your dreams."),
    (None, "Bloom where you are planted."),
    (None, "Appreciate. Appreciate. Appreciate."),
    (None, "Happy News is on its way."),
    ("If you can't be a good example", "you'll just have to be\na horrible warning"),
    ("Mathematicians deal with\nlarge numbers sometimes", "but never in their income"),
    ("Half the fun of the travel", "is the esthetic of lostness"),
    ("They muddy the water", "to make it seem deep"),
    (None, "The art of being wise is\nthe art of knowing\nwhat to overlook."),
    ("Do, or do not.", "There is no try"),
    (None, "Science and everyday life\ncannot and should not\nbe separated."),
    ("Today I will be happier", "than a bird\nwith a french fry."),
    ("Suffer the pain of discipline", "or suffer the pain of regret"),
    ("Dance the dance you dance", "Don't dance the dance\npeople who dance dance"),
    ("It is easier to build\nstrong children", "than to repair\nbroken men"),
    ("The love of knowledge", "is a kind of madness."),
    ("Yesterday", "you said tomorrow"),
    ("If it is important to you,\nyou will find a way", "If not,\nyou'll find an excuse"),
    ("Do unto others 20% better\nthan you would expect\nthem to do unto you",
            "to correct for subjective error"),
    ("We are all born ignorant", "but one must work hard\nto remain stupid."),
    ("Patience is not the ability to wait",
            "but the ability to keep\na good attitude while waiting"),
    ("You can do anything", "but not everything."),
    ("Even if I knew that tomorrow\nthe world would go to pieces",
            "I would still plant\nmy apple tree"),
    ("It's hard to be an artist.", "It's hard to be anything.\nIt's hard to be."),
    ("Time flies like an arrow", "fruit flies like a banana."),
    ("Don't take life too seriously.", "You'll never get\nout of it alive"),
    ("He who lives\nin harmony with himself", "lives in harmony\nwith the universe"),
    ("I would rather\ndie on my feet", "than live on my knees"),
    ("Everything is funny", "as long as it is happening\nto somebody else"),
    ("If you're going through hell", "keep going"),
    ("The best way to cheer yourself", "is to try to cheer\nsomeone else up"),
]


