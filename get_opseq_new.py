#!/usr/bin/env python
# coding:utf-8

import sys
import os
import shutil
import datetime
import logging
import random
import zipfile
import hashlib
import subprocess
import re
import threadpool
from tempfile import NamedTemporaryFile
import threading

# Global configuration

apk_file_directory = '../../../mnt/storage/yanjie/amd'
opseq_file_directory = '../../../mnt/storage/yanjie/amd_mal_opseq'
tmp_file_directory = 'decode_data/'

family_dict = {}
family_count = {}
total_pick = 0

def getApkList(rootDir, pick_str):
    """
    :param rootDir:  root directory of dataset
    :return: A filepath list of sample
    """
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        for filename in filenames:
            if pick_str in filename:  # exists .txt
                file = os.path.join(parent, filename)
                filePath.append(file)

    return filePath


# Exception class to signify an Apktool Exception
class ApkToolException(Exception):
    def __init__(self, command):
        self.command = command

    def __str__(self):
        return repr(self.command)


class Analysis:
    def __init__(self, path, opseq_path):
        self.dir = path
        self.opseq_path = opseq_path
        self.max_jobs = 20
        self.lock = threading.Lock()
        self.total_pick = 0
        self.developer = {}

    def apktool_decode_apk(self, apk_file, out_file, include_libs):
        '''
        :param apk_file: he whole path of apk file (include file name)
        :param out_file: path/decodefile.smail     (the decode file path)
        :param include_libs: None
        :return:
        '''
        # Runs the apktool on a given apk
        apktooldir = "../.local/bin"
        apktoolcmd = "{0}/apktool d -f {1} -o {2}".format(apktooldir, apk_file, out_file)
        # apktoolcmd = "apktool d -f {0} -o {1}".format(apk_file, out_file)
        # os.system used to execute the command
        print('apktoolcmd:', apktoolcmd)

        '''
        command example
        /usr/local/bin/apktool d -f small_proto_apks/malware/gen10_0e187773-d465-400f-942f-f95e52767222_app-release.apk -o decode_data/gen10_0e187773-d465-400f-942f-f95e52767222_app-release.apk.smali
        '''

        res = os.system(apktoolcmd)

        if res != 0: raise ApkToolException(apktoolcmd)

        # Checks if we should keep the smali files belonging to the android support libraries
        if not include_libs:
            # Don't keep the smali/android folder
            android_folder = os.path.join(out_file, "smali/android")
            if os.path.exists(android_folder):
                rm_cmd = "rm -r %s" % (android_folder)
                print('rmcmd:', rm_cmd)
                os.system(rm_cmd)


    def get_opcode_seq(self, smali_fname, dalvik_opcodes):
        # Returns opcode sequence created from smali file 'smali_fname'.
        '''
        :param smali_fname: the smali file path
        :param dalvik_opcodes: the opcode dict
        :return:
        '''
        opcode_seq = ''

        with open(smali_fname, mode="r") as bigfile:
            reader = bigfile.read()
            for i, part in enumerate(reader.split(".method")):
                add_newline = False
                if i != 0:
                    method_part = part.split(".end method")[0]
                    method_body = method_part.strip().split('\n')
                    for line in method_body:
                        line1 = line.strip()
                        if not line1.startswith('.') and not line1.startswith('#') and line1:
                            method_line = line1.split()
                            if method_line[0] in dalvik_opcodes:
                                add_newline = True
                                opcode_seq += dalvik_opcodes[method_line[0]]
                    if add_newline:
                        opcode_seq += '\n'
        return opcode_seq


    def decode_application(self, apk_file_location, tmp_file_directory, hash, include_libs):
        # Decodes the apk at apk_file_location and
        # stores the decoded folders in tmp_file_directory
        '''
        :param apk_file_location: the whole path of apk file (include file name)
        :param tmp_file_directory: the path of decode file location
        :param hash: the apk file name
        :param include_libs: None
        :return: the path of .smali file
        '''
        out_file_location = os.path.join(tmp_file_directory, hash + ".smali")
        try:
            self.apktool_decode_apk(apk_file_location, out_file_location, include_libs)
        except ApkToolException:
            # print "ApktoolException on decoding"
            logging.error("ApktoolException on decoding apk  {0} ".format(apk_file_location))
            pass
        return out_file_location


    def create_opcode_seq(self, decoded_dir, opseq_file_directory, apk_hash):
        # Returns true if creating opcode sequence file was successful,
        # searches all files in smali folder,
        # writes the coresponding opcode sequence to a .opseq file
        # and depending on the include_lib value,
        # it includes or excludes the support library files
        '''
           :param decoded_dir : the path of .smali file
           :param opseq_file_directory : the dict
           :param apk_hash : the apk file name
        '''
        apk_hash = apk_hash[:-4]
        dalvik_opcodes = {}
        # Reading Davlik opcodes into a dictionary
        with open("DalvikOpcodes.txt") as fop:
            for linee in fop:
                (key, val) = linee.split()
                dalvik_opcodes[key] = val
        try:
            smali_dir = os.path.join(decoded_dir, "smali")
            opseq_fname = os.path.join(opseq_file_directory, apk_hash + ".opseq")

            with open(opseq_fname, "a") as opseq_file:
                for root, dirs, fnames in os.walk(smali_dir):
                    for fname in fnames:
                        full_path = os.path.join(root, fname)
                        opseq_file.write(self.get_opcode_seq(full_path, dalvik_opcodes))
            opseq_file.close()

            return True
        except Exception as e:
            # print "Exception occured during opseq creation of apk " ,apk_hash
            logging.error('Exception occured during opseq creation {0}'.format(str(e)))
            return False


    def process_one(self, args):
        apk_file_location = args
        try:
            apk_hash = os.path.split(apk_file_location)[-1]
            decoded_location = self.decode_application(apk_file_location, tmp_file_directory, apk_hash, False)

            if (not os.path.exists(decoded_location) or not os.listdir(decoded_location)):
                # print "smali directory does not exist continue...."
                logging.error('NOT decoded directory: {0}'.format(apk_file_location))
                # print "NOT decoded directory:", apk_file_location
                return

            result = self.create_opcode_seq(decoded_location, opseq_file_directory, apk_hash)
            '''
               decode_location : the path of .smali file
               opseq_file_directory : the dict
               apk_hash : the apk file name
            '''

            if result:
                # print "opseq file for apk #",num_local," is created"
                logging.info('opseq file for apk is created')
            else:
                logging.error('opseq file creation was not successful')
                # print "opseq file creation was not successful"

            if os.path.exists(decoded_location):
                shutil.rmtree(decoded_location)

        except Exception as e:
            print(e, apk_file_location)
            return None


    def process(self, dir):
        print("Reading apks from", apk_file_directory)
        print("Decoding folder", tmp_file_directory)
        print("opseq folder", opseq_file_directory)
        include_libs = False
        if len(sys.argv) == 5:
            include_libs = ((sys.argv[4]) == "incl")
            print("Include Android support library smali files", include_libs)

        logging.basicConfig(filename=tmp_file_directory + '/opseq.log', level=logging.DEBUG)

        apks = getApkList(dir, '.apk')
        print("total files ", len(apks))
        args = [(apk) for apk in apks]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.process_one, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()


    def start(self):
        self.process(self.dir)


if __name__ == '__main__':
    if not os.path.exists(opseq_file_directory):
        os.mkdir(opseq_file_directory)
    analysis = Analysis(apk_file_directory, opseq_file_directory)
    analysis.start()