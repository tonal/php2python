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
#// Class for working with MO files
#// 
#// @version $Id: mo.php 1157 2015-11-20 04:30:11Z dd32 $
#// @package pomo
#// @subpackage mo
#//
php_include_file(__DIR__ + "/translations.php", once=True)
php_include_file(__DIR__ + "/streams.php", once=True)
if (not php_class_exists("MO", False)):
    class MO(Gettext_Translations):
        _nplurals = 2
        filename = ""
        #// 
        #// Returns the loaded MO file.
        #// 
        #// @return string The loaded MO file.
        #//
        def get_filename(self):
            
            return self.filename
        # end def get_filename
        #// 
        #// Fills up with the entries from MO file $filename
        #// 
        #// @param string $filename MO file to load
        #// @return bool True if the import from file was successful, otherwise false.
        #//
        def import_from_file(self, filename=None):
            
            reader = php_new_class("POMO_FileReader", lambda : POMO_FileReader(filename))
            if (not reader.is_resource()):
                return False
            # end if
            self.filename = str(filename)
            return self.import_from_reader(reader)
        # end def import_from_file
        #// 
        #// @param string $filename
        #// @return bool
        #//
        def export_to_file(self, filename=None):
            
            fh = fopen(filename, "wb")
            if (not fh):
                return False
            # end if
            res = self.export_to_file_handle(fh)
            php_fclose(fh)
            return res
        # end def export_to_file
        #// 
        #// @return string|false
        #//
        def export(self):
            
            tmp_fh = fopen("php://temp", "r+")
            if (not tmp_fh):
                return False
            # end if
            self.export_to_file_handle(tmp_fh)
            rewind(tmp_fh)
            return stream_get_contents(tmp_fh)
        # end def export
        #// 
        #// @param Translation_Entry $entry
        #// @return bool
        #//
        def is_entry_good_for_export(self, entry=None):
            
            if php_empty(lambda : entry.translations):
                return False
            # end if
            if (not php_array_filter(entry.translations)):
                return False
            # end if
            return True
        # end def is_entry_good_for_export
        #// 
        #// @param resource $fh
        #// @return true
        #//
        def export_to_file_handle(self, fh=None):
            
            entries = php_array_filter(self.entries, Array(self, "is_entry_good_for_export"))
            ksort(entries)
            magic = 2500072158
            revision = 0
            total = php_count(entries) + 1
            #// All the headers are one entry.
            originals_lenghts_addr = 28
            translations_lenghts_addr = originals_lenghts_addr + 8 * total
            size_of_hash = 0
            hash_addr = translations_lenghts_addr + 8 * total
            current_addr = hash_addr
            fwrite(fh, pack("V*", magic, revision, total, originals_lenghts_addr, translations_lenghts_addr, size_of_hash, hash_addr))
            fseek(fh, originals_lenghts_addr)
            #// Headers' msgid is an empty string.
            fwrite(fh, pack("VV", 0, current_addr))
            current_addr += 1
            originals_table = " "
            reader = php_new_class("POMO_Reader", lambda : POMO_Reader())
            for entry in entries:
                originals_table += self.export_original(entry) + " "
                length = reader.strlen(self.export_original(entry))
                fwrite(fh, pack("VV", length, current_addr))
                current_addr += length + 1
                pass
            # end for
            exported_headers = self.export_headers()
            fwrite(fh, pack("VV", reader.strlen(exported_headers), current_addr))
            current_addr += php_strlen(exported_headers) + 1
            translations_table = exported_headers + " "
            for entry in entries:
                translations_table += self.export_translations(entry) + " "
                length = reader.strlen(self.export_translations(entry))
                fwrite(fh, pack("VV", length, current_addr))
                current_addr += length + 1
            # end for
            fwrite(fh, originals_table)
            fwrite(fh, translations_table)
            return True
        # end def export_to_file_handle
        #// 
        #// @param Translation_Entry $entry
        #// @return string
        #//
        def export_original(self, entry=None):
            
            #// TODO: Warnings for control characters.
            exported = entry.singular
            if entry.is_plural:
                exported += " " + entry.plural
            # end if
            if entry.context:
                exported = entry.context + "" + exported
            # end if
            return exported
        # end def export_original
        #// 
        #// @param Translation_Entry $entry
        #// @return string
        #//
        def export_translations(self, entry=None):
            
            #// TODO: Warnings for control characters.
            return php_implode(" ", entry.translations) if entry.is_plural else entry.translations[0]
        # end def export_translations
        #// 
        #// @return string
        #//
        def export_headers(self):
            
            exported = ""
            for header,value in self.headers:
                exported += str(header) + str(": ") + str(value) + str("\n")
            # end for
            return exported
        # end def export_headers
        #// 
        #// @param int $magic
        #// @return string|false
        #//
        def get_byteorder(self, magic=None):
            
            #// The magic is 0x950412de.
            #// bug in PHP 5.0.2, see https://savannah.nongnu.org/bugs/?func=detailitem&item_id=10565
            magic_little = int(-1794895138)
            magic_little_64 = int(2500072158)
            #// 0xde120495
            magic_big = int(-569244523) & 4294967295
            if magic_little == magic or magic_little_64 == magic:
                return "little"
            elif magic_big == magic:
                return "big"
            else:
                return False
            # end if
        # end def get_byteorder
        #// 
        #// @param POMO_FileReader $reader
        #// @return bool True if the import was successful, otherwise false.
        #//
        def import_from_reader(self, reader=None):
            
            endian_string = MO.get_byteorder(reader.readint32())
            if False == endian_string:
                return False
            # end if
            reader.setendian(endian_string)
            endian = "N" if "big" == endian_string else "V"
            header = reader.read(24)
            if reader.strlen(header) != 24:
                return False
            # end if
            #// Parse header.
            header = unpack(str(endian) + str("revision/") + str(endian) + str("total/") + str(endian) + str("originals_lenghts_addr/") + str(endian) + str("translations_lenghts_addr/") + str(endian) + str("hash_length/") + str(endian) + str("hash_addr"), header)
            if (not php_is_array(header)):
                return False
            # end if
            #// Support revision 0 of MO format specs, only.
            if 0 != header["revision"]:
                return False
            # end if
            #// Seek to data blocks.
            reader.seekto(header["originals_lenghts_addr"])
            #// Read originals' indices.
            originals_lengths_length = header["translations_lenghts_addr"] - header["originals_lenghts_addr"]
            if originals_lengths_length != header["total"] * 8:
                return False
            # end if
            originals = reader.read(originals_lengths_length)
            if reader.strlen(originals) != originals_lengths_length:
                return False
            # end if
            #// Read translations' indices.
            translations_lenghts_length = header["hash_addr"] - header["translations_lenghts_addr"]
            if translations_lenghts_length != header["total"] * 8:
                return False
            # end if
            translations = reader.read(translations_lenghts_length)
            if reader.strlen(translations) != translations_lenghts_length:
                return False
            # end if
            #// Transform raw data into set of indices.
            originals = reader.str_split(originals, 8)
            translations = reader.str_split(translations, 8)
            #// Skip hash table.
            strings_addr = header["hash_addr"] + header["hash_length"] * 4
            reader.seekto(strings_addr)
            strings = reader.read_all()
            reader.close()
            i = 0
            while i < header["total"]:
                
                o = unpack(str(endian) + str("length/") + str(endian) + str("pos"), originals[i])
                t = unpack(str(endian) + str("length/") + str(endian) + str("pos"), translations[i])
                if (not o) or (not t):
                    return False
                # end if
                #// Adjust offset due to reading strings to separate space before.
                o["pos"] -= strings_addr
                t["pos"] -= strings_addr
                original = reader.substr(strings, o["pos"], o["length"])
                translation = reader.substr(strings, t["pos"], t["length"])
                if "" == original:
                    self.set_headers(self.make_headers(translation))
                else:
                    entry = self.make_entry(original, translation)
                    self.entries[entry.key()] = entry
                # end if
                i += 1
            # end while
            return True
        # end def import_from_reader
        #// 
        #// Build a Translation_Entry from original string and translation strings,
        #// found in a MO file
        #// 
        #// @static
        #// @param string $original original string to translate from MO file. Might contain
        #// 0x04 as context separator or 0x00 as singular/plural separator
        #// @param string $translation translation string from MO file. Might contain
        #// 0x00 as a plural translations separator
        #// @return Translation_Entry Entry instance.
        #//
        def make_entry(self, original=None, translation=None):
            
            entry = php_new_class("Translation_Entry", lambda : Translation_Entry())
            #// Look for context, separated by \4.
            parts = php_explode("", original)
            if (php_isset(lambda : parts[1])):
                original = parts[1]
                entry.context = parts[0]
            # end if
            #// Look for plural original.
            parts = php_explode(" ", original)
            entry.singular = parts[0]
            if (php_isset(lambda : parts[1])):
                entry.is_plural = True
                entry.plural = parts[1]
            # end if
            #// Plural translations are also separated by \0.
            entry.translations = php_explode(" ", translation)
            return entry
        # end def make_entry
        #// 
        #// @param int $count
        #// @return string
        #//
        def select_plural_form(self, count=None):
            
            return self.gettext_select_plural_form(count)
        # end def select_plural_form
        #// 
        #// @return int
        #//
        def get_plural_forms_count(self):
            
            return self._nplurals
        # end def get_plural_forms_count
    # end class MO
# end if
