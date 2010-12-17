# Copyright (C) Michigan State University 2010-2011

"""
All the commands that can be used by Twill to control aws images
"""

import twill, twill.utils
import awssettings
from boto.ec2.connection import EC2Connection
import time
import sys

# export:
__all__ = ['loadsettings',
           'savesettings',
           'adduser',
           'deluser',
           'showuser',
           'showusers',
           'addimage',
           'delimage',
           'showimage',
           'showimages',
           'startinstance',
           'stopinstance',
           'stopinstances',
           'showinstances'
           ]

settings = awssettings.AwsAccount()

def loadsettings(filename):
    """
    Loads settings from a filename
    """
    settings.load_settings(filename)

def savesettings(filename):
    """
    Saves the settings to a filename
    """
    settings.save_settings(filename)

def adduser(username, accesskey, secretkey, pkname=None):
    """
    Adds a user and their settings
    """
    settings.add_user(username, accesskey, secretkey, pkname)

def deluser(username):
    """
    Deletes a user and their settings
    """
    settings.del_user(username)

def showuser(username):
    """
    Prints the user information of a given user to stdout
    """
    user = settings.get_user(username)
    if user:
        _print_user(user)
    else:
        print "No such user '%s'" % username

def showusers():
    """
    Prints all the user information to stdout
    """
    all_users = settings.get_all_users()
    for user in all_users:
        _print_user(settings.get_user(user))

def addimage(imagename, imageid):
    """
    Adds the AWS image information to the container
    """
    settings.add_image(imagename, imageid)

def delimage(imagename):
    """
    Deletes an image
    """
    settings.del_image(imagename)

def showimage(imagename):
    """
    Prints image information to stdout
    """
    image = settings.get_image(imagename)
    if image:
        _print_image(image)
    else:
        print "No such image '%s'" % imagename

def showimages():
    """
    Prints information on all images stored
    """
    images = settings.get_all_images()
    for image in images:
        _print_image(settings.get_image(image))

def startinstance(imagename, username=None, instance_type='m1.large'):
    """
    Starts an AWS instance from an image
    """
    if not settings.get_image(imagename):
        raise SystemExit("Invalid imagename '%s'" % imagename)

    username, conn = _getbotoconn(username)

    print "starting an instance from the %s image under the %s account of " \
        "type %s" % \
        (imagename, username, instance_type)

    username, accesskey, secretkey, pkname = settings.get_user(username)
    imagename, imageid = settings.get_image(imagename)

    image = conn.get_image(imageid)
    reservation = None
    if pkname:
        reservation = image.run(instance_type=instance_type, key_name=pkname)
    else:
        reservation = image.run(instance_type=instance_type)

    instance = reservation.instances[0]

    # The image has been started in the pending state, wait for it to transition
    # into the running state
    while True:
        if instance.update() == u'running':
            # [AN] it would be nice if the user knew it was still working
            break
        time.sleep(1)

    print ""
    print "Instance started"
    print "DNS name: %s" % instance.dns_name

def showinstances(username=None):
    """
    Prints information about all instances
    """
    username, conn = _getbotoconn(username)

    print "all instances running under the %s account" % username

    reservations = conn.get_all_instances()
    for reservation in reservations:
        _print_reservation(reservation)

def stopinstance(instanceid, username=None):
    """
    Stops a running AWS instance.
    """
    username, conn = _getbotoconn(username)
    print "stopping instance %s running under the %s account" % (instanceid,
                                                                 username)

    running_instances = _getrunninginstances(conn)

    if instanceid in running_instances:
        running_instances[instanceid].stop()
        print "instance %s stopped" % instanceid
    else:
        print "not instance %s found" % instanceid

def stopinstances(username=None):
    """
    Stops all running instances
    """
    username, conn = _getbotoconn(username)
    print "stopping instances running under the %s account" % username

    running_instances = _getrunninginstances(conn)
    for instid, instance in running_instances.iteritems():
        instance.stop()
        print "instance %s stopped" % instid

# utility functions
def _print_user(usertuple):
    """
    Function for printing a user tuple
    """
    if usertuple:
        print "username: %s\n" \
            "accesskey: %s\n" \
            "secretkey: %s\n" \
            "pkname:    %s\n" % usertuple

def _print_image(imagetuple):
    """
    Function for printing an image tuple
    """
    if imagetuple:
        print "imagename: %s\n" \
            "imageid: %s\n" % imagetuple

def _print_reservation(reservation):
    """
    Prints information on an AWS reservation. Only running instances are
    printed, all others are ignored
    """
    for inst in reservation.instances:
        if inst.state != u'running':
            continue
        print "ID:           %s" % inst.id
        print "state:        %s" % inst.state
        print "IP:           %s" % inst.ip_address
        print "private IP:   %s" % inst.private_ip_address
        print "DNS:          %s" % inst.public_dns_name
        print "private DNS:  %s" % inst.private_dns_name
        print "architecture: %s" % inst.architecture
        print "image ID:     %s" % inst.image_id
        print "class:        %s" % inst.instance_class
        print "type:         %s" % inst.instance_type
        print "key_name:     %s" % inst.key_name
        print "launch time:  %s" % inst.launch_time
        print ""

def _getbotoconn(username):
    """
    This utility function first tries to retrive proper AWS credentials given a
    username and then uses those proper AWS credentials to create and return a
    boto connection object. If username is None, the first user stored in the
    settings is loaded. If there are no users stored in the settings, and/or
    the username given is invalid, a ValueError is raised. The return value is
    a tuple containing the username used to create the connection object and
    the connection object like so:
    (username, connection_object)
    """
    user_settings = None

    if not username:
        try: # Try loading first user settings
            username = settings.get_all_users()[0]
            user_settings = settings.get_user(username)
        except IndexError:
            user_settings = None
            pass
    else:
        user_settings = settings.get_user(username)

    if not user_settings:
        raise ValueError('invalid user specified or no users saved')

    username, accesskey, secretkey, pkname = user_settings
    conn = EC2Connection(accesskey, secretkey)
    return (username, conn)

def _getrunninginstances(conn):
    """
    Returns all running instances in a dictionary with associations:
    instance-id: <instance_structure>
    """
    running_instances = {}

    reservations = conn.get_all_instances()
    for reservation in reservations:
        for instance in reservation.instances:
            if instance.state == u'running':
                running_instances[instance.id] = instance

    return running_instances
