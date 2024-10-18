CONTROLLER_HOST=apt173 

./controller_setup.sh \
--username wbcheng \
--private_ssh_key_path "/users/wbcheng/.ssh/id_rsa" \
--controller_node $CONTROLLER_HOST.apt.emulab.net \
--git_email wcheng78@gatech.edu \
--swarm_node_number 6 \
--client_node_number 5
