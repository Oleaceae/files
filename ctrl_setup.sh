CONTROLLER_HOST=ms1030
HOST_NAME=utah.cloudlab.us

./controller_setup.sh \
--username wbcheng \
--private_ssh_key_path "/users/wbcheng/.ssh/id_rsa" \
--controller_node $CONTROLLER_HOST.$HOST_NAME \
--git_email wcheng78@gatech.edu \
--swarm_node_number 6 \
--client_node_number 5
