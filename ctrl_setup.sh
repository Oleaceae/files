CONTROLLER_NODE=pc755.emulab.net

./controller_setup.sh \
--username wbcheng \
--private_ssh_key_path "/users/wbcheng/.ssh/id_rsa" \
--controller_node $CONTROLLER_NODE \
--git_email wcheng78@gatech.edu \
--swarm_node_number 6 \
--client_node_number 5
