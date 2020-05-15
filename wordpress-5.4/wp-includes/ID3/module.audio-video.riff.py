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
#// module.audio-video.riff.php
#// module for analyzing RIFF files
#// multiple formats supported by this module:
#// Wave, AVI, AIFF/AIFC, (MP3,AC3)/RIFF, Wavpack v3, 8SVX
#// dependencies: module.audio.mp3.php
#// module.audio.ac3.php
#// module.audio.dts.php
#// 
#// 
#// 
#// @todo Parse AC-3/DTS audio inside WAVE correctly
#// @todo Rewrite RIFF parser totally
#//
getid3_lib.includedependency(GETID3_INCLUDEPATH + "module.audio.mp3.php", __FILE__, True)
getid3_lib.includedependency(GETID3_INCLUDEPATH + "module.audio.ac3.php", __FILE__, True)
getid3_lib.includedependency(GETID3_INCLUDEPATH + "module.audio.dts.php", __FILE__, True)
class getid3_riff(getid3_handler):
    container = "riff"
    #// default
    #// 
    #// @return bool
    #// 
    #// @throws getid3_exception
    #//
    def analyze(self):
        
        info = self.getid3.info
        #// initialize these values to an empty array, otherwise they default to NULL
        #// and you can't append array values to a NULL value
        info["riff"] = Array({"raw": Array()})
        #// Shortcuts
        thisfile_riff = info["riff"]
        thisfile_riff_raw = thisfile_riff["raw"]
        thisfile_audio = info["audio"]
        thisfile_video = info["video"]
        thisfile_audio_dataformat = thisfile_audio["dataformat"]
        thisfile_riff_audio = thisfile_riff["audio"]
        thisfile_riff_video = thisfile_riff["video"]
        thisfile_riff_WAVE = Array()
        Original["avdataoffset"] = info["avdataoffset"]
        Original["avdataend"] = info["avdataend"]
        self.fseek(info["avdataoffset"])
        RIFFheader = self.fread(12)
        offset = self.ftell()
        RIFFtype = php_substr(RIFFheader, 0, 4)
        RIFFsize = php_substr(RIFFheader, 4, 4)
        RIFFsubtype = php_substr(RIFFheader, 8, 4)
        for case in Switch(RIFFtype):
            if case("FORM"):
                #// AIFF, AIFC
                #// $info['fileformat']   = 'aiff';
                self.container = "aiff"
                thisfile_riff["header_size"] = self.eitherendian2int(RIFFsize)
                thisfile_riff[RIFFsubtype] = self.parseriff(offset, offset + thisfile_riff["header_size"] - 4)
                break
            # end if
            if case("RIFF"):
                pass
            # end if
            if case("SDSS"):
                pass
            # end if
            if case("RMP3"):
                #// RMP3 is identical to RIFF, just renamed. Used by [unknown program] when creating RIFF-MP3s
                #// $info['fileformat']   = 'riff';
                self.container = "riff"
                thisfile_riff["header_size"] = self.eitherendian2int(RIFFsize)
                if RIFFsubtype == "RMP3":
                    #// RMP3 is identical to WAVE, just renamed. Used by [unknown program] when creating RIFF-MP3s
                    RIFFsubtype = "WAVE"
                # end if
                if RIFFsubtype != "AMV ":
                    #// AMV files are RIFF-AVI files with parts of the spec deliberately broken, such as chunk size fields hardcoded to zero (because players known in hardware that these fields are always a certain size
                    #// Handled separately in ParseRIFFAMV()
                    thisfile_riff[RIFFsubtype] = self.parseriff(offset, offset + thisfile_riff["header_size"] - 4)
                # end if
                if info["avdataend"] - info["filesize"] == 1:
                    #// LiteWave appears to incorrectly *not* pad actual output file
                    #// to nearest WORD boundary so may appear to be short by one
                    #// byte, in which case - skip warning
                    info["avdataend"] = info["filesize"]
                # end if
                nextRIFFoffset = Original["avdataoffset"] + 8 + thisfile_riff["header_size"]
                #// 8 = "RIFF" + 32-bit offset
                while True:
                    
                    if not (nextRIFFoffset < php_min(info["filesize"], info["avdataend"])):
                        break
                    # end if
                    try: 
                        self.fseek(nextRIFFoffset)
                    except getid3_exception as e:
                        if e.getcode() == 10:
                            #// $this->warning('RIFF parser: '.$e->getMessage());
                            self.error("AVI extends beyond " + round(PHP_INT_MAX / 1073741824) + "GB and PHP filesystem functions cannot read that far, playtime may be wrong")
                            self.warning("[avdataend] value may be incorrect, multiple AVIX chunks may be present")
                            break
                        else:
                            raise e
                        # end if
                    # end try
                    nextRIFFheader = self.fread(12)
                    if nextRIFFoffset == info["avdataend"] - 1:
                        if php_substr(nextRIFFheader, 0, 1) == " ":
                            break
                        # end if
                    # end if
                    nextRIFFheaderID = php_substr(nextRIFFheader, 0, 4)
                    nextRIFFsize = self.eitherendian2int(php_substr(nextRIFFheader, 4, 4))
                    nextRIFFtype = php_substr(nextRIFFheader, 8, 4)
                    chunkdata = Array()
                    chunkdata["offset"] = nextRIFFoffset + 8
                    chunkdata["size"] = nextRIFFsize
                    nextRIFFoffset = chunkdata["offset"] + chunkdata["size"]
                    for case in Switch(nextRIFFheaderID):
                        if case("RIFF"):
                            chunkdata["chunks"] = self.parseriff(chunkdata["offset"] + 4, nextRIFFoffset)
                            if (not (php_isset(lambda : thisfile_riff[nextRIFFtype]))):
                                thisfile_riff[nextRIFFtype] = Array()
                            # end if
                            thisfile_riff[nextRIFFtype][-1] = chunkdata
                            break
                        # end if
                        if case("AMV "):
                            info["riff"] = None
                            info["amv"] = self.parseriffamv(chunkdata["offset"] + 4, nextRIFFoffset)
                            break
                        # end if
                        if case("JUNK"):
                            #// ignore
                            thisfile_riff[nextRIFFheaderID][-1] = chunkdata
                            break
                        # end if
                        if case("IDVX"):
                            info["divxtag"]["comments"] = self.parsedivxtag(self.fread(chunkdata["size"]))
                            break
                        # end if
                        if case():
                            if info["filesize"] == chunkdata["offset"] - 8 + 128:
                                DIVXTAG = nextRIFFheader + self.fread(128 - 12)
                                if php_substr(DIVXTAG, -7) == "DIVXTAG":
                                    #// DIVXTAG is supposed to be inside an IDVX chunk in a LIST chunk, but some bad encoders just slap it on the end of a file
                                    self.warning("Found wrongly-structured DIVXTAG at offset " + self.ftell() - 128 + ", parsing anyway")
                                    info["divxtag"]["comments"] = self.parsedivxtag(DIVXTAG)
                                    break
                                # end if
                            # end if
                            self.warning("Expecting \"RIFF|JUNK|IDVX\" at " + nextRIFFoffset + ", found \"" + nextRIFFheaderID + "\" (" + getid3_lib.printhexbytes(nextRIFFheaderID) + ") - skipping rest of file")
                            break
                        # end if
                    # end for
                # end while
                if RIFFsubtype == "WAVE":
                    thisfile_riff_WAVE = thisfile_riff["WAVE"]
                # end if
                break
            # end if
            if case():
                self.error("Cannot parse RIFF (this is maybe not a RIFF / WAV / AVI file?) - expecting \"FORM|RIFF|SDSS|RMP3\" found \"" + RIFFsubtype + "\" instead")
                #// unset($info['fileformat']);
                return False
            # end if
        # end for
        streamindex = 0
        for case in Switch(RIFFsubtype):
            if case("WAVE"):
                info["fileformat"] = "wav"
                if php_empty(lambda : thisfile_audio["bitrate_mode"]):
                    thisfile_audio["bitrate_mode"] = "cbr"
                # end if
                if php_empty(lambda : thisfile_audio_dataformat):
                    thisfile_audio_dataformat = "wav"
                # end if
                if (php_isset(lambda : thisfile_riff_WAVE["data"][0]["offset"])):
                    info["avdataoffset"] = thisfile_riff_WAVE["data"][0]["offset"] + 8
                    info["avdataend"] = info["avdataoffset"] + thisfile_riff_WAVE["data"][0]["size"]
                # end if
                if (php_isset(lambda : thisfile_riff_WAVE["fmt "][0]["data"])):
                    thisfile_riff_audio[streamindex] = self.parsewaveformatex(thisfile_riff_WAVE["fmt "][0]["data"])
                    thisfile_audio["wformattag"] = thisfile_riff_audio[streamindex]["raw"]["wFormatTag"]
                    if (not (php_isset(lambda : thisfile_riff_audio[streamindex]["bitrate"]))) or thisfile_riff_audio[streamindex]["bitrate"] == 0:
                        self.error("Corrupt RIFF file: bitrate_audio == zero")
                        return False
                    # end if
                    thisfile_riff_raw["fmt "] = thisfile_riff_audio[streamindex]["raw"]
                    thisfile_riff_audio[streamindex]["raw"] = None
                    thisfile_audio["streams"][streamindex] = thisfile_riff_audio[streamindex]
                    thisfile_audio = getid3_lib.array_merge_noclobber(thisfile_audio, thisfile_riff_audio[streamindex])
                    if php_substr(thisfile_audio["codec"], 0, php_strlen("unknown: 0x")) == "unknown: 0x":
                        self.warning("Audio codec = " + thisfile_audio["codec"])
                    # end if
                    thisfile_audio["bitrate"] = thisfile_riff_audio[streamindex]["bitrate"]
                    if php_empty(lambda : info["playtime_seconds"]):
                        #// may already be set (e.g. DTS-WAV)
                        info["playtime_seconds"] = float(info["avdataend"] - info["avdataoffset"] * 8 / thisfile_audio["bitrate"])
                    # end if
                    thisfile_audio["lossless"] = False
                    if (php_isset(lambda : thisfile_riff_WAVE["data"][0]["offset"])) and (php_isset(lambda : thisfile_riff_raw["fmt "]["wFormatTag"])):
                        for case in Switch(thisfile_riff_raw["fmt "]["wFormatTag"]):
                            if case(1):
                                #// PCM
                                thisfile_audio["lossless"] = True
                                break
                            # end if
                            if case(8192):
                                #// AC-3
                                thisfile_audio_dataformat = "ac3"
                                break
                            # end if
                            if case():
                                break
                            # end if
                        # end for
                    # end if
                    thisfile_audio["streams"][streamindex]["wformattag"] = thisfile_audio["wformattag"]
                    thisfile_audio["streams"][streamindex]["bitrate_mode"] = thisfile_audio["bitrate_mode"]
                    thisfile_audio["streams"][streamindex]["lossless"] = thisfile_audio["lossless"]
                    thisfile_audio["streams"][streamindex]["dataformat"] = thisfile_audio_dataformat
                # end if
                if (php_isset(lambda : thisfile_riff_WAVE["rgad"][0]["data"])):
                    #// shortcuts
                    rgadData = thisfile_riff_WAVE["rgad"][0]["data"]
                    thisfile_riff_raw["rgad"] = Array({"track": Array(), "album": Array()})
                    thisfile_riff_raw_rgad = thisfile_riff_raw["rgad"]
                    thisfile_riff_raw_rgad_track = thisfile_riff_raw_rgad["track"]
                    thisfile_riff_raw_rgad_album = thisfile_riff_raw_rgad["album"]
                    thisfile_riff_raw_rgad["fPeakAmplitude"] = getid3_lib.littleendian2float(php_substr(rgadData, 0, 4))
                    thisfile_riff_raw_rgad["nRadioRgAdjust"] = self.eitherendian2int(php_substr(rgadData, 4, 2))
                    thisfile_riff_raw_rgad["nAudiophileRgAdjust"] = self.eitherendian2int(php_substr(rgadData, 6, 2))
                    nRadioRgAdjustBitstring = php_str_pad(getid3_lib.dec2bin(thisfile_riff_raw_rgad["nRadioRgAdjust"]), 16, "0", STR_PAD_LEFT)
                    nAudiophileRgAdjustBitstring = php_str_pad(getid3_lib.dec2bin(thisfile_riff_raw_rgad["nAudiophileRgAdjust"]), 16, "0", STR_PAD_LEFT)
                    thisfile_riff_raw_rgad_track["name"] = getid3_lib.bin2dec(php_substr(nRadioRgAdjustBitstring, 0, 3))
                    thisfile_riff_raw_rgad_track["originator"] = getid3_lib.bin2dec(php_substr(nRadioRgAdjustBitstring, 3, 3))
                    thisfile_riff_raw_rgad_track["signbit"] = getid3_lib.bin2dec(php_substr(nRadioRgAdjustBitstring, 6, 1))
                    thisfile_riff_raw_rgad_track["adjustment"] = getid3_lib.bin2dec(php_substr(nRadioRgAdjustBitstring, 7, 9))
                    thisfile_riff_raw_rgad_album["name"] = getid3_lib.bin2dec(php_substr(nAudiophileRgAdjustBitstring, 0, 3))
                    thisfile_riff_raw_rgad_album["originator"] = getid3_lib.bin2dec(php_substr(nAudiophileRgAdjustBitstring, 3, 3))
                    thisfile_riff_raw_rgad_album["signbit"] = getid3_lib.bin2dec(php_substr(nAudiophileRgAdjustBitstring, 6, 1))
                    thisfile_riff_raw_rgad_album["adjustment"] = getid3_lib.bin2dec(php_substr(nAudiophileRgAdjustBitstring, 7, 9))
                    thisfile_riff["rgad"]["peakamplitude"] = thisfile_riff_raw_rgad["fPeakAmplitude"]
                    if thisfile_riff_raw_rgad_track["name"] != 0 and thisfile_riff_raw_rgad_track["originator"] != 0:
                        thisfile_riff["rgad"]["track"]["name"] = getid3_lib.rgadnamelookup(thisfile_riff_raw_rgad_track["name"])
                        thisfile_riff["rgad"]["track"]["originator"] = getid3_lib.rgadoriginatorlookup(thisfile_riff_raw_rgad_track["originator"])
                        thisfile_riff["rgad"]["track"]["adjustment"] = getid3_lib.rgadadjustmentlookup(thisfile_riff_raw_rgad_track["adjustment"], thisfile_riff_raw_rgad_track["signbit"])
                    # end if
                    if thisfile_riff_raw_rgad_album["name"] != 0 and thisfile_riff_raw_rgad_album["originator"] != 0:
                        thisfile_riff["rgad"]["album"]["name"] = getid3_lib.rgadnamelookup(thisfile_riff_raw_rgad_album["name"])
                        thisfile_riff["rgad"]["album"]["originator"] = getid3_lib.rgadoriginatorlookup(thisfile_riff_raw_rgad_album["originator"])
                        thisfile_riff["rgad"]["album"]["adjustment"] = getid3_lib.rgadadjustmentlookup(thisfile_riff_raw_rgad_album["adjustment"], thisfile_riff_raw_rgad_album["signbit"])
                    # end if
                # end if
                if (php_isset(lambda : thisfile_riff_WAVE["fact"][0]["data"])):
                    thisfile_riff_raw["fact"]["NumberOfSamples"] = self.eitherendian2int(php_substr(thisfile_riff_WAVE["fact"][0]["data"], 0, 4))
                    pass
                # end if
                if (not php_empty(lambda : thisfile_riff_raw["fmt "]["nAvgBytesPerSec"])):
                    thisfile_audio["bitrate"] = getid3_lib.castasint(thisfile_riff_raw["fmt "]["nAvgBytesPerSec"] * 8)
                # end if
                if (php_isset(lambda : thisfile_riff_WAVE["bext"][0]["data"])):
                    #// shortcut
                    thisfile_riff_WAVE_bext_0 = thisfile_riff_WAVE["bext"][0]
                    thisfile_riff_WAVE_bext_0["title"] = php_trim(php_substr(thisfile_riff_WAVE_bext_0["data"], 0, 256))
                    thisfile_riff_WAVE_bext_0["author"] = php_trim(php_substr(thisfile_riff_WAVE_bext_0["data"], 256, 32))
                    thisfile_riff_WAVE_bext_0["reference"] = php_trim(php_substr(thisfile_riff_WAVE_bext_0["data"], 288, 32))
                    thisfile_riff_WAVE_bext_0["origin_date"] = php_substr(thisfile_riff_WAVE_bext_0["data"], 320, 10)
                    thisfile_riff_WAVE_bext_0["origin_time"] = php_substr(thisfile_riff_WAVE_bext_0["data"], 330, 8)
                    thisfile_riff_WAVE_bext_0["time_reference"] = getid3_lib.littleendian2int(php_substr(thisfile_riff_WAVE_bext_0["data"], 338, 8))
                    thisfile_riff_WAVE_bext_0["bwf_version"] = getid3_lib.littleendian2int(php_substr(thisfile_riff_WAVE_bext_0["data"], 346, 1))
                    thisfile_riff_WAVE_bext_0["reserved"] = php_substr(thisfile_riff_WAVE_bext_0["data"], 347, 254)
                    thisfile_riff_WAVE_bext_0["coding_history"] = php_explode("\r\n", php_trim(php_substr(thisfile_riff_WAVE_bext_0["data"], 601)))
                    if php_preg_match("#^([0-9]{4}).([0-9]{2}).([0-9]{2})$#", thisfile_riff_WAVE_bext_0["origin_date"], matches_bext_date):
                        if php_preg_match("#^([0-9]{2}).([0-9]{2}).([0-9]{2})$#", thisfile_riff_WAVE_bext_0["origin_time"], matches_bext_time):
                            dummy, bext_timestamp["year"], bext_timestamp["month"], bext_timestamp["day"] = matches_bext_date
                            dummy, bext_timestamp["hour"], bext_timestamp["minute"], bext_timestamp["second"] = matches_bext_time
                            thisfile_riff_WAVE_bext_0["origin_date_unix"] = gmmktime(bext_timestamp["hour"], bext_timestamp["minute"], bext_timestamp["second"], bext_timestamp["month"], bext_timestamp["day"], bext_timestamp["year"])
                        else:
                            self.warning("RIFF.WAVE.BEXT.origin_time is invalid")
                        # end if
                    else:
                        self.warning("RIFF.WAVE.BEXT.origin_date is invalid")
                    # end if
                    thisfile_riff["comments"]["author"][-1] = thisfile_riff_WAVE_bext_0["author"]
                    thisfile_riff["comments"]["title"][-1] = thisfile_riff_WAVE_bext_0["title"]
                # end if
                if (php_isset(lambda : thisfile_riff_WAVE["MEXT"][0]["data"])):
                    #// shortcut
                    thisfile_riff_WAVE_MEXT_0 = thisfile_riff_WAVE["MEXT"][0]
                    thisfile_riff_WAVE_MEXT_0["raw"]["sound_information"] = getid3_lib.littleendian2int(php_substr(thisfile_riff_WAVE_MEXT_0["data"], 0, 2))
                    thisfile_riff_WAVE_MEXT_0["flags"]["homogenous"] = bool(thisfile_riff_WAVE_MEXT_0["raw"]["sound_information"] & 1)
                    if thisfile_riff_WAVE_MEXT_0["flags"]["homogenous"]:
                        thisfile_riff_WAVE_MEXT_0["flags"]["padding"] = False if thisfile_riff_WAVE_MEXT_0["raw"]["sound_information"] & 2 else True
                        thisfile_riff_WAVE_MEXT_0["flags"]["22_or_44"] = bool(thisfile_riff_WAVE_MEXT_0["raw"]["sound_information"] & 4)
                        thisfile_riff_WAVE_MEXT_0["flags"]["free_format"] = bool(thisfile_riff_WAVE_MEXT_0["raw"]["sound_information"] & 8)
                        thisfile_riff_WAVE_MEXT_0["nominal_frame_size"] = getid3_lib.littleendian2int(php_substr(thisfile_riff_WAVE_MEXT_0["data"], 2, 2))
                    # end if
                    thisfile_riff_WAVE_MEXT_0["anciliary_data_length"] = getid3_lib.littleendian2int(php_substr(thisfile_riff_WAVE_MEXT_0["data"], 6, 2))
                    thisfile_riff_WAVE_MEXT_0["raw"]["anciliary_data_def"] = getid3_lib.littleendian2int(php_substr(thisfile_riff_WAVE_MEXT_0["data"], 8, 2))
                    thisfile_riff_WAVE_MEXT_0["flags"]["anciliary_data_left"] = bool(thisfile_riff_WAVE_MEXT_0["raw"]["anciliary_data_def"] & 1)
                    thisfile_riff_WAVE_MEXT_0["flags"]["anciliary_data_free"] = bool(thisfile_riff_WAVE_MEXT_0["raw"]["anciliary_data_def"] & 2)
                    thisfile_riff_WAVE_MEXT_0["flags"]["anciliary_data_right"] = bool(thisfile_riff_WAVE_MEXT_0["raw"]["anciliary_data_def"] & 4)
                # end if
                if (php_isset(lambda : thisfile_riff_WAVE["cart"][0]["data"])):
                    #// shortcut
                    thisfile_riff_WAVE_cart_0 = thisfile_riff_WAVE["cart"][0]
                    thisfile_riff_WAVE_cart_0["version"] = php_substr(thisfile_riff_WAVE_cart_0["data"], 0, 4)
                    thisfile_riff_WAVE_cart_0["title"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0["data"], 4, 64))
                    thisfile_riff_WAVE_cart_0["artist"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0["data"], 68, 64))
                    thisfile_riff_WAVE_cart_0["cut_id"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0["data"], 132, 64))
                    thisfile_riff_WAVE_cart_0["client_id"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0["data"], 196, 64))
                    thisfile_riff_WAVE_cart_0["category"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0["data"], 260, 64))
                    thisfile_riff_WAVE_cart_0["classification"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0["data"], 324, 64))
                    thisfile_riff_WAVE_cart_0["out_cue"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0["data"], 388, 64))
                    thisfile_riff_WAVE_cart_0["start_date"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0["data"], 452, 10))
                    thisfile_riff_WAVE_cart_0["start_time"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0["data"], 462, 8))
                    thisfile_riff_WAVE_cart_0["end_date"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0["data"], 470, 10))
                    thisfile_riff_WAVE_cart_0["end_time"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0["data"], 480, 8))
                    thisfile_riff_WAVE_cart_0["producer_app_id"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0["data"], 488, 64))
                    thisfile_riff_WAVE_cart_0["producer_app_version"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0["data"], 552, 64))
                    thisfile_riff_WAVE_cart_0["user_defined_text"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0["data"], 616, 64))
                    thisfile_riff_WAVE_cart_0["zero_db_reference"] = getid3_lib.littleendian2int(php_substr(thisfile_riff_WAVE_cart_0["data"], 680, 4), True)
                    i = 0
                    while i < 8:
                        
                        thisfile_riff_WAVE_cart_0["post_time"][i]["usage_fourcc"] = php_substr(thisfile_riff_WAVE_cart_0["data"], 684 + i * 8, 4)
                        thisfile_riff_WAVE_cart_0["post_time"][i]["timer_value"] = getid3_lib.littleendian2int(php_substr(thisfile_riff_WAVE_cart_0["data"], 684 + i * 8 + 4, 4))
                        i += 1
                    # end while
                    thisfile_riff_WAVE_cart_0["url"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0["data"], 748, 1024))
                    thisfile_riff_WAVE_cart_0["tag_text"] = php_explode("\r\n", php_trim(php_substr(thisfile_riff_WAVE_cart_0["data"], 1772)))
                    thisfile_riff["comments"]["tag_text"][-1] = php_substr(thisfile_riff_WAVE_cart_0["data"], 1772)
                    thisfile_riff["comments"]["artist"][-1] = thisfile_riff_WAVE_cart_0["artist"]
                    thisfile_riff["comments"]["title"][-1] = thisfile_riff_WAVE_cart_0["title"]
                # end if
                if (php_isset(lambda : thisfile_riff_WAVE["SNDM"][0]["data"])):
                    #// SoundMiner metadata
                    #// shortcuts
                    thisfile_riff_WAVE_SNDM_0 = thisfile_riff_WAVE["SNDM"][0]
                    thisfile_riff_WAVE_SNDM_0_data = thisfile_riff_WAVE_SNDM_0["data"]
                    SNDM_startoffset = 0
                    SNDM_endoffset = thisfile_riff_WAVE_SNDM_0["size"]
                    while True:
                        
                        if not (SNDM_startoffset < SNDM_endoffset):
                            break
                        # end if
                        SNDM_thisTagOffset = 0
                        SNDM_thisTagSize = getid3_lib.bigendian2int(php_substr(thisfile_riff_WAVE_SNDM_0_data, SNDM_startoffset + SNDM_thisTagOffset, 4))
                        SNDM_thisTagOffset += 4
                        SNDM_thisTagKey = php_substr(thisfile_riff_WAVE_SNDM_0_data, SNDM_startoffset + SNDM_thisTagOffset, 4)
                        SNDM_thisTagOffset += 4
                        SNDM_thisTagDataSize = getid3_lib.bigendian2int(php_substr(thisfile_riff_WAVE_SNDM_0_data, SNDM_startoffset + SNDM_thisTagOffset, 2))
                        SNDM_thisTagOffset += 2
                        SNDM_thisTagDataFlags = getid3_lib.bigendian2int(php_substr(thisfile_riff_WAVE_SNDM_0_data, SNDM_startoffset + SNDM_thisTagOffset, 2))
                        SNDM_thisTagOffset += 2
                        SNDM_thisTagDataText = php_substr(thisfile_riff_WAVE_SNDM_0_data, SNDM_startoffset + SNDM_thisTagOffset, SNDM_thisTagDataSize)
                        SNDM_thisTagOffset += SNDM_thisTagDataSize
                        if SNDM_thisTagSize != 4 + 4 + 2 + 2 + SNDM_thisTagDataSize:
                            self.warning("RIFF.WAVE.SNDM.data contains tag not expected length (expected: " + SNDM_thisTagSize + ", found: " + 4 + 4 + 2 + 2 + SNDM_thisTagDataSize + ") at offset " + SNDM_startoffset + " (file offset " + thisfile_riff_WAVE_SNDM_0["offset"] + SNDM_startoffset + ")")
                            break
                        elif SNDM_thisTagSize <= 0:
                            self.warning("RIFF.WAVE.SNDM.data contains zero-size tag at offset " + SNDM_startoffset + " (file offset " + thisfile_riff_WAVE_SNDM_0["offset"] + SNDM_startoffset + ")")
                            break
                        # end if
                        SNDM_startoffset += SNDM_thisTagSize
                        thisfile_riff_WAVE_SNDM_0["parsed_raw"][SNDM_thisTagKey] = SNDM_thisTagDataText
                        parsedkey = self.wavesndmtaglookup(SNDM_thisTagKey)
                        if parsedkey:
                            thisfile_riff_WAVE_SNDM_0["parsed"][parsedkey] = SNDM_thisTagDataText
                        else:
                            self.warning("RIFF.WAVE.SNDM contains unknown tag \"" + SNDM_thisTagKey + "\" at offset " + SNDM_startoffset + " (file offset " + thisfile_riff_WAVE_SNDM_0["offset"] + SNDM_startoffset + ")")
                        # end if
                    # end while
                    tagmapping = Array({"tracktitle": "title", "category": "genre", "cdtitle": "album"})
                    for fromkey,tokey in tagmapping:
                        if (php_isset(lambda : thisfile_riff_WAVE_SNDM_0["parsed"][fromkey])):
                            thisfile_riff["comments"][tokey][-1] = thisfile_riff_WAVE_SNDM_0["parsed"][fromkey]
                        # end if
                    # end for
                # end if
                if (php_isset(lambda : thisfile_riff_WAVE["iXML"][0]["data"])):
                    #// requires functions simplexml_load_string and get_object_vars
                    parsedXML = getid3_lib.xml2array(thisfile_riff_WAVE["iXML"][0]["data"])
                    if parsedXML:
                        thisfile_riff_WAVE["iXML"][0]["parsed"] = parsedXML
                        if (php_isset(lambda : parsedXML["SPEED"]["MASTER_SPEED"])):
                            php_no_error(lambda: numerator, denominator = php_explode("/", parsedXML["SPEED"]["MASTER_SPEED"]))
                            thisfile_riff_WAVE["iXML"][0]["master_speed"] = numerator / denominator if denominator else 1000
                        # end if
                        if (php_isset(lambda : parsedXML["SPEED"]["TIMECODE_RATE"])):
                            php_no_error(lambda: numerator, denominator = php_explode("/", parsedXML["SPEED"]["TIMECODE_RATE"]))
                            thisfile_riff_WAVE["iXML"][0]["timecode_rate"] = numerator / denominator if denominator else 1000
                        # end if
                        if (php_isset(lambda : parsedXML["SPEED"]["TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_LO"])) and (not php_empty(lambda : parsedXML["SPEED"]["TIMESTAMP_SAMPLE_RATE"])) and (not php_empty(lambda : thisfile_riff_WAVE["iXML"][0]["timecode_rate"])):
                            samples_since_midnight = floatval(php_ltrim(parsedXML["SPEED"]["TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_HI"] + parsedXML["SPEED"]["TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_LO"], "0"))
                            timestamp_sample_rate = php_max(parsedXML["SPEED"]["TIMESTAMP_SAMPLE_RATE"]) if php_is_array(parsedXML["SPEED"]["TIMESTAMP_SAMPLE_RATE"]) else parsedXML["SPEED"]["TIMESTAMP_SAMPLE_RATE"]
                            #// XML could possibly contain more than one TIMESTAMP_SAMPLE_RATE tag, returning as array instead of integer [why? does it make sense? perhaps doesn't matter but getID3 needs to deal with it] - see https://github.com/JamesHeinrich/getID3/issues/105
                            thisfile_riff_WAVE["iXML"][0]["timecode_seconds"] = samples_since_midnight / timestamp_sample_rate
                            h = floor(thisfile_riff_WAVE["iXML"][0]["timecode_seconds"] / 3600)
                            m = floor(thisfile_riff_WAVE["iXML"][0]["timecode_seconds"] - h * 3600 / 60)
                            s = floor(thisfile_riff_WAVE["iXML"][0]["timecode_seconds"] - h * 3600 - m * 60)
                            f = thisfile_riff_WAVE["iXML"][0]["timecode_seconds"] - h * 3600 - m * 60 - s * thisfile_riff_WAVE["iXML"][0]["timecode_rate"]
                            thisfile_riff_WAVE["iXML"][0]["timecode_string"] = php_sprintf("%02d:%02d:%02d:%05.2f", h, m, s, f)
                            thisfile_riff_WAVE["iXML"][0]["timecode_string_round"] = php_sprintf("%02d:%02d:%02d:%02d", h, m, s, round(f))
                            samples_since_midnight = None
                            timestamp_sample_rate = None
                            h = None
                            m = None
                            s = None
                            f = None
                        # end if
                        parsedXML = None
                    # end if
                # end if
                if (not (php_isset(lambda : thisfile_audio["bitrate"]))) and (php_isset(lambda : thisfile_riff_audio[streamindex]["bitrate"])):
                    thisfile_audio["bitrate"] = thisfile_riff_audio[streamindex]["bitrate"]
                    info["playtime_seconds"] = float(info["avdataend"] - info["avdataoffset"] * 8 / thisfile_audio["bitrate"])
                # end if
                if (not php_empty(lambda : info["wavpack"])):
                    thisfile_audio_dataformat = "wavpack"
                    thisfile_audio["bitrate_mode"] = "vbr"
                    thisfile_audio["encoder"] = "WavPack v" + info["wavpack"]["version"]
                    #// Reset to the way it was - RIFF parsing will have messed this up
                    info["avdataend"] = Original["avdataend"]
                    thisfile_audio["bitrate"] = info["avdataend"] - info["avdataoffset"] * 8 / info["playtime_seconds"]
                    self.fseek(info["avdataoffset"] - 44)
                    RIFFdata = self.fread(44)
                    OrignalRIFFheaderSize = getid3_lib.littleendian2int(php_substr(RIFFdata, 4, 4)) + 8
                    OrignalRIFFdataSize = getid3_lib.littleendian2int(php_substr(RIFFdata, 40, 4)) + 44
                    if OrignalRIFFheaderSize > OrignalRIFFdataSize:
                        info["avdataend"] -= OrignalRIFFheaderSize - OrignalRIFFdataSize
                        self.fseek(info["avdataend"])
                        RIFFdata += self.fread(OrignalRIFFheaderSize - OrignalRIFFdataSize)
                    # end if
                    #// move the data chunk after all other chunks (if any)
                    #// so that the RIFF parser doesn't see EOF when trying
                    #// to skip over the data chunk
                    RIFFdata = php_substr(RIFFdata, 0, 36) + php_substr(RIFFdata, 44) + php_substr(RIFFdata, 36, 8)
                    getid3_riff = php_new_class("getid3_riff", lambda : getid3_riff(self.getid3))
                    getid3_riff.parseriffdata(RIFFdata)
                    getid3_riff = None
                # end if
                if (php_isset(lambda : thisfile_riff_raw["fmt "]["wFormatTag"])):
                    for case in Switch(thisfile_riff_raw["fmt "]["wFormatTag"]):
                        if case(1):
                            #// PCM
                            if (not php_empty(lambda : info["ac3"])):
                                #// Dolby Digital WAV files masquerade as PCM-WAV, but they're not
                                thisfile_audio["wformattag"] = 8192
                                thisfile_audio["codec"] = self.wformattaglookup(thisfile_audio["wformattag"])
                                thisfile_audio["lossless"] = False
                                thisfile_audio["bitrate"] = info["ac3"]["bitrate"]
                                thisfile_audio["sample_rate"] = info["ac3"]["sample_rate"]
                            # end if
                            if (not php_empty(lambda : info["dts"])):
                                #// Dolby DTS files masquerade as PCM-WAV, but they're not
                                thisfile_audio["wformattag"] = 8193
                                thisfile_audio["codec"] = self.wformattaglookup(thisfile_audio["wformattag"])
                                thisfile_audio["lossless"] = False
                                thisfile_audio["bitrate"] = info["dts"]["bitrate"]
                                thisfile_audio["sample_rate"] = info["dts"]["sample_rate"]
                            # end if
                            break
                        # end if
                        if case(2222):
                            #// ClearJump LiteWave
                            thisfile_audio["bitrate_mode"] = "vbr"
                            thisfile_audio_dataformat = "litewave"
                            #// typedef struct tagSLwFormat {
                            #// WORD    m_wCompFormat;     // low byte defines compression method, high byte is compression flags
                            #// DWORD   m_dwScale;         // scale factor for lossy compression
                            #// DWORD   m_dwBlockSize;     // number of samples in encoded blocks
                            #// WORD    m_wQuality;        // alias for the scale factor
                            #// WORD    m_wMarkDistance;   // distance between marks in bytes
                            #// WORD    m_wReserved;
                            #// 
                            #// following paramters are ignored if CF_FILESRC is not set
                            #// DWORD   m_dwOrgSize;       // original file size in bytes
                            #// WORD    m_bFactExists;     // indicates if 'fact' chunk exists in the original file
                            #// DWORD   m_dwRiffChunkSize; // riff chunk size in the original file
                            #// 
                            #// PCMWAVEFORMAT m_OrgWf;     // original wave format
                            #// }SLwFormat, *PSLwFormat;
                            #// shortcut
                            thisfile_riff["litewave"]["raw"] = Array()
                            riff_litewave = thisfile_riff["litewave"]
                            riff_litewave_raw = riff_litewave["raw"]
                            flags = Array({"compression_method": 1, "compression_flags": 1, "m_dwScale": 4, "m_dwBlockSize": 4, "m_wQuality": 2, "m_wMarkDistance": 2, "m_wReserved": 2, "m_dwOrgSize": 4, "m_bFactExists": 2, "m_dwRiffChunkSize": 4})
                            litewave_offset = 18
                            for flag,length in flags:
                                riff_litewave_raw[flag] = getid3_lib.littleendian2int(php_substr(thisfile_riff_WAVE["fmt "][0]["data"], litewave_offset, length))
                                litewave_offset += length
                            # end for
                            #// $riff_litewave['quality_factor'] = intval(round((2000 - $riff_litewave_raw['m_dwScale']) / 20));
                            riff_litewave["quality_factor"] = riff_litewave_raw["m_wQuality"]
                            riff_litewave["flags"]["raw_source"] = False if riff_litewave_raw["compression_flags"] & 1 else True
                            riff_litewave["flags"]["vbr_blocksize"] = False if riff_litewave_raw["compression_flags"] & 2 else True
                            riff_litewave["flags"]["seekpoints"] = bool(riff_litewave_raw["compression_flags"] & 4)
                            thisfile_audio["lossless"] = True if riff_litewave_raw["m_wQuality"] == 100 else False
                            thisfile_audio["encoder_options"] = "-q" + riff_litewave["quality_factor"]
                            break
                        # end if
                        if case():
                            break
                        # end if
                    # end for
                # end if
                if info["avdataend"] > info["filesize"]:
                    for case in Switch(thisfile_audio_dataformat if (not php_empty(lambda : thisfile_audio_dataformat)) else ""):
                        if case("wavpack"):
                            pass
                        # end if
                        if case("lpac"):
                            pass
                        # end if
                        if case("ofr"):
                            pass
                        # end if
                        if case("ofs"):
                            break
                        # end if
                        if case("litewave"):
                            if info["avdataend"] - info["filesize"] == 1:
                                pass
                            else:
                                #// Short by more than one byte, throw warning
                                self.warning("Probably truncated file - expecting " + thisfile_riff[RIFFsubtype]["data"][0]["size"] + " bytes of data, only found " + info["filesize"] - info["avdataoffset"] + " (short by " + thisfile_riff[RIFFsubtype]["data"][0]["size"] - info["filesize"] - info["avdataoffset"] + " bytes)")
                                info["avdataend"] = info["filesize"]
                            # end if
                            break
                        # end if
                        if case():
                            if info["avdataend"] - info["filesize"] == 1 and thisfile_riff[RIFFsubtype]["data"][0]["size"] % 2 == 0 and info["filesize"] - info["avdataoffset"] % 2 == 1:
                                #// output file appears to be incorrectly *not* padded to nearest WORD boundary
                                #// Output less severe warning
                                self.warning("File should probably be padded to nearest WORD boundary, but it is not (expecting " + thisfile_riff[RIFFsubtype]["data"][0]["size"] + " bytes of data, only found " + info["filesize"] - info["avdataoffset"] + " therefore short by " + thisfile_riff[RIFFsubtype]["data"][0]["size"] - info["filesize"] - info["avdataoffset"] + " bytes)")
                                info["avdataend"] = info["filesize"]
                            else:
                                #// Short by more than one byte, throw warning
                                self.warning("Probably truncated file - expecting " + thisfile_riff[RIFFsubtype]["data"][0]["size"] + " bytes of data, only found " + info["filesize"] - info["avdataoffset"] + " (short by " + thisfile_riff[RIFFsubtype]["data"][0]["size"] - info["filesize"] - info["avdataoffset"] + " bytes)")
                                info["avdataend"] = info["filesize"]
                            # end if
                            break
                        # end if
                    # end for
                # end if
                if (not php_empty(lambda : info["mpeg"]["audio"]["LAME"]["audio_bytes"])):
                    if info["avdataend"] - info["avdataoffset"] - info["mpeg"]["audio"]["LAME"]["audio_bytes"] == 1:
                        info["avdataend"] -= 1
                        self.warning("Extra null byte at end of MP3 data assumed to be RIFF padding and therefore ignored")
                    # end if
                # end if
                if (php_isset(lambda : thisfile_audio_dataformat)) and thisfile_audio_dataformat == "ac3":
                    thisfile_audio["bits_per_sample"] = None
                    if (not php_empty(lambda : info["ac3"]["bitrate"])) and info["ac3"]["bitrate"] != thisfile_audio["bitrate"]:
                        thisfile_audio["bitrate"] = info["ac3"]["bitrate"]
                    # end if
                # end if
                break
            # end if
            if case("AVI "):
                info["fileformat"] = "avi"
                info["mime_type"] = "video/avi"
                thisfile_video["bitrate_mode"] = "vbr"
                #// maybe not, but probably
                thisfile_video["dataformat"] = "avi"
                thisfile_riff_video_current = Array()
                if (php_isset(lambda : thisfile_riff[RIFFsubtype]["movi"]["offset"])):
                    info["avdataoffset"] = thisfile_riff[RIFFsubtype]["movi"]["offset"] + 8
                    if (php_isset(lambda : thisfile_riff["AVIX"])):
                        info["avdataend"] = thisfile_riff["AVIX"][php_count(thisfile_riff["AVIX"]) - 1]["chunks"]["movi"]["offset"] + thisfile_riff["AVIX"][php_count(thisfile_riff["AVIX"]) - 1]["chunks"]["movi"]["size"]
                    else:
                        info["avdataend"] = thisfile_riff["AVI "]["movi"]["offset"] + thisfile_riff["AVI "]["movi"]["size"]
                    # end if
                    if info["avdataend"] > info["filesize"]:
                        self.warning("Probably truncated file - expecting " + info["avdataend"] - info["avdataoffset"] + " bytes of data, only found " + info["filesize"] - info["avdataoffset"] + " (short by " + info["avdataend"] - info["filesize"] + " bytes)")
                        info["avdataend"] = info["filesize"]
                    # end if
                # end if
                if (php_isset(lambda : thisfile_riff["AVI "]["hdrl"]["strl"]["indx"])):
                    #// $bIndexType = array(
                    #// 0x00 => 'AVI_INDEX_OF_INDEXES',
                    #// 0x01 => 'AVI_INDEX_OF_CHUNKS',
                    #// 0x80 => 'AVI_INDEX_IS_DATA',
                    #// );
                    #// $bIndexSubtype = array(
                    #// 0x01 => array(
                    #// 0x01 => 'AVI_INDEX_2FIELD',
                    #// ),
                    #// );
                    for streamnumber,steamdataarray in thisfile_riff["AVI "]["hdrl"]["strl"]["indx"]:
                        ahsisd = thisfile_riff["AVI "]["hdrl"]["strl"]["indx"][streamnumber]["data"]
                        thisfile_riff_raw["indx"][streamnumber]["wLongsPerEntry"] = self.eitherendian2int(php_substr(ahsisd, 0, 2))
                        thisfile_riff_raw["indx"][streamnumber]["bIndexSubType"] = self.eitherendian2int(php_substr(ahsisd, 2, 1))
                        thisfile_riff_raw["indx"][streamnumber]["bIndexType"] = self.eitherendian2int(php_substr(ahsisd, 3, 1))
                        thisfile_riff_raw["indx"][streamnumber]["nEntriesInUse"] = self.eitherendian2int(php_substr(ahsisd, 4, 4))
                        thisfile_riff_raw["indx"][streamnumber]["dwChunkId"] = php_substr(ahsisd, 8, 4)
                        thisfile_riff_raw["indx"][streamnumber]["dwReserved"] = self.eitherendian2int(php_substr(ahsisd, 12, 4))
                        ahsisd = None
                    # end for
                # end if
                if (php_isset(lambda : thisfile_riff["AVI "]["hdrl"]["avih"][streamindex]["data"])):
                    avihData = thisfile_riff["AVI "]["hdrl"]["avih"][streamindex]["data"]
                    #// shortcut
                    thisfile_riff_raw["avih"] = Array()
                    thisfile_riff_raw_avih = thisfile_riff_raw["avih"]
                    thisfile_riff_raw_avih["dwMicroSecPerFrame"] = self.eitherendian2int(php_substr(avihData, 0, 4))
                    #// frame display rate (or 0L)
                    if thisfile_riff_raw_avih["dwMicroSecPerFrame"] == 0:
                        self.error("Corrupt RIFF file: avih.dwMicroSecPerFrame == zero")
                        return False
                    # end if
                    flags = Array("dwMaxBytesPerSec", "dwPaddingGranularity", "dwFlags", "dwTotalFrames", "dwInitialFrames", "dwStreams", "dwSuggestedBufferSize", "dwWidth", "dwHeight", "dwScale", "dwRate", "dwStart", "dwLength")
                    avih_offset = 4
                    for flag in flags:
                        thisfile_riff_raw_avih[flag] = self.eitherendian2int(php_substr(avihData, avih_offset, 4))
                        avih_offset += 4
                    # end for
                    flags = Array({"hasindex": 16, "mustuseindex": 32, "interleaved": 256, "trustcktype": 2048, "capturedfile": 65536, "copyrighted": 131088})
                    for flag,value in flags:
                        thisfile_riff_raw_avih["flags"][flag] = bool(thisfile_riff_raw_avih["dwFlags"] & value)
                    # end for
                    #// shortcut
                    thisfile_riff_video[streamindex] = Array()
                    #// @var array $thisfile_riff_video_current
                    thisfile_riff_video_current = thisfile_riff_video[streamindex]
                    if thisfile_riff_raw_avih["dwWidth"] > 0:
                        thisfile_riff_video_current["frame_width"] = thisfile_riff_raw_avih["dwWidth"]
                        thisfile_video["resolution_x"] = thisfile_riff_video_current["frame_width"]
                    # end if
                    if thisfile_riff_raw_avih["dwHeight"] > 0:
                        thisfile_riff_video_current["frame_height"] = thisfile_riff_raw_avih["dwHeight"]
                        thisfile_video["resolution_y"] = thisfile_riff_video_current["frame_height"]
                    # end if
                    if thisfile_riff_raw_avih["dwTotalFrames"] > 0:
                        thisfile_riff_video_current["total_frames"] = thisfile_riff_raw_avih["dwTotalFrames"]
                        thisfile_video["total_frames"] = thisfile_riff_video_current["total_frames"]
                    # end if
                    thisfile_riff_video_current["frame_rate"] = round(1000000 / thisfile_riff_raw_avih["dwMicroSecPerFrame"], 3)
                    thisfile_video["frame_rate"] = thisfile_riff_video_current["frame_rate"]
                # end if
                if (php_isset(lambda : thisfile_riff["AVI "]["hdrl"]["strl"]["strh"][0]["data"])):
                    if php_is_array(thisfile_riff["AVI "]["hdrl"]["strl"]["strh"]):
                        i = 0
                        while i < php_count(thisfile_riff["AVI "]["hdrl"]["strl"]["strh"]):
                            
                            if (php_isset(lambda : thisfile_riff["AVI "]["hdrl"]["strl"]["strh"][i]["data"])):
                                strhData = thisfile_riff["AVI "]["hdrl"]["strl"]["strh"][i]["data"]
                                strhfccType = php_substr(strhData, 0, 4)
                                if (php_isset(lambda : thisfile_riff["AVI "]["hdrl"]["strl"]["strf"][i]["data"])):
                                    strfData = thisfile_riff["AVI "]["hdrl"]["strl"]["strf"][i]["data"]
                                    #// shortcut
                                    thisfile_riff_raw_strf_strhfccType_streamindex = thisfile_riff_raw["strf"][strhfccType][streamindex]
                                    for case in Switch(strhfccType):
                                        if case("auds"):
                                            thisfile_audio["bitrate_mode"] = "cbr"
                                            thisfile_audio_dataformat = "wav"
                                            if (php_isset(lambda : thisfile_riff_audio)) and php_is_array(thisfile_riff_audio):
                                                streamindex = php_count(thisfile_riff_audio)
                                            # end if
                                            thisfile_riff_audio[streamindex] = self.parsewaveformatex(strfData)
                                            thisfile_audio["wformattag"] = thisfile_riff_audio[streamindex]["raw"]["wFormatTag"]
                                            #// shortcut
                                            thisfile_audio["streams"][streamindex] = thisfile_riff_audio[streamindex]
                                            thisfile_audio_streams_currentstream = thisfile_audio["streams"][streamindex]
                                            if thisfile_audio_streams_currentstream["bits_per_sample"] == 0:
                                                thisfile_audio_streams_currentstream["bits_per_sample"] = None
                                            # end if
                                            thisfile_audio_streams_currentstream["wformattag"] = thisfile_audio_streams_currentstream["raw"]["wFormatTag"]
                                            thisfile_audio_streams_currentstream["raw"] = None
                                            #// shortcut
                                            thisfile_riff_raw["strf"][strhfccType][streamindex] = thisfile_riff_audio[streamindex]["raw"]
                                            thisfile_riff_audio[streamindex]["raw"] = None
                                            thisfile_audio = getid3_lib.array_merge_noclobber(thisfile_audio, thisfile_riff_audio[streamindex])
                                            thisfile_audio["lossless"] = False
                                            for case in Switch(thisfile_riff_raw_strf_strhfccType_streamindex["wFormatTag"]):
                                                if case(1):
                                                    #// PCM
                                                    thisfile_audio_dataformat = "wav"
                                                    thisfile_audio["lossless"] = True
                                                    break
                                                # end if
                                                if case(80):
                                                    #// MPEG Layer 2 or Layer 1
                                                    thisfile_audio_dataformat = "mp2"
                                                    break
                                                # end if
                                                if case(85):
                                                    #// MPEG Layer 3
                                                    thisfile_audio_dataformat = "mp3"
                                                    break
                                                # end if
                                                if case(255):
                                                    #// AAC
                                                    thisfile_audio_dataformat = "aac"
                                                    break
                                                # end if
                                                if case(353):
                                                    pass
                                                # end if
                                                if case(354):
                                                    pass
                                                # end if
                                                if case(355):
                                                    #// Windows Media Lossess v9
                                                    thisfile_audio_dataformat = "wma"
                                                    break
                                                # end if
                                                if case(8192):
                                                    #// AC-3
                                                    thisfile_audio_dataformat = "ac3"
                                                    break
                                                # end if
                                                if case(8193):
                                                    #// DTS
                                                    thisfile_audio_dataformat = "dts"
                                                    break
                                                # end if
                                                if case():
                                                    thisfile_audio_dataformat = "wav"
                                                    break
                                                # end if
                                            # end for
                                            thisfile_audio_streams_currentstream["dataformat"] = thisfile_audio_dataformat
                                            thisfile_audio_streams_currentstream["lossless"] = thisfile_audio["lossless"]
                                            thisfile_audio_streams_currentstream["bitrate_mode"] = thisfile_audio["bitrate_mode"]
                                            break
                                        # end if
                                        if case("iavs"):
                                            pass
                                        # end if
                                        if case("vids"):
                                            #// shortcut
                                            thisfile_riff_raw["strh"][i] = Array()
                                            thisfile_riff_raw_strh_current = thisfile_riff_raw["strh"][i]
                                            thisfile_riff_raw_strh_current["fccType"] = php_substr(strhData, 0, 4)
                                            #// same as $strhfccType;
                                            thisfile_riff_raw_strh_current["fccHandler"] = php_substr(strhData, 4, 4)
                                            thisfile_riff_raw_strh_current["dwFlags"] = self.eitherendian2int(php_substr(strhData, 8, 4))
                                            #// Contains AVITF_* flags
                                            thisfile_riff_raw_strh_current["wPriority"] = self.eitherendian2int(php_substr(strhData, 12, 2))
                                            thisfile_riff_raw_strh_current["wLanguage"] = self.eitherendian2int(php_substr(strhData, 14, 2))
                                            thisfile_riff_raw_strh_current["dwInitialFrames"] = self.eitherendian2int(php_substr(strhData, 16, 4))
                                            thisfile_riff_raw_strh_current["dwScale"] = self.eitherendian2int(php_substr(strhData, 20, 4))
                                            thisfile_riff_raw_strh_current["dwRate"] = self.eitherendian2int(php_substr(strhData, 24, 4))
                                            thisfile_riff_raw_strh_current["dwStart"] = self.eitherendian2int(php_substr(strhData, 28, 4))
                                            thisfile_riff_raw_strh_current["dwLength"] = self.eitherendian2int(php_substr(strhData, 32, 4))
                                            thisfile_riff_raw_strh_current["dwSuggestedBufferSize"] = self.eitherendian2int(php_substr(strhData, 36, 4))
                                            thisfile_riff_raw_strh_current["dwQuality"] = self.eitherendian2int(php_substr(strhData, 40, 4))
                                            thisfile_riff_raw_strh_current["dwSampleSize"] = self.eitherendian2int(php_substr(strhData, 44, 4))
                                            thisfile_riff_raw_strh_current["rcFrame"] = self.eitherendian2int(php_substr(strhData, 48, 4))
                                            thisfile_riff_video_current["codec"] = self.fourcclookup(thisfile_riff_raw_strh_current["fccHandler"])
                                            thisfile_video["fourcc"] = thisfile_riff_raw_strh_current["fccHandler"]
                                            if (not thisfile_riff_video_current["codec"]) and (php_isset(lambda : thisfile_riff_raw_strf_strhfccType_streamindex["fourcc"])) and self.fourcclookup(thisfile_riff_raw_strf_strhfccType_streamindex["fourcc"]):
                                                thisfile_riff_video_current["codec"] = self.fourcclookup(thisfile_riff_raw_strf_strhfccType_streamindex["fourcc"])
                                                thisfile_video["fourcc"] = thisfile_riff_raw_strf_strhfccType_streamindex["fourcc"]
                                            # end if
                                            thisfile_video["codec"] = thisfile_riff_video_current["codec"]
                                            thisfile_video["pixel_aspect_ratio"] = float(1)
                                            for case in Switch(thisfile_riff_raw_strh_current["fccHandler"]):
                                                if case("HFYU"):
                                                    pass
                                                # end if
                                                if case("IRAW"):
                                                    pass
                                                # end if
                                                if case("YUY2"):
                                                    #// Uncompressed YUV 4:2:2
                                                    thisfile_video["lossless"] = True
                                                    break
                                                # end if
                                                if case():
                                                    thisfile_video["lossless"] = False
                                                    break
                                                # end if
                                            # end for
                                            for case in Switch(strhfccType):
                                                if case("vids"):
                                                    thisfile_riff_raw_strf_strhfccType_streamindex = self.parsebitmapinfoheader(php_substr(strfData, 0, 40), self.container == "riff")
                                                    thisfile_video["bits_per_sample"] = thisfile_riff_raw_strf_strhfccType_streamindex["biBitCount"]
                                                    if thisfile_riff_video_current["codec"] == "DV":
                                                        thisfile_riff_video_current["dv_type"] = 2
                                                    # end if
                                                    break
                                                # end if
                                                if case("iavs"):
                                                    thisfile_riff_video_current["dv_type"] = 1
                                                    break
                                                # end if
                                            # end for
                                            break
                                        # end if
                                        if case():
                                            self.warning("Unhandled fccType for stream (" + i + "): \"" + strhfccType + "\"")
                                            break
                                        # end if
                                    # end for
                                # end if
                            # end if
                            if (php_isset(lambda : thisfile_riff_raw_strf_strhfccType_streamindex)) and (php_isset(lambda : thisfile_riff_raw_strf_strhfccType_streamindex["fourcc"])):
                                thisfile_video["fourcc"] = thisfile_riff_raw_strf_strhfccType_streamindex["fourcc"]
                                if self.fourcclookup(thisfile_video["fourcc"]):
                                    thisfile_riff_video_current["codec"] = self.fourcclookup(thisfile_video["fourcc"])
                                    thisfile_video["codec"] = thisfile_riff_video_current["codec"]
                                # end if
                                for case in Switch(thisfile_riff_raw_strf_strhfccType_streamindex["fourcc"]):
                                    if case("HFYU"):
                                        pass
                                    # end if
                                    if case("IRAW"):
                                        pass
                                    # end if
                                    if case("YUY2"):
                                        #// Uncompressed YUV 4:2:2
                                        thisfile_video["lossless"] = True
                                        break
                                    # end if
                                    if case():
                                        thisfile_video["lossless"] = False
                                        break
                                    # end if
                                # end for
                            # end if
                            i += 1
                        # end while
                    # end if
                # end if
                break
            # end if
            if case("AMV "):
                info["fileformat"] = "amv"
                info["mime_type"] = "video/amv"
                thisfile_video["bitrate_mode"] = "vbr"
                #// it's MJPEG, presumably contant-quality encoding, thereby VBR
                thisfile_video["dataformat"] = "mjpeg"
                thisfile_video["codec"] = "mjpeg"
                thisfile_video["lossless"] = False
                thisfile_video["bits_per_sample"] = 24
                thisfile_audio["dataformat"] = "adpcm"
                thisfile_audio["lossless"] = False
                break
            # end if
            if case("CDDA"):
                info["fileformat"] = "cda"
                info["mime_type"] = None
                thisfile_audio_dataformat = "cda"
                info["avdataoffset"] = 44
                if (php_isset(lambda : thisfile_riff["CDDA"]["fmt "][0]["data"])):
                    #// shortcut
                    thisfile_riff_CDDA_fmt_0 = thisfile_riff["CDDA"]["fmt "][0]
                    thisfile_riff_CDDA_fmt_0["unknown1"] = self.eitherendian2int(php_substr(thisfile_riff_CDDA_fmt_0["data"], 0, 2))
                    thisfile_riff_CDDA_fmt_0["track_num"] = self.eitherendian2int(php_substr(thisfile_riff_CDDA_fmt_0["data"], 2, 2))
                    thisfile_riff_CDDA_fmt_0["disc_id"] = self.eitherendian2int(php_substr(thisfile_riff_CDDA_fmt_0["data"], 4, 4))
                    thisfile_riff_CDDA_fmt_0["start_offset_frame"] = self.eitherendian2int(php_substr(thisfile_riff_CDDA_fmt_0["data"], 8, 4))
                    thisfile_riff_CDDA_fmt_0["playtime_frames"] = self.eitherendian2int(php_substr(thisfile_riff_CDDA_fmt_0["data"], 12, 4))
                    thisfile_riff_CDDA_fmt_0["unknown6"] = self.eitherendian2int(php_substr(thisfile_riff_CDDA_fmt_0["data"], 16, 4))
                    thisfile_riff_CDDA_fmt_0["unknown7"] = self.eitherendian2int(php_substr(thisfile_riff_CDDA_fmt_0["data"], 20, 4))
                    thisfile_riff_CDDA_fmt_0["start_offset_seconds"] = float(thisfile_riff_CDDA_fmt_0["start_offset_frame"]) / 75
                    thisfile_riff_CDDA_fmt_0["playtime_seconds"] = float(thisfile_riff_CDDA_fmt_0["playtime_frames"]) / 75
                    info["comments"]["track_number"] = thisfile_riff_CDDA_fmt_0["track_num"]
                    info["playtime_seconds"] = thisfile_riff_CDDA_fmt_0["playtime_seconds"]
                    #// hardcoded data for CD-audio
                    thisfile_audio["lossless"] = True
                    thisfile_audio["sample_rate"] = 44100
                    thisfile_audio["channels"] = 2
                    thisfile_audio["bits_per_sample"] = 16
                    thisfile_audio["bitrate"] = thisfile_audio["sample_rate"] * thisfile_audio["channels"] * thisfile_audio["bits_per_sample"]
                    thisfile_audio["bitrate_mode"] = "cbr"
                # end if
                break
            # end if
            if case("AIFF"):
                pass
            # end if
            if case("AIFC"):
                info["fileformat"] = "aiff"
                info["mime_type"] = "audio/x-aiff"
                thisfile_audio["bitrate_mode"] = "cbr"
                thisfile_audio_dataformat = "aiff"
                thisfile_audio["lossless"] = True
                if (php_isset(lambda : thisfile_riff[RIFFsubtype]["SSND"][0]["offset"])):
                    info["avdataoffset"] = thisfile_riff[RIFFsubtype]["SSND"][0]["offset"] + 8
                    info["avdataend"] = info["avdataoffset"] + thisfile_riff[RIFFsubtype]["SSND"][0]["size"]
                    if info["avdataend"] > info["filesize"]:
                        if info["avdataend"] == info["filesize"] + 1 and info["filesize"] % 2 == 1:
                            pass
                        else:
                            self.warning("Probable truncated AIFF file: expecting " + thisfile_riff[RIFFsubtype]["SSND"][0]["size"] + " bytes of audio data, only " + info["filesize"] - info["avdataoffset"] + " bytes found")
                        # end if
                        info["avdataend"] = info["filesize"]
                    # end if
                # end if
                if (php_isset(lambda : thisfile_riff[RIFFsubtype]["COMM"][0]["data"])):
                    #// shortcut
                    thisfile_riff_RIFFsubtype_COMM_0_data = thisfile_riff[RIFFsubtype]["COMM"][0]["data"]
                    thisfile_riff_audio["channels"] = getid3_lib.bigendian2int(php_substr(thisfile_riff_RIFFsubtype_COMM_0_data, 0, 2), True)
                    thisfile_riff_audio["total_samples"] = getid3_lib.bigendian2int(php_substr(thisfile_riff_RIFFsubtype_COMM_0_data, 2, 4), False)
                    thisfile_riff_audio["bits_per_sample"] = getid3_lib.bigendian2int(php_substr(thisfile_riff_RIFFsubtype_COMM_0_data, 6, 2), True)
                    thisfile_riff_audio["sample_rate"] = int(getid3_lib.bigendian2float(php_substr(thisfile_riff_RIFFsubtype_COMM_0_data, 8, 10)))
                    if thisfile_riff[RIFFsubtype]["COMM"][0]["size"] > 18:
                        thisfile_riff_audio["codec_fourcc"] = php_substr(thisfile_riff_RIFFsubtype_COMM_0_data, 18, 4)
                        CodecNameSize = getid3_lib.bigendian2int(php_substr(thisfile_riff_RIFFsubtype_COMM_0_data, 22, 1), False)
                        thisfile_riff_audio["codec_name"] = php_substr(thisfile_riff_RIFFsubtype_COMM_0_data, 23, CodecNameSize)
                        for case in Switch(thisfile_riff_audio["codec_name"]):
                            if case("NONE"):
                                thisfile_audio["codec"] = "Pulse Code Modulation (PCM)"
                                thisfile_audio["lossless"] = True
                                break
                            # end if
                            if case(""):
                                for case in Switch(thisfile_riff_audio["codec_fourcc"]):
                                    if case("sowt"):
                                        thisfile_riff_audio["codec_name"] = "Two's Compliment Little-Endian PCM"
                                        thisfile_audio["lossless"] = True
                                        break
                                    # end if
                                    if case("twos"):
                                        thisfile_riff_audio["codec_name"] = "Two's Compliment Big-Endian PCM"
                                        thisfile_audio["lossless"] = True
                                        break
                                    # end if
                                    if case():
                                        break
                                    # end if
                                # end for
                                break
                            # end if
                            if case():
                                thisfile_audio["codec"] = thisfile_riff_audio["codec_name"]
                                thisfile_audio["lossless"] = False
                                break
                            # end if
                        # end for
                    # end if
                    thisfile_audio["channels"] = thisfile_riff_audio["channels"]
                    if thisfile_riff_audio["bits_per_sample"] > 0:
                        thisfile_audio["bits_per_sample"] = thisfile_riff_audio["bits_per_sample"]
                    # end if
                    thisfile_audio["sample_rate"] = thisfile_riff_audio["sample_rate"]
                    if thisfile_audio["sample_rate"] == 0:
                        self.error("Corrupted AIFF file: sample_rate == zero")
                        return False
                    # end if
                    info["playtime_seconds"] = thisfile_riff_audio["total_samples"] / thisfile_audio["sample_rate"]
                # end if
                if (php_isset(lambda : thisfile_riff[RIFFsubtype]["COMT"])):
                    offset = 0
                    CommentCount = getid3_lib.bigendian2int(php_substr(thisfile_riff[RIFFsubtype]["COMT"][0]["data"], offset, 2), False)
                    offset += 2
                    i = 0
                    while i < CommentCount:
                        
                        info["comments_raw"][i]["timestamp"] = getid3_lib.bigendian2int(php_substr(thisfile_riff[RIFFsubtype]["COMT"][0]["data"], offset, 4), False)
                        offset += 4
                        info["comments_raw"][i]["marker_id"] = getid3_lib.bigendian2int(php_substr(thisfile_riff[RIFFsubtype]["COMT"][0]["data"], offset, 2), True)
                        offset += 2
                        CommentLength = getid3_lib.bigendian2int(php_substr(thisfile_riff[RIFFsubtype]["COMT"][0]["data"], offset, 2), False)
                        offset += 2
                        info["comments_raw"][i]["comment"] = php_substr(thisfile_riff[RIFFsubtype]["COMT"][0]["data"], offset, CommentLength)
                        offset += CommentLength
                        info["comments_raw"][i]["timestamp_unix"] = getid3_lib.datemac2unix(info["comments_raw"][i]["timestamp"])
                        thisfile_riff["comments"]["comment"][-1] = info["comments_raw"][i]["comment"]
                        i += 1
                    # end while
                # end if
                CommentsChunkNames = Array({"NAME": "title", "author": "artist", "(c) ": "copyright", "ANNO": "comment"})
                for key,value in CommentsChunkNames:
                    if (php_isset(lambda : thisfile_riff[RIFFsubtype][key][0]["data"])):
                        thisfile_riff["comments"][value][-1] = thisfile_riff[RIFFsubtype][key][0]["data"]
                    # end if
                # end for
                break
            # end if
            if case("8SVX"):
                info["fileformat"] = "8svx"
                info["mime_type"] = "audio/8svx"
                thisfile_audio["bitrate_mode"] = "cbr"
                thisfile_audio_dataformat = "8svx"
                thisfile_audio["bits_per_sample"] = 8
                thisfile_audio["channels"] = 1
                #// overridden below, if need be
                ActualBitsPerSample = 0
                if (php_isset(lambda : thisfile_riff[RIFFsubtype]["BODY"][0]["offset"])):
                    info["avdataoffset"] = thisfile_riff[RIFFsubtype]["BODY"][0]["offset"] + 8
                    info["avdataend"] = info["avdataoffset"] + thisfile_riff[RIFFsubtype]["BODY"][0]["size"]
                    if info["avdataend"] > info["filesize"]:
                        self.warning("Probable truncated AIFF file: expecting " + thisfile_riff[RIFFsubtype]["BODY"][0]["size"] + " bytes of audio data, only " + info["filesize"] - info["avdataoffset"] + " bytes found")
                    # end if
                # end if
                if (php_isset(lambda : thisfile_riff[RIFFsubtype]["VHDR"][0]["offset"])):
                    #// shortcut
                    thisfile_riff_RIFFsubtype_VHDR_0 = thisfile_riff[RIFFsubtype]["VHDR"][0]
                    thisfile_riff_RIFFsubtype_VHDR_0["oneShotHiSamples"] = getid3_lib.bigendian2int(php_substr(thisfile_riff_RIFFsubtype_VHDR_0["data"], 0, 4))
                    thisfile_riff_RIFFsubtype_VHDR_0["repeatHiSamples"] = getid3_lib.bigendian2int(php_substr(thisfile_riff_RIFFsubtype_VHDR_0["data"], 4, 4))
                    thisfile_riff_RIFFsubtype_VHDR_0["samplesPerHiCycle"] = getid3_lib.bigendian2int(php_substr(thisfile_riff_RIFFsubtype_VHDR_0["data"], 8, 4))
                    thisfile_riff_RIFFsubtype_VHDR_0["samplesPerSec"] = getid3_lib.bigendian2int(php_substr(thisfile_riff_RIFFsubtype_VHDR_0["data"], 12, 2))
                    thisfile_riff_RIFFsubtype_VHDR_0["ctOctave"] = getid3_lib.bigendian2int(php_substr(thisfile_riff_RIFFsubtype_VHDR_0["data"], 14, 1))
                    thisfile_riff_RIFFsubtype_VHDR_0["sCompression"] = getid3_lib.bigendian2int(php_substr(thisfile_riff_RIFFsubtype_VHDR_0["data"], 15, 1))
                    thisfile_riff_RIFFsubtype_VHDR_0["Volume"] = getid3_lib.fixedpoint16_16(php_substr(thisfile_riff_RIFFsubtype_VHDR_0["data"], 16, 4))
                    thisfile_audio["sample_rate"] = thisfile_riff_RIFFsubtype_VHDR_0["samplesPerSec"]
                    for case in Switch(thisfile_riff_RIFFsubtype_VHDR_0["sCompression"]):
                        if case(0):
                            thisfile_audio["codec"] = "Pulse Code Modulation (PCM)"
                            thisfile_audio["lossless"] = True
                            ActualBitsPerSample = 8
                            break
                        # end if
                        if case(1):
                            thisfile_audio["codec"] = "Fibonacci-delta encoding"
                            thisfile_audio["lossless"] = False
                            ActualBitsPerSample = 4
                            break
                        # end if
                        if case():
                            self.warning("Unexpected sCompression value in 8SVX.VHDR chunk - expecting 0 or 1, found \"" + thisfile_riff_RIFFsubtype_VHDR_0["sCompression"] + "\"")
                            break
                        # end if
                    # end for
                # end if
                if (php_isset(lambda : thisfile_riff[RIFFsubtype]["CHAN"][0]["data"])):
                    ChannelsIndex = getid3_lib.bigendian2int(php_substr(thisfile_riff[RIFFsubtype]["CHAN"][0]["data"], 0, 4))
                    for case in Switch(ChannelsIndex):
                        if case(6):
                            #// Stereo
                            thisfile_audio["channels"] = 2
                            break
                        # end if
                        if case(2):
                            pass
                        # end if
                        if case(4):
                            #// Right channel only
                            thisfile_audio["channels"] = 1
                            break
                        # end if
                        if case():
                            self.warning("Unexpected value in 8SVX.CHAN chunk - expecting 2 or 4 or 6, found \"" + ChannelsIndex + "\"")
                            break
                        # end if
                    # end for
                # end if
                CommentsChunkNames = Array({"NAME": "title", "author": "artist", "(c) ": "copyright", "ANNO": "comment"})
                for key,value in CommentsChunkNames:
                    if (php_isset(lambda : thisfile_riff[RIFFsubtype][key][0]["data"])):
                        thisfile_riff["comments"][value][-1] = thisfile_riff[RIFFsubtype][key][0]["data"]
                    # end if
                # end for
                thisfile_audio["bitrate"] = thisfile_audio["sample_rate"] * ActualBitsPerSample * thisfile_audio["channels"]
                if (not php_empty(lambda : thisfile_audio["bitrate"])):
                    info["playtime_seconds"] = info["avdataend"] - info["avdataoffset"] / thisfile_audio["bitrate"] / 8
                # end if
                break
            # end if
            if case("CDXA"):
                info["fileformat"] = "vcd"
                #// Asume Video CD
                info["mime_type"] = "video/mpeg"
                if (not php_empty(lambda : thisfile_riff["CDXA"]["data"][0]["size"])):
                    getid3_lib.includedependency(GETID3_INCLUDEPATH + "module.audio-video.mpeg.php", __FILE__, True)
                    getid3_temp = php_new_class("getID3", lambda : getID3())
                    getid3_temp.openfile(self.getid3.filename, None, self.getid3.fp)
                    getid3_mpeg = php_new_class("getid3_mpeg", lambda : getid3_mpeg(getid3_temp))
                    getid3_mpeg.analyze()
                    if php_empty(lambda : getid3_temp.info["error"]):
                        info["audio"] = getid3_temp.info["audio"]
                        info["video"] = getid3_temp.info["video"]
                        info["mpeg"] = getid3_temp.info["mpeg"]
                        info["warning"] = getid3_temp.info["warning"]
                    # end if
                    getid3_temp = None
                    getid3_mpeg = None
                # end if
                break
            # end if
            if case("WEBP"):
                #// https://developers.google.com/speed/webp/docs/riff_container
                #// https://tools.ietf.org/html/rfc6386
                #// https://chromium.googlesource.com/webm/libwebp/+/master/doc/webp-lossless-bitstream-spec.txt
                info["fileformat"] = "webp"
                info["mime_type"] = "image/webp"
                if (not php_empty(lambda : thisfile_riff["WEBP"]["VP8 "][0]["size"])):
                    old_offset = self.ftell()
                    self.fseek(thisfile_riff["WEBP"]["VP8 "][0]["offset"] + 8)
                    #// 4 bytes "VP8 " + 4 bytes chunk size
                    WEBP_VP8_header = self.fread(10)
                    self.fseek(old_offset)
                    if php_substr(WEBP_VP8_header, 3, 3) == "*":
                        thisfile_riff["WEBP"]["VP8 "][0]["keyframe"] = (not getid3_lib.littleendian2int(php_substr(WEBP_VP8_header, 0, 3)) & 8388608)
                        thisfile_riff["WEBP"]["VP8 "][0]["version"] = getid3_lib.littleendian2int(php_substr(WEBP_VP8_header, 0, 3)) & 7340032 >> 20
                        thisfile_riff["WEBP"]["VP8 "][0]["show_frame"] = getid3_lib.littleendian2int(php_substr(WEBP_VP8_header, 0, 3)) & 524288
                        thisfile_riff["WEBP"]["VP8 "][0]["data_bytes"] = getid3_lib.littleendian2int(php_substr(WEBP_VP8_header, 0, 3)) & 524287 >> 0
                        thisfile_riff["WEBP"]["VP8 "][0]["scale_x"] = getid3_lib.littleendian2int(php_substr(WEBP_VP8_header, 6, 2)) & 49152 >> 14
                        thisfile_riff["WEBP"]["VP8 "][0]["width"] = getid3_lib.littleendian2int(php_substr(WEBP_VP8_header, 6, 2)) & 16383
                        thisfile_riff["WEBP"]["VP8 "][0]["scale_y"] = getid3_lib.littleendian2int(php_substr(WEBP_VP8_header, 8, 2)) & 49152 >> 14
                        thisfile_riff["WEBP"]["VP8 "][0]["height"] = getid3_lib.littleendian2int(php_substr(WEBP_VP8_header, 8, 2)) & 16383
                        info["video"]["resolution_x"] = thisfile_riff["WEBP"]["VP8 "][0]["width"]
                        info["video"]["resolution_y"] = thisfile_riff["WEBP"]["VP8 "][0]["height"]
                    else:
                        self.error("Expecting 9D 01 2A at offset " + thisfile_riff["WEBP"]["VP8 "][0]["offset"] + 8 + 3 + ", found \"" + getid3_lib.printhexbytes(php_substr(WEBP_VP8_header, 3, 3)) + "\"")
                    # end if
                # end if
                if (not php_empty(lambda : thisfile_riff["WEBP"]["VP8L"][0]["size"])):
                    old_offset = self.ftell()
                    self.fseek(thisfile_riff["WEBP"]["VP8L"][0]["offset"] + 8)
                    #// 4 bytes "VP8L" + 4 bytes chunk size
                    WEBP_VP8L_header = self.fread(10)
                    self.fseek(old_offset)
                    if php_substr(WEBP_VP8L_header, 0, 1) == "/":
                        width_height_flags = getid3_lib.littleendian2bin(php_substr(WEBP_VP8L_header, 1, 4))
                        thisfile_riff["WEBP"]["VP8L"][0]["width"] = bindec(php_substr(width_height_flags, 18, 14)) + 1
                        thisfile_riff["WEBP"]["VP8L"][0]["height"] = bindec(php_substr(width_height_flags, 4, 14)) + 1
                        thisfile_riff["WEBP"]["VP8L"][0]["alpha_is_used"] = bool(bindec(php_substr(width_height_flags, 3, 1)))
                        thisfile_riff["WEBP"]["VP8L"][0]["version"] = bindec(php_substr(width_height_flags, 0, 3))
                        info["video"]["resolution_x"] = thisfile_riff["WEBP"]["VP8L"][0]["width"]
                        info["video"]["resolution_y"] = thisfile_riff["WEBP"]["VP8L"][0]["height"]
                    else:
                        self.error("Expecting 2F at offset " + thisfile_riff["WEBP"]["VP8L"][0]["offset"] + 8 + ", found \"" + getid3_lib.printhexbytes(php_substr(WEBP_VP8L_header, 0, 1)) + "\"")
                    # end if
                # end if
                break
            # end if
            if case():
                self.error("Unknown RIFF type: expecting one of (WAVE|RMP3|AVI |CDDA|AIFF|AIFC|8SVX|CDXA|WEBP), found \"" + RIFFsubtype + "\" instead")
            # end if
        # end for
        for case in Switch(RIFFsubtype):
            if case("WAVE"):
                pass
            # end if
            if case("AIFF"):
                pass
            # end if
            if case("AIFC"):
                ID3v2_key_good = "id3 "
                ID3v2_keys_bad = Array("ID3 ", "tag ")
                for ID3v2_key_bad in ID3v2_keys_bad:
                    if (php_isset(lambda : thisfile_riff[RIFFsubtype][ID3v2_key_bad])) and (not php_array_key_exists(ID3v2_key_good, thisfile_riff[RIFFsubtype])):
                        thisfile_riff[RIFFsubtype][ID3v2_key_good] = thisfile_riff[RIFFsubtype][ID3v2_key_bad]
                        self.warning("mapping \"" + ID3v2_key_bad + "\" chunk to \"" + ID3v2_key_good + "\"")
                    # end if
                # end for
                if (php_isset(lambda : thisfile_riff[RIFFsubtype]["id3 "])):
                    getid3_lib.includedependency(GETID3_INCLUDEPATH + "module.tag.id3v2.php", __FILE__, True)
                    getid3_temp = php_new_class("getID3", lambda : getID3())
                    getid3_temp.openfile(self.getid3.filename, None, self.getid3.fp)
                    getid3_id3v2 = php_new_class("getid3_id3v2", lambda : getid3_id3v2(getid3_temp))
                    getid3_id3v2.StartingOffset = thisfile_riff[RIFFsubtype]["id3 "][0]["offset"] + 8
                    thisfile_riff[RIFFsubtype]["id3 "][0]["valid"] = getid3_id3v2.analyze()
                    if thisfile_riff[RIFFsubtype]["id3 "][0]["valid"]:
                        info["id3v2"] = getid3_temp.info["id3v2"]
                    # end if
                    getid3_temp = None
                    getid3_id3v2 = None
                # end if
                break
            # end if
        # end for
        if (php_isset(lambda : thisfile_riff_WAVE["DISP"])) and php_is_array(thisfile_riff_WAVE["DISP"]):
            thisfile_riff["comments"]["title"][-1] = php_trim(php_substr(thisfile_riff_WAVE["DISP"][php_count(thisfile_riff_WAVE["DISP"]) - 1]["data"], 4))
        # end if
        if (php_isset(lambda : thisfile_riff_WAVE["INFO"])) and php_is_array(thisfile_riff_WAVE["INFO"]):
            self.parsecomments(thisfile_riff_WAVE["INFO"], thisfile_riff["comments"])
        # end if
        if (php_isset(lambda : thisfile_riff["AVI "]["INFO"])) and php_is_array(thisfile_riff["AVI "]["INFO"]):
            self.parsecomments(thisfile_riff["AVI "]["INFO"], thisfile_riff["comments"])
        # end if
        if php_empty(lambda : thisfile_audio["encoder"]) and (not php_empty(lambda : info["mpeg"]["audio"]["LAME"]["short_version"])):
            thisfile_audio["encoder"] = info["mpeg"]["audio"]["LAME"]["short_version"]
        # end if
        if (not (php_isset(lambda : info["playtime_seconds"]))):
            info["playtime_seconds"] = 0
        # end if
        if (php_isset(lambda : thisfile_riff_raw["strh"][0]["dwLength"])) and (php_isset(lambda : thisfile_riff_raw["avih"]["dwMicroSecPerFrame"])):
            #// needed for >2GB AVIs where 'avih' chunk only lists number of frames in that chunk, not entire movie
            info["playtime_seconds"] = thisfile_riff_raw["strh"][0]["dwLength"] * thisfile_riff_raw["avih"]["dwMicroSecPerFrame"] / 1000000
        elif (php_isset(lambda : thisfile_riff_raw["avih"]["dwTotalFrames"])) and (php_isset(lambda : thisfile_riff_raw["avih"]["dwMicroSecPerFrame"])):
            info["playtime_seconds"] = thisfile_riff_raw["avih"]["dwTotalFrames"] * thisfile_riff_raw["avih"]["dwMicroSecPerFrame"] / 1000000
        # end if
        if info["playtime_seconds"] > 0:
            if (php_isset(lambda : thisfile_riff_audio)) and (php_isset(lambda : thisfile_riff_video)):
                if (not (php_isset(lambda : info["bitrate"]))):
                    info["bitrate"] = info["avdataend"] - info["avdataoffset"] / info["playtime_seconds"] * 8
                # end if
            elif (php_isset(lambda : thisfile_riff_audio)) and (not (php_isset(lambda : thisfile_riff_video))):
                if (not (php_isset(lambda : thisfile_audio["bitrate"]))):
                    thisfile_audio["bitrate"] = info["avdataend"] - info["avdataoffset"] / info["playtime_seconds"] * 8
                # end if
            elif (not (php_isset(lambda : thisfile_riff_audio))) and (php_isset(lambda : thisfile_riff_video)):
                if (not (php_isset(lambda : thisfile_video["bitrate"]))):
                    thisfile_video["bitrate"] = info["avdataend"] - info["avdataoffset"] / info["playtime_seconds"] * 8
                # end if
            # end if
        # end if
        if (php_isset(lambda : thisfile_riff_video)) and (php_isset(lambda : thisfile_audio["bitrate"])) and thisfile_audio["bitrate"] > 0 and info["playtime_seconds"] > 0:
            info["bitrate"] = info["avdataend"] - info["avdataoffset"] / info["playtime_seconds"] * 8
            thisfile_audio["bitrate"] = 0
            thisfile_video["bitrate"] = info["bitrate"]
            for channelnumber,audioinfoarray in thisfile_riff_audio:
                thisfile_video["bitrate"] -= audioinfoarray["bitrate"]
                thisfile_audio["bitrate"] += audioinfoarray["bitrate"]
            # end for
            if thisfile_video["bitrate"] <= 0:
                thisfile_video["bitrate"] = None
            # end if
            if thisfile_audio["bitrate"] <= 0:
                thisfile_audio["bitrate"] = None
            # end if
        # end if
        if (php_isset(lambda : info["mpeg"]["audio"])):
            thisfile_audio_dataformat = "mp" + info["mpeg"]["audio"]["layer"]
            thisfile_audio["sample_rate"] = info["mpeg"]["audio"]["sample_rate"]
            thisfile_audio["channels"] = info["mpeg"]["audio"]["channels"]
            thisfile_audio["bitrate"] = info["mpeg"]["audio"]["bitrate"]
            thisfile_audio["bitrate_mode"] = php_strtolower(info["mpeg"]["audio"]["bitrate_mode"])
            if (not php_empty(lambda : info["mpeg"]["audio"]["codec"])):
                thisfile_audio["codec"] = info["mpeg"]["audio"]["codec"] + " " + thisfile_audio["codec"]
            # end if
            if (not php_empty(lambda : thisfile_audio["streams"])):
                for streamnumber,streamdata in thisfile_audio["streams"]:
                    if streamdata["dataformat"] == thisfile_audio_dataformat:
                        thisfile_audio["streams"][streamnumber]["sample_rate"] = thisfile_audio["sample_rate"]
                        thisfile_audio["streams"][streamnumber]["channels"] = thisfile_audio["channels"]
                        thisfile_audio["streams"][streamnumber]["bitrate"] = thisfile_audio["bitrate"]
                        thisfile_audio["streams"][streamnumber]["bitrate_mode"] = thisfile_audio["bitrate_mode"]
                        thisfile_audio["streams"][streamnumber]["codec"] = thisfile_audio["codec"]
                    # end if
                # end for
            # end if
            getid3_mp3 = php_new_class("getid3_mp3", lambda : getid3_mp3(self.getid3))
            thisfile_audio["encoder_options"] = getid3_mp3.guessencoderoptions()
            getid3_mp3 = None
        # end if
        if (not php_empty(lambda : thisfile_riff_raw["fmt "]["wBitsPerSample"])) and thisfile_riff_raw["fmt "]["wBitsPerSample"] > 0:
            for case in Switch(thisfile_audio_dataformat):
                if case("ac3"):
                    break
                # end if
                if case():
                    thisfile_audio["bits_per_sample"] = thisfile_riff_raw["fmt "]["wBitsPerSample"]
                    break
                # end if
            # end for
        # end if
        if php_empty(lambda : thisfile_riff_raw):
            thisfile_riff["raw"] = None
        # end if
        if php_empty(lambda : thisfile_riff_audio):
            thisfile_riff["audio"] = None
        # end if
        if php_empty(lambda : thisfile_riff_video):
            thisfile_riff["video"] = None
        # end if
        return True
    # end def analyze
    #// 
    #// @param int $startoffset
    #// @param int $maxoffset
    #// 
    #// @return array|false
    #// 
    #// @throws Exception
    #// @throws getid3_exception
    #//
    def parseriffamv(self, startoffset=None, maxoffset=None):
        
        #// AMV files are RIFF-AVI files with parts of the spec deliberately broken, such as chunk size fields hardcoded to zero (because players known in hardware that these fields are always a certain size
        #// https://code.google.com/p/amv-codec-tools/wiki/AmvDocumentation
        #// typedef struct _amvmainheader {
        #// FOURCC fcc; // 'amvh'
        #// DWORD cb;
        #// DWORD dwMicroSecPerFrame;
        #// BYTE reserve[28];
        #// DWORD dwWidth;
        #// DWORD dwHeight;
        #// DWORD dwSpeed;
        #// DWORD reserve0;
        #// DWORD reserve1;
        #// BYTE bTimeSec;
        #// BYTE bTimeMin;
        #// WORD wTimeHour;
        #// } AMVMAINHEADER;
        info = self.getid3.info
        RIFFchunk = False
        try: 
            self.fseek(startoffset)
            maxoffset = php_min(maxoffset, info["avdataend"])
            AMVheader = self.fread(284)
            if php_substr(AMVheader, 0, 8) != "hdrlamvh":
                raise php_new_class("Exception", lambda : Exception("expecting \"hdrlamv\" at offset " + startoffset + 0 + ", found \"" + php_substr(AMVheader, 0, 8) + "\""))
            # end if
            if php_substr(AMVheader, 8, 4) != "8   ":
                raise php_new_class("Exception", lambda : Exception("expecting \"0x38000000\" at offset " + startoffset + 8 + ", found \"" + getid3_lib.printhexbytes(php_substr(AMVheader, 8, 4)) + "\""))
            # end if
            RIFFchunk = Array()
            RIFFchunk["amvh"]["us_per_frame"] = getid3_lib.littleendian2int(php_substr(AMVheader, 12, 4))
            RIFFchunk["amvh"]["reserved28"] = php_substr(AMVheader, 16, 28)
            #// null? reserved?
            RIFFchunk["amvh"]["resolution_x"] = getid3_lib.littleendian2int(php_substr(AMVheader, 44, 4))
            RIFFchunk["amvh"]["resolution_y"] = getid3_lib.littleendian2int(php_substr(AMVheader, 48, 4))
            RIFFchunk["amvh"]["frame_rate_int"] = getid3_lib.littleendian2int(php_substr(AMVheader, 52, 4))
            RIFFchunk["amvh"]["reserved0"] = getid3_lib.littleendian2int(php_substr(AMVheader, 56, 4))
            #// 1? reserved?
            RIFFchunk["amvh"]["reserved1"] = getid3_lib.littleendian2int(php_substr(AMVheader, 60, 4))
            #// 0? reserved?
            RIFFchunk["amvh"]["runtime_sec"] = getid3_lib.littleendian2int(php_substr(AMVheader, 64, 1))
            RIFFchunk["amvh"]["runtime_min"] = getid3_lib.littleendian2int(php_substr(AMVheader, 65, 1))
            RIFFchunk["amvh"]["runtime_hrs"] = getid3_lib.littleendian2int(php_substr(AMVheader, 66, 2))
            info["video"]["frame_rate"] = 1000000 / RIFFchunk["amvh"]["us_per_frame"]
            info["video"]["resolution_x"] = RIFFchunk["amvh"]["resolution_x"]
            info["video"]["resolution_y"] = RIFFchunk["amvh"]["resolution_y"]
            info["playtime_seconds"] = RIFFchunk["amvh"]["runtime_hrs"] * 3600 + RIFFchunk["amvh"]["runtime_min"] * 60 + RIFFchunk["amvh"]["runtime_sec"]
            #// the rest is all hardcoded(?) and does not appear to be useful until you get to audio info at offset 256, even then everything is probably hardcoded
            if php_substr(AMVheader, 68, 20) != "LIST" + "    " + "strlstrh" + "8   ":
                raise php_new_class("Exception", lambda : Exception("expecting \"LIST<0x00000000>strlstrh<0x38000000>\" at offset " + startoffset + 68 + ", found \"" + getid3_lib.printhexbytes(php_substr(AMVheader, 68, 20)) + "\""))
            # end if
            #// followed by 56 bytes of null: substr($AMVheader,  88, 56) -> 144
            if php_substr(AMVheader, 144, 8) != "strf" + "$   ":
                raise php_new_class("Exception", lambda : Exception("expecting \"strf<0x24000000>\" at offset " + startoffset + 144 + ", found \"" + getid3_lib.printhexbytes(php_substr(AMVheader, 144, 8)) + "\""))
            # end if
            #// followed by 36 bytes of null: substr($AMVheader, 144, 36) -> 180
            if php_substr(AMVheader, 188, 20) != "LIST" + "    " + "strlstrh" + "0   ":
                raise php_new_class("Exception", lambda : Exception("expecting \"LIST<0x00000000>strlstrh<0x30000000>\" at offset " + startoffset + 188 + ", found \"" + getid3_lib.printhexbytes(php_substr(AMVheader, 188, 20)) + "\""))
            # end if
            #// followed by 48 bytes of null: substr($AMVheader, 208, 48) -> 256
            if php_substr(AMVheader, 256, 8) != "strf" + "   ":
                raise php_new_class("Exception", lambda : Exception("expecting \"strf<0x14000000>\" at offset " + startoffset + 256 + ", found \"" + getid3_lib.printhexbytes(php_substr(AMVheader, 256, 8)) + "\""))
            # end if
            #// followed by 20 bytes of a modified WAVEFORMATEX:
            #// typedef struct {
            #// WORD wFormatTag;       //(Fixme: this is equal to PCM's 0x01 format code)
            #// WORD nChannels;        //(Fixme: this is always 1)
            #// DWORD nSamplesPerSec;  //(Fixme: for all known sample files this is equal to 22050)
            #// DWORD nAvgBytesPerSec; //(Fixme: for all known sample files this is equal to 44100)
            #// WORD nBlockAlign;      //(Fixme: this seems to be 2 in AMV files, is this correct ?)
            #// WORD wBitsPerSample;   //(Fixme: this seems to be 16 in AMV files instead of the expected 4)
            #// WORD cbSize;           //(Fixme: this seems to be 0 in AMV files)
            #// WORD reserved;
            #// } WAVEFORMATEX;
            RIFFchunk["strf"]["wformattag"] = getid3_lib.littleendian2int(php_substr(AMVheader, 264, 2))
            RIFFchunk["strf"]["nchannels"] = getid3_lib.littleendian2int(php_substr(AMVheader, 266, 2))
            RIFFchunk["strf"]["nsamplespersec"] = getid3_lib.littleendian2int(php_substr(AMVheader, 268, 4))
            RIFFchunk["strf"]["navgbytespersec"] = getid3_lib.littleendian2int(php_substr(AMVheader, 272, 4))
            RIFFchunk["strf"]["nblockalign"] = getid3_lib.littleendian2int(php_substr(AMVheader, 276, 2))
            RIFFchunk["strf"]["wbitspersample"] = getid3_lib.littleendian2int(php_substr(AMVheader, 278, 2))
            RIFFchunk["strf"]["cbsize"] = getid3_lib.littleendian2int(php_substr(AMVheader, 280, 2))
            RIFFchunk["strf"]["reserved"] = getid3_lib.littleendian2int(php_substr(AMVheader, 282, 2))
            info["audio"]["lossless"] = False
            info["audio"]["sample_rate"] = RIFFchunk["strf"]["nsamplespersec"]
            info["audio"]["channels"] = RIFFchunk["strf"]["nchannels"]
            info["audio"]["bits_per_sample"] = RIFFchunk["strf"]["wbitspersample"]
            info["audio"]["bitrate"] = info["audio"]["sample_rate"] * info["audio"]["channels"] * info["audio"]["bits_per_sample"]
            info["audio"]["bitrate_mode"] = "cbr"
        except getid3_exception as e:
            if e.getcode() == 10:
                self.warning("RIFFAMV parser: " + e.getmessage())
            else:
                raise e
            # end if
        # end try
        return RIFFchunk
    # end def parseriffamv
    #// 
    #// @param int $startoffset
    #// @param int $maxoffset
    #// 
    #// @return array|false
    #// @throws getid3_exception
    #//
    def parseriff(self, startoffset=None, maxoffset=None):
        
        info = self.getid3.info
        RIFFchunk = False
        FoundAllChunksWeNeed = False
        try: 
            self.fseek(startoffset)
            maxoffset = php_min(maxoffset, info["avdataend"])
            while True:
                
                if not (self.ftell() < maxoffset):
                    break
                # end if
                chunknamesize = self.fread(8)
                #// $chunkname =                          substr($chunknamesize, 0, 4);
                chunkname = php_str_replace(" ", "_", php_substr(chunknamesize, 0, 4))
                #// note: chunk names of 4 null bytes do appear to be legal (has been observed inside INFO and PRMI chunks, for example), but makes traversing array keys more difficult
                chunksize = self.eitherendian2int(php_substr(chunknamesize, 4, 4))
                #// if (strlen(trim($chunkname, "\x00")) < 4) {
                if php_strlen(chunkname) < 4:
                    self.error("Expecting chunk name at offset " + self.ftell() - 8 + " but found nothing. Aborting RIFF parsing.")
                    break
                # end if
                if chunksize == 0 and chunkname != "JUNK":
                    self.warning("Chunk (" + chunkname + ") size at offset " + self.ftell() - 4 + " is zero. Aborting RIFF parsing.")
                    break
                # end if
                if chunksize % 2 != 0:
                    #// all structures are packed on word boundaries
                    chunksize += 1
                # end if
                for case in Switch(chunkname):
                    if case("LIST"):
                        listname = self.fread(4)
                        if php_preg_match("#^(movi|rec )$#i", listname):
                            RIFFchunk[listname]["offset"] = self.ftell() - 4
                            RIFFchunk[listname]["size"] = chunksize
                            if (not FoundAllChunksWeNeed):
                                WhereWeWere = self.ftell()
                                AudioChunkHeader = self.fread(12)
                                AudioChunkStreamNum = php_substr(AudioChunkHeader, 0, 2)
                                AudioChunkStreamType = php_substr(AudioChunkHeader, 2, 2)
                                AudioChunkSize = getid3_lib.littleendian2int(php_substr(AudioChunkHeader, 4, 4))
                                if AudioChunkStreamType == "wb":
                                    FirstFourBytes = php_substr(AudioChunkHeader, 8, 4)
                                    if php_preg_match("/^\\xFF[\\xE2-\\xE7\\xF2-\\xF7\\xFA-\\xFF][\\x00-\\xEB]/s", FirstFourBytes):
                                        #// MP3
                                        if getid3_mp3.mpegaudioheaderbytesvalid(FirstFourBytes):
                                            getid3_temp = php_new_class("getID3", lambda : getID3())
                                            getid3_temp.openfile(self.getid3.filename, None, self.getid3.fp)
                                            getid3_temp.info["avdataoffset"] = self.ftell() - 4
                                            getid3_temp.info["avdataend"] = self.ftell() + AudioChunkSize
                                            getid3_mp3 = php_new_class("getid3_mp3", lambda : getid3_mp3(getid3_temp, __CLASS__))
                                            getid3_mp3.getonlympegaudioinfo(getid3_temp.info["avdataoffset"], False)
                                            if (php_isset(lambda : getid3_temp.info["mpeg"]["audio"])):
                                                info["mpeg"]["audio"] = getid3_temp.info["mpeg"]["audio"]
                                                info["audio"] = getid3_temp.info["audio"]
                                                info["audio"]["dataformat"] = "mp" + info["mpeg"]["audio"]["layer"]
                                                info["audio"]["sample_rate"] = info["mpeg"]["audio"]["sample_rate"]
                                                info["audio"]["channels"] = info["mpeg"]["audio"]["channels"]
                                                info["audio"]["bitrate"] = info["mpeg"]["audio"]["bitrate"]
                                                info["audio"]["bitrate_mode"] = php_strtolower(info["mpeg"]["audio"]["bitrate_mode"])
                                                pass
                                            # end if
                                            getid3_temp = None
                                            getid3_mp3 = None
                                        # end if
                                    elif php_strpos(FirstFourBytes, getid3_ac3.syncword) == 0:
                                        #// AC3
                                        getid3_temp = php_new_class("getID3", lambda : getID3())
                                        getid3_temp.openfile(self.getid3.filename, None, self.getid3.fp)
                                        getid3_temp.info["avdataoffset"] = self.ftell() - 4
                                        getid3_temp.info["avdataend"] = self.ftell() + AudioChunkSize
                                        getid3_ac3 = php_new_class("getid3_ac3", lambda : getid3_ac3(getid3_temp))
                                        getid3_ac3.analyze()
                                        if php_empty(lambda : getid3_temp.info["error"]):
                                            info["audio"] = getid3_temp.info["audio"]
                                            info["ac3"] = getid3_temp.info["ac3"]
                                            if (not php_empty(lambda : getid3_temp.info["warning"])):
                                                for key,value in getid3_temp.info["warning"]:
                                                    self.warning(value)
                                                # end for
                                            # end if
                                        # end if
                                        getid3_temp = None
                                        getid3_ac3 = None
                                    # end if
                                # end if
                                FoundAllChunksWeNeed = True
                                self.fseek(WhereWeWere)
                            # end if
                            self.fseek(chunksize - 4, SEEK_CUR)
                        else:
                            if (not (php_isset(lambda : RIFFchunk[listname]))):
                                RIFFchunk[listname] = Array()
                            # end if
                            LISTchunkParent = listname
                            LISTchunkMaxOffset = self.ftell() - 4 + chunksize
                            parsedChunk = self.parseriff(self.ftell(), LISTchunkMaxOffset)
                            if parsedChunk:
                                RIFFchunk[listname] = php_array_merge_recursive(RIFFchunk[listname], parsedChunk)
                            # end if
                        # end if
                        break
                    # end if
                    if case():
                        if php_preg_match("#^[0-9]{2}(wb|pc|dc|db)$#", chunkname):
                            self.fseek(chunksize, SEEK_CUR)
                            break
                        # end if
                        thisindex = 0
                        if (php_isset(lambda : RIFFchunk[chunkname])) and php_is_array(RIFFchunk[chunkname]):
                            thisindex = php_count(RIFFchunk[chunkname])
                        # end if
                        RIFFchunk[chunkname][thisindex]["offset"] = self.ftell() - 8
                        RIFFchunk[chunkname][thisindex]["size"] = chunksize
                        for case in Switch(chunkname):
                            if case("data"):
                                info["avdataoffset"] = self.ftell()
                                info["avdataend"] = info["avdataoffset"] + chunksize
                                testData = self.fread(36)
                                if testData == "":
                                    break
                                # end if
                                if php_preg_match("/^\\xFF[\\xE2-\\xE7\\xF2-\\xF7\\xFA-\\xFF][\\x00-\\xEB]/s", php_substr(testData, 0, 4)):
                                    #// Probably is MP3 data
                                    if getid3_mp3.mpegaudioheaderbytesvalid(php_substr(testData, 0, 4)):
                                        getid3_temp = php_new_class("getID3", lambda : getID3())
                                        getid3_temp.openfile(self.getid3.filename, None, self.getid3.fp)
                                        getid3_temp.info["avdataoffset"] = info["avdataoffset"]
                                        getid3_temp.info["avdataend"] = info["avdataend"]
                                        getid3_mp3 = php_new_class("getid3_mp3", lambda : getid3_mp3(getid3_temp, __CLASS__))
                                        getid3_mp3.getonlympegaudioinfo(info["avdataoffset"], False)
                                        if php_empty(lambda : getid3_temp.info["error"]):
                                            info["audio"] = getid3_temp.info["audio"]
                                            info["mpeg"] = getid3_temp.info["mpeg"]
                                        # end if
                                        getid3_temp = None
                                        getid3_mp3 = None
                                    # end if
                                elif php_substr(testData, 0, 2) == getid3_ac3.syncword or php_substr(testData, 8, 2) == php_strrev(getid3_ac3.syncword):
                                    isRegularAC3 = php_substr(testData, 0, 2) == getid3_ac3.syncword
                                    #// This is probably AC-3 data
                                    getid3_temp = php_new_class("getID3", lambda : getID3())
                                    if isRegularAC3:
                                        getid3_temp.openfile(self.getid3.filename, None, self.getid3.fp)
                                        getid3_temp.info["avdataoffset"] = info["avdataoffset"]
                                        getid3_temp.info["avdataend"] = info["avdataend"]
                                    # end if
                                    getid3_ac3 = php_new_class("getid3_ac3", lambda : getid3_ac3(getid3_temp))
                                    if isRegularAC3:
                                        getid3_ac3.analyze()
                                    else:
                                        #// Dolby Digital WAV
                                        #// AC-3 content, but not encoded in same format as normal AC-3 file
                                        #// For one thing, byte order is swapped
                                        ac3_data = ""
                                        i = 0
                                        while i < 28:
                                            
                                            ac3_data += php_substr(testData, 8 + i + 1, 1)
                                            ac3_data += php_substr(testData, 8 + i + 0, 1)
                                            i += 2
                                        # end while
                                        getid3_ac3.analyzestring(ac3_data)
                                    # end if
                                    if php_empty(lambda : getid3_temp.info["error"]):
                                        info["audio"] = getid3_temp.info["audio"]
                                        info["ac3"] = getid3_temp.info["ac3"]
                                        if (not php_empty(lambda : getid3_temp.info["warning"])):
                                            for newerror in getid3_temp.info["warning"]:
                                                self.warning("getid3_ac3() says: [" + newerror + "]")
                                            # end for
                                        # end if
                                    # end if
                                    getid3_temp = None
                                    getid3_ac3 = None
                                elif php_preg_match("/^(" + php_implode("|", php_array_map("preg_quote", getid3_dts.syncwords)) + ")/", testData):
                                    #// This is probably DTS data
                                    getid3_temp = php_new_class("getID3", lambda : getID3())
                                    getid3_temp.openfile(self.getid3.filename, None, self.getid3.fp)
                                    getid3_temp.info["avdataoffset"] = info["avdataoffset"]
                                    getid3_dts = php_new_class("getid3_dts", lambda : getid3_dts(getid3_temp))
                                    getid3_dts.analyze()
                                    if php_empty(lambda : getid3_temp.info["error"]):
                                        info["audio"] = getid3_temp.info["audio"]
                                        info["dts"] = getid3_temp.info["dts"]
                                        info["playtime_seconds"] = getid3_temp.info["playtime_seconds"]
                                        #// may not match RIFF calculations since DTS-WAV often used 14/16 bit-word packing
                                        if (not php_empty(lambda : getid3_temp.info["warning"])):
                                            for newerror in getid3_temp.info["warning"]:
                                                self.warning("getid3_dts() says: [" + newerror + "]")
                                            # end for
                                        # end if
                                    # end if
                                    getid3_temp = None
                                    getid3_dts = None
                                elif php_substr(testData, 0, 4) == "wvpk":
                                    #// This is WavPack data
                                    info["wavpack"]["offset"] = info["avdataoffset"]
                                    info["wavpack"]["size"] = getid3_lib.littleendian2int(php_substr(testData, 4, 4))
                                    self.parsewavpackheader(php_substr(testData, 8, 28))
                                else:
                                    pass
                                # end if
                                nextoffset = info["avdataend"]
                                self.fseek(nextoffset)
                                break
                            # end if
                            if case("iXML"):
                                pass
                            # end if
                            if case("bext"):
                                pass
                            # end if
                            if case("cart"):
                                pass
                            # end if
                            if case("fmt "):
                                pass
                            # end if
                            if case("strh"):
                                pass
                            # end if
                            if case("strf"):
                                pass
                            # end if
                            if case("indx"):
                                pass
                            # end if
                            if case("MEXT"):
                                pass
                            # end if
                            if case("DISP"):
                                pass
                            # end if
                            if case("JUNK"):
                                #// should be: never read data in
                                #// but some programs write their version strings in a JUNK chunk (e.g. VirtualDub, AVIdemux, etc)
                                if chunksize < 1048576:
                                    if chunksize > 0:
                                        RIFFchunk[chunkname][thisindex]["data"] = self.fread(chunksize)
                                        if chunkname == "JUNK":
                                            if php_preg_match("#^([\\x20-\\x7F]+)#", RIFFchunk[chunkname][thisindex]["data"], matches):
                                                #// only keep text characters [chr(32)-chr(127)]
                                                info["riff"]["comments"]["junk"][-1] = php_trim(matches[1])
                                            # end if
                                            RIFFchunk[chunkname][thisindex]["data"] = None
                                        # end if
                                    # end if
                                else:
                                    self.warning("Chunk \"" + chunkname + "\" at offset " + self.ftell() + " is unexpectedly larger than 1MB (claims to be " + number_format(chunksize) + " bytes), skipping data")
                                    self.fseek(chunksize, SEEK_CUR)
                                # end if
                                break
                            # end if
                            if case("scot"):
                                #// https://cmsdk.com/node-js/adding-scot-chunk-to-wav-file.html
                                RIFFchunk[chunkname][thisindex]["data"] = self.fread(chunksize)
                                RIFFchunk[chunkname][thisindex]["parsed"]["alter"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 0, 1)
                                RIFFchunk[chunkname][thisindex]["parsed"]["attrib"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 1, 1)
                                RIFFchunk[chunkname][thisindex]["parsed"]["artnum"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 2, 2))
                                RIFFchunk[chunkname][thisindex]["parsed"]["title"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 4, 43)
                                #// "name" in other documentation
                                RIFFchunk[chunkname][thisindex]["parsed"]["copy"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 47, 4)
                                RIFFchunk[chunkname][thisindex]["parsed"]["padd"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 51, 1)
                                RIFFchunk[chunkname][thisindex]["parsed"]["asclen"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 52, 5)
                                RIFFchunk[chunkname][thisindex]["parsed"]["startseconds"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 57, 2))
                                RIFFchunk[chunkname][thisindex]["parsed"]["starthundredths"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 59, 2))
                                RIFFchunk[chunkname][thisindex]["parsed"]["endseconds"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 61, 2))
                                RIFFchunk[chunkname][thisindex]["parsed"]["endhundreths"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 63, 2))
                                RIFFchunk[chunkname][thisindex]["parsed"]["sdate"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 65, 6)
                                RIFFchunk[chunkname][thisindex]["parsed"]["kdate"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 71, 6)
                                RIFFchunk[chunkname][thisindex]["parsed"]["start_hr"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 77, 1)
                                RIFFchunk[chunkname][thisindex]["parsed"]["kill_hr"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 78, 1)
                                RIFFchunk[chunkname][thisindex]["parsed"]["digital"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 79, 1)
                                RIFFchunk[chunkname][thisindex]["parsed"]["sample_rate"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 80, 2))
                                RIFFchunk[chunkname][thisindex]["parsed"]["stereo"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 82, 1)
                                RIFFchunk[chunkname][thisindex]["parsed"]["compress"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 83, 1)
                                RIFFchunk[chunkname][thisindex]["parsed"]["eomstrt"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 84, 4))
                                RIFFchunk[chunkname][thisindex]["parsed"]["eomlen"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 88, 2))
                                RIFFchunk[chunkname][thisindex]["parsed"]["attrib2"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 90, 4))
                                RIFFchunk[chunkname][thisindex]["parsed"]["future1"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 94, 12)
                                RIFFchunk[chunkname][thisindex]["parsed"]["catfontcolor"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 106, 4))
                                RIFFchunk[chunkname][thisindex]["parsed"]["catcolor"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 110, 4))
                                RIFFchunk[chunkname][thisindex]["parsed"]["segeompos"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 114, 4))
                                RIFFchunk[chunkname][thisindex]["parsed"]["vt_startsecs"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 118, 2))
                                RIFFchunk[chunkname][thisindex]["parsed"]["vt_starthunds"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 120, 2))
                                RIFFchunk[chunkname][thisindex]["parsed"]["priorcat"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 122, 3)
                                RIFFchunk[chunkname][thisindex]["parsed"]["priorcopy"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 125, 4)
                                RIFFchunk[chunkname][thisindex]["parsed"]["priorpadd"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 129, 1)
                                RIFFchunk[chunkname][thisindex]["parsed"]["postcat"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 130, 3)
                                RIFFchunk[chunkname][thisindex]["parsed"]["postcopy"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 133, 4)
                                RIFFchunk[chunkname][thisindex]["parsed"]["postpadd"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 137, 1)
                                RIFFchunk[chunkname][thisindex]["parsed"]["hrcanplay"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 138, 21)
                                RIFFchunk[chunkname][thisindex]["parsed"]["future2"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 159, 108)
                                RIFFchunk[chunkname][thisindex]["parsed"]["artist"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 267, 34)
                                RIFFchunk[chunkname][thisindex]["parsed"]["comment"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 301, 34)
                                #// "trivia" in other documentation
                                RIFFchunk[chunkname][thisindex]["parsed"]["intro"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 335, 2)
                                RIFFchunk[chunkname][thisindex]["parsed"]["end"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 337, 1)
                                RIFFchunk[chunkname][thisindex]["parsed"]["year"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 338, 4)
                                RIFFchunk[chunkname][thisindex]["parsed"]["obsolete2"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 342, 1)
                                RIFFchunk[chunkname][thisindex]["parsed"]["rec_hr"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 343, 1)
                                RIFFchunk[chunkname][thisindex]["parsed"]["rdate"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 344, 6)
                                RIFFchunk[chunkname][thisindex]["parsed"]["mpeg_bitrate"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 350, 2))
                                RIFFchunk[chunkname][thisindex]["parsed"]["pitch"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 352, 2))
                                RIFFchunk[chunkname][thisindex]["parsed"]["playlevel"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 354, 2))
                                RIFFchunk[chunkname][thisindex]["parsed"]["lenvalid"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 356, 1)
                                RIFFchunk[chunkname][thisindex]["parsed"]["filelength"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 357, 4))
                                RIFFchunk[chunkname][thisindex]["parsed"]["newplaylevel"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 361, 2))
                                RIFFchunk[chunkname][thisindex]["parsed"]["chopsize"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 363, 4))
                                RIFFchunk[chunkname][thisindex]["parsed"]["vteomovr"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 367, 4))
                                RIFFchunk[chunkname][thisindex]["parsed"]["desiredlen"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 371, 4))
                                RIFFchunk[chunkname][thisindex]["parsed"]["triggers"] = getid3_lib.littleendian2int(php_substr(RIFFchunk[chunkname][thisindex]["data"], 375, 4))
                                RIFFchunk[chunkname][thisindex]["parsed"]["fillout"] = php_substr(RIFFchunk[chunkname][thisindex]["data"], 379, 33)
                                for key in Array("title", "artist", "comment"):
                                    if php_trim(RIFFchunk[chunkname][thisindex]["parsed"][key]):
                                        info["riff"]["comments"][key] = Array(RIFFchunk[chunkname][thisindex]["parsed"][key])
                                    # end if
                                # end for
                                if RIFFchunk[chunkname][thisindex]["parsed"]["filelength"] and (not php_empty(lambda : info["filesize"])) and RIFFchunk[chunkname][thisindex]["parsed"]["filelength"] != info["filesize"]:
                                    self.warning("RIFF.WAVE.scot.filelength (" + RIFFchunk[chunkname][thisindex]["parsed"]["filelength"] + ") different from actual filesize (" + info["filesize"] + ")")
                                # end if
                                break
                            # end if
                            if case():
                                if (not php_empty(lambda : LISTchunkParent)) and (php_isset(lambda : LISTchunkMaxOffset)) and RIFFchunk[chunkname][thisindex]["offset"] + RIFFchunk[chunkname][thisindex]["size"] <= LISTchunkMaxOffset:
                                    RIFFchunk[LISTchunkParent][chunkname][thisindex]["offset"] = RIFFchunk[chunkname][thisindex]["offset"]
                                    RIFFchunk[LISTchunkParent][chunkname][thisindex]["size"] = RIFFchunk[chunkname][thisindex]["size"]
                                    RIFFchunk[chunkname][thisindex]["offset"] = None
                                    RIFFchunk[chunkname][thisindex]["size"] = None
                                    if (php_isset(lambda : RIFFchunk[chunkname][thisindex])) and php_empty(lambda : RIFFchunk[chunkname][thisindex]):
                                        RIFFchunk[chunkname][thisindex] = None
                                    # end if
                                    if (php_isset(lambda : RIFFchunk[chunkname])) and php_empty(lambda : RIFFchunk[chunkname]):
                                        RIFFchunk[chunkname] = None
                                    # end if
                                    RIFFchunk[LISTchunkParent][chunkname][thisindex]["data"] = self.fread(chunksize)
                                elif chunksize < 2048:
                                    #// only read data in if smaller than 2kB
                                    RIFFchunk[chunkname][thisindex]["data"] = self.fread(chunksize)
                                else:
                                    self.fseek(chunksize, SEEK_CUR)
                                # end if
                                break
                            # end if
                        # end for
                        break
                    # end if
                # end for
            # end while
        except getid3_exception as e:
            if e.getcode() == 10:
                self.warning("RIFF parser: " + e.getmessage())
            else:
                raise e
            # end if
        # end try
        return RIFFchunk
    # end def parseriff
    #// 
    #// @param string $RIFFdata
    #// 
    #// @return bool
    #//
    def parseriffdata(self, RIFFdata=None):
        
        info = self.getid3.info
        if RIFFdata:
            tempfile = php_tempnam(GETID3_TEMP_DIR, "getID3")
            fp_temp = fopen(tempfile, "wb")
            RIFFdataLength = php_strlen(RIFFdata)
            NewLengthString = getid3_lib.littleendian2string(RIFFdataLength, 4)
            i = 0
            while i < 4:
                
                RIFFdata[i + 4] = NewLengthString[i]
                i += 1
            # end while
            fwrite(fp_temp, RIFFdata)
            php_fclose(fp_temp)
            getid3_temp = php_new_class("getID3", lambda : getID3())
            getid3_temp.openfile(tempfile)
            getid3_temp.info["filesize"] = RIFFdataLength
            getid3_temp.info["filenamepath"] = info["filenamepath"]
            getid3_temp.info["tags"] = info["tags"]
            getid3_temp.info["warning"] = info["warning"]
            getid3_temp.info["error"] = info["error"]
            getid3_temp.info["comments"] = info["comments"]
            getid3_temp.info["audio"] = info["audio"] if (php_isset(lambda : info["audio"])) else Array()
            getid3_temp.info["video"] = info["video"] if (php_isset(lambda : info["video"])) else Array()
            getid3_riff = php_new_class("getid3_riff", lambda : getid3_riff(getid3_temp))
            getid3_riff.analyze()
            info["riff"] = getid3_temp.info["riff"]
            info["warning"] = getid3_temp.info["warning"]
            info["error"] = getid3_temp.info["error"]
            info["tags"] = getid3_temp.info["tags"]
            info["comments"] = getid3_temp.info["comments"]
            getid3_riff = None
            getid3_temp = None
            unlink(tempfile)
        # end if
        return False
    # end def parseriffdata
    #// 
    #// @param array $RIFFinfoArray
    #// @param array $CommentsTargetArray
    #// 
    #// @return bool
    #//
    @classmethod
    def parsecomments(self, RIFFinfoArray=None, CommentsTargetArray=None):
        
        RIFFinfoKeyLookup = Array({"IARL": "archivallocation", "IART": "artist", "ICDS": "costumedesigner", "ICMS": "commissionedby", "ICMT": "comment", "ICNT": "country", "ICOP": "copyright", "ICRD": "creationdate", "IDIM": "dimensions", "IDIT": "digitizationdate", "IDPI": "resolution", "IDST": "distributor", "IEDT": "editor", "IENG": "engineers", "IFRM": "accountofparts", "IGNR": "genre", "IKEY": "keywords", "ILGT": "lightness", "ILNG": "language", "IMED": "orignalmedium", "IMUS": "composer", "INAM": "title", "IPDS": "productiondesigner", "IPLT": "palette", "IPRD": "product", "IPRO": "producer", "IPRT": "part", "IRTD": "rating", "ISBJ": "subject", "ISFT": "software", "ISGN": "secondarygenre", "ISHP": "sharpness", "ISRC": "sourcesupplier", "ISRF": "digitizationsource", "ISTD": "productionstudio", "ISTR": "starring", "ITCH": "encoded_by", "IWEB": "url", "IWRI": "writer", "____": "comment"})
        for key,value in RIFFinfoKeyLookup:
            if (php_isset(lambda : RIFFinfoArray[key])):
                for commentid,commentdata in RIFFinfoArray[key]:
                    if php_trim(commentdata["data"]) != "":
                        if (php_isset(lambda : CommentsTargetArray[value])):
                            CommentsTargetArray[value][-1] = php_trim(commentdata["data"])
                        else:
                            CommentsTargetArray[value] = Array(php_trim(commentdata["data"]))
                        # end if
                    # end if
                # end for
            # end if
        # end for
        return True
    # end def parsecomments
    #// 
    #// @param string $WaveFormatExData
    #// 
    #// @return array
    #//
    @classmethod
    def parsewaveformatex(self, WaveFormatExData=None):
        
        #// shortcut
        WaveFormatEx = Array()
        WaveFormatEx["raw"] = Array()
        WaveFormatEx_raw = WaveFormatEx["raw"]
        WaveFormatEx_raw["wFormatTag"] = php_substr(WaveFormatExData, 0, 2)
        WaveFormatEx_raw["nChannels"] = php_substr(WaveFormatExData, 2, 2)
        WaveFormatEx_raw["nSamplesPerSec"] = php_substr(WaveFormatExData, 4, 4)
        WaveFormatEx_raw["nAvgBytesPerSec"] = php_substr(WaveFormatExData, 8, 4)
        WaveFormatEx_raw["nBlockAlign"] = php_substr(WaveFormatExData, 12, 2)
        WaveFormatEx_raw["wBitsPerSample"] = php_substr(WaveFormatExData, 14, 2)
        if php_strlen(WaveFormatExData) > 16:
            WaveFormatEx_raw["cbSize"] = php_substr(WaveFormatExData, 16, 2)
        # end if
        WaveFormatEx_raw = php_array_map("getid3_lib::LittleEndian2Int", WaveFormatEx_raw)
        WaveFormatEx["codec"] = self.wformattaglookup(WaveFormatEx_raw["wFormatTag"])
        WaveFormatEx["channels"] = WaveFormatEx_raw["nChannels"]
        WaveFormatEx["sample_rate"] = WaveFormatEx_raw["nSamplesPerSec"]
        WaveFormatEx["bitrate"] = WaveFormatEx_raw["nAvgBytesPerSec"] * 8
        WaveFormatEx["bits_per_sample"] = WaveFormatEx_raw["wBitsPerSample"]
        return WaveFormatEx
    # end def parsewaveformatex
    #// 
    #// @param string $WavPackChunkData
    #// 
    #// @return bool
    #//
    def parsewavpackheader(self, WavPackChunkData=None):
        
        #// typedef struct {
        #// char ckID [4];
        #// long ckSize;
        #// short version;
        #// short bits;                // added for version 2.00
        #// short flags, shift;        // added for version 3.00
        #// long total_samples, crc, crc2;
        #// char extension [4], extra_bc, extras [3];
        #// } WavpackHeader;
        #// shortcut
        info = self.getid3.info
        info["wavpack"] = Array()
        thisfile_wavpack = info["wavpack"]
        thisfile_wavpack["version"] = getid3_lib.littleendian2int(php_substr(WavPackChunkData, 0, 2))
        if thisfile_wavpack["version"] >= 2:
            thisfile_wavpack["bits"] = getid3_lib.littleendian2int(php_substr(WavPackChunkData, 2, 2))
        # end if
        if thisfile_wavpack["version"] >= 3:
            thisfile_wavpack["flags_raw"] = getid3_lib.littleendian2int(php_substr(WavPackChunkData, 4, 2))
            thisfile_wavpack["shift"] = getid3_lib.littleendian2int(php_substr(WavPackChunkData, 6, 2))
            thisfile_wavpack["total_samples"] = getid3_lib.littleendian2int(php_substr(WavPackChunkData, 8, 4))
            thisfile_wavpack["crc1"] = getid3_lib.littleendian2int(php_substr(WavPackChunkData, 12, 4))
            thisfile_wavpack["crc2"] = getid3_lib.littleendian2int(php_substr(WavPackChunkData, 16, 4))
            thisfile_wavpack["extension"] = php_substr(WavPackChunkData, 20, 4)
            thisfile_wavpack["extra_bc"] = getid3_lib.littleendian2int(php_substr(WavPackChunkData, 24, 1))
            i = 0
            while i <= 2:
                
                thisfile_wavpack["extras"][-1] = getid3_lib.littleendian2int(php_substr(WavPackChunkData, 25 + i, 1))
                i += 1
            # end while
            #// shortcut
            thisfile_wavpack["flags"] = Array()
            thisfile_wavpack_flags = thisfile_wavpack["flags"]
            thisfile_wavpack_flags["mono"] = bool(thisfile_wavpack["flags_raw"] & 1)
            thisfile_wavpack_flags["fast_mode"] = bool(thisfile_wavpack["flags_raw"] & 2)
            thisfile_wavpack_flags["raw_mode"] = bool(thisfile_wavpack["flags_raw"] & 4)
            thisfile_wavpack_flags["calc_noise"] = bool(thisfile_wavpack["flags_raw"] & 8)
            thisfile_wavpack_flags["high_quality"] = bool(thisfile_wavpack["flags_raw"] & 16)
            thisfile_wavpack_flags["3_byte_samples"] = bool(thisfile_wavpack["flags_raw"] & 32)
            thisfile_wavpack_flags["over_20_bits"] = bool(thisfile_wavpack["flags_raw"] & 64)
            thisfile_wavpack_flags["use_wvc"] = bool(thisfile_wavpack["flags_raw"] & 128)
            thisfile_wavpack_flags["noiseshaping"] = bool(thisfile_wavpack["flags_raw"] & 256)
            thisfile_wavpack_flags["very_fast_mode"] = bool(thisfile_wavpack["flags_raw"] & 512)
            thisfile_wavpack_flags["new_high_quality"] = bool(thisfile_wavpack["flags_raw"] & 1024)
            thisfile_wavpack_flags["cancel_extreme"] = bool(thisfile_wavpack["flags_raw"] & 2048)
            thisfile_wavpack_flags["cross_decorrelation"] = bool(thisfile_wavpack["flags_raw"] & 4096)
            thisfile_wavpack_flags["new_decorrelation"] = bool(thisfile_wavpack["flags_raw"] & 8192)
            thisfile_wavpack_flags["joint_stereo"] = bool(thisfile_wavpack["flags_raw"] & 16384)
            thisfile_wavpack_flags["extra_decorrelation"] = bool(thisfile_wavpack["flags_raw"] & 32768)
            thisfile_wavpack_flags["override_noiseshape"] = bool(thisfile_wavpack["flags_raw"] & 65536)
            thisfile_wavpack_flags["override_jointstereo"] = bool(thisfile_wavpack["flags_raw"] & 131072)
            thisfile_wavpack_flags["copy_source_filetime"] = bool(thisfile_wavpack["flags_raw"] & 262144)
            thisfile_wavpack_flags["create_exe"] = bool(thisfile_wavpack["flags_raw"] & 524288)
        # end if
        return True
    # end def parsewavpackheader
    #// 
    #// @param string $BITMAPINFOHEADER
    #// @param bool   $littleEndian
    #// 
    #// @return array
    #//
    @classmethod
    def parsebitmapinfoheader(self, BITMAPINFOHEADER=None, littleEndian=True):
        
        parsed["biSize"] = php_substr(BITMAPINFOHEADER, 0, 4)
        #// number of bytes required by the BITMAPINFOHEADER structure
        parsed["biWidth"] = php_substr(BITMAPINFOHEADER, 4, 4)
        #// width of the bitmap in pixels
        parsed["biHeight"] = php_substr(BITMAPINFOHEADER, 8, 4)
        #// height of the bitmap in pixels. If biHeight is positive, the bitmap is a 'bottom-up' DIB and its origin is the lower left corner. If biHeight is negative, the bitmap is a 'top-down' DIB and its origin is the upper left corner
        parsed["biPlanes"] = php_substr(BITMAPINFOHEADER, 12, 2)
        #// number of color planes on the target device. In most cases this value must be set to 1
        parsed["biBitCount"] = php_substr(BITMAPINFOHEADER, 14, 2)
        #// Specifies the number of bits per pixels
        parsed["biSizeImage"] = php_substr(BITMAPINFOHEADER, 20, 4)
        #// size of the bitmap data section of the image (the actual pixel data, excluding BITMAPINFOHEADER and RGBQUAD structures)
        parsed["biXPelsPerMeter"] = php_substr(BITMAPINFOHEADER, 24, 4)
        #// horizontal resolution, in pixels per metre, of the target device
        parsed["biYPelsPerMeter"] = php_substr(BITMAPINFOHEADER, 28, 4)
        #// vertical resolution, in pixels per metre, of the target device
        parsed["biClrUsed"] = php_substr(BITMAPINFOHEADER, 32, 4)
        #// actual number of color indices in the color table used by the bitmap. If this value is zero, the bitmap uses the maximum number of colors corresponding to the value of the biBitCount member for the compression mode specified by biCompression
        parsed["biClrImportant"] = php_substr(BITMAPINFOHEADER, 36, 4)
        #// number of color indices that are considered important for displaying the bitmap. If this value is zero, all colors are important
        parsed = php_array_map("getid3_lib::" + "Little" if littleEndian else "Big" + "Endian2Int", parsed)
        parsed["fourcc"] = php_substr(BITMAPINFOHEADER, 16, 4)
        #// compression identifier
        return parsed
    # end def parsebitmapinfoheader
    #// 
    #// @param string $DIVXTAG
    #// @param bool   $raw
    #// 
    #// @return array
    #//
    @classmethod
    def parsedivxtag(self, DIVXTAG=None, raw=False):
        
        DIVXTAGgenre = Array({0: "Action", 1: "Action/Adventure", 2: "Adventure", 3: "Adult", 4: "Anime", 5: "Cartoon", 6: "Claymation", 7: "Comedy", 8: "Commercial", 9: "Documentary", 10: "Drama", 11: "Home Video", 12: "Horror", 13: "Infomercial", 14: "Interactive", 15: "Mystery", 16: "Music Video", 17: "Other", 18: "Religion", 19: "Sci Fi", 20: "Thriller", 21: "Western"})
        DIVXTAGrating = Array({0: "Unrated", 1: "G", 2: "PG", 3: "PG-13", 4: "R", 5: "NC-17"})
        parsed = Array()
        parsed["title"] = php_trim(php_substr(DIVXTAG, 0, 32))
        parsed["artist"] = php_trim(php_substr(DIVXTAG, 32, 28))
        parsed["year"] = php_intval(php_trim(php_substr(DIVXTAG, 60, 4)))
        parsed["comment"] = php_trim(php_substr(DIVXTAG, 64, 48))
        parsed["genre_id"] = php_intval(php_trim(php_substr(DIVXTAG, 112, 3)))
        parsed["rating_id"] = php_ord(php_substr(DIVXTAG, 115, 1))
        #// $parsed['padding'] =             substr($DIVXTAG, 116,  5);  // 5-byte null
        #// $parsed['magic']   =             substr($DIVXTAG, 121,  7);  // "DIVXTAG"
        parsed["genre"] = DIVXTAGgenre[parsed["genre_id"]] if (php_isset(lambda : DIVXTAGgenre[parsed["genre_id"]])) else parsed["genre_id"]
        parsed["rating"] = DIVXTAGrating[parsed["rating_id"]] if (php_isset(lambda : DIVXTAGrating[parsed["rating_id"]])) else parsed["rating_id"]
        if (not raw):
            parsed["genre_id"] = None
            parsed["rating_id"] = None
            for key,value in parsed:
                if php_empty(lambda : value):
                    parsed[key] = None
                # end if
            # end for
        # end if
        for tag,value in parsed:
            parsed[tag] = Array(value)
        # end for
        return parsed
    # end def parsedivxtag
    #// 
    #// @param string $tagshortname
    #// 
    #// @return string
    #//
    @classmethod
    def wavesndmtaglookup(self, tagshortname=None):
        
        begin = 0
        #// This is not a comment!
        #// ©kwd    keywords
        #// ©BPM    bpm
        #// ©trt    tracktitle
        #// ©des    description
        #// ©gen    category
        #// ©fin    featuredinstrument
        #// ©LID    longid
        #// ©bex    bwdescription
        #// ©pub    publisher
        #// ©cdt    cdtitle
        #// ©alb    library
        #// ©com    composer
        #//
        return getid3_lib.embeddedlookup(tagshortname, begin, 0, __FILE__, "riff-sndm")
    # end def wavesndmtaglookup
    #// 
    #// @param int $wFormatTag
    #// 
    #// @return string
    #//
    @classmethod
    def wformattaglookup(self, wFormatTag=None):
        
        begin = 0
        #// This is not a comment!
        #// 0x0000  Microsoft Unknown Wave Format
        #// 0x0001  Pulse Code Modulation (PCM)
        #// 0x0002  Microsoft ADPCM
        #// 0x0003  IEEE Float
        #// 0x0004  Compaq Computer VSELP
        #// 0x0005  IBM CVSD
        #// 0x0006  Microsoft A-Law
        #// 0x0007  Microsoft mu-Law
        #// 0x0008  Microsoft DTS
        #// 0x0010  OKI ADPCM
        #// 0x0011  Intel DVI/IMA ADPCM
        #// 0x0012  Videologic MediaSpace ADPCM
        #// 0x0013  Sierra Semiconductor ADPCM
        #// 0x0014  Antex Electronics G.723 ADPCM
        #// 0x0015  DSP Solutions DigiSTD
        #// 0x0016  DSP Solutions DigiFIX
        #// 0x0017  Dialogic OKI ADPCM
        #// 0x0018  MediaVision ADPCM
        #// 0x0019  Hewlett-Packard CU
        #// 0x0020  Yamaha ADPCM
        #// 0x0021  Speech Compression Sonarc
        #// 0x0022  DSP Group TrueSpeech
        #// 0x0023  Echo Speech EchoSC1
        #// 0x0024  Audiofile AF36
        #// 0x0025  Audio Processing Technology APTX
        #// 0x0026  AudioFile AF10
        #// 0x0027  Prosody 1612
        #// 0x0028  LRC
        #// 0x0030  Dolby AC2
        #// 0x0031  Microsoft GSM 6.10
        #// 0x0032  MSNAudio
        #// 0x0033  Antex Electronics ADPCME
        #// 0x0034  Control Resources VQLPC
        #// 0x0035  DSP Solutions DigiREAL
        #// 0x0036  DSP Solutions DigiADPCM
        #// 0x0037  Control Resources CR10
        #// 0x0038  Natural MicroSystems VBXADPCM
        #// 0x0039  Crystal Semiconductor IMA ADPCM
        #// 0x003A  EchoSC3
        #// 0x003B  Rockwell ADPCM
        #// 0x003C  Rockwell Digit LK
        #// 0x003D  Xebec
        #// 0x0040  Antex Electronics G.721 ADPCM
        #// 0x0041  G.728 CELP
        #// 0x0042  MSG723
        #// 0x0050  MPEG Layer-2 or Layer-1
        #// 0x0052  RT24
        #// 0x0053  PAC
        #// 0x0055  MPEG Layer-3
        #// 0x0059  Lucent G.723
        #// 0x0060  Cirrus
        #// 0x0061  ESPCM
        #// 0x0062  Voxware
        #// 0x0063  Canopus Atrac
        #// 0x0064  G.726 ADPCM
        #// 0x0065  G.722 ADPCM
        #// 0x0066  DSAT
        #// 0x0067  DSAT Display
        #// 0x0069  Voxware Byte Aligned
        #// 0x0070  Voxware AC8
        #// 0x0071  Voxware AC10
        #// 0x0072  Voxware AC16
        #// 0x0073  Voxware AC20
        #// 0x0074  Voxware MetaVoice
        #// 0x0075  Voxware MetaSound
        #// 0x0076  Voxware RT29HW
        #// 0x0077  Voxware VR12
        #// 0x0078  Voxware VR18
        #// 0x0079  Voxware TQ40
        #// 0x0080  Softsound
        #// 0x0081  Voxware TQ60
        #// 0x0082  MSRT24
        #// 0x0083  G.729A
        #// 0x0084  MVI MV12
        #// 0x0085  DF G.726
        #// 0x0086  DF GSM610
        #// 0x0088  ISIAudio
        #// 0x0089  Onlive
        #// 0x0091  SBC24
        #// 0x0092  Dolby AC3 SPDIF
        #// 0x0093  MediaSonic G.723
        #// 0x0094  Aculab PLC    Prosody 8kbps
        #// 0x0097  ZyXEL ADPCM
        #// 0x0098  Philips LPCBB
        #// 0x0099  Packed
        #// 0x00FF  AAC
        #// 0x0100  Rhetorex ADPCM
        #// 0x0101  IBM mu-law
        #// 0x0102  IBM A-law
        #// 0x0103  IBM AVC Adaptive Differential Pulse Code Modulation (ADPCM)
        #// 0x0111  Vivo G.723
        #// 0x0112  Vivo Siren
        #// 0x0123  Digital G.723
        #// 0x0125  Sanyo LD ADPCM
        #// 0x0130  Sipro Lab Telecom ACELP NET
        #// 0x0131  Sipro Lab Telecom ACELP 4800
        #// 0x0132  Sipro Lab Telecom ACELP 8V3
        #// 0x0133  Sipro Lab Telecom G.729
        #// 0x0134  Sipro Lab Telecom G.729A
        #// 0x0135  Sipro Lab Telecom Kelvin
        #// 0x0140  Windows Media Video V8
        #// 0x0150  Qualcomm PureVoice
        #// 0x0151  Qualcomm HalfRate
        #// 0x0155  Ring Zero Systems TUB GSM
        #// 0x0160  Microsoft Audio 1
        #// 0x0161  Windows Media Audio V7 / V8 / V9
        #// 0x0162  Windows Media Audio Professional V9
        #// 0x0163  Windows Media Audio Lossless V9
        #// 0x0200  Creative Labs ADPCM
        #// 0x0202  Creative Labs Fastspeech8
        #// 0x0203  Creative Labs Fastspeech10
        #// 0x0210  UHER Informatic GmbH ADPCM
        #// 0x0220  Quarterdeck
        #// 0x0230  I-link Worldwide VC
        #// 0x0240  Aureal RAW Sport
        #// 0x0250  Interactive Products HSX
        #// 0x0251  Interactive Products RPELP
        #// 0x0260  Consistent Software CS2
        #// 0x0270  Sony SCX
        #// 0x0300  Fujitsu FM Towns Snd
        #// 0x0400  BTV Digital
        #// 0x0401  Intel Music Coder
        #// 0x0450  QDesign Music
        #// 0x0680  VME VMPCM
        #// 0x0681  AT&T Labs TPC
        #// 0x08AE  ClearJump LiteWave
        #// 0x1000  Olivetti GSM
        #// 0x1001  Olivetti ADPCM
        #// 0x1002  Olivetti CELP
        #// 0x1003  Olivetti SBC
        #// 0x1004  Olivetti OPR
        #// 0x1100  Lernout & Hauspie Codec (0x1100)
        #// 0x1101  Lernout & Hauspie CELP Codec (0x1101)
        #// 0x1102  Lernout & Hauspie SBC Codec (0x1102)
        #// 0x1103  Lernout & Hauspie SBC Codec (0x1103)
        #// 0x1104  Lernout & Hauspie SBC Codec (0x1104)
        #// 0x1400  Norris
        #// 0x1401  AT&T ISIAudio
        #// 0x1500  Soundspace Music Compression
        #// 0x181C  VoxWare RT24 Speech
        #// 0x1FC4  NCT Soft ALF2CD (www.nctsoft.com)
        #// 0x2000  Dolby AC3
        #// 0x2001  Dolby DTS
        #// 0x2002  WAVE_FORMAT_14_4
        #// 0x2003  WAVE_FORMAT_28_8
        #// 0x2004  WAVE_FORMAT_COOK
        #// 0x2005  WAVE_FORMAT_DNET
        #// 0x674F  Ogg Vorbis 1
        #// 0x6750  Ogg Vorbis 2
        #// 0x6751  Ogg Vorbis 3
        #// 0x676F  Ogg Vorbis 1+
        #// 0x6770  Ogg Vorbis 2+
        #// 0x6771  Ogg Vorbis 3+
        #// 0x7A21  GSM-AMR (CBR, no SID)
        #// 0x7A22  GSM-AMR (VBR, including SID)
        #// 0xFFFE  WAVE_FORMAT_EXTENSIBLE
        #// 0xFFFF  WAVE_FORMAT_DEVELOPMENT
        #//
        return getid3_lib.embeddedlookup("0x" + php_str_pad(php_strtoupper(dechex(wFormatTag)), 4, "0", STR_PAD_LEFT), begin, 0, __FILE__, "riff-wFormatTag")
    # end def wformattaglookup
    #// 
    #// @param string $fourcc
    #// 
    #// @return string
    #//
    @classmethod
    def fourcclookup(self, fourcc=None):
        
        begin = 0
        #// This is not a comment!
        #// swot    http://developer.apple.com/qa/snd/snd07.html
        #// ____    No Codec (____)
        #// _BIT    BI_BITFIELDS (Raw RGB)
        #// _JPG    JPEG compressed
        #// _PNG    PNG compressed W3C/ISO/IEC (RFC-2083)
        #// _RAW    Full Frames (Uncompressed)
        #// _RGB    Raw RGB Bitmap
        #// _RL4    RLE 4bpp RGB
        #// _RL8    RLE 8bpp RGB
        #// 3IV1    3ivx MPEG-4 v1
        #// 3IV2    3ivx MPEG-4 v2
        #// 3IVX    3ivx MPEG-4
        #// AASC    Autodesk Animator
        #// ABYR    Kensington ?ABYR?
        #// AEMI    Array Microsystems VideoONE MPEG1-I Capture
        #// AFLC    Autodesk Animator FLC
        #// AFLI    Autodesk Animator FLI
        #// AMPG    Array Microsystems VideoONE MPEG
        #// ANIM    Intel RDX (ANIM)
        #// AP41    AngelPotion Definitive
        #// ASV1    Asus Video v1
        #// ASV2    Asus Video v2
        #// ASVX    Asus Video 2.0 (audio)
        #// AUR2    AuraVision Aura 2 Codec - YUV 4:2:2
        #// AURA    AuraVision Aura 1 Codec - YUV 4:1:1
        #// AVDJ    Independent JPEG Group\'s codec (AVDJ)
        #// AVRN    Independent JPEG Group\'s codec (AVRN)
        #// AYUV    4:4:4 YUV (AYUV)
        #// AZPR    Quicktime Apple Video (AZPR)
        #// BGR     Raw RGB32
        #// BLZ0    Blizzard DivX MPEG-4
        #// BTVC    Conexant Composite Video
        #// BINK    RAD Game Tools Bink Video
        #// BT20    Conexant Prosumer Video
        #// BTCV    Conexant Composite Video Codec
        #// BW10    Data Translation Broadway MPEG Capture
        #// CC12    Intel YUV12
        #// CDVC    Canopus DV
        #// CFCC    Digital Processing Systems DPS Perception
        #// CGDI    Microsoft Office 97 Camcorder Video
        #// CHAM    Winnov Caviara Champagne
        #// CJPG    Creative WebCam JPEG
        #// CLJR    Cirrus Logic YUV 4:1:1
        #// CMYK    Common Data Format in Printing (Colorgraph)
        #// CPLA    Weitek 4:2:0 YUV Planar
        #// CRAM    Microsoft Video 1 (CRAM)
        #// cvid    Radius Cinepak
        #// CVID    Radius Cinepak
        #// CWLT    Microsoft Color WLT DIB
        #// CYUV    Creative Labs YUV
        #// CYUY    ATI YUV
        #// D261    H.261
        #// D263    H.263
        #// DIB     Device Independent Bitmap
        #// DIV1    FFmpeg OpenDivX
        #// DIV2    Microsoft MPEG-4 v1/v2
        #// DIV3    DivX ;-) MPEG-4 v3.x Low-Motion
        #// DIV4    DivX ;-) MPEG-4 v3.x Fast-Motion
        #// DIV5    DivX MPEG-4 v5.x
        #// DIV6    DivX ;-) (MS MPEG-4 v3.x)
        #// DIVX    DivX MPEG-4 v4 (OpenDivX / Project Mayo)
        #// divx    DivX MPEG-4
        #// DMB1    Matrox Rainbow Runner hardware MJPEG
        #// DMB2    Paradigm MJPEG
        #// DSVD    ?DSVD?
        #// DUCK    Duck TrueMotion 1.0
        #// DPS0    DPS/Leitch Reality Motion JPEG
        #// DPSC    DPS/Leitch PAR Motion JPEG
        #// DV25    Matrox DVCPRO codec
        #// DV50    Matrox DVCPRO50 codec
        #// DVC     IEC 61834 and SMPTE 314M (DVC/DV Video)
        #// DVCP    IEC 61834 and SMPTE 314M (DVC/DV Video)
        #// DVHD    IEC Standard DV 1125 lines @ 30fps / 1250 lines @ 25fps
        #// DVMA    Darim Vision DVMPEG (dummy for MPEG compressor) (www.darvision.com)
        #// DVSL    IEC Standard DV compressed in SD (SDL)
        #// DVAN    ?DVAN?
        #// DVE2    InSoft DVE-2 Videoconferencing
        #// dvsd    IEC 61834 and SMPTE 314M DVC/DV Video
        #// DVSD    IEC 61834 and SMPTE 314M DVC/DV Video
        #// DVX1    Lucent DVX1000SP Video Decoder
        #// DVX2    Lucent DVX2000S Video Decoder
        #// DVX3    Lucent DVX3000S Video Decoder
        #// DX50    DivX v5
        #// DXT1    Microsoft DirectX Compressed Texture (DXT1)
        #// DXT2    Microsoft DirectX Compressed Texture (DXT2)
        #// DXT3    Microsoft DirectX Compressed Texture (DXT3)
        #// DXT4    Microsoft DirectX Compressed Texture (DXT4)
        #// DXT5    Microsoft DirectX Compressed Texture (DXT5)
        #// DXTC    Microsoft DirectX Compressed Texture (DXTC)
        #// DXTn    Microsoft DirectX Compressed Texture (DXTn)
        #// EM2V    Etymonix MPEG-2 I-frame (www.etymonix.com)
        #// EKQ0    Elsa ?EKQ0?
        #// ELK0    Elsa ?ELK0?
        #// ESCP    Eidos Escape
        #// ETV1    eTreppid Video ETV1
        #// ETV2    eTreppid Video ETV2
        #// ETVC    eTreppid Video ETVC
        #// FLIC    Autodesk FLI/FLC Animation
        #// FLV1    Sorenson Spark
        #// FLV4    On2 TrueMotion VP6
        #// FRWT    Darim Vision Forward Motion JPEG (www.darvision.com)
        #// FRWU    Darim Vision Forward Uncompressed (www.darvision.com)
        #// FLJP    D-Vision Field Encoded Motion JPEG
        #// FPS1    FRAPS v1
        #// FRWA    SoftLab-Nsk Forward Motion JPEG w/ alpha channel
        #// FRWD    SoftLab-Nsk Forward Motion JPEG
        #// FVF1    Iterated Systems Fractal Video Frame
        #// GLZW    Motion LZW (gabest@freemail.hu)
        #// GPEG    Motion JPEG (gabest@freemail.hu)
        #// GWLT    Microsoft Greyscale WLT DIB
        #// H260    Intel ITU H.260 Videoconferencing
        #// H261    Intel ITU H.261 Videoconferencing
        #// H262    Intel ITU H.262 Videoconferencing
        #// H263    Intel ITU H.263 Videoconferencing
        #// H264    Intel ITU H.264 Videoconferencing
        #// H265    Intel ITU H.265 Videoconferencing
        #// H266    Intel ITU H.266 Videoconferencing
        #// H267    Intel ITU H.267 Videoconferencing
        #// H268    Intel ITU H.268 Videoconferencing
        #// H269    Intel ITU H.269 Videoconferencing
        #// HFYU    Huffman Lossless Codec
        #// HMCR    Rendition Motion Compensation Format (HMCR)
        #// HMRR    Rendition Motion Compensation Format (HMRR)
        #// I263    FFmpeg I263 decoder
        #// IF09    Indeo YVU9 ("YVU9 with additional delta-frame info after the U plane")
        #// IUYV    Interlaced version of UYVY (www.leadtools.com)
        #// IY41    Interlaced version of Y41P (www.leadtools.com)
        #// IYU1    12 bit format used in mode 2 of the IEEE 1394 Digital Camera 1.04 spec    IEEE standard
        #// IYU2    24 bit format used in mode 2 of the IEEE 1394 Digital Camera 1.04 spec    IEEE standard
        #// IYUV    Planar YUV format (8-bpp Y plane, followed by 8-bpp 2×2 U and V planes)
        #// i263    Intel ITU H.263 Videoconferencing (i263)
        #// I420    Intel Indeo 4
        #// IAN     Intel Indeo 4 (RDX)
        #// ICLB    InSoft CellB Videoconferencing
        #// IGOR    Power DVD
        #// IJPG    Intergraph JPEG
        #// ILVC    Intel Layered Video
        #// ILVR    ITU-T H.263+
        #// IPDV    I-O Data Device Giga AVI DV Codec
        #// IR21    Intel Indeo 2.1
        #// IRAW    Intel YUV Uncompressed
        #// IV30    Intel Indeo 3.0
        #// IV31    Intel Indeo 3.1
        #// IV32    Ligos Indeo 3.2
        #// IV33    Ligos Indeo 3.3
        #// IV34    Ligos Indeo 3.4
        #// IV35    Ligos Indeo 3.5
        #// IV36    Ligos Indeo 3.6
        #// IV37    Ligos Indeo 3.7
        #// IV38    Ligos Indeo 3.8
        #// IV39    Ligos Indeo 3.9
        #// IV40    Ligos Indeo Interactive 4.0
        #// IV41    Ligos Indeo Interactive 4.1
        #// IV42    Ligos Indeo Interactive 4.2
        #// IV43    Ligos Indeo Interactive 4.3
        #// IV44    Ligos Indeo Interactive 4.4
        #// IV45    Ligos Indeo Interactive 4.5
        #// IV46    Ligos Indeo Interactive 4.6
        #// IV47    Ligos Indeo Interactive 4.7
        #// IV48    Ligos Indeo Interactive 4.8
        #// IV49    Ligos Indeo Interactive 4.9
        #// IV50    Ligos Indeo Interactive 5.0
        #// JBYR    Kensington ?JBYR?
        #// JPEG    Still Image JPEG DIB
        #// JPGL    Pegasus Lossless Motion JPEG
        #// KMVC    Team17 Software Karl Morton\'s Video Codec
        #// LSVM    Vianet Lighting Strike Vmail (Streaming) (www.vianet.com)
        #// LEAD    LEAD Video Codec
        #// Ljpg    LEAD MJPEG Codec
        #// MDVD    Alex MicroDVD Video (hacked MS MPEG-4) (www.tiasoft.de)
        #// MJPA    Morgan Motion JPEG (MJPA) (www.morgan-multimedia.com)
        #// MJPB    Morgan Motion JPEG (MJPB) (www.morgan-multimedia.com)
        #// MMES    Matrox MPEG-2 I-frame
        #// MP2v    Microsoft S-Mpeg 4 version 1 (MP2v)
        #// MP42    Microsoft S-Mpeg 4 version 2 (MP42)
        #// MP43    Microsoft S-Mpeg 4 version 3 (MP43)
        #// MP4S    Microsoft S-Mpeg 4 version 3 (MP4S)
        #// MP4V    FFmpeg MPEG-4
        #// MPG1    FFmpeg MPEG 1/2
        #// MPG2    FFmpeg MPEG 1/2
        #// MPG3    FFmpeg DivX ;-) (MS MPEG-4 v3)
        #// MPG4    Microsoft MPEG-4
        #// MPGI    Sigma Designs MPEG
        #// MPNG    PNG images decoder
        #// MSS1    Microsoft Windows Screen Video
        #// MSZH    LCL (Lossless Codec Library) (www.geocities.co.jp/Playtown-Denei/2837/LRC.htm)
        #// M261    Microsoft H.261
        #// M263    Microsoft H.263
        #// M4S2    Microsoft Fully Compliant MPEG-4 v2 simple profile (M4S2)
        #// m4s2    Microsoft Fully Compliant MPEG-4 v2 simple profile (m4s2)
        #// MC12    ATI Motion Compensation Format (MC12)
        #// MCAM    ATI Motion Compensation Format (MCAM)
        #// MJ2C    Morgan Multimedia Motion JPEG2000
        #// mJPG    IBM Motion JPEG w/ Huffman Tables
        #// MJPG    Microsoft Motion JPEG DIB
        #// MP42    Microsoft MPEG-4 (low-motion)
        #// MP43    Microsoft MPEG-4 (fast-motion)
        #// MP4S    Microsoft MPEG-4 (MP4S)
        #// mp4s    Microsoft MPEG-4 (mp4s)
        #// MPEG    Chromatic Research MPEG-1 Video I-Frame
        #// MPG4    Microsoft MPEG-4 Video High Speed Compressor
        #// MPGI    Sigma Designs MPEG
        #// MRCA    FAST Multimedia Martin Regen Codec
        #// MRLE    Microsoft Run Length Encoding
        #// MSVC    Microsoft Video 1
        #// MTX1    Matrox ?MTX1?
        #// MTX2    Matrox ?MTX2?
        #// MTX3    Matrox ?MTX3?
        #// MTX4    Matrox ?MTX4?
        #// MTX5    Matrox ?MTX5?
        #// MTX6    Matrox ?MTX6?
        #// MTX7    Matrox ?MTX7?
        #// MTX8    Matrox ?MTX8?
        #// MTX9    Matrox ?MTX9?
        #// MV12    Motion Pixels Codec (old)
        #// MWV1    Aware Motion Wavelets
        #// nAVI    SMR Codec (hack of Microsoft MPEG-4) (IRC #shadowrealm)
        #// NT00    NewTek LightWave HDTV YUV w/ Alpha (www.newtek.com)
        #// NUV1    NuppelVideo
        #// NTN1    Nogatech Video Compression 1
        #// NVS0    nVidia GeForce Texture (NVS0)
        #// NVS1    nVidia GeForce Texture (NVS1)
        #// NVS2    nVidia GeForce Texture (NVS2)
        #// NVS3    nVidia GeForce Texture (NVS3)
        #// NVS4    nVidia GeForce Texture (NVS4)
        #// NVS5    nVidia GeForce Texture (NVS5)
        #// NVT0    nVidia GeForce Texture (NVT0)
        #// NVT1    nVidia GeForce Texture (NVT1)
        #// NVT2    nVidia GeForce Texture (NVT2)
        #// NVT3    nVidia GeForce Texture (NVT3)
        #// NVT4    nVidia GeForce Texture (NVT4)
        #// NVT5    nVidia GeForce Texture (NVT5)
        #// PIXL    MiroXL, Pinnacle PCTV
        #// PDVC    I-O Data Device Digital Video Capture DV codec
        #// PGVV    Radius Video Vision
        #// PHMO    IBM Photomotion
        #// PIM1    MPEG Realtime (Pinnacle Cards)
        #// PIM2    Pegasus Imaging ?PIM2?
        #// PIMJ    Pegasus Imaging Lossless JPEG
        #// PVEZ    Horizons Technology PowerEZ
        #// PVMM    PacketVideo Corporation MPEG-4
        #// PVW2    Pegasus Imaging Wavelet Compression
        #// Q1.0    Q-Team\'s QPEG 1.0 (www.q-team.de)
        #// Q1.1    Q-Team\'s QPEG 1.1 (www.q-team.de)
        #// QPEG    Q-Team QPEG 1.0
        #// qpeq    Q-Team QPEG 1.1
        #// RGB     Raw BGR32
        #// RGBA    Raw RGB w/ Alpha
        #// RMP4    REALmagic MPEG-4 (unauthorized XVID copy) (www.sigmadesigns.com)
        #// ROQV    Id RoQ File Video Decoder
        #// RPZA    Quicktime Apple Video (RPZA)
        #// RUD0    Rududu video codec (http://rududu.ifrance.com/rududu/)
        #// RV10    RealVideo 1.0 (aka RealVideo 5.0)
        #// RV13    RealVideo 1.0 (RV13)
        #// RV20    RealVideo G2
        #// RV30    RealVideo 8
        #// RV40    RealVideo 9
        #// RGBT    Raw RGB w/ Transparency
        #// RLE     Microsoft Run Length Encoder
        #// RLE4    Run Length Encoded (4bpp, 16-color)
        #// RLE8    Run Length Encoded (8bpp, 256-color)
        #// RT21    Intel Indeo RealTime Video 2.1
        #// rv20    RealVideo G2
        #// rv30    RealVideo 8
        #// RVX     Intel RDX (RVX )
        #// SMC     Apple Graphics (SMC )
        #// SP54    Logitech Sunplus Sp54 Codec for Mustek GSmart Mini 2
        #// SPIG    Radius Spigot
        #// SVQ3    Sorenson Video 3 (Apple Quicktime 5)
        #// s422    Tekram VideoCap C210 YUV 4:2:2
        #// SDCC    Sun Communication Digital Camera Codec
        #// SFMC    CrystalNet Surface Fitting Method
        #// SMSC    Radius SMSC
        #// SMSD    Radius SMSD
        #// smsv    WorldConnect Wavelet Video
        #// SPIG    Radius Spigot
        #// SPLC    Splash Studios ACM Audio Codec (www.splashstudios.net)
        #// SQZ2    Microsoft VXTreme Video Codec V2
        #// STVA    ST Microelectronics CMOS Imager Data (Bayer)
        #// STVB    ST Microelectronics CMOS Imager Data (Nudged Bayer)
        #// STVC    ST Microelectronics CMOS Imager Data (Bunched)
        #// STVX    ST Microelectronics CMOS Imager Data (Extended CODEC Data Format)
        #// STVY    ST Microelectronics CMOS Imager Data (Extended CODEC Data Format with Correction Data)
        #// SV10    Sorenson Video R1
        #// SVQ1    Sorenson Video
        #// T420    Toshiba YUV 4:2:0
        #// TM2A    Duck TrueMotion Archiver 2.0 (www.duck.com)
        #// TVJP    Pinnacle/Truevision Targa 2000 board (TVJP)
        #// TVMJ    Pinnacle/Truevision Targa 2000 board (TVMJ)
        #// TY0N    Tecomac Low-Bit Rate Codec (www.tecomac.com)
        #// TY2C    Trident Decompression Driver
        #// TLMS    TeraLogic Motion Intraframe Codec (TLMS)
        #// TLST    TeraLogic Motion Intraframe Codec (TLST)
        #// TM20    Duck TrueMotion 2.0
        #// TM2X    Duck TrueMotion 2X
        #// TMIC    TeraLogic Motion Intraframe Codec (TMIC)
        #// TMOT    Horizons Technology TrueMotion S
        #// tmot    Horizons TrueMotion Video Compression
        #// TR20    Duck TrueMotion RealTime 2.0
        #// TSCC    TechSmith Screen Capture Codec
        #// TV10    Tecomac Low-Bit Rate Codec
        #// TY2N    Trident ?TY2N?
        #// U263    UB Video H.263/H.263+/H.263++ Decoder
        #// UMP4    UB Video MPEG 4 (www.ubvideo.com)
        #// UYNV    Nvidia UYVY packed 4:2:2
        #// UYVP    Evans & Sutherland YCbCr 4:2:2 extended precision
        #// UCOD    eMajix.com ClearVideo
        #// ULTI    IBM Ultimotion
        #// UYVY    UYVY packed 4:2:2
        #// V261    Lucent VX2000S
        #// VIFP    VFAPI Reader Codec (www.yks.ne.jp/~hori/)
        #// VIV1    FFmpeg H263+ decoder
        #// VIV2    Vivo H.263
        #// VQC2    Vector-quantised codec 2 (research) http://eprints.ecs.soton.ac.uk/archive/00001310/01/VTC97-js.pdf)
        #// VTLP    Alaris VideoGramPiX
        #// VYU9    ATI YUV (VYU9)
        #// VYUY    ATI YUV (VYUY)
        #// V261    Lucent VX2000S
        #// V422    Vitec Multimedia 24-bit YUV 4:2:2 Format
        #// V655    Vitec Multimedia 16-bit YUV 4:2:2 Format
        #// VCR1    ATI Video Codec 1
        #// VCR2    ATI Video Codec 2
        #// VCR3    ATI VCR 3.0
        #// VCR4    ATI VCR 4.0
        #// VCR5    ATI VCR 5.0
        #// VCR6    ATI VCR 6.0
        #// VCR7    ATI VCR 7.0
        #// VCR8    ATI VCR 8.0
        #// VCR9    ATI VCR 9.0
        #// VDCT    Vitec Multimedia Video Maker Pro DIB
        #// VDOM    VDOnet VDOWave
        #// VDOW    VDOnet VDOLive (H.263)
        #// VDTZ    Darim Vison VideoTizer YUV
        #// VGPX    Alaris VideoGramPiX
        #// VIDS    Vitec Multimedia YUV 4:2:2 CCIR 601 for V422
        #// VIVO    Vivo H.263 v2.00
        #// vivo    Vivo H.263
        #// VIXL    Miro/Pinnacle Video XL
        #// VLV1    VideoLogic/PURE Digital Videologic Capture
        #// VP30    On2 VP3.0
        #// VP31    On2 VP3.1
        #// VP6F    On2 TrueMotion VP6
        #// VX1K    Lucent VX1000S Video Codec
        #// VX2K    Lucent VX2000S Video Codec
        #// VXSP    Lucent VX1000SP Video Codec
        #// WBVC    Winbond W9960
        #// WHAM    Microsoft Video 1 (WHAM)
        #// WINX    Winnov Software Compression
        #// WJPG    AverMedia Winbond JPEG
        #// WMV1    Windows Media Video V7
        #// WMV2    Windows Media Video V8
        #// WMV3    Windows Media Video V9
        #// WNV1    Winnov Hardware Compression
        #// XYZP    Extended PAL format XYZ palette (www.riff.org)
        #// x263    Xirlink H.263
        #// XLV0    NetXL Video Decoder
        #// XMPG    Xing MPEG (I-Frame only)
        #// XVID    XviD MPEG-4 (www.xvid.org)
        #// XXAN    ?XXAN?
        #// YU92    Intel YUV (YU92)
        #// YUNV    Nvidia Uncompressed YUV 4:2:2
        #// YUVP    Extended PAL format YUV palette (www.riff.org)
        #// Y211    YUV 2:1:1 Packed
        #// Y411    YUV 4:1:1 Packed
        #// Y41B    Weitek YUV 4:1:1 Planar
        #// Y41P    Brooktree PC1 YUV 4:1:1 Packed
        #// Y41T    Brooktree PC1 YUV 4:1:1 with transparency
        #// Y42B    Weitek YUV 4:2:2 Planar
        #// Y42T    Brooktree UYUV 4:2:2 with transparency
        #// Y422    ADS Technologies Copy of UYVY used in Pyro WebCam firewire camera
        #// Y800    Simple, single Y plane for monochrome images
        #// Y8      Grayscale video
        #// YC12    Intel YUV 12 codec
        #// YUV8    Winnov Caviar YUV8
        #// YUV9    Intel YUV9
        #// YUY2    Uncompressed YUV 4:2:2
        #// YUYV    Canopus YUV
        #// YV12    YVU12 Planar
        #// YVU9    Intel YVU9 Planar (8-bpp Y plane, followed by 8-bpp 4x4 U and V planes)
        #// YVYU    YVYU 4:2:2 Packed
        #// ZLIB    Lossless Codec Library zlib compression (www.geocities.co.jp/Playtown-Denei/2837/LRC.htm)
        #// ZPEG    Metheus Video Zipper
        #//
        return getid3_lib.embeddedlookup(fourcc, begin, 0, __FILE__, "riff-fourcc")
    # end def fourcclookup
    #// 
    #// @param string $byteword
    #// @param bool   $signed
    #// 
    #// @return int|float|false
    #//
    def eitherendian2int(self, byteword=None, signed=False):
        
        if self.container == "riff":
            return getid3_lib.littleendian2int(byteword, signed)
        # end if
        return getid3_lib.bigendian2int(byteword, False, signed)
    # end def eitherendian2int
# end class getid3_riff
