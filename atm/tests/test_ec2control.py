import os
from atm import twillm

class Test_control(object):
    """
    Make sure that EC2 instances can be started and stopped correctly. The
    configuration file must exist in the folder the tests are
    being run in prior to starting the tests. This configuration file will
    contain sensitive user credentials, so it cannot be included with the
    source and must be generated per installation. The configuration file
    must be named '.atmconfig' and must contain informaion of the form:
    [awsuser]
    username = me
    secretkey = <your secret key>
    accesskey = <your access key>
    privatekeyname = <your private key>

    [awsimage]
    imagename = ubuntu1010x64
    imageid = ami-a0c83ec9
    """

    def test_start_stop(self):
        """
        Tests starting and stopping an aws instance
        """
        if not os.path.isfile(twillm.CONFIG_FILE):
            raise EnvironmentError("'%s' config file not found" % \
                                       twillm.CONFIG_FILE)

        twillm.use_aws_creds('me')

        assert twillm.showinstances() == 0, 'there should be 0 instances ' \
            'running, there are %d' % twillm.showinstances()
        twillm.startinstance('ubuntu1010x64')
        assert twillm.showinstances() == 1, 'there should be 1 instance ' \
            'running, there are %d' % twillm.showinstances()
        
        twillm.stopinstances()
        assert twillm.showinstances() == 0, 'there should be 0 instances ' \
            'running, there are %d' % twillm.showinstances()
