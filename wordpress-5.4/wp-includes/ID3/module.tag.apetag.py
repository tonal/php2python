#!/usr/bin/env python3
# coding: utf-8
if '__PHP2PY_LOADED__' not in globals():
    import cgi
    import os
    import os.path
    import copy
    import sys
    from goto import with_goto
    with open(os.getenv('PHP2PY_COMPAT', 'php_compat.py')) as f:
        exec(compile(f.read(), '<string>', 'exec'))
    # end with
    globals()['__PHP2PY_LOADED__'] = True
# end if
#// 
#// getID3() by James Heinrich <info@getid3.org>
#// available at https://github.com/JamesHeinrich/getID3
#// or https://www.getid3.org
#// or http://getid3.sourceforge.net
#// see readme.txt for more details
#// 
#// 
#// module.tag.apetag.php
#// module for analyzing APE tags
#// dependencies: NONE
#// 
#//
class getid3_apetag(getid3_handler):
    inline_attachments = True
    overrideendoffset = 0
    #// 
    #// @return bool
    #//
    def analyze(self):
        
        info = self.getid3.info
        if (not getid3_lib.intvaluesupported(info["filesize"])):
            self.warning("Unable to check for APEtags because file is larger than " + round(PHP_INT_MAX / 1073741824) + "GB")
            return False
        # end if
        id3v1tagsize = 128
        apetagheadersize = 32
        lyrics3tagsize = 10
        if self.overrideendoffset == 0:
            self.fseek(0 - id3v1tagsize - apetagheadersize - lyrics3tagsize, SEEK_END)
            APEfooterID3v1 = self.fread(id3v1tagsize + apetagheadersize + lyrics3tagsize)
            #// if (preg_match('/APETAGEX.{24}TAG.{125}$/i', $APEfooterID3v1)) {
            if php_substr(APEfooterID3v1, php_strlen(APEfooterID3v1) - id3v1tagsize - apetagheadersize, 8) == "APETAGEX":
                #// APE tag found before ID3v1
                info["ape"]["tag_offset_end"] = info["filesize"] - id3v1tagsize
                pass
            elif php_substr(APEfooterID3v1, php_strlen(APEfooterID3v1) - apetagheadersize, 8) == "APETAGEX":
                #// APE tag found, no ID3v1
                info["ape"]["tag_offset_end"] = info["filesize"]
            # end if
        else:
            self.fseek(self.overrideendoffset - apetagheadersize)
            if self.fread(8) == "APETAGEX":
                info["ape"]["tag_offset_end"] = self.overrideendoffset
            # end if
        # end if
        if (not (php_isset(lambda : info["ape"]["tag_offset_end"]))):
            info["ape"] = None
            return False
        # end if
        #// shortcut
        thisfile_ape = info["ape"]
        self.fseek(thisfile_ape["tag_offset_end"] - apetagheadersize)
        APEfooterData = self.fread(32)
        thisfile_ape["footer"] = self.parseapeheaderfooter(APEfooterData)
        if (not thisfile_ape["footer"]):
            self.error("Error parsing APE footer at offset " + thisfile_ape["tag_offset_end"])
            return False
        # end if
        if (php_isset(lambda : thisfile_ape["footer"]["flags"]["header"])) and thisfile_ape["footer"]["flags"]["header"]:
            self.fseek(thisfile_ape["tag_offset_end"] - thisfile_ape["footer"]["raw"]["tagsize"] - apetagheadersize)
            thisfile_ape["tag_offset_start"] = self.ftell()
            APEtagData = self.fread(thisfile_ape["footer"]["raw"]["tagsize"] + apetagheadersize)
        else:
            thisfile_ape["tag_offset_start"] = thisfile_ape["tag_offset_end"] - thisfile_ape["footer"]["raw"]["tagsize"]
            self.fseek(thisfile_ape["tag_offset_start"])
            APEtagData = self.fread(thisfile_ape["footer"]["raw"]["tagsize"])
        # end if
        info["avdataend"] = thisfile_ape["tag_offset_start"]
        if (php_isset(lambda : info["id3v1"]["tag_offset_start"])) and info["id3v1"]["tag_offset_start"] < thisfile_ape["tag_offset_end"]:
            self.warning("ID3v1 tag information ignored since it appears to be a false synch in APEtag data")
            info["id3v1"] = None
            for key,value in info["warning"]:
                if value == "Some ID3v1 fields do not use NULL characters for padding":
                    info["warning"][key] = None
                    sort(info["warning"])
                    break
                # end if
            # end for
        # end if
        offset = 0
        if (php_isset(lambda : thisfile_ape["footer"]["flags"]["header"])) and thisfile_ape["footer"]["flags"]["header"]:
            thisfile_ape["header"] = self.parseapeheaderfooter(php_substr(APEtagData, 0, apetagheadersize))
            if thisfile_ape["header"]:
                offset += apetagheadersize
            else:
                self.error("Error parsing APE header at offset " + thisfile_ape["tag_offset_start"])
                return False
            # end if
        # end if
        #// shortcut
        info["replay_gain"] = Array()
        thisfile_replaygain = info["replay_gain"]
        i = 0
        while i < thisfile_ape["footer"]["raw"]["tag_items"]:
            
            value_size = getid3_lib.littleendian2int(php_substr(APEtagData, offset, 4))
            offset += 4
            item_flags = getid3_lib.littleendian2int(php_substr(APEtagData, offset, 4))
            offset += 4
            if php_strstr(php_substr(APEtagData, offset), " ") == False:
                self.error("Cannot find null-byte (0x00) separator between ItemKey #" + i + " and value. ItemKey starts " + offset + " bytes into the APE tag, at file offset " + thisfile_ape["tag_offset_start"] + offset)
                return False
            # end if
            ItemKeyLength = php_strpos(APEtagData, " ", offset) - offset
            item_key = php_strtolower(php_substr(APEtagData, offset, ItemKeyLength))
            #// shortcut
            thisfile_ape["items"][item_key] = Array()
            thisfile_ape_items_current = thisfile_ape["items"][item_key]
            thisfile_ape_items_current["offset"] = thisfile_ape["tag_offset_start"] + offset
            offset += ItemKeyLength + 1
            #// skip 0x00 terminator
            thisfile_ape_items_current["data"] = php_substr(APEtagData, offset, value_size)
            offset += value_size
            thisfile_ape_items_current["flags"] = self.parseapetagflags(item_flags)
            for case in Switch(thisfile_ape_items_current["flags"]["item_contents_raw"]):
                if case(0):
                    pass
                # end if
                if case(2):
                    #// Locator (URL, filename, etc), UTF-8 encoded
                    thisfile_ape_items_current["data"] = php_explode(" ", thisfile_ape_items_current["data"])
                    break
                # end if
                if case(1):
                    pass
                # end if
                if case():
                    break
                # end if
            # end for
            for case in Switch(php_strtolower(item_key)):
                if case("replaygain_track_gain"):
                    if php_preg_match("#^([\\-\\+][0-9\\.,]{8})( dB)?$#", thisfile_ape_items_current["data"][0], matches):
                        thisfile_replaygain["track"]["adjustment"] = float(php_str_replace(",", ".", matches[1]))
                        #// float casting will see "0,95" as zero!
                        thisfile_replaygain["track"]["originator"] = "unspecified"
                    else:
                        self.warning("MP3gainTrackGain value in APEtag appears invalid: \"" + thisfile_ape_items_current["data"][0] + "\"")
                    # end if
                    break
                # end if
                if case("replaygain_track_peak"):
                    if php_preg_match("#^([0-9\\.,]{8})$#", thisfile_ape_items_current["data"][0], matches):
                        thisfile_replaygain["track"]["peak"] = float(php_str_replace(",", ".", matches[1]))
                        #// float casting will see "0,95" as zero!
                        thisfile_replaygain["track"]["originator"] = "unspecified"
                        if thisfile_replaygain["track"]["peak"] <= 0:
                            self.warning("ReplayGain Track peak from APEtag appears invalid: " + thisfile_replaygain["track"]["peak"] + " (original value = \"" + thisfile_ape_items_current["data"][0] + "\")")
                        # end if
                    else:
                        self.warning("MP3gainTrackPeak value in APEtag appears invalid: \"" + thisfile_ape_items_current["data"][0] + "\"")
                    # end if
                    break
                # end if
                if case("replaygain_album_gain"):
                    if php_preg_match("#^([\\-\\+][0-9\\.,]{8})( dB)?$#", thisfile_ape_items_current["data"][0], matches):
                        thisfile_replaygain["album"]["adjustment"] = float(php_str_replace(",", ".", matches[1]))
                        #// float casting will see "0,95" as zero!
                        thisfile_replaygain["album"]["originator"] = "unspecified"
                    else:
                        self.warning("MP3gainAlbumGain value in APEtag appears invalid: \"" + thisfile_ape_items_current["data"][0] + "\"")
                    # end if
                    break
                # end if
                if case("replaygain_album_peak"):
                    if php_preg_match("#^([0-9\\.,]{8})$#", thisfile_ape_items_current["data"][0], matches):
                        thisfile_replaygain["album"]["peak"] = float(php_str_replace(",", ".", matches[1]))
                        #// float casting will see "0,95" as zero!
                        thisfile_replaygain["album"]["originator"] = "unspecified"
                        if thisfile_replaygain["album"]["peak"] <= 0:
                            self.warning("ReplayGain Album peak from APEtag appears invalid: " + thisfile_replaygain["album"]["peak"] + " (original value = \"" + thisfile_ape_items_current["data"][0] + "\")")
                        # end if
                    else:
                        self.warning("MP3gainAlbumPeak value in APEtag appears invalid: \"" + thisfile_ape_items_current["data"][0] + "\"")
                    # end if
                    break
                # end if
                if case("mp3gain_undo"):
                    if php_preg_match("#^[\\-\\+][0-9]{3},[\\-\\+][0-9]{3},[NW]$#", thisfile_ape_items_current["data"][0]):
                        mp3gain_undo_left, mp3gain_undo_right, mp3gain_undo_wrap = php_explode(",", thisfile_ape_items_current["data"][0])
                        thisfile_replaygain["mp3gain"]["undo_left"] = php_intval(mp3gain_undo_left)
                        thisfile_replaygain["mp3gain"]["undo_right"] = php_intval(mp3gain_undo_right)
                        thisfile_replaygain["mp3gain"]["undo_wrap"] = True if mp3gain_undo_wrap == "Y" else False
                    else:
                        self.warning("MP3gainUndo value in APEtag appears invalid: \"" + thisfile_ape_items_current["data"][0] + "\"")
                    # end if
                    break
                # end if
                if case("mp3gain_minmax"):
                    if php_preg_match("#^[0-9]{3},[0-9]{3}$#", thisfile_ape_items_current["data"][0]):
                        mp3gain_globalgain_min, mp3gain_globalgain_max = php_explode(",", thisfile_ape_items_current["data"][0])
                        thisfile_replaygain["mp3gain"]["globalgain_track_min"] = php_intval(mp3gain_globalgain_min)
                        thisfile_replaygain["mp3gain"]["globalgain_track_max"] = php_intval(mp3gain_globalgain_max)
                    else:
                        self.warning("MP3gainMinMax value in APEtag appears invalid: \"" + thisfile_ape_items_current["data"][0] + "\"")
                    # end if
                    break
                # end if
                if case("mp3gain_album_minmax"):
                    if php_preg_match("#^[0-9]{3},[0-9]{3}$#", thisfile_ape_items_current["data"][0]):
                        mp3gain_globalgain_album_min, mp3gain_globalgain_album_max = php_explode(",", thisfile_ape_items_current["data"][0])
                        thisfile_replaygain["mp3gain"]["globalgain_album_min"] = php_intval(mp3gain_globalgain_album_min)
                        thisfile_replaygain["mp3gain"]["globalgain_album_max"] = php_intval(mp3gain_globalgain_album_max)
                    else:
                        self.warning("MP3gainAlbumMinMax value in APEtag appears invalid: \"" + thisfile_ape_items_current["data"][0] + "\"")
                    # end if
                    break
                # end if
                if case("tracknumber"):
                    if php_is_array(thisfile_ape_items_current["data"]):
                        for comment in thisfile_ape_items_current["data"]:
                            thisfile_ape["comments"]["track_number"][-1] = comment
                        # end for
                    # end if
                    break
                # end if
                if case("cover art (artist)"):
                    pass
                # end if
                if case("cover art (back)"):
                    pass
                # end if
                if case("cover art (band logo)"):
                    pass
                # end if
                if case("cover art (band)"):
                    pass
                # end if
                if case("cover art (colored fish)"):
                    pass
                # end if
                if case("cover art (composer)"):
                    pass
                # end if
                if case("cover art (conductor)"):
                    pass
                # end if
                if case("cover art (front)"):
                    pass
                # end if
                if case("cover art (icon)"):
                    pass
                # end if
                if case("cover art (illustration)"):
                    pass
                # end if
                if case("cover art (lead)"):
                    pass
                # end if
                if case("cover art (leaflet)"):
                    pass
                # end if
                if case("cover art (lyricist)"):
                    pass
                # end if
                if case("cover art (media)"):
                    pass
                # end if
                if case("cover art (movie scene)"):
                    pass
                # end if
                if case("cover art (other icon)"):
                    pass
                # end if
                if case("cover art (other)"):
                    pass
                # end if
                if case("cover art (performance)"):
                    pass
                # end if
                if case("cover art (publisher logo)"):
                    pass
                # end if
                if case("cover art (recording)"):
                    pass
                # end if
                if case("cover art (studio)"):
                    #// list of possible cover arts from http://taglib-sharp.sourcearchive.com/documentation/2.0.3.0-2/Ape_2Tag_8cs-source.html
                    if php_is_array(thisfile_ape_items_current["data"]):
                        self.warning("APEtag \"" + item_key + "\" should be flagged as Binary data, but was incorrectly flagged as UTF-8")
                        thisfile_ape_items_current["data"] = php_implode(" ", thisfile_ape_items_current["data"])
                    # end if
                    thisfile_ape_items_current["filename"], thisfile_ape_items_current["data"] = php_explode(" ", thisfile_ape_items_current["data"], 2)
                    thisfile_ape_items_current["data_offset"] = thisfile_ape_items_current["offset"] + php_strlen(thisfile_ape_items_current["filename"] + " ")
                    thisfile_ape_items_current["data_length"] = php_strlen(thisfile_ape_items_current["data"])
                    while True:
                        thisfile_ape_items_current["image_mime"] = ""
                        imageinfo = Array()
                        imagechunkcheck = getid3_lib.getdataimagesize(thisfile_ape_items_current["data"], imageinfo)
                        if imagechunkcheck == False or (not (php_isset(lambda : imagechunkcheck[2]))):
                            self.warning("APEtag \"" + item_key + "\" contains invalid image data")
                            break
                        # end if
                        thisfile_ape_items_current["image_mime"] = image_type_to_mime_type(imagechunkcheck[2])
                        if self.inline_attachments == False:
                            thisfile_ape_items_current["data"] = None
                            break
                        # end if
                        if self.inline_attachments == True:
                            pass
                        elif php_is_int(self.inline_attachments):
                            if self.inline_attachments < thisfile_ape_items_current["data_length"]:
                                #// too big, skip
                                self.warning("attachment at " + thisfile_ape_items_current["offset"] + " is too large to process inline (" + number_format(thisfile_ape_items_current["data_length"]) + " bytes)")
                                thisfile_ape_items_current["data"] = None
                                break
                            # end if
                        elif php_is_string(self.inline_attachments):
                            self.inline_attachments = php_rtrim(php_str_replace(Array("/", "\\"), DIRECTORY_SEPARATOR, self.inline_attachments), DIRECTORY_SEPARATOR)
                            if (not php_is_dir(self.inline_attachments)) or (not getID3.is_writable(self.inline_attachments)):
                                #// cannot write, skip
                                self.warning("attachment at " + thisfile_ape_items_current["offset"] + " cannot be saved to \"" + self.inline_attachments + "\" (not writable)")
                                thisfile_ape_items_current["data"] = None
                                break
                            # end if
                        # end if
                        #// if we get this far, must be OK
                        if php_is_string(self.inline_attachments):
                            destination_filename = self.inline_attachments + DIRECTORY_SEPARATOR + php_md5(info["filenamepath"]) + "_" + thisfile_ape_items_current["data_offset"]
                            if (not php_file_exists(destination_filename)) or getID3.is_writable(destination_filename):
                                file_put_contents(destination_filename, thisfile_ape_items_current["data"])
                            else:
                                self.warning("attachment at " + thisfile_ape_items_current["offset"] + " cannot be saved to \"" + destination_filename + "\" (not writable)")
                            # end if
                            thisfile_ape_items_current["data_filename"] = destination_filename
                            thisfile_ape_items_current["data"] = None
                        else:
                            if (not (php_isset(lambda : info["ape"]["comments"]["picture"]))):
                                info["ape"]["comments"]["picture"] = Array()
                            # end if
                            comments_picture_data = Array()
                            for picture_key in Array("data", "image_mime", "image_width", "image_height", "imagetype", "picturetype", "description", "datalength"):
                                if (php_isset(lambda : thisfile_ape_items_current[picture_key])):
                                    comments_picture_data[picture_key] = thisfile_ape_items_current[picture_key]
                                # end if
                            # end for
                            info["ape"]["comments"]["picture"][-1] = comments_picture_data
                            comments_picture_data = None
                        # end if
                        
                        if False:
                            break
                        # end if
                    # end while
                    break
                # end if
                if case():
                    if php_is_array(thisfile_ape_items_current["data"]):
                        for comment in thisfile_ape_items_current["data"]:
                            thisfile_ape["comments"][php_strtolower(item_key)][-1] = comment
                        # end for
                    # end if
                    break
                # end if
            # end for
            i += 1
        # end while
        if php_empty(lambda : thisfile_replaygain):
            info["replay_gain"] = None
        # end if
        return True
    # end def analyze
    #// 
    #// @param string $APEheaderFooterData
    #// 
    #// @return array|false
    #//
    def parseapeheaderfooter(self, APEheaderFooterData=None):
        
        #// http://www.uni-jena.de/~pfk/mpp/sv8/apeheader.html
        #// shortcut
        headerfooterinfo["raw"] = Array()
        headerfooterinfo_raw = headerfooterinfo["raw"]
        headerfooterinfo_raw["footer_tag"] = php_substr(APEheaderFooterData, 0, 8)
        if headerfooterinfo_raw["footer_tag"] != "APETAGEX":
            return False
        # end if
        headerfooterinfo_raw["version"] = getid3_lib.littleendian2int(php_substr(APEheaderFooterData, 8, 4))
        headerfooterinfo_raw["tagsize"] = getid3_lib.littleendian2int(php_substr(APEheaderFooterData, 12, 4))
        headerfooterinfo_raw["tag_items"] = getid3_lib.littleendian2int(php_substr(APEheaderFooterData, 16, 4))
        headerfooterinfo_raw["global_flags"] = getid3_lib.littleendian2int(php_substr(APEheaderFooterData, 20, 4))
        headerfooterinfo_raw["reserved"] = php_substr(APEheaderFooterData, 24, 8)
        headerfooterinfo["tag_version"] = headerfooterinfo_raw["version"] / 1000
        if headerfooterinfo["tag_version"] >= 2:
            headerfooterinfo["flags"] = self.parseapetagflags(headerfooterinfo_raw["global_flags"])
        # end if
        return headerfooterinfo
    # end def parseapeheaderfooter
    #// 
    #// @param int $rawflagint
    #// 
    #// @return array
    #//
    def parseapetagflags(self, rawflagint=None):
        
        #// "Note: APE Tags 1.0 do not use any of the APE Tag flags.
        #// All are set to zero on creation and ignored on reading."
        #// http://wiki.hydrogenaud.io/index.php?title=Ape_Tags_Flags
        flags["header"] = bool(rawflagint & 2147483648)
        flags["footer"] = bool(rawflagint & 1073741824)
        flags["this_is_header"] = bool(rawflagint & 536870912)
        flags["item_contents_raw"] = rawflagint & 6 >> 1
        flags["read_only"] = bool(rawflagint & 1)
        flags["item_contents"] = self.apecontenttypeflaglookup(flags["item_contents_raw"])
        return flags
    # end def parseapetagflags
    #// 
    #// @param int $contenttypeid
    #// 
    #// @return string
    #//
    def apecontenttypeflaglookup(self, contenttypeid=None):
        
        APEcontentTypeFlagLookup = Array({0: "utf-8", 1: "binary", 2: "external", 3: "reserved"})
        return APEcontentTypeFlagLookup[contenttypeid] if (php_isset(lambda : APEcontentTypeFlagLookup[contenttypeid])) else "invalid"
    # end def apecontenttypeflaglookup
    #// 
    #// @param string $itemkey
    #// 
    #// @return bool
    #//
    def apetagitemisutf8lookup(self, itemkey=None):
        
        APEtagItemIsUTF8Lookup = Array("title", "subtitle", "artist", "album", "debut album", "publisher", "conductor", "track", "composer", "comment", "copyright", "publicationright", "file", "year", "record date", "record location", "genre", "media", "related", "isrc", "abstract", "language", "bibliography")
        return php_in_array(php_strtolower(itemkey), APEtagItemIsUTF8Lookup)
    # end def apetagitemisutf8lookup
# end class getid3_apetag
