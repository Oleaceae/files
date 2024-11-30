#set username number
ACCOUNT_NAME=wbcheng
EXPR_NAME=$ACCOUNT_NAME-234169
CONTROLLER_HOST=pc779
HOST_NAME=emulab.net

sudo apt update
sudo apt install -y python3-pip python2

# Setup ssh key
mv id_rsa* ~/.ssh

# Clone git repo
git clone https://github.com/WindowsXp-Beta/SocialNetwork.git
mv SocialNetwork/* ~
rm -rf SocialNetwork

# Setup Java
tar -xzvf jdk1.8.0_241.tar.gz
mv jdk1.8.0_241 ~/RubbosClient/elba/rubbos
mv jdk-8u241-linux-x64.tar.gz ~/RubbosClient/rubbos
chmod +x ~/RubbosClient/elba/rubbos/jdk1.8.0_241/bin/java

# Change to dir ~
cd ~

# Change config
sed -i "s/\$your_cloud_lab_username/$ACCOUNT_NAME/g" ./config/config.json
sed -i "s/\$username-six_digit_number/$EXPR_NAME/g" ./config/config.json
sed -i "s/\$host_ssh_name/$HOST_NAME/g" ./config/config.json

# Change hardcoded path
sed -i "s/azhang/$ACCOUNT_NAME/g" ./socialNetwork/runtime_files/rubbos.properties_1000

# Change controller_setup.sh
sed -i "98,105d" controller_setup.sh

# Setup Controller
./controller_setup.sh \
--username $ACCOUNT_NAME \
--private_ssh_key_path "/users/$ACCOUNT_NAME/.ssh/id_rsa" \
--controller_node $CONTROLLER_HOST.$HOST_NAME \
--git_email wcheng78@gatech.edu \
--swarm_node_number 6 \
--client_node_number 5

# Delete start.sh in setup_docker_dwarm.py before correcting swarm.yml hostname
cd ~/SetupScripts
sed -i "122d" setup_docker_swarm.py 
sed -i "118,119d" setup_docker_swarm.py 
sed -i "102d" setup_docker_swarm.py 

# Setup docker swarm environment
python setup_docker_swarm.py -a 10.10.1.1 -n 6 -cn 5

cd ~/DeathStarBench/socialNetwork
# Change docker-compose-swarm.yml
if [[ `hostname` == *"infosphere-pg0"* ]]; then
    # change infosphere to infosphere-pg0
    sed -i "s/\.infosphere\./\.infosphere-pg0\./g" ./docker-compose-swarm.yml
else
    # change infosphere-pg0 to infosphere
    sed -i "s/\.infosphere-pg0\./\.infosphere\./g" ./docker-compose-swarm.yml
fi

# [Optional] io_intensive and cpu_intensive is not used, comment out
sed -i "493,503s/^/#/" ./docker-compose-swarm.yml

# Move scripts to working dir
cd ~/files
mv *.py ~/DeathStarBench/socialNetwork
mv config.json ~/DeathStarBench/socialNetwork
mv compose-post.lua ~/DeathStarBench/socialNetwork/wrk2/scripts/social-network

echo "All Done"
echo "To start the swarm, switch to ~/DeathStarBench/socialNetwork and run \"sudo ./start.sh all\""
