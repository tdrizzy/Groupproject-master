#!/usr/bin/env bash

export PATH=/opt/apps/soc09109/soc09109-env/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin:/opt/puppetlabs/bin

cd /opt/apps/soc09109/soc09109
source instance/env.sh
cd /opt/apps/soc09109/soc09109

python -m notify.main > /dev/null
