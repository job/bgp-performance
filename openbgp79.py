
from base import *
import json

class OpenBGP79(Container):
    CONTAINER_NAME = None
    GUEST_DIR = '/root/config'

    def __init__(self, host_dir, conf, image='bgperf/openbgp79'):
        super(OpenBGP79, self).__init__(self.CONTAINER_NAME, image, host_dir, self.GUEST_DIR, conf)

    @classmethod
    def build_image(cls, force=False, tag='bgperf/openbgp79', checkout='', nocache=False):

        cls.dockerfile = '''
FROM ubuntu:latest
EXPOSE 179
WORKDIR /root
RUN apt update && apt install -y autoconf build-essential wget flex git libreadline-dev libncurses5-dev libtool m4 unzip byacc libevent-dev
RUN groupadd _bgpd && \
   useradd -g _bgpd -s /sbin/nologin -d /var/empty -c 'OpenBGPD daemon' _bgpd && \
   mkdir -p /var/empty && \
   chown 0 /var/empty && \
   chgrp 0 /var/empty && \
   chmod 0755 /var/empty
RUN mkdir /etc/bgpd
RUN wget -q https://cdn.openbsd.org/pub/OpenBSD/OpenBGPD/openbgpd-{0}.tar.gz
RUN tar vfxz openbgpd-{0}.tar.gz
RUN cd /root/openbgpd-{0} && \
    YACC=byacc ./configure --sysconfdir=/etc/bgpd && \
    make && \
    make install
'''.format('7.9')
        super(OpenBGP79, cls).build_image(force, tag, nocache)


class OpenBGPTarget79(OpenBGP79, Target):
    
    CONTAINER_NAME = 'bgperf_openbgp79_target'
    CONFIG_FILE_NAME = 'bgpd.conf'

    def __init__(self, host_dir, conf, image='bgperf/openbgp79'):
        super(OpenBGPTarget79, self).__init__(host_dir, conf, image=image)

    def write_config(self):

        config = """ASN="{0}"

AS $ASN
router-id {1}
listen on {1}
fib-update no
""".format(self.conf['as'], self.conf['router-id'])

        def gen_neighbor_config(n):
            return ('''neighbor {0} {{
    remote-as {1}
    enforce neighbor-as no
    set nexthop self
}}
'''.format(n['router-id'], n['as']) )
    
        
        def gen_prefix_configs(n):
            pass

        def gen_filter(name, match):
            c = ['function {0}()'.format(name), '{']
            for typ, name in match:
                c.append(' if ! {0}() then return false;'.format(name))
            c.append('return true;')
            c.append('}')
            return '\n'.join(c) + '\n'

        def gen_prefix_filter(n, match):
            pass

        def gen_aspath_filter(n, match):
            pass

        def gen_community_filter(n, match):
            pass      

        def gen_ext_community_filter(n, match):
            pass   

        with open('{0}/{1}'.format(self.host_dir, self.CONFIG_FILE_NAME), 'w') as f:
            f.write(config)

            if 'policy' in self.scenario_global_conf:
                for k, v in self.scenario_global_conf['policy'].items():
                    match_info = []
                    for i, match in enumerate(v['match']):
                        n = '{0}_match_{1}'.format(k, i)
                        if match['type'] == 'prefix':
                            f.write(gen_prefix_filter(n, match))
                        elif match['type'] == 'as-path':
                            f.write(gen_aspath_filter(n, match))
                        elif match['type'] == 'community':
                            f.write(gen_community_filter(n, match))
                        elif match['type'] == 'ext-community':
                            f.write(gen_ext_community_filter(n, match))
                        match_info.append((match['type'], n))
                    f.write(gen_filter(k, match_info))

            for n in sorted(list(flatten(list(t.get('neighbors', {}).values()) for t in self.scenario_global_conf['testers'])) + [self.scenario_global_conf['monitor']], key=lambda n: n['as']):
                f.write(gen_neighbor_config(n))
            f.write('allow to any\n')
            
            if 'filter_test' in self.conf:
                f.write(self.get_filter_test_config())
                if self.conf['filter_test'] == 'ixp':
                    f.write("deny quick from any inet prefixlen > 24\n")
                    f.write('deny quick from any transit-as {174,701,1299,2914,3257,3320,3356,3491,4134,5511,6453,6461,6762,6830,7018}\n')
            else:
                f.write('allow from any\n')

            f.flush()

    def get_startup_cmd(self):
        return '\n'.join(
            ['#!/bin/bash',
             'ulimit -n 65536',
             '/usr/local/sbin/bgpd -v -f {guest_dir}/{config_file_name} -d > {guest_dir}/openbgp.log 2>&1']
        ).format(
            guest_dir=self.guest_dir,
            config_file_name=self.CONFIG_FILE_NAME,
            debug_level='info')

    def get_version_cmd(self):
        return "/usr/local/sbin/bgpctl -V"

    def exec_version_cmd(self):
        version = self.get_version_cmd()
        i= dckr.exec_create(container=self.name, cmd=version, stderr=True)
        return dckr.exec_start(i['Id'], stream=False, detach=False).decode('utf-8').strip('\n')

    def get_neighbors_state(self):
        neighbors_accepted = {}
        neighbors_received_full = {}
        neighbor_received_output = json.loads(self.local("/usr/local/sbin/bgpctl -j show neighbor").decode('utf-8'))
        for neigh in neighbor_received_output['neighbors']:
            neighbors_accepted[neigh['remote_addr']] = neigh['stats']['prefixes']['received']
            neighbors_received_full[neigh['remote_addr']] = False if neigh['stats']['update']['received']['eor'] == 0 else True
    

        return neighbors_received_full, neighbors_accepted


    def get_filter_test_config(self): 
        file = open("filters/openbgp.conf", mode='r')
        filters = file.read()
        file.close
        return filters
