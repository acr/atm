# Copyright (C) Michigan State University 2010-2011

"""
A class that manages user credentials, image information and allowes pickeling
and unpickeling that information to/from disk
"""

import ConfigParser
import os

class AwsAccount(object):
    def __init__(self, filename):
        self._USERKEY = 'awsuser'
        self._IMAGEKEY = 'awsimage'
        self._IMAGENAME = 'imagename'
        self._IMAGEID = 'imageid'
        self._USERNAME = 'username'
        self._ACCESSKEY = 'accesskey'
        self._SECRETKEY = 'secretkey'
        self._PKNAME = 'privatekeyname'
        self._filename = filename
        self._numusers = 0
        self._numimgs = 0

        self._container = {
            self._USERKEY : {},
            self._IMAGEKEY : {}
            }

        if os.path.isfile(self._filename):
            self.load_settings()

    def load_settings(self):
        """
        Loads settings from a config file. This method initializes the internal
        dictionary of AWS information and initializes the 'num*' member
        variables to what was loaded from the config file
        """
        if not os.path.isfile(self._filename):
            raise ValueError("'%s' is not a valid file" % self._filename)

        self._numusers = 0
        self._numimgs = 0

        cf = ConfigParser.ConfigParser()
        cf.read(self._filename)

        for section in cf.sections():
            cfile_setting = dict(cf.items(section))
            if section.startswith(self._USERKEY):
                self._add_user_to_container(
                    cfile_setting[self._USERNAME],
                    cfile_setting[self._ACCESSKEY],
                    cfile_setting[self._SECRETKEY],
                    cfile_setting[self._PKNAME]
                    )
                self._numusers += 1
            elif section.startswith(self._IMAGEKEY):
                self._add_image_to_container(
                    cfile_setting[self._IMAGENAME],
                    cfile_setting[self._IMAGEID]
                    )
                self._numimgs += 1

    def save_settings(self):
        """
        Dumps the dictionary containing the AWS information into a config file
        """
        cf = ConfigParser.ConfigParser()
        # Save user information
        for usernum, username in enumerate(self._container[self._USERKEY]):
            section = '%s%d' % (self._USERKEY, usernum)
            cf.add_section(section)
            user_entry = self._container[self._USERKEY][username]
            cf.set(section, self._USERNAME, username)
            for option, value in user_entry.iteritems():
                cf.set(section, option, value)

        # Save image information
        for imagenum, imagename in enumerate(self._container[self._IMAGEKEY]):
            section = '%s%d' % (self._IMAGEKEY, imagenum)
            cf.add_section(section)
            imgid = self._container[self._IMAGEKEY][imagename]
            cf.set(section, self._IMAGENAME, imagename)
            cf.set(section, self._IMAGEID, imgid)

        f = open(self._filename, 'w')
        cf.write(f)
        f.close()

    def add_user(self, username, accesskey, secretkey, pkname):
        """
        Adds a user entry to the container
        """
        self._add_user_to_container(username, accesskey, secretkey, pkname)
        self.save_settings()

    def del_user(self, username):
        """
        Removes a user entry from the container
        """
        try:
            self._container[self._USERKEY].pop(username)
            self.save_settings()
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
        self._add_image_to_container(imagename, imageid)
        self.save_settings()

    def del_image(self, imagename):
        """
        Removes an image from the container
        """
        try:
            self._container[self._IMAGEKEY].pop(imagename)
            self.save_settings()
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

    # Utility methods
    def _add_user_to_container(self, username, accesskey, secretkey, pkname):
	"""
	Adds a user to the container
	"""
        self._container[self._USERKEY][username] = {self._ACCESSKEY: accesskey,
                                                    self._SECRETKEY: secretkey,
                                                    self._PKNAME: pkname
                                                    }

    def _add_image_to_container(self, imagename, imageid):
        """
        Adds an image to the container
        """
        self._container[self._IMAGEKEY][imagename] = imageid
