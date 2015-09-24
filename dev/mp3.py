# -*- coding: utf-8 -*-
# vim: ts=4 expandtab si

import os,sys

from config import *
from flac import flac, flacdecode
from shell import shell
from time import time
import uuid
import subprocess as sp

class lameMp3:
    def __init__(self,lame_options):
        self.opts = lame_options


    def generateLameMeta(self,metastring):
        tagstring = ""

        #pointer to the parseEscapechars method in the shell class
        parseEscapechars = shell().parseEscapechars

        #Dealing with genres defined within lame
        acceptable_genres=[\
        "A Cappella",\
        "Acid",\
        "Acid Jazz",\
        "Acid Punk",\
        "Acoustic",\
        "Alternative",\
        "Alt. Rock",\
        "Ambient",\
        "Anime",\
        "Avantgarde",\
        "Ballad",\
        "Bass",\
        "Beat",\
        "Bebob",\
        "Big Band",\
        "Black Metal",\
        "Bluegrass",\
        "Blues",\
        "Booty Bass",\
        "BritPop",\
        "Cabaret",\
        "Celtic",\
        "Chamber Music",\
        "Chanson",\
        "Chorus",\
        "Christian Gangsta Rap",\
        "Christian Rap",\
        "Christian Rock",\
        "Classical",\
        "Classic Rock",\
        "Club",\
        "Club-House",\
        "Comedy",\
        "Contemporary Christian",\
        "Country",\
        "Crossover",\
        "Cult",\
        "Dance",\
        "Dance Hall",\
        "Darkwave",\
        "Death Metal",\
        "Disco",\
        "Dream",\
        "Drum & Bass",\
        "Drum Solo",\
        "Duet",\
        "Easy Listening",\
        "Electronic",\
        "Ethnic",\
        "Eurodance",\
        "Euro-House",\
        "Euro-Techno",\
        "Fast-Fusion",\
        "Folk",\
        "Folklore",\
        "Folk/Rock",\
        "Freestyle",\
        "Funk",\
        "Fusion",\
        "Game",\
        "Gangsta Rap",\
        "Goa",\
        "Gospel",\
        "Gothic",\
        "Gothic Rock",\
        "Grunge",\
        "Hardcore",\
        "Hard Rock",\
        "Heavy Metal",\
        "Hip-Hop",\
        "House",\
        "Humour",\
        "Indie",\
        "Industrial",\
        "Instrumental",\
        "Instrumental Pop",\
        "Instrumental Rock",\
        "Jazz",\
        "Jazz+Funk",\
        "JPop",\
        "Jungle",\
        "Latin", \
        "Lo-Fi", \
        "Meditative", \
        "Merengue", \
        "Metal", \
        "Musical", \
        "National Folk", \
        "Native American", \
        "Negerpunk", \
        "New Age", \
        "New Wave", \
        "Noise", \
        "Oldies", \
        "Opera", \
        "Other", \
        "Polka", \
        "Polsk Punk", \
        "Pop", \
        "Pop-Folk", \
        "Pop/Funk", \
        "Porn Groove", \
        "Power Ballad", \
        "Pranks", \
        "Primus", \
        "Progressive Rock", \
        "Psychedelic", \
        "Psychedelic Rock", \
        "Punk", \
        "Punk Rock", \
        "Rap", \
        "Rave", \
        "R&B", \
        "Reggae", \
        "Retro", \
        "Revival", \
        "Rhythmic Soul", \
        "Rock", \
        "Rock & Roll", \
        "Salsa", \
        "Samba", \
        "Satire", \
        "Showtunes", \
        "Ska", \
        "Slow Jam", \
        "Slow Rock", \
        "Sonata", \
        "Soul", \
        "Sound Clip", \
        "Soundtrack", \
        "Southern Rock", \
        "Space", \
        "Speech", \
        "Swing", \
        "Symphonic Rock", \
        "Symphony", \
        "Synthpop", \
        "Tango", \
        "Techno", \
        "Techno-Industrial", \
        "Terror", \
        "Thrash Metal", \
        "Top 40", \
        "Trailer", \
        "Trance", \
        "Tribal", \
        "Trip-Hop", \
        "Vocal"]

        genre_is_acceptable = 0 #By default the genre is not acceptable
        current_genre = "" #variable stores current genre tag

        for genre in acceptable_genres:
            #print string.strip(metastring['GENRE'])+" ==> "+string.strip(genre)
            try:
                current_genre = metastring['GENRE'].strip().upper()
            except(KeyError):
                current_genre = "NO GENRE TAG"

            #case-insesitive comparison
            if current_genre == genre.strip().upper():
                genre_is_acceptable = 1   #we can use the genre


        if genre_is_acceptable == 0:  #if genre cannot be used
            print "The Genre \"" + current_genre + "\" cannot be used with lame, setting to \"Other\" "
            metastring['GENRE'] = "Other"       #set GENRE to Other

        else:
            #Capitalise the Genre, as per lame requirements
            metastring['GENRE'] = metastring['GENRE'].capitalize()
            genre_is_acceptable = 0 #reset the boolean value for the next time


        try:
            tagstring = "--tt " + "\"" +  parseEscapechars(metastring["TITLE"],True) + "\""

        except(KeyError):
            pass #well we skip the comment field if is doesn't exist

        try:
            tagstring = tagstring + " --ta " + "\"" + parseEscapechars(metastring['ARTIST'],True) + "\""
        except(KeyError):
            pass

        try:
            tagstring = tagstring + " --tl " + "\"" + parseEscapechars(metastring['ALBUM'],True) + "\""
        except(KeyError):
            pass

        try:
            tagstring = tagstring + " --ty " + "\"" + parseEscapechars(metastring['DATE'],True) + "\""
        except(KeyError):
            pass
        try:
            tagstring = tagstring + " --tg " + "\"" + parseEscapechars(metastring['GENRE'],True) + "\""
        except(KeyError):
            pass

        try:
            tagstring = tagstring + " --tn " + "\"" + parseEscapechars(metastring['TRACKNUMBER'],True) + "\""
        except(KeyError):
            pass

        #COMMENTS AND CDDB ARE PLACED TOGETHER, as there exists no seperate
        #"CDDB Field" option for mp3. this is only if we have a comment to begin with
        try:
            tagstring = tagstring + " --tc " + "\"" + parseEscapechars(metastring['COMMENT'],True)

            try:
                tagstring = tagstring + "  || CDDB:" + parseEscapechars(metastring['CDDB'],True) + "\""
            except(KeyError):
                tagstring = tagstring + "\""    #close the final "comment field, without CDDB info

        except(KeyError):
        #this is for if we have a CDDB value
            try:
                tagstring = tagstring + " --tc  \"CDDB:" + parseEscapechars(metastring['CDDB'],True) + "\""
            except(KeyError):
                pass

        #Metadata population complete
        return tagstring

    def mp3convert(self,infile,outfile,logq):
        pipe = "/tmp/flac2all_"+str(uuid.uuid4()).strip()
        startTime = time()
        inmetadata = flac().getflacmeta(infile)
        os.mkfifo(pipe)

        try:
            metastring = self.generateLameMeta(inmetadata)
        except(UnboundLocalError):
            metastring = "" #If we do not get meta information. leave blank

        (decoder,stderr) = flacdecode(infile,pipe)()
        encoder = sp.check_call("%slame --silent %s %s -o %s.mp3 %s" % (
            lamepath,
            self.opts,
            pipe,
            shell().parseEscapechars(outfile),            
            metastring
            ) ,shell=True) 

        os.unlink(pipe) 
        errline = stderr.read()
        errline = errline.upper()
        if errline.strip() != '':
            print "ERRORLINE: %s" % errline
        if errline.find("ERROR") != -1:
            logq.put([infile,"mp3","ERROR: decoder error: %s" % errline,-1,time()-startTime], timeout=10)
            return False

        logq.put([infile,outfile,"mp3","SUCCESS",0, time() - startTime])


