#!/bin/bash

# for example, www.comp-int-hum.org
FQDN=$1
EMAIL=$2
PASS="st4rcod3r"

# Install and configure Postgresql
sudo amazon-linux-extras install -y postgresql11
sudo yum install -y emacs tmux python3 postgresql-server
sudo systemctl stop postgresql
sudo systemctl disable postgresql
sudo rm -rf /var/lib/pgsql/data
export PGSETUP_INITDB_OPTIONS="--auth=peer --auth-host=md5"
sudo -E postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
pushd /tmp
sudo -u postgres createuser -d cih
sudo -u postgres createdb -O cih cih
sudo -u postgres psql -c "ALTER USER cih WITH PASSWORD '${PASS}'"
popd
exit
# Set up working environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Install Elasticsearch and Kibana

sudo yum -q -y erase kibana elasticsearch
sudo rm -rf /etc/kibana /etc/elasticsearch /var/lib/kibana /var/lib/elasticsearch
sudo rpm --import https://artifacts.elastic.co/GPG-KEY-elasticsearch

sudo tee /etc/yum.repos.d/elasticsearch.repo >/dev/null <<EOF
[elasticsearch]
name=Elasticsearch repository for 7.x packages
baseurl=https://artifacts.elastic.co/packages/7.x/yum
gpgcheck=1
gpgkey=https://artifacts.elastic.co/GPG-KEY-elasticsearch
enabled=0
autorefresh=1
type=rpm-md
EOF

sudo tee /etc/yum.repos.d/kibana.repo >/dev/null <<EOF
[kibana-7.x]
name=Kibana repository for 7.x packages
baseurl=https://artifacts.elastic.co/packages/7.x/yum
gpgcheck=1
gpgkey=https://artifacts.elastic.co/GPG-KEY-elasticsearch
enabled=1
autorefresh=1
type=rpm-md
EOF

sudo yum install -y elasticsearch kibana

sudo systemctl daemon-reload
sudo systemctl enable elasticsearch.service
sudo systemctl enable kibana.service

sudo mkdir -p /etc/systemd/system/elasticsearch.service.d/
sudo tee /etc/systemd/system/elasticsearch.service.d/override.conf >/dev/null <<EOF
[Service]
LimitMEMLOCK=infinity
EOF

ES_HOME=/usr/share/elasticsearch
ES_PATH_CONF=/etc/elasticsearch
K_PATH_CONF=/etc/kibana
ES_TMP=/tmp/es_build

sudo -E mkdir -p ${ES_TMP}
sudo -E tee ${ES_TMP}/instance.yml >/dev/null <<EOF
instances:
  - name: "starcoder"
    dns: ["${FQDN}"]
EOF
sudo -E ${ES_HOME}/bin/elasticsearch-certutil cert --keep-ca-key --pem --in ${ES_TMP}/instance.yml --out ${ES_TMP}/certs.zip
sudo -E unzip ${ES_TMP}/certs.zip -d ${ES_TMP}/certs
sudo -E mkdir -p ${ES_PATH_CONF}/certs
sudo -E mkdir -p ${K_PATH_CONF}/certs
sudo -E cp ${ES_TMP}/certs/ca/ca* ${ES_TMP}/certs/starcoder/* ${ES_PATH_CONF}/certs
sudo -E cp ${ES_TMP}/certs/ca/ca* ${ES_TMP}/certs/starcoder/* ${K_PATH_CONF}/certs
sudo -E chown -R root:kibana ${K_PATH_CONF}/certs
sudo -E rm -rf ${ES_TMP}

sudo tee /etc/elasticsearch/jvm.options.d/overrides >/dev/null <<EOF
-Xms8g
-Xmx8g
EOF

sudo -E tee -a /etc/elasticsearch/elasticsearch.yml >/dev/null <<EOF
cluster.name: "cih"
discovery.type: single-node
network.host: 0.0.0.0
xpack.security.enabled: true
xpack.security.http.ssl.enabled: true
xpack.security.http.ssl.key: certs/starcoder.key
xpack.security.http.ssl.certificate: certs/starcoder.crt
xpack.security.http.ssl.certificate_authorities: certs/ca.crt
xpack.security.transport.ssl.enabled: true
xpack.security.transport.ssl.key: certs/starcoder.key
xpack.security.transport.ssl.certificate: certs/starcoder.crt
xpack.security.transport.ssl.certificate_authorities: certs/ca.crt
EOF

sudo systemctl start elasticsearch.service
sudo -E ${ES_HOME}/bin/elasticsearch-setup-passwords auto -b -u "https://${FQDN}:9200" > /tmp/pw
sudo -E mv /tmp/pw /etc/elasticsearch/passwords
sudo -E chown root:elasticsearch /etc/elasticsearch/passwords

sudo -E tee -a /etc/kibana/kibana.yml >/dev/null <<EOF
server.host: "0.0.0.0"
server.name: "CIH"
elasticsearch.hosts: ["https://localhost:9200"]
elasticsearch.username: "kibana_system"
elasticsearch.password: "${PASS}"
server.ssl.enabled: false
server.ssl.certificate: /etc/kibana/certs/starcoder.crt
server.ssl.key: /etc/kibana/certs/starcoder.key
elasticsearch.ssl.certificate: /etc/kibana/certs/starcoder.crt
elasticsearch.ssl.key: /etc/kibana/certs/starcoder.key
elasticsearch.ssl.verificationMode: none
EOF

sudo systemctl start kibana.service
sudo systemctl daemon-reload

git clone https://github.com/starcoder/cih-servers.git
git clone https://github.com/starcoder/starcoder-python.git
git clone https://github.com/starcoder/starcoder-experiments.git

pushd cih-servers
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
popd

sudo wget -r --no-parent -A 'epel-release-*.rpm' https://dl.fedoraproject.org/pub/epel/7/x86_64/Packages/e/
rpm -Uvh dl.fedoraproject.org/pub/epel/7/x86_64/Packages/e/epel-release-*.rpm
yum-config-manager --enable epel*
yum install -y certbot python2-certbot-nginx
sudo yum install nginx -y
sudo certbot --nginx -d ${FQDN} --agree-tos -m ${EMAIL} -n
