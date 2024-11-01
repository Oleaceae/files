#set username number
EXPR_NAME=wbcheng-226837
CONTROLLER_HOST=ms1030
HOST_NAME=utah.cloudlab.us

# Clone git repo
git clone https://github.com/WindowsXp-Beta/SocialNetwork.git
mv SocialNetwork/* ~
rm -rf SocialNetwork

# Setup Java
tar -xzvf jdk1.8.0_241.tar.gz
mv jdk1.8.0_241 ~/RubbosClient/elba/rubbos
mv jdk-8u241-linux-x64.tar.gz ~/RubbosClient/rubbos
chmod +x ~/RubbosClient/elba/rubbos/jdk1.8.0_241/bin/java

# Move ctrl_setup.sh to ~
mv ctrl_setup.sh ..

# Change to dir ~
cd ~

# Change config
sed -i.bak 's/$your_cloud_lab_username/wbcheng/g' ./config/config.json
sed -i.bak "s/\$username-six_digit_number/$EXPR_NAME/g" ./config/config.json
sed -i.bak "s/\$host_ssh_name/$HOST_NAME/g" ./config/config.json

# Change hardcoded path
sed -i.bak 's/azhang/wbcheng/g' ./socialNetwork/runtime_files/rubbos.properties_1000

# Setup controller
exit
#./controller_setup.sh \
#--username wbcheng \
#--private_ssh_key_path "/users/wbcheng/.ssh/id_rsa" \
#--controller_node $CONTROLLER_HOST.$HOSTNAME \
#--git_email wcheng78@gatech.edu \
#--swarm_node_number 6 \
#--client_node_number 5
