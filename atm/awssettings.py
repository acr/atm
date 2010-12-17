# Copyright (C) Michigan State University 2010-2011

"""
A class that manages user credentials, image information and allowes pickeling
and unpickeling that information to/from disk
"""

import pickle
import os

class AwsAccount(object):
    def __init__(self, filename=None):
        self._USERKEY = 'AWSUSERS'
        self._IMAGEKEY = 'AWSIMAGES'
        self._ACCESSKEY = 'AK'
        self._SECRETKEY = 'SK'
        self._PKNAME = 'PKN'

        self._container = {
            self._USERKEY : {},
            self._IMAGEKEY : {}
            }

        if filename:
            self.load_settings(filename)

    def load_settings(self, filename):
        """
        Loads settings from a pickled file
        """
        if not os.path.isfile(filename):
            raise ValueError("'%s' is not a valid file" % filename)
        f = open(filename, 'r')
        self._container = pickle.load(f)
        f.close()

    def save_settings(self, filename):
        """
        Saves settings to a pickled file
        """
        f = open(filename, 'w')
        pickle.dump(self._container, f)
        f.close()

    def add_user(self, username, accesskey, secretkey, pkname):
        """
        Adds a user entry to the container
        """
        self._container[self._USERKEY][username] = {self._ACCESSKEY: accesskey,
                                              self._SECRETKEY: secretkey,
                                              self._PKNAME: pkname
                                              }

    def del_user(self, username):
        """
        Removes a user entry from the container
        """
        try:
            self._container[self._USERKEY].pop(username)
        except KeyError:
            pass

    def get_user(self, username):
        """
        Returns an ordered tuple of the user information:
        (username, accesskey, secretkey, pkname)
        or return None if the username does not exist in the container
        """
        result = None
        try:
            subres = self._container[self._USERKEY][username]
            result = (username, subres[self._ACCESSKEY],
                      subres[self._SECRETKEY], subres[self._PKNAME])
        except KeyError:
            pass

        return result

    def get_all_users(self):
        """
        Returns the dictionary keys holding all the user information
        """
        return self._container[self._USERKEY].keys()

    def add_image(self, imagename, imageid):
        """
        Adds and image entry to the conainer
        """
        self._container[self._IMAGEKEY][imagename] = imageid

    def del_image(self, imagename):
        """
        Removes an image from the container
        """
        try:
            self._container[self._IMAGEKEY].pop(imagename)
        except KeyError:
            pass

    def get_image(self, imagename):
        """
        Returns an ordered tuple of image information:
        (imagname, imageid)
        or None if the image does not exist in the container
        """
        result = None
        try:
            result = (imagename, self._container[self._IMAGEKEY][imagename])
        except KeyError:
            pass

        return result

    def get_all_images(self):
        """
        Returns the dictionary keys holding the image information
        """
        return self._container[self._IMAGEKEY].keys()
